"""Confidence cascades: answer with a fast, cheap model first; send only its unsure
answers to a stronger one. Uses per-question probabilities, which the summary
benchmark doesn't keep.

    python cascade_analysis.py            # Laya (local) -> Jev (OpenRouter) on 200 SST-2 reviews
Writes cascade.json: per-question predictions, and accuracy / escalation / time / cost
for a range of confidence thresholds. Laya can run on the CPU here (--laya-device cpu):
that changes its speed, not its answers, so time estimates use its measured GPU p50.
"""
import argparse
import json
import sys
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from systemone_bench import TASKS, jev_decide, laya_agent, laya_decide, openrouter_key  # noqa: E402

THRESHOLDS = (0.6, 0.7, 0.8, 0.9, 0.95, 0.99)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--laya-device", default="cuda")
    a = ap.parse_args()
    rows = json.load(open(HERE / TASKS["sst2"]["file"]))
    laya = laya_agent(device=a.laya_device)
    jev = httpx.Client(timeout=120, headers={"Authorization": f"Bearer {openrouter_key()}"})
    res = json.load(open(HERE / "results.json"))
    laya_ms = res["laya"]["sst2_choice"]["p50_ms"]           # GPU-measured
    jev_ms = res["jev-openrouter"]["sst2"]["p50_ms"]
    jev_cost_each = res["jev-openrouter"]["sst2"]["total_cost_usd"] / res["jev-openrouter"]["sst2"]["n"]

    items = []
    for i, r in enumerate(rows):
        la, _, _ = laya_decide(laya, r["text"], {"q": TASKS["sst2_choice"]["question"]})
        lp = la["q"]["probabilities"]
        lpred, lconf = max(lp, key=lp.get), max(lp.values())
        ja, usage, _ = jev_decide(jev, "typesafe/jev-1.13", r["text"], {"q": TASKS["sst2"]["question"]})
        py = ja["q"]["noul"]
        jpred, jconf = ("positive", py) if py >= 0.5 else ("negative", 1 - py)
        gold = TASKS["sst2"]["labels"][r["label"]]
        items.append({"i": i, "gold": gold, "laya": lpred, "laya_conf": lconf, "jev": jpred, "jev_conf": jconf,
                      "jev_cost": usage.get("cost", 0.0)})
        if i % 50 == 49:
            print(f"{i + 1}/{len(rows)}", flush=True)

    n = len(items)
    acc = lambda pairs: sum(p == g for p, g in pairs) / len(pairs) if pairs else None
    out = {"laya_alone": {"accuracy": acc([(x["laya"], x["gold"]) for x in items]), "ms": laya_ms, "cost_per_1k": 0.0},
           "jev_alone": {"accuracy": acc([(x["jev"], x["gold"]) for x in items]), "ms": jev_ms,
                         "cost_per_1k": 1000 * jev_cost_each},
           "cascade": []}
    for t in THRESHOLDS:
        kept = [x for x in items if x["laya_conf"] >= t]
        esc = [x for x in items if x["laya_conf"] < t]
        final = [(x["laya"], x["gold"]) for x in kept] + [(x["jev"], x["gold"]) for x in esc]
        out["cascade"].append({
            "threshold": t, "answered_by_laya_pct": 100 * len(kept) / n,
            "laya_accuracy_on_kept": acc([(x["laya"], x["gold"]) for x in kept]),
            "overall_accuracy": acc(final),
            "mean_ms": laya_ms + len(esc) / n * jev_ms,
            "cost_per_1k": 1000 * jev_cost_each * len(esc) / n})
        print(json.dumps(out["cascade"][-1]), flush=True)
    print("laya alone", out["laya_alone"], "| jev alone", out["jev_alone"])
    out["items"] = items
    (HERE / "cascade.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
