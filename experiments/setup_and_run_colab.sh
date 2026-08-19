#!/bin/bash

echo "=== 1. System dependencies installation ==="
curl -fsSL https://ollama.com/install.sh | sh
pip install nvidia-ml-py psutil httpx

echo "=== 2. Starting Ollama server in background ==="
ollama serve &
sleep 5

echo "=== 3. Pulling LLM models ==="
ollama pull mistral
#ollama pull qwen2.5:7b
#ollama pull llama3
#ollama pull gemma2:2b
#ollama pull phi3:mini

echo "=== 4. Executing latency tests ==="
python3 experiments/run_latency_test.py