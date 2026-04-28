#!/usr/bin/env bash
# Benchmark a GGUF model on this laptop with llama.cpp + CUDA.
# Usage:  ./run_bench.sh <gguf_path> [n_gpu_layers]
# Example: ./run_bench.sh models/qwen3-8b/*Q4_K_M*.gguf 99

set -euo pipefail

LLAMA_DIR="/home/ubuntu/workspace/projects/all-about-ai/llm-inference/build/llama.cpp/build-cuda/bin"
MODEL_RAW="${1:?usage: run_bench.sh <gguf_path> [ngl]}"
MODEL="$(readlink -f "$MODEL_RAW")"   # resolve to absolute path before cd
NGL="${2:-99}"   # 99 = offload all layers to GPU; reduce if it OOMs

if [[ ! -f "$MODEL" ]]; then
  echo "Model file not found: $MODEL" >&2
  exit 1
fi

cd "$LLAMA_DIR"
export LD_LIBRARY_PATH="$LLAMA_DIR:${LD_LIBRARY_PATH:-}"

echo "=== Model:    $MODEL"
echo "=== n_gpu_layers: $NGL"
echo "=== Started:  $(date)"
echo

# llama-bench runs a fixed prompt-processing + token-generation benchmark.
./llama-bench \
  -m "$MODEL" \
  -ngl "$NGL" \
  -p 512 \
  -n 128 \
  -t "$(nproc)" \
  -r 2

echo
echo "=== Finished: $(date)"
