import os
import io
from app.stt.base import STTBase
from elevenlabs.client import AsyncElevenLabs

class ElevenLabsClient(STTBase):
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.client = AsyncElevenLabs(api_key=self.api_key) if self.api_key else None

    async def transcribe(self, audio_data: bytes) -> str:
        if not self.client:
            raise ValueError("ELEVENLABS_API_KEY environment variable is not set")

        file_obj = io.BytesIO(audio_data)
        file_obj.name = "audio.wav"

        try:
            response = await self.client.speech_to_text.convert(
                file=file_obj,
                model_id="scribe_v1",
            )

            if hasattr(response, "text"):
                return response.text
            elif isinstance(response, dict):
                return response.get("text", "")
            return str(response)
        except Exception as e:
            raise Exception(f"ElevenLabs SDK request failed: {str(e)}")