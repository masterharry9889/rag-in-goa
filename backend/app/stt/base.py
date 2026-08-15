from abc import ABC, abstractmethod

class STTBase(ABC):
    @abstractmethod
    async def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio data to text."""
        pass