# RAG-in-Goa: Voice-Enabled RAG System

## Overview
A voice-enabled Retrieval-Augmented Generation (RAG) system that transcribes user speech, retrieves relevant context from a dataset, and generates answers end-to-end.

## Architecture
![Architecture Diagram](docs/architecture.png)

## Setup
1. Clone the repository
2. Copy `.env.example` to `.env` and fill in the required environment variables
3. Run `docker-compose up --build` to start the backend, frontend, and vector database
4. Access the frontend at `http://localhost:3000`

## Latency Results
See `benchmarks/latency_report.md` for P50/P70/P100 latency measurements.

## Demo
Live demo available at: [Link to be added]

## Videos
- Team/process video: [Link to be added]
- Demo video: [Link to be added]

## Requirements
- Speech-to-text: Sarvam or ElevenLabs (configured via `.env`)
- Chunking: Multiple strategies (fixed-size, semantic, recursive, metadata-aware, sentence-window)
- Latency: Under 200ms end-to-end
- Harness: LangGraph orchestration with retries and error handling
- Guardrails: Input filtering, grounding checks, hallucination detection, refusal templates

## Dataset
We use the MSMARCO-XI dataset from Hugging Face: https://huggingface.co/datasets/ai4bharat/MSMARCO-XI