import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class SarvamClient:
    def __init__(self):
        self.api_key = settings.sarvam_api_key
        self.base_url = "https://api.sarvam.ai"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio bytes using Sarvam STT.
        Wrapped with retry logic (max 2 retries -> 3 attempts total) and exponential backoff.
        """
        # Sarvam speech-to-text-translate API endpoint
        url = f"{self.base_url}/speech-to-text"
        
        headers = {
            "api-subscription-key": self.api_key
        }
        
        # We assume the file is passed as a form-data payload, you might need to adjust
        # depending on exact Sarvam API spec for files, typically 'file' parameter.
        files = {
            'file': ('audio.wav', audio_bytes, 'audio/wav')
        }
        
        # Specifying language code might be required by Sarvam API.
        # Often hi-IN for Hindi.
        data = {
            'language_code': 'hi-IN'
        }
        
        # Add explicit timeout
        response = requests.post(url, headers=headers, files=files, data=data, timeout=15.0)
        response.raise_for_status()
        
        result = response.json()
        return result.get("transcript", "")

sarvam_client = SarvamClient()
