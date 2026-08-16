from sarvamai import AsyncSarvamAI
import inspect

client = AsyncSarvamAI(api_subscription_key="test")
print(inspect.signature(client.speech_to_text.transcribe))
