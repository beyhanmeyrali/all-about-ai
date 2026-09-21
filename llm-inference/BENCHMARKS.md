# LLM Benchmark Results — RTX 5060 Laptop (Blackwell, 8 GB)

Hardware: NVIDIA RTX 5060 Laptop (sm_120, 7707 MiB VRAM) + AMD Ryzen AI 9 365 (10C/20T) + 29 GB RAM.
llama.cpp build: `b1-50494a2`, built with CUDA 13.1, sm_120a.

Method: `llama-bench -p 512 -n 128`. Two metrics:
- **pp512** = prompt-processing speed (tok/s). How fast the model reads your input.
- **tg128** = token-generation speed (tok/s). How fast it writes its answer — this is the one that feels like "typing speed."

## Results

| Model | Quant | Size | n_gpu_layers | pp512 (t/s) | tg128 (t/s) | Notes |
|---|---|---:|---:|---:|---:|---|
| Qwen 3 8B | Q4_K_M | 4.68 GiB | 99 (all) | **2263.2** | **63.7** | Full GPU, no offload. Snappy chat. |
| Qwen 3 30B-A3B (MoE) | Q4_K_M | 17.28 GiB | 16 layers | 531.3 | 39.5 | Naive layer split. Already great. |
| Qwen 3 30B-A3B (MoE) | Q4_K_M | 17.28 GiB | 99 + ncmoe=36 | 546.9 | 49.8 | Attention on GPU, 36/48 expert sets on CPU. |
| Qwen 3 30B-A3B (MoE) | Q4_K_M | 17.28 GiB | 99 + ncmoe=33 | 574.7 | 51.2 | Tighter — fewer experts on CPU. |
| Qwen 3 30B-A3B (MoE) | Q4_K_M | 17.28 GiB | 99 + ncmoe=32 | 586.7 | 52.4 | Tighter still. |
| Qwen 3 30B-A3B (MoE) | Q4_K_M | 17.28 GiB | **99 + ncmoe=31** | **599.4** | **53.8** | **Sweet spot.** ncmoe=30 OOMs. |
| Qwen3.6-35B-A3B (MoE, hybrid attn) | UD-Q4_K_M | 20.60 GiB | 99 + ncmoe=40 | 439.3 | 32.3 | All experts on CPU — safe baseline. |
| Qwen3.6-35B-A3B (MoE, hybrid attn) | UD-Q4_K_M | 20.60 GiB | 99 + ncmoe=36 | 454.2 | 34.2 | Tighter. |
| Qwen3.6-35B-A3B (MoE, hybrid attn) | UD-Q4_K_M | 20.60 GiB | **99 + ncmoe=34** | **485.9** | **37.8** | **Sweet spot.** Cleanest variance (±0.4). |
| Qwen3.6-35B-A3B (MoE, hybrid attn) | UD-Q4_K_M | 20.60 GiB | 99 + ncmoe=33 | 494.9 | 37.3 | Within noise of 34. |
| Qwen3.6-35B-A3B (MoE, hybrid attn) | UD-Q4_K_M | 20.60 GiB | 99 + ncmoe=32 | 502.5 | 35.9 | Past the peak — KV+buffer pressure. |
| Qwen3.6-35B-A3B (MoE, hybrid attn) | UD-Q4_K_M | 20.60 GiB | 99 + ncmoe=31 | 514.3 | 36.7 | pp climbs, tg dips — bandwidth hits. |
| Qwen3.6-35B-A3B (MoE, hybrid attn) | UD-Q4_K_M | 20.60 GiB | 99 + ncmoe=30 | 508.1 | 33.7 | Volatile (±5.2) — near the wall. |
| Qwen3.6-35B-A3B (MoE, hybrid attn) | UD-Q4_K_M | 20.60 GiB | 99 + ncmoe=29 | — | — | **OOM — won't load.** |
| Gemma 4 26B-A4B (MoE, hybrid SWA) | UD-Q4_K_M | 15.77 GiB | 99 + ncmoe=30 | 527.3 | 27.9 | All experts on CPU — safe baseline. |
| Gemma 4 26B-A4B (MoE, hybrid SWA) | UD-Q4_K_M | 15.77 GiB | **99 + ncmoe=28** | **546.2** | **28.7** | **Sweet spot.** Only 2 of 30 expert layers fit on GPU. |
| Gemma 4 26B-A4B (MoE, hybrid SWA) | UD-Q4_K_M | 15.77 GiB | 99 + ncmoe=26 | 577.2 | 26.0 | Variance rising (±3.0) — VRAM pressure. |
| Gemma 4 26B-A4B (MoE, hybrid SWA) | UD-Q4_K_M | 15.77 GiB | 99 + ncmoe=22 | 666.2 | 11.2 | Thrashing — past the usable wall. |
| Gemma 4 26B-A4B (MoE, hybrid SWA) | UD-Q4_K_M | 15.77 GiB | 99 + ncmoe=20 | — | — | **OOM — won't load.** |
| Phi-4-reasoning 14B (dense) | Q4_K_M | 8.43 GiB | 32 | 810.3 | 21.0 | Conservative — 32 of 40 layers on GPU. |
| Phi-4-reasoning 14B (dense) | Q4_K_M | 8.43 GiB | 34 | 917.0 | 22.7 | Tighter. |
| Phi-4-reasoning 14B (dense) | Q4_K_M | 8.43 GiB | **35** | **969.2** | **23.8** | **Sweet spot.** ngl=36 OOMs. |
| Qwen3.6-27B (dense, hybrid attn) | Q3_K_M | 12.64 GiB | 16 | 314.1 | 6.0 | Conservative — 16 of ~64 layers on GPU. |
| Qwen3.6-27B (dense, hybrid attn) | Q3_K_M | 12.64 GiB | 28 | 356.2 | 7.1 | Tighter. |
| Qwen3.6-27B (dense, hybrid attn) | Q3_K_M | 12.64 GiB | 32 | 352.5 | 7.6 | Tighter still. |
| Qwen3.6-27B (dense, hybrid attn) | Q3_K_M | 12.64 GiB | **33** | 343.2 | **7.8** | **Sweet spot.** ngl=34 OOMs. *Dense penalty is real.* |
| Ornith-1.5-35B-A3B (MoE, qwen35moe hybrid SSM) | Q4_K_M | 20.35 GiB | 99 + ncmoe=37 | 98.5 | 44.9 | All-but-4 expert layers on CPU. *Build `b1-1719747`; weights on local NVMe. pp512 noisy (VM+swap active).* |
| Ornith-1.5-35B-A3B (MoE, qwen35moe hybrid SSM) | Q4_K_M | 20.35 GiB | 99 + ncmoe=35 | 164.4 | 53.1 | Tighter. |
| Ornith-1.5-35B-A3B (MoE, qwen35moe hybrid SSM) | Q4_K_M | 20.35 GiB | **99 + ncmoe=34** | 212.6 | **56.2** | **Sweet spot** (tied w/ 32, most VRAM headroom for KV). 41 layers, 256 experts, 8 active. *Single-run; 3-rep confirm = 52.9, see clean block below.* |
| Ornith-1.5-35B-A3B (MoE, qwen35moe hybrid SSM) | Q4_K_M | 20.35 GiB | 99 + ncmoe=33 | 177.5 | 55.3 | Within noise of 34. |
| Ornith-1.5-35B-A3B (MoE, qwen35moe hybrid SSM) | Q4_K_M | 20.35 GiB | 99 + ncmoe=32 | 267.5 | 56.5 | Fastest tg, no OOM (VM still holding ~8 GB RAM — more headroom than the Qwen3.6-35B run). |

