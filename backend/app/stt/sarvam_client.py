import os
import requests
import base64
from app.stt.base import STTBase

class SarvamClient(STTBase):
    def __init__(self):
        self.api_key = os.getenv("SARVAM_API_KEY")
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY environment variable is not set")
        self.url = "https://api.sarvam.ai/speech-to-text"  # Example endpoint, adjust as needed

    async def transcribe(self, audio_data: bytes) -> str:
        # Encode the audio data to base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "audio": audio_base64,
            "language_code": "en-IN"  # Example, adjust as needed
        }
        
        response = requests.post(self.url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Sarvam API request failed with status {response.status_code}: {response.text}")
        
        result = response.json()
        # Assuming the response has a key 'transcript' or similar
        # Adjust based on the actual Sarvam API response format
        return result.get("transcript", "")