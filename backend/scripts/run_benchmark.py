"""
Script to run benchmarks on the RAG pipeline.
Runs N test queries and outputs P50/P70/P100 latency report.
"""
import time
import json
import asyncio
import os
from typing import List, Dict
from harness.graph import create_rag_graph
from observability.latency_logger import LatencyLogger
from observability.metrics_store import MetricsStore
from indexing.vector_store import VectorStore
from indexing.embedder import Embedder
from scripts.download_dataset import download_dataset
from scripts.build_index import build_index

async def run_benchmark(num_queries: int = 100):
    """Run benchmark on the RAG pipeline."""
    # Initialize the RAG graph
    app = create_rag_graph()

    # Initialize observability components
    latency_logger = LatencyLogger()
    metrics_store = MetricsStore(latency_logger)

    # Define paths
    vector_store_path = os.getenv("VECTOR_DB_PATH", "./data/processed/vector_db")
    index_exists = os.path.exists(f"{vector_store_path}.index") and os.path.exists(f"{vector_store_path}_texts.json")

    # If the vector store doesn't exist, build it with a small subset
    if not index_exists:
        print("Vector store not found. Building index with a subset of the dataset...")
        # Download a small subset of the dataset for building the index
        dataset_for_index = download_dataset(limit=100)  # Limit to 100 for quick indexing
        # Build the index (this function will chunk, embed, and store)
        build_index(dataset=dataset_for_index, vector_store_path=vector_store_path)
        print("Index built.")
    else:
        print("Using existing vector store.")

    # Download dataset for benchmark queries
    print(f"Downloading dataset for {num_queries} benchmark queries...")
    dataset_queries = download_dataset(limit=num_queries)
    # Extract queries from the dataset
    test_queries = []
    for example in dataset_queries:
        # Assuming the dataset has a 'query' field
        if 'query' in example:
            test_queries.append(example['query'])
        else:
            # Fallback: if no 'query' field, try to find a suitable field
            # For MSMARCO-XI, the field might be 'question' or similar
            for key in ['question', 'query', 'text']:
                if key in example:
                    test_queries.append(example[key])
                    break
            else:
                # If none found, use a placeholder
                test_queries.append("What is the capital of India?")
    # Ensure we have exactly num_queries
    test_queries = test_queries[:num_queries]
    if len(test_queries) < num_queries:
        # Repeat if necessary
        repeats = (num_queries + len(test_queries) - 1) // len(test_queries)
        test_queries = (test_queries * repeats)[:num_queries]

    results = []

    for i, query in enumerate(test_queries):
        # In a real implementation, we would need to convert text to audio for STT
        # For now, we'll simulate by providing the query directly as transcript
        # and skipping the STT node (or we could mock the STT node)
        initial_state = {
            "query": query,
            "transcript": query,  # Simulating that STT returned the query as transcript
            "audio_data": b"fake audio data",  # Placeholder
            "chunks": [],
            "answer": "",
            "error": None,
            "retry_count": 0,
            "latency_ms": 0.0
        }

        start_time = time.time()
        try:
            # Run the graph
            final_state = await app.ainvoke(initial_state)
            total_latency = (time.time() - start_time) * 1000

            # Log the total latency (we would need to modify the graph to log this)
            # For now, we'll just store it
            results.append({
                "query": query,
                "latency_ms": total_latency,
                "answer": final_state.get("answer", ""),
                "error": final_state.get("error")
            })

            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{num_queries} queries")

        except Exception as e:
            print(f"Error processing query {i}: {e}")
            results.append({
                "query": query,
                "latency_ms": 0,
                "answer": "",
                "error": str(e)
            })

    # Calculate percentiles
    latencies = [r["latency_ms"] for r in results if r["latency_ms"] > 0]
    if latencies:
        import numpy as np
        p50 = np.percentile(latencies, 50)
        p70 = np.percentile(latencies, 70)
        p100 = np.percentile(latencies, 100)
    else:
        p50 = p70 = p100 = 0.0

    # Generate report
    report = {
        "benchmark_config": {
            "num_queries": num_queries,
            "timestamp": time.time()
        },
        "latency_metrics": {
            "p50_ms": round(p50, 2),
            "p70_ms": round(p70, 2),
            "p100_ms": round(p100, 2)
        },
        "summary": {
            "total_queries": num_queries,
            "successful_queries": len([r for r in results if r["error"] is None]),
            "failed_queries": len([r for r in results if r["error"] is not None])
        }
    }

    # Save report
    os.makedirs("../benchmarks", exist_ok=True)
    with open("../benchmarks/latency_report.md", "w") as f:
        f.write("# Latency Benchmark Report\n\n")
        f.write(f"**Timestamp:** {time.ctime()}\n\n")
        f.write(f"**Number of Queries:** {num_queries}\n\n")
        f.write("## Latency Metrics (milliseconds)\n\n")
        f.write(f"- **P50:** {report['latency_metrics']['p50_ms']} ms\n")
        f.write(f"- **P70:** {report['latency_metrics']['p70_ms']} ms\n")
        f.write(f"- **P100:** {report['latency_metrics']['p100_ms']} ms\n\n")
        f.write("## Summary\n\n")
        f.write(f"- **Successful Queries:** {report['summary']['successful_queries']}\n")
        f.write(f"- **Failed Queries:** {report['summary']['failed_queries']}\n")

    print("Benchmark completed. Report saved to benchmarks/latency_report.md")
    return report

if __name__ == "__main__":
    asyncio.run(run_benchmark())