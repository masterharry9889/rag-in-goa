import time
import statistics
from typing import List, Dict
from app.graph.build_graph import build_graph
from app.graph.state import GraphState
from app.latency.report import percentiles, write_report
import numpy as np

def run_benchmark_queries(graph, queries: List[str]) -> List[float]:
    """
    Run a list of queries through the graph and retrieve retrieval latency.
    Returns list of retrieval latencies in milliseconds.
    """
    latencies = []
    
    for query in queries:
        initial_state: GraphState = {
            "audio_data": None,
            "text_query": query,
            "transcribed_text": None,
            "chunks": None,
            "retrieved_texts": None,
            "generated_answer": None,
            "input_guard_passed": None,
            "output_guard_passed": None,
            "refusal_reason": None,
            "final_answer": None,
            "citations": None,
            "latency_trace": {}
        }
        
        try:
            result = graph.invoke(initial_state)
            if "latency_trace" in result and "retrieve" in result["latency_trace"]:
                latencies.append(result["latency_trace"]["retrieve"])
        except Exception as e:
            print(f"Error processing query '{query[:50]}...': {e}")
            continue
            
    return latencies

def run_benchmark():
    print("Loading held-out queries for benchmark...")
    
    sample_queries = [
        "भारत की राजधानी क्या है?",
        "हिंदी भाषा में कितने vowel हैं?",
        "महात्मा गांधी कब पैदा हुए?",
        "गंगा नदी कहाँ से शुरू होती है?",
        "भारत में कितने राज्य हैं?",
        "सूर्य सबसे近ी नक्षत्र कौन सा है?",
        "पानी का सूत्र क्या है?",
        "मानव शरीर में कितनी हड्डियाँ होती हैं?",
        "भारत का राष्ट्रीय पक्षी कौन सा है?",
        "इंटरनेट किसने खोजा?",
    ] * 5  # 50 queries
    
    print(f"Running benchmark on {len(sample_queries)} queries...")
    
    graph = build_graph()
    retrieval_latencies = run_benchmark_queries(graph, sample_queries)
    stats = percentiles(retrieval_latencies)
    
    print("\n=== RETRIEVAL LATENCY BENCHMARK RESULTS ===")
    print(f"Number of queries: {stats['n']}")
    print(f"P50 latency: {stats['p50']:.2f} ms")
    print(f"P70 latency: {stats['p70']:.2f} ms")
    print(f"P100 latency: {stats['p100']:.2f} ms")
    print(f"Target P70: < 200 ms")
    print(f"Meets target: {'YES' if stats['p70'] < 200 else 'NO'}")
    
    write_report(stats, retrieval_latencies, prefix="retrieval")
    return stats

if __name__ == "__main__":
    run_benchmark()