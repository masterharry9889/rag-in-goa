import pytest
from app.latency.benchmark import run_benchmark

def test_latency_budget():
    """
    Fails CI if retrieval P70 latency > 200ms
    """
    stats = run_benchmark()
    
    assert stats["p70"] < 200, f"Retrieval P70 latency {stats['p70']}ms exceeds 200ms budget!"
