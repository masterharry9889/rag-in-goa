import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.harness.graph import create_rag_graph

async def test():
    app_graph = create_rag_graph()
    
    mock_wav = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    
    initial_state = {
        "audio_data": b'',
        "query": "hello",
        "transcript": "what is this about?",
        "chunks": [],
        "answer": "",
        "error": None,
        "retry_count": 0,
        "latency_ms": 0.0
    }
    
    print("Running graph...")
    result = await app_graph.ainvoke(initial_state)
    print("Result:", result)

if __name__ == "__main__":
    asyncio.run(test())
