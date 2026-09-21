# diffusiongemma/ — Jev-style System One reads on llama.cpp

Code for [../DIFFUSIONGEMMA.md](../DIFFUSIONGEMMA.md). Read that first: it covers the why, the numbers, and the caveats.

| File | What it does |
|---|---|
| `build.sh` | Fetches llama.cpp PR #24423 (DiffusionGemma, unmerged) into `../build/llama.cpp-diffusiongemma`, grafts in `dg-systemone-server`, and builds for CUDA sm_120 |
| `dg-systemone-server.cpp` | JSON-lines read server: prefill the prompt once, run one bidirectional canvas pass, return log-probs at the answer slots. Honours `-ngl`, `--n-cpu-moe`, `-fa`, `-ub`, `--no-op-offload`. |
| `openjev_llamacpp.py` | Runs [OpenJev](https://github.com/razorback16/openjev)'s Jev-compatible `/v1/systemone` API with this server as its backend (text only) |
| `systemone_bench.py` | Accuracy, calibration (ECE/Brier), and latency on 200 SST-2 + 200 AG News; autoregressive baselines through any llama-server |
| `results.json` | Every measured run, with the exact server arguments |
| `data/` | The fixed eval subsets (`random.seed(0)`) |

Quick start on an 8 GB NVIDIA GPU:

```bash
./build.sh
git clone https://github.com/razorback16/openjev ../build/openjev-src
uv venv .venv && uv pip install --python .venv/bin/python -e ../build/openjev-src
.venv/bin/python openjev_llamacpp.py -m <diffusiongemma-26B-A4B-it-Q4_K_M.gguf> \
    -ngl 99 --n-cpu-moe 20 -fa on -c 2048 -ub 512 --no-op-offload     # API on :8080
```
