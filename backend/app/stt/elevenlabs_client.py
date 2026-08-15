import os
import requests
import base64
from stt.base import STTBase

class ElevenLabsClient(STTBase):
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable is not set")
        # ElevenLabs API endpoint for speech to text
        self.url = "https://api.elevenlabs.io/v1/speech-to-text"

    async def transcribe(self, audio_data: bytes) -> str:
        # Encode the audio data to base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "audio": audio_base64,
            # You might need to specify the model_id, etc. Check ElevenLabs documentation.
            "model_id": "scribe_v1"  # Example, adjust as needed
        }
        
        response = requests.post(self.url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception(f"ElevenLabs API request failed with status {response.status_code}: {response.text}")
        
        result = response.json()
        # Adjust based on the actual ElevenLabs API response format
        return result.get("text", "")