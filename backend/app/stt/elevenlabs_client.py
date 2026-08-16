import os
import io
from app.stt.base import STTBase
from elevenlabs.client import AsyncElevenLabs

class ElevenLabsClient(STTBase):
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable is not set")
        self.client = AsyncElevenLabs(api_key=self.api_key)

    async def transcribe(self, audio_data: bytes) -> str:
        file_obj = io.BytesIO(audio_data)
        file_obj.name = "audio.wav"
        
        try:
            response = await self.client.speech_to_text.convert(
                file=file_obj,
                model_id="scribe_v1",  # Adjust model as needed
            )
            
            if hasattr(response, "text"):
                return response.text
            elif isinstance(response, dict):
                return response.get("text", "")
            return str(response)
        except Exception as e:
            raise Exception(f"ElevenLabs SDK request failed: {str(e)}")