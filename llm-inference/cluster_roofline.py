#!/usr/bin/env python3
"""
cluster_roofline.py — predict LLM decode speed from memory-bandwidth first principles.

THE PHYSICS (one sentence):
    Decode is bandwidth-bound. To emit one token the engine must read every ACTIVE
    weight byte out of memory and do almost no arithmetic on it. So:

        time_per_token  =  bytes_per_token / effective_bandwidth   (+ network, if clustered)

Everything else in this file is bookkeeping on top of that one line.

THREE MODES
-----------
single    One machine. Weights may straddle two memory pools (fast VRAM + slow system
          RAM) — that is exactly what an 8 GB laptop running a 30B MoE does. Read time
          is the SUM of both pools' read times, because they are read for the same token.

pipeline  Layers are split across N nodes. Node k holds 1/N of the layers and reads its
          share ONLY when the token reaches it — i.e. the nodes read SEQUENTIALLY.
          Total read time is therefore UNCHANGED versus one node that held everything.
          You then PAY (N-1) network hops per token to hand the hidden state along.
          => Pipeline parallelism is break-even at best, strictly worse in practice.
          What it buys you is CAPACITY (a model that fits nowhere else), never speed.

tensor    Every layer's weights are sharded across all N nodes, so all N read their 1/N
          share SIMULTANEOUSLY. Read time genuinely divides by N. But each layer needs
          the shards recombined — an all-reduce/all-gather collective, typically 2 per
          layer. That is collectives_per_layer * n_layers ROUND TRIPS PER TOKEN.
          => Real speedup only if that latency term stays small next to the read term.
             On TCP/Ethernet (~300 us) it does not. On RDMA (<50 us) it can.

UNITS — read this, it is the documented failure mode here
---------------------------------------------------------
GB is decimal (10^9 bytes). GiB is binary (2^30 bytes). They differ by 7.4%.
Model files on Hugging Face are quoted in GiB; bandwidth specs are quoted in decimal GB/s.
Mixing them silently biases every prediction by ~7%. This tool ALWAYS parses an explicit
unit and ALWAYS labels the unit it printed. Bare numbers default to DECIMAL (GB, GB/s)
because that is the convention for bandwidth, which is the term you divide BY.

EXAMPLES
--------
  # Founder's laptop: Qwen3 30B-A3B, 3B active @ ~0.56 B/param, 65% of it read from DDR5.
  cluster_roofline.py --bytes-per-token 1.68GB --bandwidth 448 \\
      --bandwidth-slow 80 --slow-frac 0.65 --measured 53.8

  # Same laptop, dense 27B Q3_K_M: EVERY byte of the file is active every token.
  cluster_roofline.py --model-gib 12.64 --active-frac 1.0 --bandwidth 448 \\
      --bandwidth-slow 80 --slow-frac 0.484 --measured 7.8

  # Geerling's 4x Framework cluster: 405B Q4_K_M over pipeline parallelism.
  cluster_roofline.py --model-gib 226.37 --active-frac 1.0 --bandwidth 212 \\
      --mode pipeline --nodes 4 --link-latency-us 200 --measured 0.70

  # The tensor-parallel latency wall, 94-layer 235B-A22B, TCP vs RDMA:
  cluster_roofline.py --bytes-per-token 12.32GB --bandwidth 242 --mode tensor \\
      --nodes 4 --layers 94 --link-latency-us 300
  cluster_roofline.py --bytes-per-token 12.32GB --bandwidth 242 --mode tensor \\
      --nodes 4 --layers 94 --link-latency-us 50

  # The on-camera walkthrough:
  cluster_roofline.py --demo
"""

from __future__ import annotations

import argparse
import re
import sys

# ---------------------------------------------------------------- units

_SIZE_UNITS = {
    "b": 1,
    "kb": 10**3, "mb": 10**6, "gb": 10**9, "tb": 10**12,
    "kib": 2**10, "mib": 2**20, "gib": 2**30, "tib": 2**40,
}
_NUM = re.compile(r"^\s*([0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)\s*([a-zA-Z/]*)\s*$")


