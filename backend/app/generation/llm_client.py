import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMClient:
    def __init__(self, provider: str = None, api_key: str = None):
        """
        Initialize the LLM client.
        :param provider: The LLM provider (e.g., 'openai', 'anthropic', 'groq')
        :param api_key: The API key for the provider. If not provided, it will be read from environment variables.
        """
        self.provider = provider or os.getenv("LLM_PROVIDER", "openai")
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
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _initialize_client(self):
        """Initialize the LLM client based on the provider."""
        if self.provider == "openai":
            try:
                from openai import OpenAI
                return OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("OpenAI package not installed. Install it with 'pip install openai'")
        elif self.provider == "anthropic":
            try:
                import anthropic
                return anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("Anthropic package not installed. Install it with 'pip install anthropic'")
        elif self.provider == "groq":
            try:
                from groq import Groq
                return Groq(api_key=self.api_key)
            except ImportError:
                raise ImportError("Groq package not installed. Install it with 'pip install groq'")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """
        Generate text from the LLM.
        :param prompt: The prompt to send to the LLM.
        :param max_tokens: Maximum number of tokens to generate.
        :param temperature: Sampling temperature.
        :return: The generated text.
        """
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # You can change this to a different model
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # You can change this to a different model
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        elif self.provider == "groq":
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",  # You can change this to a different model
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")