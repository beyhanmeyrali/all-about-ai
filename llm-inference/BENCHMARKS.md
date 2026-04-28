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
- **Phi-4-reasoning 14B at 23.8 t/s**: smartest *dense* model that still feels usable. Best per-byte reasoning quality.
- **Qwen3.6-27B dense at 7.8 t/s**: the dense penalty is dramatic. A 27B *dense* model is **~7× slower** than a 30B *MoE* on the same hardware. This is the most important contrast in the table — it makes the case for MoE on small VRAM concrete.
- Pattern for MoE on small VRAM: use `-ngl 99 -ncmoe N` to keep attention on GPU, push experts to CPU. Tune N down until OOM, then back off by 1.
- Pattern for dense on small VRAM: use `-ngl N` directly. Find the largest N that loads, no MoE escape hatch.
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

## The headline chart

```
          tok/s (generation)
            0    10   20   30   40   50   60   70
            ┝━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┷━━━━┥
Qwen 3 8B   ████████████████████████████████ 63.7  ← fits VRAM, full GPU
30B-A3B MoE █████████████████████████████ 53.8     ← MoE magic: 30B fits via expert offload
Phi-4 14B   ████████████ 23.8                      ← dense, tight fit
Qwen3.6-27B ████ 7.8                                ← dense penalty: 27B busts VRAM
```

Same hardware (RTX 5060 8 GB) — the *architecture* and *fit strategy* matter more than parameter count.
