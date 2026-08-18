#!/bin/bash
set -e

export PYTHONPATH="."
python app/latency/benchmark.py