### Clean apples-to-apples — same build `b1-1719747`, same session, 3 reps each, VM resident (~8 GB RAM held)

Both 35B/A3B/256-expert MoEs at the same `-ngl 99 -ncmoe 34`, back-to-back, so build/version and machine state are held constant. This supersedes the cross-build 56.2-vs-37.8 comparison.

| Model | Quant | Size | n_gpu_layers | pp512 (t/s) | tg128 (t/s) | Notes |
|---|---|---:|---:|---:|---:|---|
| Qwen3.6-35B-A3B (MoE, hybrid attn) | UD-Q4_K_M | 20.60 GiB | 99 + ncmoe=34 | 169.7 ± 21.3 | **47.5 ± 0.6** | New build lifts tg ~26 % vs the old-build 37.8 (row above). |
| Qwen3.6-35B-A3B **abliterated** (Huihui) | Q4_K_M | 19.70 GiB | 99 + ncmoe=34 | 181.2 ± 46.0 | **50.2 ± 3.5** | Uncensored finetune, same arch. ~+6 % over base — but it's plain Q4_K_M (0.9 GiB smaller) vs the base's UD-Q4_K_M, so most of the edge is quant, not abliteration. ±3.5 partly overlaps base. |
| Ornith-1.5-35B-A3B (MoE, qwen35moe hybrid SSM) | Q4_K_M | 20.35 GiB | 99 + ncmoe=34 | 193.6 ± 42.6 | **52.9 ± 1.9** | **~11 % faster tg** than base Qwen3.6. pp512 within noise. Fastest of the three. |