def parse_size(text: str, default_unit: str = "gb") -> float:
    """'226.37GiB' -> bytes. Bare number -> default_unit (decimal GB)."""
    m = _NUM.match(str(text))
    if not m:
        raise argparse.ArgumentTypeError(f"cannot parse size {text!r}")
    value, unit = float(m.group(1)), (m.group(2) or default_unit).lower()
    if unit not in _SIZE_UNITS:
        raise argparse.ArgumentTypeError(f"unknown size unit {unit!r} in {text!r}")
    return value * _SIZE_UNITS[unit]


def parse_bandwidth(text: str) -> float:
    """'448' or '448GB/s' or '400GiB/s' -> bytes/second. Bare number -> decimal GB/s."""
    return parse_size(str(text).lower().replace("/s", "").replace("ps", ""), "gb")


def gb(byte_count: float) -> str:
    return f"{byte_count / 10**9:.3f} GB"


def gib(byte_count: float) -> str:
    return f"{byte_count / 2**30:.3f} GiB"


# ---------------------------------------------------------------- model

def predict(
    bytes_per_token: float,
    bandwidth: float,
    bandwidth_slow: float | None = None,
    slow_frac: float = 0.0,
    mode: str = "single",
    nodes: int = 1,
    layers: int = 0,
    link_latency_s: float = 0.0,
    collectives_per_layer: int = 2,
) -> dict:
    """Return per-token timing breakdown. All times in seconds, all sizes in bytes."""
    if not 0.0 <= slow_frac <= 1.0:
        raise ValueError("--slow-frac must be in [0, 1]")
    if nodes < 1:
        raise ValueError("--nodes must be >= 1")

    # --- Step 1: single-node read time, honouring a two-pool weight split.
    # Both pools are read for the SAME token, so their times ADD (they are not
    # alternatives, they are two serial legs of one token's memory traffic).
    bytes_slow = bytes_per_token * slow_frac
    bytes_fast = bytes_per_token - bytes_slow
    if bytes_slow > 0 and not bandwidth_slow:
        raise ValueError("--slow-frac > 0 requires --bandwidth-slow "
                         "(you told me some weights live in a second memory pool "
                         "but not how fast that pool is)")
    t_fast = bytes_fast / bandwidth
    t_slow = (bytes_slow / bandwidth_slow) if bytes_slow > 0 else 0.0
    t_read_single = t_fast + t_slow
    effective_bw = bytes_per_token / t_read_single if t_read_single else float("inf")

    # --- Step 2: what the cluster topology does to that read time, plus network cost.
    if mode == "single":
        t_read, t_net, hops = t_read_single, 0.0, 0
    elif mode == "pipeline":
        # Each node reads its 1/N share, but only when the token arrives at it.
        # N sequential reads of (bytes/N) == one read of (bytes). No read speedup, ever.
        t_read = t_read_single
        hops = nodes - 1
        t_net = hops * link_latency_s
    elif mode == "tensor":
        # All N nodes read their 1/N shard at the same instant -> read time / N.
        t_read = t_read_single / nodes
        # ...but every layer must recombine its shards. That is the bill.
        hops = collectives_per_layer * layers if nodes > 1 else 0
        t_net = hops * link_latency_s
    else:
        raise ValueError(f"unknown mode {mode!r}")

    t_token = t_read + t_net
    return {
        "mode": mode, "nodes": nodes,
        "bytes_per_token": bytes_per_token,
        "bytes_fast": bytes_fast, "bytes_slow": bytes_slow,
        "t_read_single": t_read_single, "effective_bw": effective_bw,
        "t_read": t_read, "t_net": t_net, "t_token": t_token,
        "round_trips": hops,
        "tokens_per_s": (1.0 / t_token) if t_token > 0 else float("inf"),
    }


# ---------------------------------------------------------------- output

