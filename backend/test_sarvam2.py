import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
from app.stt.sarvam_client import SarvamClient

async def test():
    client = SarvamClient()
    mock_wav = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    print("Sending mock wav to Sarvam API...")
    try:
        result = await client.transcribe(mock_wav)
        print("Success!", result)
    except Exception as e:
        print("Error:", repr(e))

if __name__ == "__main__":
    asyncio.run(test())
