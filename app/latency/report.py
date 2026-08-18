import json
import csv
import numpy as np
from typing import List, Dict

def percentiles(latencies_ms: List[float]) -> Dict[str, float]:
    """
    Computes P50/P70/P100 from a list of latencies.
    """
    if not latencies_ms:
        return {"p50": 0.0, "p70": 0.0, "p100": 0.0, "n": 0}
        
    return {
        "p50": float(np.percentile(latencies_ms, 50)),
        "p70": float(np.percentile(latencies_ms, 70)),
        "p100": float(np.max(latencies_ms)),
        "n": len(latencies_ms),
    }

def write_report(stats: Dict[str, float], latencies: List[float], prefix: str = "retrieval"):
    """
    Writes the latencies and percentiles to JSON and CSV.
    """
    # Write JSON
    with open(f"{prefix}_latency_report.json", "w") as f:
        json.update = {"stats": stats, "raw_latencies": latencies}
        json.dump(json.update, f, indent=4)
        
    # Write CSV for percentiles
    with open(f"{prefix}_latency_stats.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value (ms)"])
        writer.writerow(["P50", f"{stats['p50']:.2f}"])
        writer.writerow(["P70", f"{stats['p70']:.2f}"])
        writer.writerow(["P100", f"{stats['p100']:.2f}"])
        writer.writerow(["N", f"{stats['n']}"])
        
    print(f"Reports saved as {prefix}_latency_report.json and {prefix}_latency_stats.csv")