def render(r: dict, measured: float | None = None, label: str | None = None) -> str:
    ms = 1000.0
    rows = [
        ("topology", f"{r['mode']}  x{r['nodes']} node(s)"),
        ("bytes / token", f"{gb(r['bytes_per_token'])}  ({gib(r['bytes_per_token'])})"),
    ]
    if r["bytes_slow"] > 0:
        rows.append(("  from fast pool", gb(r["bytes_fast"])))
        rows.append(("  from slow pool", gb(r["bytes_slow"])))
        rows.append(("effective bandwidth", f"{r['effective_bw'] / 10**9:.1f} GB/s"))
    rows += [
        ("read time / token", f"{r['t_read'] * ms:.2f} ms"),
        ("network time / token", f"{r['t_net'] * ms:.2f} ms"
                                 f"   ({r['round_trips']} round trip(s))"),
        ("TOTAL / token", f"{r['t_token'] * ms:.2f} ms"),
        ("PREDICTED CEILING", f"{r['tokens_per_s']:.2f} tok/s"),
    ]
    # When clustered, always show what ONE machine would have done. That comparison
    # IS the answer to "should I cluster?" -- never make the viewer compute it.
    if r["mode"] != "single" and r["nodes"] > 1:
        solo_tps = 1.0 / r["t_read_single"]
        ratio = r["tokens_per_s"] / solo_tps
        # Don't print "1.00x SLOWER" -- that reads as a contradiction on screen.
        # Within half a percent, the honest word is break-even.
        verdict = ("SPEEDUP" if ratio > 1.005 else
                   "SLOWER THAN 1 NODE" if ratio < 0.995 else "BREAK-EVEN AT BEST")
        rows.append(("vs ONE machine",
                     f"{solo_tps:.2f} tok/s ({r['t_read_single'] * ms:.2f} ms)"
                     f"  ->  {ratio:.2f}x  {verdict}"))
    if measured is not None:
        rows.append(("measured", f"{measured:.2f} tok/s"))
        rows.append(("% of roofline", f"{100.0 * measured / r['tokens_per_s']:.1f} %"))

    width = max(len(k) for k, _ in rows)
    body = [f"  {k.ljust(width)} : {v}" for k, v in rows]
    bar = max(78, max(len(b) for b in body))
    head = ("── " + label + " ").ljust(bar, "─") if label else "─" * bar
    return "\n".join([head] + body)


# ---------------------------------------------------------------- demo

DEMO = [
    # (label, kwargs, measured, note)
    ("1. SINGLE NODE — the founder's laptop, Qwen3 30B-A3B MoE",
     dict(bytes_per_token=1.68e9, bandwidth=448e9, bandwidth_slow=80e9, slow_frac=0.65),
     53.8, "3B active x 0.56 B/param. 65% of it crawls out of DDR5. That is the whole story."),

    ("2. SAME LAPTOP, DENSE — Qwen3.6-27B Q3_K_M",
     dict(bytes_per_token=12.64 * 2**30, bandwidth=448e9, bandwidth_slow=80e9, slow_frac=0.484),
     7.8, "Fewer parameters than the MoE. 8x more bytes per token. 7x slower. Bytes decide."),

    ("3. PIPELINE, 2 NODES — the break-even proof",
     dict(bytes_per_token=1.68e9, bandwidth=448e9, bandwidth_slow=80e9, slow_frac=0.65,
          mode="pipeline", nodes=2, link_latency_s=200e-6),
     None, "Read time is IDENTICAL to case 1. Two machines bought zero bandwidth, and cost a hop."),

    ("4. PIPELINE, 4 NODES — Geerling's cluster, Hermes-3 405B Q4_K_M",
     dict(bytes_per_token=226.37 * 2**30, bandwidth=212e9,
          mode="pipeline", nodes=4, link_latency_s=200e-6),
     0.70, "Predict 0.87 from bandwidth alone. He measured 0.70. Roofline called it within 20%."),

    ("5. TENSOR PARALLEL over TCP — Qwen3-235B-A22B, 94 layers",
     dict(bytes_per_token=12.32e9, bandwidth=242e9, mode="tensor", nodes=4,
          layers=94, link_latency_s=300e-6, collectives_per_layer=2),
     None, "188 round trips per token at 300 us = 56.4 ms of pure waiting -- more than the "
           "entire ~51 ms single-node token budget. Four machines, and you went BACKWARDS."),

    ("6. TENSOR PARALLEL over RDMA — same model, same 188 round trips",
     dict(bytes_per_token=12.32e9, bandwidth=242e9, mode="tensor", nodes=4,
          layers=94, link_latency_s=50e-6, collectives_per_layer=2),
     None, "Nothing changed but the wire. 300 us -> 50 us turns 'slower than one machine' "
           "into a real 2.3x. Note: 4 nodes, 2.3x -- latency still eats the other 1.7x. "
           "Clustering is a latency problem wearing a bandwidth costume."),
]


