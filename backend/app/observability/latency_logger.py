import time
from typing import Dict, List
from collections import defaultdict

class LatencyLogger:
    def __init__(self):
        self.latencies: Dict[str, List[float]] = defaultdict(list)

    def log(self, stage: str, latency_ms: float):
        """Log latency for a given stage."""
        self.latencies[stage].append(latency_ms)

    def get_latencies(self, stage: str) -> List[float]:
        """Get all latencies for a stage."""
        return self.latencies.get(stage, [])

    def clear(self):
        """Clear all logged latencies."""
        self.latencies.clear()