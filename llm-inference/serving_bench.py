#!/usr/bin/env python3
"""
serving_bench.py — measure what one 8 GB laptop GPU can actually serve.

The hyperscale serving story (SERVING_AT_SCALE.md) rests on two claims that are
usually quoted from papers. This measures BOTH of them on one consumer GPU, so
the numbers in this repo are first-party rather than borrowed:

  1. CONTINUOUS BATCHING is a throughput multiplier.
     llama.cpp exposes the exact toggle: -cb vs -nocb. Same GPU, same model,
     same requests — only the scheduler changes. Whatever multiple comes out is
     the honest one for this hardware.

  2. The KV CACHE is the concurrency wall.
     Sweep concurrency and watch aggregate throughput stop scaling. The knee is
     where the GPU runs out of room to hold conversations, not compute.

Method (deliberately boring, so it is reproducible):
  * start llama-server with one configuration
  * fire N concurrent completion requests, all identical, fixed token count
  * measure wall time, aggregate output tok/s, per-stream tok/s, TTFT
  * shut the server down, next configuration

Everything reported is measured on THIS machine. Nothing is scaled, projected
or borrowed. stdlib only.

    python3 serving_bench.py --model /path/model.gguf --sweep 1,2,4,8,16
"""
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SERVER = "/home/ubuntu/workspace/tools/llama.cpp/build/bin/llama-server"
HOST, PORT = "127.0.0.1", 8099
PROMPT = ("Write a clear, calm explanation of how a bicycle stays upright when "
          "it is moving. Be concrete and use plain words.")

# Realistic traffic is MIXED: some users ask for a sentence, some for an essay.
# A batch is only held hostage if its members finish at different times, so a
# uniform workload cannot reveal what continuous batching does. These lengths are
# cycled across the concurrent clients.
MIXED_LENGTHS = [32, 64, 96, 128, 192, 256, 384, 512]
ARRIVAL_JITTER_SEC = 0.35   # requests do not all land on the same millisecond


def wait_ready(timeout: float = 180) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with urllib.request.urlopen(f"http://{HOST}:{PORT}/health", timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(1)
    return False


def vram_mb() -> int:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            text=True).strip().splitlines()[0]
        return int(out)
    except Exception:
        return -1


def one_request(n_predict: int) -> dict:
    """One completion. Returns TTFT and per-stream tok/s, measured client-side."""
    body = json.dumps({
        "prompt": PROMPT, "n_predict": n_predict, "temperature": 0.7,
        "stream": True, "cache_prompt": False,
    }).encode()
    req = urllib.request.Request(f"http://{HOST}:{PORT}/completion", data=body,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    ttft = None
    toks = 0
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            for raw in r:
                line = raw.decode("utf-8", "ignore").strip()
                if not line.startswith("data:"):
                    continue
                if ttft is None:
                    ttft = time.time() - t0
                toks += 1
    except Exception as e:
        return {"ok": False, "err": str(e)[:80]}
    dt = time.time() - t0
    return {"ok": True, "ttft": ttft or dt, "sec": dt, "toks": toks,
            "tps": toks / dt if dt > 0 else 0.0}


def run_config(model: str, concurrency: int, cont_batch: bool, ctx: int,
               n_predict: int) -> dict:
    """Start a server, hammer it at `concurrency`, tear it down."""
    args = [SERVER, "-m", model, "--host", HOST, "--port", str(PORT),
            "-ngl", "99", "-c", str(ctx), "-np", str(concurrency),
            "--no-webui", "-fa", "on"]
    args.append("-cb" if cont_batch else "-nocb")
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        if not wait_ready():
            return {"ok": False, "err": "server did not become ready"}
        one_request(16)                      # warm up, not measured
        used = vram_mb()
        # each client gets a DIFFERENT output length and a slightly different
        # start time — see MIXED_LENGTHS above for why this matters.
        def client(i: int) -> dict:
            time.sleep((i % 4) * ARRIVAL_JITTER_SEC)
            return one_request(MIXED_LENGTHS[i % len(MIXED_LENGTHS)])

        t0 = time.time()
        with ThreadPoolExecutor(max_workers=concurrency) as ex:
            res = list(ex.map(client, range(concurrency)))
        wall = time.time() - t0
        good = [r for r in res if r.get("ok")]
        if not good:
            return {"ok": False, "err": res[0].get("err", "all requests failed")}
        total_toks = sum(r["toks"] for r in good)
        return {
            "ok": True, "concurrency": concurrency, "cont_batching": cont_batch,
            "requests_ok": len(good), "wall_sec": round(wall, 2),
            "aggregate_tps": round(total_toks / wall, 1),
            "per_stream_tps": round(statistics.mean(r["tps"] for r in good), 1),
            "mean_ttft_sec": round(statistics.mean(r["ttft"] for r in good), 2),
            "vram_mb": used,
        }
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
        time.sleep(3)                        # let VRAM actually free


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--sweep", default="1,2,4,8,16",
                    help="comma-separated concurrency levels")
    ap.add_argument("--ctx", type=int, default=8192, help="TOTAL context, split across slots")
    ap.add_argument("--n-predict", type=int, default=128)
    ap.add_argument("--out", default="serving_bench_results.json")
    a = ap.parse_args()

    levels = [int(x) for x in a.sweep.split(",")]
    rows = []
    print(f"model   : {Path(a.model).name}")
    print(f"ctx     : {a.ctx} total, split across slots")
    print(f"predict : {a.n_predict} tokens/request\n")
    for cb in (True, False):
        for n in levels:
            tag = "cont-batching" if cb else "NO batching  "
            print(f"  {tag} · concurrency {n:>3} ... ", end="", flush=True)
            r = run_config(a.model, n, cb, a.ctx, a.n_predict)
            if r.get("ok"):
                print(f"agg {r['aggregate_tps']:>7.1f} tok/s | "
                      f"per-stream {r['per_stream_tps']:>5.1f} | "
                      f"TTFT {r['mean_ttft_sec']:>5.2f}s | {r['vram_mb']} MB")
                rows.append(r)
            else:
                print(f"FAILED: {r.get('err')}")
                rows.append({"ok": False, "concurrency": n, "cont_batching": cb,
                             "err": r.get("err")})
    Path(a.out).write_text(json.dumps(rows, indent=2))
    print(f"\nwrote {a.out}  ({len([r for r in rows if r.get('ok')])} good runs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
