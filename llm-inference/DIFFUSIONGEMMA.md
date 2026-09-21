# DiffusionGemma as a Decision Engine — Jev, OpenJev, and an 8 GB Laptop

> A viral post says Google's open DiffusionGemma, run through a vLLM patch, is an open-source **Jev**: a "System One" model that answers structured questions in one parallel pass, "~0.2 s flat", with "zero hallucinations". The Docker image it points to needs a 24 GB+ GPU. So I ported the idea to llama.cpp, ran it on the 8 GB RTX 5060 laptop, and measured it against Qwen 3 30B-A3B on the same 400 labelled questions.

**⚠️ Every number below was measured on this laptop unless marked otherwise.** Vendor and upstream figures are labelled as theirs. There is a [claims audit](#8-a-claims-audit) near the end.

---

## 1. The idea in one picture

A chat LLM answers a multiple-choice question the way a person fills in a form with a typewriter: it writes `q1: B`, one character at a time. Then your code has to parse what it typed, and sometimes it typed `B: Sports` instead.

A **System One read** hands the model a form that's already typed out, with only the answer boxes left blank. The model looks at the whole form at once and says how likely each option is for each box. Nothing is written and nothing is parsed.

```
prompt  (read once, causally)            canvas  (one bidirectional pass)
┌─────────────────────────────────────┐ ┌───────────────────────────────────────────┐
│ system: Q1 Is the review positive?  │ │ <thought/> q 1 : [??] \n q 2 : [??] <turn|>│
│           yes / no                  │ │                   ▲                ▲       │
│         Q2 Topic? A sports B tech … │ │        noise token│      noise token│      │
│ user:   "Battery dies by noon…"     │ └───────────────────┼────────────────┼───────┘
└─────────────────────────────────────┘                     ▼                ▼
                                          P(yes)=0.00 P(no)=1.00   P(A)=.0003 P(B)=.9997
```

The trick only works on a **diffusion** language model. A diffusion model is trained to fill in a whole block of noisy positions at the same time, and every position can see every other one. DiffusionGemma is Google's open-weights 26B-A4B text-diffusion MoE (Apache-2.0), built on the Gemma 4 backbone.

---

## 2. Who's who

| Name | What it is | Status (Sep 2026) |
|---|---|---|
| **Jev** (TypeSafe AI) | Proprietary "System One model". You send a state plus typed questions (yes/no, `choice`, `score`) and get back probabilities and a confidence. It's trained with "reinforcement learning for calibrated decisions". The vendor claims 70–500 ms and a 40–200× speed-up over frontier LLMs. | Hosted API only |
| **DiffusionGemma 26B-A4B** | Google's open text-diffusion MoE: 128 experts, 8 active, ~3.8 B active parameters, 256-token canvas, Gemma 4 vocabulary (262 K) | Open weights |
| **vLLM PR [#57250](https://github.com/vllm-project/vllm/pull/57250)** (Matt Mastracci) | Adds seeded canvases, read-only steps, and step caps, so DiffusionGemma can do System One reads. Ships a prototype `/v1/systemone` example server. | **Open, not merged** |
| **[OpenJev](https://github.com/razorback16/openjev)** (razorback16) | Jev-compatible API server (TypeSafe's SDKs work unchanged) on top of that PR. Two backends: **vLLM** (NVIDIA, 24 GB+) and **MLX** (Apple silicon). | v0.3.0 |
| **llama.cpp PR [#24423](https://github.com/ggml-org/llama.cpp/pull/24423)** (Unsloth) | DiffusionGemma in llama.cpp: `llama-diffusion-cli` for chat, plus a prompt-KV cache (PREFILL → DECODE) | **Open, not merged** |
| **This repo** | `diffusiongemma/`: a llama.cpp System One read server and a third OpenJev backend, so the Jev API runs on an **8 GB** GPU | New |

---

## 3. Why not the one-liner Docker command

The post's command:

```bash
docker run --gpus all -p 8000:8000 -v ~/.cache/huggingface:/root/.cache/huggingface razorback16/openjev:latest
```

It has three problems:

1. **Wrong port.** OpenJev serves on **8080**. Port 8000 is the internal vLLM server, and it's bound to `127.0.0.1` inside the container, so mapping it exposes nothing. The project's own README uses `docker compose up -d`, which maps 8080 and sets `ipc: host`.
2. **It needs 24 GB+ of VRAM.** The default checkpoint is `nvidia/diffusiongemma-26B-A4B-it-NVFP4` on vLLM. vLLM has no equivalent of llama.cpp's `--n-cpu-moe`, so an 8 GB card can't load it.
3. **It's a fork of an unmerged PR.** That's fine for experiments, but it's not "vLLM supports this".

So on this laptop, the path is **llama.cpp PR #24423 + expert offload + a small read server**.

---

## 4. Running it on 8 GB

```bash
cd llm-inference/diffusiongemma
./build.sh                       # llama.cpp PR #24423 + dg-systemone-server, CUDA sm_120
hf download unsloth/diffusiongemma-26B-A4B-it-GGUF --include "*Q4_K_M*" --local-dir ../models/diffusiongemma-26b-a4b   # 16.8 GB

uv venv .venv && uv pip install --python .venv/bin/python -e ../build/openjev-src   # git clone razorback16/openjev there first
.venv/bin/python openjev_llamacpp.py \
    -m ../models/diffusiongemma-26b-a4b/diffusiongemma-26B-A4B-it-Q4_K_M.gguf \
    -ngl 99 --n-cpu-moe 20 -fa on -c 2048 -ub 512 --no-op-offload

curl -s localhost:8080/v1/systemone -H 'content-type: application/json' -d '{
  "model": "jev-latest",
  "state": "The new phone battery dies by noon and the screen cracked in a week. Avoid.",
  "questions": {
    "positive": {"type": "noul", "instructions": "Is the review positive?"},
    "topic":    {"type": "choice", "criteria": {"sports": "", "tech": "", "food": ""}},
    "stars":    {"type": "score", "instructions": "Stars the reviewer would give", "criteria": ["1","2","3","4","5"]}
  }}'
```

Measured answer from this exact request (abridged; 1.38 s including OpenJev's automatic re-reads): `positive: 0.0001` · `topic: tech (p=0.9998)` · `stars: score 0.10 on the 0–4 index scale, so "1" star at p=0.90, with 9 % on "2", confidence 0.79`. The less clear-cut question gets the lower confidence, which is the point.

The pieces:

| File | Role |
|---|---|
| [`diffusiongemma/dg-systemone-server.cpp`](diffusiongemma/dg-systemone-server.cpp) | A persistent process that loads the GGUF once. For each read it runs **PREFILL**(prompt) into the PR's prompt-KV store, then **one DECODE** over the canvas with self-conditioning off, and returns temperature-1 log-probs at the answer slots. A repeated prompt skips the prefill. |
| [`diffusiongemma/openjev_llamacpp.py`](diffusiongemma/openjev_llamacpp.py) | A third OpenJev backend. All of OpenJev's schema, template, noise seeding, re-read policy, and response shape are reused; only `one_read` is swapped. Text only: no images, `think`, `steps>1`, or `/v1/chat/completions`. |
| [`diffusiongemma/systemone_bench.py`](diffusiongemma/systemone_bench.py) | Accuracy, calibration, and latency benchmark, plus two autoregressive baselines. Results go to [`results.json`](diffusiongemma/results.json). |
| [`diffusiongemma/build.sh`](diffusiongemma/build.sh) | Fetches PR #24423 and grafts in the server. |

---

## 5. Three things I had to fix to make it fit — and one I couldn't

### 5.1 A 4.2 GB buffer that had nothing to do with the model

The first sweep ran out of memory below `--n-cpu-moe 28`. The failing allocation was a **4,218 MiB compute buffer**, not expert weights. llama.cpp reserves full-vocabulary logits for every row of a micro-batch: 262,144 vocab × 4 bytes = **1 MiB per token**. With the micro-batch equal to a 4,096-token context, that's 4 GiB before a single expert loads.

The fix was a 512-token micro-batch and chunked prefill. The canvas is at most 64 tokens for OpenJev, so it always fits. Result: **peak VRAM at `ncmoe=28` fell from 7,439 to 3,737 MiB**, and the offload floor moved from 28 to **20** of 30 expert layers.

### 5.2 Prefill was being shipped over PCIe

With `ncmoe` fixed, the prefill still took ~620 ms for a ~100-token prompt, and it got faster as more experts moved to the GPU. That points to llama.cpp's **op offload**: for batches of 32+ tokens it copies CPU-resident expert weights to the GPU to do the matrix multiply, so every prefill streamed about 10 GB over PCIe. Computing them in place with **`--no-op-offload`** cut prefill **624 → 423 ms** and a decision **1,000 → 800 ms**. (The server has to pass the flag through into `llama_context_params`. My first version didn't, and the "no change" result was the clue.)

### 5.3 The re-read policy assumes a big GPU

OpenJev re-reads with fresh noise, up to 4 times, when a slot's entropy is above 0.1. It measures that entropy over the **whole-vocabulary** top-k. DiffusionGemma leaks a few percent of probability to `<turn|>`, `<eos>`, and punctuation even when it's sure (`yes` 0.86–0.94 of the full vocabulary, >0.98 of the two labels). So the entropy is 0.26–0.59 and **every request is read 4 times**. On vLLM the 4 reads run as one batch and cost almost nothing. On one laptop GPU they run in sequence: **+280 ms for +1 accuracy point** (§6.1).

### 5.4 Not fixed: probabilities depend on the kernel path

The same prompt and canvas give different label log-probs depending on the code path:

| Path (PR's own reference server, same request) | World | Sports | Business | Sci/Tech |
|---|---:|---:|---:|---:|
| unified forward, flash-attn off | −3.06 | **−0.18** | −5.40 | −4.64 |
| unified forward, flash-attn on | −6.49 | **−0.33** | −5.47 | −3.56 |
| prompt-KV cache, flash-attn off | −3.05 | **−0.49** | −4.11 | −4.37 |
| prompt-KV cache, flash-attn on | −4.55 | **−0.05** | −5.28 | −3.80 |

My server's chunked vs single-shot prefill shows the same kind of spread. Every run is deterministic, and **the winning label never changed** in any comparison. But the losing labels move by 1–3 nats. My best explanation: in a Q4 MoE, tiny numerical differences (F16 vs F32 attention accumulation, chunk boundaries) flip which experts get routed. **Treat the confidence as a reliable ranking signal, not a number that's accurate to three decimals.**

---

## 6. Results

Setup: Q4_K_M GGUF, `-ngl 99 --n-cpu-moe 20 -fa on -ub 512 --no-op-offload`, peak VRAM 7.6 GB. Tasks: 200 random SST-2 validation reviews (yes/no: *is it positive?*) and 200 random AG News test articles (4-way topic choice), seed 0. Prompts average 103 and 152 tokens. Every system gets the **same OpenJev-generated system prompt**.

Baselines: **Qwen 3 30B-A3B** Q4_K_M on stock llama.cpp `b1-1719747` (`-ncmoe 34`, llama-server), used two ways:
- **generate**: it writes `q1: <label>` in up to 16 tokens, thinking disabled;
- **read**: its chat reply is pre-filled up to `q1:`, and I take the next-token probabilities of the labels. That's the autoregressive version of a System One read: one prefill, zero generated tokens.

### 6.1 Accuracy, calibration, latency

| System | SST-2 acc | AG News acc | Invalid replies | ECE ↓ (SST-2 / AG) | Mean confidence (SST-2 / AG) | p50 latency (SST-2 / AG) |
|---|---:|---:|---:|---|---|---|
| Qwen 3 30B-A3B — generate | 83.0 % | 65.5 % (75.0 % if parsed leniently) | **31 / 400** | — | — | 549 / 652 ms |
| Qwen 3 30B-A3B — read | 83.0 % | 73.5 % | 0 | 0.170 / 0.230 | 0.992 / 0.965 | 506 / 601 ms |
| **DiffusionGemma — 1 read** | **89.0 %** | **77.0 %** | **0** | **0.077** / 0.167 | 0.967 / 0.937 | **534 / 700 ms** |
| DiffusionGemma — OpenJev default (≤ 4 reads) | 90.5 % | 78.0 % | 0 | 0.087 / 0.163 | 0.968 / 0.937 | 816 / 991 ms |

*ECE = expected calibration error: the average gap between the confidence it states and how often it's right (10 bins; 0 is perfect). Brier scores are in `results.json`.*

How to read this:
- **Accuracy: DiffusionGemma wins by 3.5–6 points** on both tasks, with the same prompt. (Caveat: Qwen 3 is a 2025 model and a different family. Gemma 4 26B-A4B, the same backbone run autoregressively, wasn't on disk.)
- **Qwen's "invalid replies" are real format drift.** On AG News it answered `D: D`, `B: Sports`, or a bare `C` 31 times, even though it was told the exact format. Scored leniently it reaches 75.0 %, still below DiffusionGemma.
- **You don't need diffusion to get zero format errors.** The Qwen *read* also has none, at the same latency as generating. What diffusion adds is below.
- **Calibration is the clearest difference.** Qwen's read says it's 99.2 % sure on SST-2 and is right 83 % of the time. DiffusionGemma says 96.7 % and is right 89 %. Both are overconfident on AG News, where World, Business, and Sci/Tech overlap; DiffusionGemma less so.
- **For one question on a new state, the two cost about the same** (~0.5–0.7 s). Almost all of that is reading the prompt (prefill: 435 ms for SST-2, 606 ms for AG News). The canvas pass itself is **~93 ms**.

### 6.2 Many questions, one pass — the part diffusion is actually good at

The same AG News article, N yes/no questions per request, one read each (re-reads off):

| Questions per request | Same state asked again (prompt cached) | New state (prefill + read) |
|---:|---:|---:|
| 1 | 94 ms | 556 ms |
| 2 | 99 ms | 625 ms |
| 5 | 163 ms | 875 ms |
| 10 | **294 ms** | 1,331 ms |
| 20 | 2,686 ms | 2,720 ms |

- **Ten answers cost 3.1× one answer, not 10×.** An autoregressive model writes answer 1, then answer 2, and so on. Here all ten slots are filled in the same pass, and each slot can see the others.
- **It isn't flat, though.** A longer canvas is a bigger batch, which touches more of the 128 experts in each layer, and on this laptop most of them sit in system RAM.
- **Cold latency grows because the prompt grows.** OpenJev puts every question's wording in the system prompt.
- **20 questions falls off a cliff.** Past 10 questions OpenJev switches to a compact format and splits into two canvases, each with its own system prompt. My server caches one prompt, so the two groups keep evicting each other and it re-prefills every time. A two-entry cache would fix it.

### 6.3 Offload sweep (30 SST-2 decisions, OpenJev default policy, op-offload on)

| `--n-cpu-moe` | Peak VRAM | p50 decision | Prefill p50 | Canvas pass p50 |
|---:|---:|---:|---:|---:|
| 28 | 3,737 MiB | 1,277 ms | 820 ms | 112 ms |
| 26 | 4,795 MiB | 1,205 ms | 765 ms | 108 ms |
| 24 | 5,671 MiB | 1,136 ms | 720 ms | 102 ms |
| 22 | 6,639 MiB | 1,062 ms | 670 ms | 96 ms |
| **20** | **7,607 MiB** | 1,000 ms | 624 ms | 90 ms |
| **20 + `--no-op-offload`** | 7,607 MiB | **801 ms** | **423 ms** | 91 ms |
| 18 | — | **OOM** | — | — |

### 6.4 Chat-style generation (for completeness)

`llama-diffusion-cli -ngl 99 --n-cpu-moe 28 -fa on -n 256` (26 runs out of memory: generation needs a 1.4 GB transposed embedding for self-conditioning, plus a bigger micro-batch):

| Mode | Speed | Notes |
|---|---:|---|
| DiffusionGemma, diffusion generation | **14.6 tok/s** | 256-token block in 20 denoising steps × ~875 ms. The reply was coherent (a short thought block, then a correct explanation of the refrigeration cycle). Op-offload on or off made no difference (14.5 vs 14.7). |
| Gemma 4 26B-A4B, autoregressive (same backbone, same `ncmoe=28`, [BENCHMARKS.md](BENCHMARKS.md)) | 28.7 tok/s | |

On 8 GB, **diffusion generation is about 2× slower than autoregressive generation on the same backbone**. Each denoising step is a 256-token batch that touches nearly every expert, and those experts live in system RAM. The "1,100 tok/s" headline is an H100 with FP8, with everything in VRAM.

---

## 7. So when do you use which?

| | Autoregressive LLM (Qwen, Gemma 4, …) | DiffusionGemma as a System One reader |
|---|---|---|
| **You send** | A prompt and instructions about format | A state plus **typed questions**: yes/no, choice (≤128 options), score (≤10 levels) |
| **You get** | Text to parse | A probability for every option, a confidence, and nothing to parse |
| **Several questions** | Answered in sequence; later answers see earlier ones | Filled in one pass; slots see each other both ways |
| **Open-ended output** | ✅ chat, code, writing, extraction | ❌ every answer must be a single-token slot |
| **Reasoning first** | ✅ thinking tokens | Only through an optional `think` pass, which is text generation again (not available in the llama.cpp backend) |
| **8 GB laptop speed** | 506–652 ms per decision; 28.7–53.8 tok/s generation | 534–700 ms per new decision; **94 ms re-asking a state**; 294 ms for 10 answers; 14.6 tok/s generation |

**Good fits for System One reads:** ticket or alert triage, intent routing, content moderation, "should the agent retry / escalate?", checking 10 attributes of one document, and gating with thresholds ("auto-approve above 0.95, otherwise a human"). Thresholds only work because the confidence carries some meaning.

**Bad fits:** anything where the answer isn't a short, fixed list, anything that benefits from visible reasoning, and throughput chat on small VRAM.

---

## 8. A claims audit

| Claim in the post | Verdict | Evidence |
|---|---|---|
| "A patch contributed to vLLM by Matt Mastracci" | ⚠️ **Partly true** | It's an **open, unmerged** PR (#57250, opened 2026-09-16). OpenJev's image builds a fork of it. |
| "Evaluates choices in a single parallel pass (~0.2 s flat)" | ❌ **Not flat, and not here** | OpenJev's own figures: 94 ms p50 on an RTX PRO 6000 at concurrency 1, **760 ms at 64 concurrent**; 0.2–0.4 s on an M3 Ultra. On this 8 GB laptop: **534–700 ms** for a new state, 94 ms for a cached one. Latency grows with the number of questions (§6.2) and with prompt length. |
| "Denoises across an open canvas in a single step instead of sequential generation" | ✅ **For reads**, ⚠️ with caveats | One decoder pass per read, yes. But OpenJev's default re-reads **4×** whenever entropy > 0.1, which on this model is nearly every request (§5.3). Generation takes ~20–48 steps per 256-token block. |
| "Full bidirectional attention… standard LLMs only look backward" | ⚠️ **Misleading** | Only the **canvas** is bidirectional. The prompt is encoded **causally**, exactly like an autoregressive model, and an autoregressive answer token also attends to the entire prompt. The real gain is that answer slots see each other. |
| "Multimodal grounding (image classification, UI navigation)" | ⚠️ **Backend-dependent; untested here** | The model takes images, and OpenJev's vLLM and MLX backends support them. The llama.cpp PR and GGUF are text-only today. |
| "Zero hallucinations: schema formatting errors are entirely eliminated" | ⚠️ **Format: yes. Hallucinations: no.** | 0 invalid replies in 400 (Qwen generating: 31/400). But **10–23 % of answers were still wrong**, and an autoregressive logit read *also* had 0 format errors. Grammar-constrained decoding would too. |
| "Highly-calibrated decision engine" | ⚠️ **Better, not solved** | ECE 0.077 vs Qwen's 0.170 on SST-2. But on AG News it says 94 % and is right 77 %, and losing-label probabilities shift by 1–3 nats with the kernel path (§5.4). |
| "An open-source alternative to Jev" | ⚠️ **API-compatible alternative** | TypeSafe's SDKs work against OpenJev unchanged. But it's DiffusionGemma used zero-shot; Jev is a separately trained model with calibration-specific RL. I had no Jev access, so this comparison isn't measured here. |
| `docker run … -p 8000:8000 … razorback16/openjev:latest` | ❌ **Wrong port; wrong hardware for most readers** | The API is on **8080** (8000 is internal vLLM on 127.0.0.1). It needs **24 GB+** of VRAM. Use `docker compose up -d` from the repo on a big GPU, or §4 here on a small one. |

**Bottom line:** the core idea is real and clever. Pin the answer template, leave single-token holes, and read the distribution out of one bidirectional pass. On this laptop it gave **more accurate, better-calibrated, never-malformed decisions** than a strong autoregressive MoE, and **multi-question requests at a fraction of the cost**. It's not "0.2 s flat" on consumer hardware, it doesn't abolish wrong answers, and it's the wrong tool for anything that needs text.

---

## 9. Reproduce

```bash
cd llm-inference/diffusiongemma
# baselines (stock llama.cpp, Qwen 3 30B-A3B)
../build/llama.cpp/build-cuda/bin/llama-server -m ../models/qwen3-30b-a3b/Qwen3-30B-A3B-Q4_K_M.gguf \
    -ngl 99 -ncmoe 34 -fa on -c 4096 -np 1 --port 8081 --jinja &
.venv/bin/python systemone_bench.py --ar-url http://127.0.0.1:8081 --ar-name qwen3-30b-a3b-ar

# DiffusionGemma reads (OpenJev default policy, then single read)
A="-m ../models/diffusiongemma-26b-a4b/diffusiongemma-26B-A4B-it-Q4_K_M.gguf -ngl 99 --n-cpu-moe 20 -fa on -c 2048 -ub 512 --no-op-offload"
.venv/bin/python systemone_bench.py --reads --label diffusiongemma-openjev-default -- $A
OPENJEV_AUTO_MAX=1 .venv/bin/python systemone_bench.py --reads --no-sweep --label diffusiongemma-single-read -- $A
```

Builds: llama.cpp PR #24423 head `12e0a96`; OpenJev `2050fdb`; stock llama.cpp `b1-1719747`. Eval subsets: `diffusiongemma/data/` (from `stanfordnlp/sst2` validation and `fancyzhx/ag_news` test, `random.seed(0)`).

## Sources

- TypeSafe AI — [Introducing System One Models & Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- [razorback16/openjev](https://github.com/razorback16/openjev) — README benchmarks, `engine.py`, `mlx_backend.py`, `docker-compose.yml`
- vLLM [PR #57250](https://github.com/vllm-project/vllm/pull/57250) — structured generation mode for DiffusionGemma (Jev-like)
- llama.cpp [PR #24423](https://github.com/ggml-org/llama.cpp/pull/24423) — DiffusionGemma support
- Hugging Face — [google/diffusiongemma-26B-A4B-it](https://huggingface.co/google/diffusiongemma-26B-A4B-it), [unsloth GGUF](https://huggingface.co/unsloth/diffusiongemma-26B-A4B-it-GGUF), [nvidia NVFP4](https://huggingface.co/nvidia/diffusiongemma-26B-A4B-it-NVFP4)
