from typing import Dict, List, Optional
from observability.latency_logger import LatencyLogger
import numpy as np

class MetricsStore:
    def __init__(self, latency_logger: LatencyLogger):
        self.latency_logger = latency_logger

    def compute_percentiles(self, stage: str, percentiles: List[int] = [50, 70, 100]) -> Dict[str, float]:
        """
        Compute the specified percentiles for a given stage.
        Returns a dictionary mapping percentile to value (in milliseconds).
        """
        latencies = self.latency_logger.get_latencies(stage)
        if not latencies:
            return {f"p{p}": 0.0 for p in percentiles}
        
        # Using numpy for percentile calculation
        percentiles_values = np.percentile(latencies, percentiles)
        return {f"p{p}": float(val) for p, val in zip(percentiles, percentiles_values)}

    def get_all_metrics(self) -> Dict[str, Dict[str, float]]:
        """
        Compute metrics for all stages that have been logged.
        Returns a dictionary mapping stage to its percentile metrics.
        """
        # We don't have a direct way to get all stages from LatencyLogger without modifying it.
        # For simplicity, we'll assume we know the stages: stt, retrieval, guardrails, generation
        stages = ["stt", "retrieval", "guardrails", "generation"]
        metrics = {}
        for stage in stages:
            metrics[stage] = self.compute_percentiles(stage)
        return metrics

    def get_total_latency_percentiles(self, percentiles: List[int] = [50, 70, 100]) -> Dict[str, float]:
        """
        Compute the percentiles for the total latency (sum of all stages).
        Note: This assumes that the latency_logger has been logging the total latency per request.
        In our current setup, we are logging per stage and accumulating in the state.
        We would need to log the total latency per request to compute this accurately.
        For now, we return zeros as a placeholder.
        """
        # TODO: Implement total latency tracking
        return {f"p{p}": 0.0 for p in percentiles}