import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("SARVAM_API_KEY")
url = "https://api.sarvam.ai/speech-to-text-translate"

# A valid tiny wave file
mock_wav = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
audio_base64 = base64.b64encode(mock_wav).decode('utf-8')

payload = {
    "file": audio_base64, # Note: Sarvam API actually expects form-data for files usually, but let's see. Wait, in sarvam_client.py it sends json payload.
}
