#!/usr/bin/env python3
"""
kv_cache_calc.py — how much memory your conversations cost, and where the wall is.

THE ONE FORMULA:

    kv_bytes_per_token = 2 * layers * kv_heads * head_dim * dtype_bytes
                         ^
                         one K and one V

Multiply by sequence length for one conversation, by concurrency for the fleet.
That is the whole of it — everything else in LLM serving memory management is
bookkeeping on top of this line.

Why 2 GB per conversation matters: an H100 has 80 GB. Divide and you have the
number of conversations ONE GPU can hold, before weights. That number is usually
much smaller than people expect, and it is the reason PagedAttention exists.

    python3 kv_cache_calc.py --preset llama-70b --seq 8192 --concurrent 1000000
    python3 kv_cache_calc.py --layers 80 --kv-heads 8 --head-dim 128 --seq 8192

Companion to SERVING_AT_SCALE.md. Stdlib only.
"""
from __future__ import annotations

import argparse

# layers, kv_heads (GQA — NOT attention heads), head_dim
PRESETS = {
    "llama-8b":    (32, 8, 128),
    "llama-70b":   (80, 8, 128),
    "llama-405b":  (126, 8, 128),
    "qwen3-30b-a3b": (48, 4, 128),
    "mistral-7b":  (32, 8, 128),
}
DTYPES = {"fp16": 2, "bf16": 2, "fp8": 1, "int8": 1, "int4": 0.5}
GPUS = {"RTX 5060 laptop": 8, "RTX 3090": 24, "RTX 5090": 32, "A100": 80, "H100": 80}


def human(b: float) -> str:
    for unit, div in (("PB", 1e15), ("TB", 1e12), ("GB", 1e9), ("MB", 1e6)):
        if b >= div:
            return f"{b / div:,.2f} {unit}"
    return f"{b:,.0f} B"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--preset", choices=sorted(PRESETS))
    p.add_argument("--layers", type=int)
    p.add_argument("--kv-heads", type=int, help="KV heads (GQA), not attention heads")
    p.add_argument("--head-dim", type=int, default=128)
    p.add_argument("--dtype", choices=sorted(DTYPES), default="fp16")
    p.add_argument("--seq", type=int, default=8192, help="context length in tokens")
    p.add_argument("--concurrent", type=int, default=1, help="simultaneous conversations")
    a = p.parse_args()

    if a.preset:
        layers, kv_heads, head_dim = PRESETS[a.preset]
        name = a.preset
    elif a.layers and a.kv_heads:
        layers, kv_heads, head_dim = a.layers, a.kv_heads, a.head_dim
        name = f"custom {layers}L/{kv_heads}kv/{head_dim}d"
    else:
        p.error("give --preset, or --layers and --kv-heads")

    per_tok = 2 * layers * kv_heads * head_dim * DTYPES[a.dtype]
    per_seq = per_tok * a.seq
    total = per_seq * a.concurrent

    print(f"\n  model      : {name}  ({a.dtype})")
    print(f"  context    : {a.seq:,} tokens")
    print(f"  per token  : {human(per_tok)}")
    print(f"  PER CONVERSATION : {human(per_seq)}")
    if a.concurrent > 1:
        print(f"  x {a.concurrent:,} concurrent : {human(total)}")

    print("\n  conversations that fit in ONE gpu (KV cache only, no weights):")
    for gpu, gb in GPUS.items():
        n = int((gb * 1e9) / per_seq)
        note = "  <- cannot fit even one" if n == 0 else ""
        print(f"    {gpu:16} {gb:>3} GB  ->  {n:>6,}{note}")

    if a.concurrent > 1:
        need = total / (80 * 1e9)
        print(f"\n  {a.concurrent:,} conversations need ~{need:,.0f} H100s of memory")
        print("  for KV CACHE ALONE — before a single model weight is loaded.")
        print("  (arithmetic, not a measurement — see SERVING_AT_SCALE.md §3)")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