## Observations

- **Qwen 3 8B** at 63.7 t/s: a 100-token reply in ~1.5 s. Feels instant.
- **Qwen 3 30B-A3B at 53.8 t/s**: 30B-class model, MoE with 3B active per token, runs on an 8 GB laptop at near-chat speed. The MoE thesis (§4 of LESSONS_LEARNED.md) is fully validated — and *better* than the 15-25 t/s prediction.
- **Qwen3.6-35B-A3B — 37.8 t/s on the old build, 47.5 t/s on the new one**: the newer 35B/A3B MoE — same active count, but bigger total weights, more experts (256 vs 128), and a hybrid Gated-DeltaNet+Gated-Attention stack. On the old build (`b1-50494a2`) it did 37.8 t/s (**~30 % slower than Qwen 3 30B-A3B**); a clean re-run on `b1-1719747` with weights on NVMe lifts it to **47.5 ± 0.6 t/s** (~+26 %). The size penalty is still real — bigger model = more weights to push when experts hit, and hybrid attention pulls more memory bandwidth — but a big chunk of the original gap was just an older build.
- **Ornith-1.5-35B-A3B is ~11 % faster than Qwen3.6-35B-A3B, not 50 %**: on the same build (`b1-1719747`), same session, 3 reps each at `ncmoe=34`, Ornith does **52.9 ± 1.9 t/s** vs Qwen3.6's **47.5 ± 0.6**. The earlier "~50 % faster" reading was a **cross-build artifact** — it compared Ornith on the new build against Qwen3.6's *old-build* 37.8. Once both run on the same build the real gap is modest (~11 %), and Ornith's own headline 56.2 was a lucky single sample; the 3-rep average is 52.9. Ornith still never OOMs across the ncmoe 32–37 sweep (curve plateaus ~53–56 t/s), and this whole comparison was made with ~8 GB RAM held by a VM, so both numbers are conservative floors.
- **Gemma 4 26B-A4B at 28.7 t/s**: a third MoE, and the most instructive contrast. It's the *smallest* of the three MoEs on disk (15.8 GiB) yet the *second-slowest* — and it can only push **2 of 30 expert layers onto the GPU** before OOM, vs the 17 that Qwen 3 30B-A3B managed. Two causes: (a) Gemma's **262K-token vocabulary** makes the embedding + output tensors enormous (~1 GB+ each at Q4) and those sit on the GPU, eating the VRAM that would otherwise hold experts; (b) **4B active params** (vs 3B for the Qwen MoEs) is 33 % more compute per token. The MoE trick still works — 28.7 t/s is very usable — but vocabulary size and active-param count both bend the result. *Total parameter count tells you almost nothing about speed.* **For the full bandwidth-arithmetic walkthrough of why these three MoEs run at three different speeds, see [LESSONS_LEARNED.md §5.7](LESSONS_LEARNED.md).**
- **Phi-4-reasoning 14B at 23.8 t/s**: smartest *dense* model that still feels usable. Best per-byte reasoning quality.
- **Qwen3.6-27B dense at 7.8 t/s**: the dense penalty is dramatic. A 27B *dense* model is **~7× slower** than a 30B *MoE* on the same hardware. This is the most important contrast in the table — it makes the case for MoE on small VRAM concrete.
- Pattern for MoE on small VRAM: use `-ngl 99 -ncmoe N` to keep attention on GPU, push experts to CPU. Tune N down until OOM, then back off by 1.
- Pattern for dense on small VRAM: use `-ngl N` directly. Find the largest N that loads, no MoE escape hatch.
- **The peak isn't always the most aggressive ncmoe**: for Qwen3.6-35B-A3B, ncmoe=34 (37.8 t/s) beats ncmoe=31 (36.7 t/s) and ncmoe=30 (33.7 t/s, volatile) even though both still fit. Past a point, KV cache + compute buffers compete with the experts you crammed onto the GPU and decode slows. *Sweet spot is the fastest stable run, not the lowest ncmoe that loads.*
- VRAM at the 30B MoE sweet spot: ~7.4 GB used (most of the 7.7 GB available).

