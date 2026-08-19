#!/bin/bash
set -e

echo "=== 1. System dependencies installation ==="
apt-get update -qq && apt-get install -y -qq zstd

if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama already installed, skipping."
fi

pip install nvidia-ml-py psutil httpx

echo "=== 2. Starting Ollama server in background ==="
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve &
    sleep 5
else
    echo "Ollama server already running, skipping."
fi

echo "=== 3. Pulling LLM models ==="
ollama pull mistral
#ollama pull qwen2.5:7b
#ollama pull llama3
#ollama pull gemma2:2b
#ollama pull phi3:mini

echo "=== 4. Executing latency tests ==="
export PYTHONPATH="$PWD:$PYTHONPATH"
python3 experiments/run_latency_test.py