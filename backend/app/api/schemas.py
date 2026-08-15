from pydantic import BaseModel

class VoiceQueryRequest(BaseModel):
    audio_data: str  # Base64 encoded audio data

class VoiceQueryResponse(BaseModel):
    transcript: str
    answer: str
    latency_ms: float