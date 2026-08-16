import os
import requests
import base64
from app.stt.base import STTBase

class SarvamClient(STTBase):
    def __init__(self):
        self.api_key = os.getenv("SARVAM_API_KEY")
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY environment variable is not set")
        self.url = "https://api.sarvam.ai/speech-to-text-translate"

    async def transcribe(self, audio_data: bytes) -> str:
        headers = {
            "api-subscription-key": self.api_key
        }
        
        payload = {
            "model": "saaras:v2.5",  # Adjust model as needed. The documentation says saaras:v1 or saaras:v3
            "prompt": ""
        }
        
        files = {
            "file": ("audio.wav", audio_data, "audio/wav")
        }
        
        response = requests.post(self.url, data=payload, files=files, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Sarvam API request failed with status {response.status_code}: {response.text}")
        
        result = response.json()
        return result.get("transcript", "")