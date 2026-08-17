import os
import yaml
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMClient:
    def __init__(self, provider: str = None, api_key: str = None):
        """
        Initialize the LLM client.
        :param provider: The LLM provider (e.g., 'openai', 'anthropic', 'groq', 'mistral')
        :param api_key: The API key for the provider. If not provided, it will be read from environment variables.
        """
        # Read defaults from config
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.yaml")
        self.config = {}
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
                if config_data and "generation" in config_data:
                    self.config = config_data["generation"]
        except Exception:
            pass

        self.provider = provider or os.getenv("LLM_PROVIDER", self.config.get("provider", "openai"))
        
        default_model = "gpt-3.5-turbo"
        if self.provider == "mistral":
            default_model = "mistral-small-latest"
        elif self.provider == "groq":
            default_model = "mixtral-8x7b-32768"
        elif self.provider == "anthropic":
            default_model = "claude-3-haiku-20240307"
            
        config_model = self.config.get("model", default_model)
        if self.provider == "groq" and "mistral" in config_model:
            config_model = "mixtral-8x7b-32768"
            
        self.model = config_model
        self.api_endpoint = self.config.get("api_endpoint")
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 500)
        self.timeout_seconds = self.config.get("timeout_seconds", 15)

        self.api_key = api_key or self._get_api_key()
        self.client = self._initialize_client()

    def _get_api_key(self) -> str:
        """Get the API key based on the provider."""
        if self.provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif self.provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        elif self.provider == "groq":
            return os.getenv("GROQ_API_KEY")
        elif self.provider == "mistral":
            return os.getenv("MISTRAL_API_KEY")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _initialize_client(self):
        """Initialize the LLM client based on the provider."""
        if not self.api_key:
            return None

        if self.provider in ["openai", "mistral"]:
            try:
                from openai import OpenAI
                client_kwargs = {"api_key": self.api_key, "timeout": self.timeout_seconds}
                if self.api_endpoint and self.provider == "mistral":
                    base_url = self.api_endpoint.replace("/chat/completions", "") if "/chat/completions" in self.api_endpoint else self.api_endpoint
                    client_kwargs["base_url"] = base_url
                return OpenAI(**client_kwargs)
            except ImportError:
                raise ImportError("OpenAI package not installed. Install it with 'pip install openai'")
        elif self.provider == "anthropic":
            try:
                import anthropic
                return anthropic.Anthropic(api_key=self.api_key, timeout=self.timeout_seconds)
            except ImportError:
                raise ImportError("Anthropic package not installed. Install it with 'pip install anthropic'")
        elif self.provider == "groq":
            try:
                from groq import Groq
                return Groq(api_key=self.api_key, timeout=self.timeout_seconds)
            except ImportError:
                raise ImportError("Groq package not installed. Install it with 'pip install groq'")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate(self, prompt: str, max_tokens: int = None, temperature: float = None) -> str:
        """
        Generate text from the LLM.
        :param prompt: The prompt to send to the LLM.
        :param max_tokens: Maximum number of tokens to generate.
        :param temperature: Sampling temperature.
        :return: The generated text.
        """
        if not self.client:
            return (
                "The app is running in demo mode because no API key is configured for the selected "
                "LLM provider. Add the provider key to the backend environment to enable live generation."
            )

        max_t = max_tokens if max_tokens is not None else self.max_tokens
        temp = temperature if temperature is not None else self.temperature

        if self.provider in ["openai", "mistral"]:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_t,
                temperature=temp
            )
            return response.choices[0].message.content.strip()
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_t,
                temperature=temp,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        elif self.provider == "groq":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_t,
                temperature=temp
            )
            return response.choices[0].message.content.strip()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")