def run_demo() -> None:
    import textwrap
    width = 78
    print()
    print("=" * width)
    print("ROOFLINE: what clustering can and cannot buy you".center(width))
    print("=" * width)
    for label, kwargs, measured, note in DEMO:
        print()
        print(render(predict(**kwargs), measured=measured, label=label))
        for line in textwrap.wrap(note, width - 6):
            print(f"  -> {line}" if line == textwrap.wrap(note, width - 6)[0] else f"     {line}")
    print()
    print("=" * width)
    print()


# ---------------------------------------------------------------- cli

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="cluster_roofline.py",
        description="Predict LLM decode tok/s from memory bandwidth. See module docstring for examples.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__[__doc__.index("EXAMPLES"):],
    )
    p.add_argument("--demo", action="store_true", help="run the on-camera walkthrough and exit")

    size = p.add_argument_group("per-token working set (pick ONE of the three)")
    size.add_argument("--bytes-per-token", help="e.g. 1.68GB / 12.32GB / 226.37GiB (bare number = GB)")
    size.add_argument("--model-gb", type=float, help="total weight size in DECIMAL GB")
    size.add_argument("--model-gib", type=float, help="total weight size in BINARY GiB")
    size.add_argument("--active-frac", type=float, default=1.0,
                      help="fraction of weights read per token: 1.0 dense, ~0.1 for a 235B/A22B MoE (default 1.0)")

    mem = p.add_argument_group("memory")
    mem.add_argument("--bandwidth", default="448", help="fast pool bandwidth, e.g. 448 or 448GB/s (default 448)")
    mem.add_argument("--bandwidth-slow", default=None, help="second pool bandwidth, e.g. 80 (system DDR5)")
    mem.add_argument("--slow-frac", type=float, default=0.0,
                     help="fraction of per-token bytes served from the SLOW pool (default 0)")

    net = p.add_argument_group("cluster")
    net.add_argument("--mode", choices=["single", "pipeline", "tensor"], default="single")
    net.add_argument("--nodes", type=int, default=1)
    net.add_argument("--layers", type=int, default=0, help="transformer layers (tensor mode only)")
    net.add_argument("--link-latency-us", type=float, default=0.0,
                     help="one-way link latency in microseconds: ~300 TCP/GbE, ~100 TB4, <50 RDMA")
    net.add_argument("--collectives-per-layer", type=int, default=2,
                     help="all-reduce/all-gather round trips per layer (default 2)")

    p.add_argument("--measured", type=float, default=None, help="measured tok/s; prints %% of roofline")

    a = p.parse_args(argv)
    if a.demo:
        run_demo()
        return 0

    if a.bytes_per_token is not None:
        bpt = parse_size(a.bytes_per_token)
    elif a.model_gb is not None:
        bpt = a.model_gb * 10**9 * a.active_frac
    elif a.model_gib is not None:
        bpt = a.model_gib * 2**30 * a.active_frac
    else:
        p.error("need one of --bytes-per-token / --model-gb / --model-gib (or --demo)")

    if a.mode == "tensor" and a.nodes > 1 and a.layers <= 0:
        p.error("--mode tensor with >1 node needs --layers (collectives scale with layer count)")

    try:
        r = predict(
            bytes_per_token=bpt,
            bandwidth=parse_bandwidth(a.bandwidth),
            bandwidth_slow=parse_bandwidth(a.bandwidth_slow) if a.bandwidth_slow else None,
            slow_frac=a.slow_frac,
            mode=a.mode, nodes=a.nodes, layers=a.layers,
            link_latency_s=a.link_latency_us * 1e-6,
            collectives_per_layer=a.collectives_per_layer,
        )
    except ValueError as e:
        p.error(str(e))
    print(render(r, measured=a.measured))
    return 0


if __name__ == "__main__":
    sys.exit(main())
