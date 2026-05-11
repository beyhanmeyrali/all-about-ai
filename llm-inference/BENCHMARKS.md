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
| Phi-4-reasoning 14B (dense) | Q4_K_M | 8.43 GiB | 32 | 810.3 | 21.0 | Conservative — 32 of 40 layers on GPU. |
| Phi-4-reasoning 14B (dense) | Q4_K_M | 8.43 GiB | 34 | 917.0 | 22.7 | Tighter. |
| Phi-4-reasoning 14B (dense) | Q4_K_M | 8.43 GiB | **35** | **969.2** | **23.8** | **Sweet spot.** ngl=36 OOMs. |
| Qwen3.6-27B (dense, hybrid attn) | Q3_K_M | 12.64 GiB | 16 | 314.1 | 6.0 | Conservative — 16 of ~64 layers on GPU. |
| Qwen3.6-27B (dense, hybrid attn) | Q3_K_M | 12.64 GiB | 28 | 356.2 | 7.1 | Tighter. |
| Qwen3.6-27B (dense, hybrid attn) | Q3_K_M | 12.64 GiB | 32 | 352.5 | 7.6 | Tighter still. |
| Qwen3.6-27B (dense, hybrid attn) | Q3_K_M | 12.64 GiB | **33** | 343.2 | **7.8** | **Sweet spot.** ngl=34 OOMs. *Dense penalty is real.* |

## Observations

- **Qwen 3 8B** at 63.7 t/s: a 100-token reply in ~1.5 s. Feels instant.
- **Qwen 3 30B-A3B at 53.8 t/s**: 30B-class model, MoE with 3B active per token, runs on an 8 GB laptop at near-chat speed. The MoE thesis (§4 of LESSONS_LEARNED.md) is fully validated — and *better* than the 15-25 t/s prediction.
- **Qwen3.6-35B-A3B at 37.8 t/s**: the newer 35B/A3B MoE — same active count, but bigger total weights, more experts (256 vs 128), and a hybrid Gated-DeltaNet+Gated-Attention stack. Still chat-speed on 8 GB VRAM, but **~30 % slower than Qwen 3 30B-A3B**. The penalty is real and traces to (a) bigger model = more weights to push when experts hit, and (b) hybrid attention pulls more memory bandwidth than pure attention.
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

The XDNA 2 NPU on this laptop (~50 TOPS INT8) is real and has Linux support via FastFlowLM and AMD's Ryzen AI 1.7.1 stack, but it's a separate toolchain (ONNX, not GGUF) and the userspace driver isn't installed here yet. See [HARDWARE_BEYOND_CUDA.md §3](HARDWARE_BEYOND_CUDA.md) for the install path and realistic use cases (Whisper, embeddings, INT8 small LLMs running in parallel with CUDA).

---

## The headline chart

```
              tok/s (generation)
                0    10   20   30   40   50   60   70
                ┝━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┥
Qwen 3 8B       ████████████████████████████████ 63.7  ← fits VRAM, full GPU
30B-A3B MoE     █████████████████████████████ 53.8     ← MoE magic: 30B via expert offload
3.6 35B-A3B MoE ███████████████████ 37.8                ← bigger MoE, hybrid attn — pays for the size
Phi-4 14B       ████████████ 23.8                       ← dense, tight fit
Qwen3.6-27B     ████ 7.8                                 ← dense penalty: 27B busts VRAM
```

Same hardware (RTX 5060 8 GB) — the *architecture* and *fit strategy* matter more than parameter count. Two rows of the same family show this clearly: **two MoE models with identical 3B active params can be 40 % apart in speed**, because total weights, expert count, and attention design all bend the bandwidth curve.
