import os
import io
from app.stt.base import STTBase
from dotenv import load_dotenv
from sarvamai import AsyncSarvamAI

load_dotenv()

class SarvamClient(STTBase):
    def __init__(self):
        self.api_key = os.getenv("SARVAM_API_KEY")
        self.client = AsyncSarvamAI(api_subscription_key=self.api_key) if self.api_key else None

    async def transcribe(self, audio_data: bytes) -> str:
        if not self.client:
            raise ValueError("SARVAM_API_KEY environment variable is not set")

        file_obj = io.BytesIO(audio_data)
        file_obj.name = "audio.wav"

        try:
            response = await self.client.speech_to_text.transcribe(
                file=file_obj,
                model="saaras:v3",
                mode="transcribe"
            )

            if hasattr(response, "transcript"):
                return response.transcript
            elif isinstance(response, dict):
                return response.get("transcript", "")
            return str(response)
        except Exception as e:
            raise Exception(f"Sarvam SDK request failed: {str(e)}")