## TurboQuant KV cache compression — long-context demo

Built [Madreag/turbo3-cuda](https://github.com/Madreag/turbo3-cuda) — the only TurboQuant fork explicitly validated on Blackwell sm_120. Same Qwen 3 8B Q4_K_M GGUF as the daily-fast baseline above.

### Qwen 3 8B at 32K context depth (`-d 32768`)

| KV cache type | Bits/value | Compression | pp4096 (t/s) | tg128 (t/s) | Status |
|---|---|---|---:|---:|---|
| **f16** (default) | 16 | 1.0× | — | — | **❌ OOM — won't even load** |
| **turbo3** | 3.125 | 5.12× | 707.1 | **24.4** | ✅ fits + runs |
| **turbo2** | 2.125 | 7.53× | 704.4 | **28.5** | ✅ fits, **fastest at long context** |

### Qwen 3 8B at short context (`-p 4096`, no depth)

| KV cache type | tg128 (t/s) | Note |
|---|---:|---|
| f16 (baseline) | 63.7 | (from upstream llama.cpp benchmarks above) |
| turbo3 | 65.3 | Slightly faster than f16 even at short context |

### What this demonstrates

1. **OOM avoidance** — at 32K context, FP16 KV cache wants ~4.6 GB just for the cache. Together with the 4.7 GB model weights that's 9.3 GB > 7.7 GB usable VRAM → won't load. TurboQuant's 5–8× compression brings the cache down to ~1 GB, freeing room.
2. **turbo2 beats turbo3 at long context** — counterintuitive but real. At long depth, KV bandwidth becomes the bottleneck. Smaller cache = faster reads = faster decode. The 7.5× compression actively *helps* speed.
3. **Quality cost is small** — Madreag's PPL data: turbo3 +1.4% over q8_0 at ctx=512, equals q8_0 at ctx=2048; turbo4 +0.97%, basically lossless.

### Qwen3.6-27B at 16K context depth, with KV compression

| ngl | KV cache | tg64 @ d16K (t/s) | Note |
|---:|---|---:|---|
| 30 | turbo3 | 2.4 | Dense + long context = brutal |
| 30 | turbo2 | 3.0 | Same long-context-faster pattern |

The 27B *dense* model at long context is dominated by CPU-offloaded weights (12.6 GB > 7.7 GB VRAM means most layers live in RAM). KV compression doesn't fix that root constraint — but it does **enable the long-context window in the first place**. Without TurboQuant, FP16 KV at 32K depth crashes outright on this laptop.

### Fork choice — why Madreag, not the alternatives

I tried [AmesianX/TurboQuant](https://github.com/AmesianX/TurboQuant) first (most feature-rich, includes TriAttention pruning). It compiled but **hung for 15+ min generating 5 tokens on Blackwell** — its `amx3` path uses `fattn-vec` kernels with a known NVIDIA compiler bug for D=256 head_dim on sm_120. Switching to **Madreag/turbo3-cuda** which has explicit RTX 5090 sm_120 validation and auto-disables the broken LUT path on Blackwell (graceful VEC fallback). Worked first try.

Other forks surveyed and rejected:
- [TheTom/turboquant_plus](https://github.com/TheTom/turboquant_plus) — Apple Metal first, base for Madreag's CUDA port
- [atomicmilkshake/llama-cpp-turboquant](https://github.com/atomicmilkshake/llama-cpp-turboquant) — sm_75/80/86 only, no Blackwell
- [spiritbuun/llama-cpp-turboquant-cuda](https://github.com/spiritbuun/llama-cpp-turboquant-cuda) — RTX 3090 (sm_86) only

---

## Alternative backend — Vulkan on the AMD Radeon 890M iGPU

We built a second llama.cpp (`build-vulkan/`, `-DGGML_VULKAN=ON`) and ran the same `llama-bench` recipe on the integrated GPU via Mesa RADV. Same build commit (`50494a2`), same models, just `--device Vulkan1`. Full reasoning + use-cases for this path: [HARDWARE_BEYOND_CUDA.md §2.5](HARDWARE_BEYOND_CUDA.md).

| Model | Size | CUDA (5060) tg128 | Vulkan (Radeon 890M iGPU) tg128 | iGPU slowdown |
|---|---:|---:|---:|---:|
| Qwen 3 8B Q4_K_M | 4.7 GB | **63.7** | 15.2 | 4.2× |
| Phi-4-reasoning 14B Q4_K_M | 8.4 GB | **23.8** | 8.2 (all on iGPU) | 2.9× |
| Qwen3.6-27B Q3_K_M | 12.6 GB | **7.8** | 5.2 (all on iGPU) | 1.5× |
| Qwen 3 30B-A3B MoE Q4_K_M | 17.3 GB | **53.8** | 23.8 (`-ncmoe 31`) | 2.3× |

**The iGPU never wins on this laptop**, even when models fit fully on its 15.8 GB UMA but bust the 5060's 7.7 GB VRAM. Reason: the 890M reads weights through DDR5-5600 (~80 GB/s, shared with the CPU); the 5060 uses private GDDR6 (~448 GB/s). The bandwidth gap dominates the memory-ceiling advantage.

**The MoE case is the interesting one**: 2.3× slowdown, much smaller than the 3–4× we see on dense models. Because most MoE weights are cold experts in RAM either way, both backends touch mostly the same DDR5 bus, and the gap narrows to whatever the *active-path* speed difference is.

**Useful regardless of speed**: the iGPU is a separate Vulkan device from the 5060, so you can run a small model on it *concurrently* with CUDA work — useful for embeddings, a small helper LLM, or any task that should not contend with the dGPU. And the iGPU draws ~5–10 W under load vs the 5060's ~50–80 W: real battery savings for idle assistant tasks.

ROCm on this iGPU (RDNA 3.5 / gfx1150) is not officially supported by AMD as of 2026; the community `HSA_OVERRIDE_GFX_VERSION` route is fragile. **Vulkan is the right path for this iGPU.** ROCm becomes the right call only when you have an AMD *discrete* GPU (RX 7900, MI300).

The XDNA 2 NPU on this laptop (~50 TOPS INT8) is real and has Linux support via FastFlowLM and AMD's Ryzen AI 1.7.1 stack. We installed it (one `.deb` + memlock tweak, no reboot) and measured it. See [NPU.md](NPU.md) for the full install walkthrough and benchmark methodology.

---

## Third backend — AMD XDNA 2 NPU via FastFlowLM

Measured with `flm v0.9.41`, FW 1.1.2.64, kernel 7.0.0-14, on AC power. NPU's own `prefill_speed_tps` / `decoding_speed_tps` from the server's `usage` field; package power from `intel-rapl` package counter delta.

### Chat models — single-stream tok/s

| Model | Active | Prefill (medium prompt) | **Decode (stable)** | vs CUDA 5060 |
|---|:---:|---:|---:|---|
| qwen3:0.6b | 0.6 B | 83 tok/s | **96.8** | n/a (no 0.6B CUDA bench here) |
| llama3.2:1b | 1.2 B | 131 tok/s | **62.7** | n/a |
| qwen3:8b | 8.2 B | 25 tok/s | **11.0** | 63.7 (5060 wins 5.8×) |

### Embeddings — embed-gemma:300m, 768-dim output

| Input | Latency (best of 5) | Effective rate |
|---|---:|---:|
| Short sentence | 188 ms | 5.3 embeds/s |
| Long paragraph (~120 tokens) | 256 ms | 3.9 embeds/s |

### Package power (Intel RAPL counter delta)

| State | Avg watts |
|---|---:|
| Idle baseline | 10.1 W |
| NPU running qwen3:0.6b (sustained decode) | **20.4 W** |
| NPU running qwen3:8b (sustained decode) | **20.5 W** |

**Two findings to remember**:
1. **NPU power is ~constant in model size**: the NPU itself is the active component, and its envelope doesn't grow with the model. The 0.6 B model gets ~9× more tokens-per-joule than the 8 B from this fact alone.
2. **While the NPU runs the 8 B at 11 tok/s, `nvidia-smi` reports the RTX 5060 sitting at 0 % util, 15 MiB, 8.55 W** — completely idle. NPU work does not contend with the dGPU for compute or VRAM. *Use them concurrently.*

Full install + methodology + scripts: [NPU.md](NPU.md).

---

## Text diffusion — DiffusionGemma 26B-A4B (Jev-style "System One" decisions)

DiffusionGemma is Google's open text-*diffusion* MoE (Gemma 4 backbone, 128 experts / 8 active). It's measured two ways here: as a **decision engine**, where one bidirectional pass over a pre-filled answer template reads out option probabilities (OpenJev), and as an ordinary **text generator**. Build: llama.cpp PR #24423 (`12e0a96`, unmerged) plus our `dg-systemone-server`. Weights: `unsloth/diffusiongemma-26B-A4B-it-GGUF` Q4_K_M, 15.6 GiB. Full write-up, method, and claims audit: [DIFFUSIONGEMMA.md](DIFFUSIONGEMMA.md).

### Decisions — 200 SST-2 (yes/no) + 200 AG News (4-way), same prompt for every system

| System | SST-2 acc | AG News acc | Invalid replies | ECE (SST-2 / AG) | p50 latency (SST-2 / AG) |
|---|---:|---:|---:|---|---|
| Qwen 3 30B-A3B — generates `q1: <label>` (`-ncmoe 34`) | 83.0 % | 65.5 % | 31 / 400 | — | 549 / 652 ms |
| Qwen 3 30B-A3B — next-token label probabilities | 83.0 % | 73.5 % | 0 | 0.170 / 0.230 | 506 / 601 ms |
| **DiffusionGemma — 1 read** (`-ncmoe 20 --no-op-offload`) | **89.0 %** | **77.0 %** | **0** | **0.077** / 0.167 | **534 / 700 ms** |
| DiffusionGemma — OpenJev default (≤ 4 reads) | 90.5 % | 78.0 % | 0 | 0.087 / 0.163 | 816 / 991 ms |

Questions per request (same article, one read each): **1 → 94 ms, 10 → 294 ms** when the state is already prefilled; 556 ms → 1.33 s for a new state.

### Offload sweep and generation

| Mode | n_gpu_layers | Peak VRAM | Result | Notes |
|---|---:|---:|---:|---|
| Decisions, `-ub 4096` (default-sized) | 99 + ncmoe=26 | — | **OOM** | 4.2 GiB full-vocab logits buffer (4096 rows × 262 K vocab × 4 B), not the experts. |
| Decisions, `-ub 512` | 99 + ncmoe=28 | 3.7 GiB | 1,277 ms / decision | |
| Decisions, `-ub 512` | 99 + ncmoe=20 | 7.6 GiB | 1,000 ms | ncmoe=18 OOMs. |
| Decisions, `-ub 512 --no-op-offload` | **99 + ncmoe=20** | 7.6 GiB | **801 ms** | Prefill 624 → 423 ms: stops streaming CPU experts over PCIe on every prompt. |
| Text generation, `llama-diffusion-cli -n 256` | 99 + ncmoe=28 | — | **14.6 tok/s** | 20 denoising steps × ~875 ms per 256-token block. ncmoe=26 OOMs (+1.4 GiB self-conditioning embedding). |
| *Gemma 4 26B-A4B, autoregressive (same backbone, from above)* | 99 + ncmoe=28 | — | *28.7 tok/s* | Diffusion generation is ~2× slower on 8 GB: every step is a 256-token batch that touches nearly every CPU-resident expert. |

**What to remember:** as a decision engine it beat a strong autoregressive MoE on accuracy (+3.5–6 points), calibration (ECE 0.077 vs 0.170), and format errors (0 vs 31), and it answers 10 questions for 3× the cost of one. As a chat model on small VRAM it's half the speed of its autoregressive twin. The "~0.2 s flat" and "zero hallucinations" claims don't hold here: see the [claims audit](DIFFUSIONGEMMA.md#8-a-claims-audit).

---

## The headline chart

```
              tok/s (generation)
                0    10   20   30   40   50   60   70
                ┝━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┥
Qwen 3 8B       ████████████████████████████████ 63.7  ← fits VRAM, full GPU
Ornith 35B-A3B  ██████████████████████████ 52.9         ← qwen35moe, new build (b1-1719747)
30B-A3B MoE     █████████████████████████ 53.8          ← MoE magic: 30B via expert offload
3.6 35B-A3B MoE ████████████████████████ 47.5           ← same-build re-run (was 37.8 on old build)
Gemma4 26B-A4B  ██████████████ 28.7                      ← MoE, but 262K vocab + 4B active limit offload
Phi-4 14B       ████████████ 23.8                       ← dense, tight fit
DiffusionGemma  ███████ 14.6                             ← same backbone as Gemma4, but text *diffusion*: 256-tok blocks
Qwen3.6-27B     ████ 7.8                                 ← dense penalty: 27B busts VRAM
```

Same hardware (RTX 5060 8 GB) — the *architecture* and *fit strategy* matter more than parameter count. Two rows of the same family show this clearly: **two MoE models with identical 3B active params can be 40 % apart in speed**, because total weights, expert count, and attention design all bend the bandwidth curve.
