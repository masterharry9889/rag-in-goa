$ErrorActionPreference = "Stop"

$env:PYTHONPATH = "."
python app/latency/benchmark.py
