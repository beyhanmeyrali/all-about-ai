"""Benchmark OpenJev-style System One reads on DiffusionGemma (llama.cpp, 8 GB GPU)
against an ordinary autoregressive LLM answering the same questions as text.

    python systemone_bench.py --reads -- -m dg.gguf -ngl 99 --n-cpu-moe 26 -fa on
    python systemone_bench.py --ar-url http://127.0.0.1:8081   # llama-server baseline

What it measures, per task (SST-2 sentiment = yes/no, AG News topic = 4-way choice,
200 held-out examples each, fixed seed):
  accuracy, latency p50/p95 per decision, ECE + Brier (calibration: does a 0.9
  answer come true 90 % of the time?), and for the AR baseline the number of
  replies that were not a valid label ("format errors").
Plus a sweep of how read latency grows with the number of questions per request.
Results are merged into results.json next to this file.
"""
import argparse
import asyncio
import json
import math
import re
import statistics
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results.json"

TASKS = {
    "sst2": {
        "file": "data/sst2_200.json",
        "question": {"type": "noul", "instructions": "Is the sentiment of this movie review positive?"},
        "labels": ["negative", "positive"],
    },
    "agnews": {
        "file": "data/agnews_200.json",
        "question": {"type": "choice", "instructions": "What is the topic of this news article?",
                     "criteria": {"World": "", "Sports": "", "Business": "", "Sci/Tech": ""}},
        "labels": ["World", "Sports", "Business", "Sci/Tech"],
    },
}


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(p / 100 * (len(xs) - 1))))]


def calibration(conf, correct, bins=10):
    """ECE over the predicted class's probability, 10 equal-width bins."""
    n, ece = len(conf), 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        idx = [i for i, c in enumerate(conf) if (lo < c <= hi) or (b == 0 and c == 0)]
        if idx:
            ece += len(idx) / n * abs(sum(correct[i] for i in idx) / len(idx) - sum(conf[i] for i in idx) / len(idx))
    return ece


def summarize(lat_ms, correct, conf=None, probs=None, gold=None, extra=None):
    out = {"n": len(correct), "accuracy": sum(correct) / len(correct),
           "p50_ms": pct(lat_ms, 50), "p95_ms": pct(lat_ms, 95), "mean_ms": statistics.mean(lat_ms)}
    if conf is not None:
        out["mean_confidence"] = statistics.mean(conf)
        out["ece"] = calibration(conf, correct)
        out["brier"] = statistics.mean(
            sum((p - (1.0 if k == g else 0.0)) ** 2 for k, p in enumerate(ps)) for ps, g in zip(probs, gold))
    out.update(extra or {})
    return out


# ----------------------------------------------------------------- System One reads

async def bench_reads(server_args, tasks, sweep, limit=None):
    sys.path.insert(0, str(HERE))
    from transformers import AutoTokenizer
    from openjev.config import Settings
    from openjev_llamacpp import TOKENIZER, LlamaCppEngine

    LlamaCppEngine.server_args = server_args
    eng = LlamaCppEngine(Settings(), AutoTokenizer.from_pretrained(TOKENIZER))
    reads = {"n": 0, "prefill_ms": [], "decode_ms": []}
    inner = eng.one_read

    async def counted(*a, **kw):
        r = await inner(*a, **kw)
        reads["n"] += 1
        (reads["decode_ms"]).append(eng.last_timing["decode_ms"])
        if not eng.last_timing["cached"]:
            reads["prefill_ms"].append(eng.last_timing["prefill_ms"])
        return r

    eng.one_read = counted
    for i in range(3):  # warm-up: CUDA graphs, allocator, page cache
        await eng.decide({"q": TASKS["sst2"]["question"]}, "warm up read number %d" % i, i)

    out = {}
    for name in tasks:
        t = TASKS[name]
        rows = json.load(open(HERE / t["file"]))[:limit]
        reads.update(n=0, prefill_ms=[], decode_ms=[])
        lat, correct, conf, probs, gold = [], [], [], [], []
        for i, r in enumerate(rows):
            t0 = time.perf_counter()
            ans, _, _ = await eng.decide({"q": t["question"]}, r["text"], 1000 + i)
            lat.append((time.perf_counter() - t0) * 1000)
            a = ans["q"]
            if a["type"] == "noul":
                p = [1 - a["noul"], a["noul"]]  # index 1 = positive = yes
            else:
                p = [a["probabilities"][k] for k in t["labels"]]
            pred = max(range(len(p)), key=p.__getitem__)
            correct.append(int(pred == r["label"]))
            conf.append(p[pred])
            probs.append(p)
            gold.append(r["label"])
        out[name] = summarize(lat, correct, conf, probs, gold, {
            "reads_per_decision": reads["n"] / len(rows),
            "prefill_ms_p50": pct(reads["prefill_ms"], 50),
            "decode_ms_p50": pct(reads["decode_ms"], 50)})
        print(name, json.dumps(out[name]), flush=True)

    if sweep:
        # how does one read scale with the number of questions? (auto re-reads off: one pass each)
        eng.s = type(eng.s)(**{**eng.s.__dict__, "auto_max": 1})
        state = json.load(open(HERE / TASKS["agnews"]["file"]))[0]["text"]
        qpool = [{"type": "noul", "instructions": f"Does the article mention {w}?"} for w in
                 ["a country", "a company", "money", "a sport", "a person", "a date", "a technology",
                  "a government", "a number", "a city", "a crime", "an election", "a product", "science",
                  "a war", "a stock market", "a team", "health", "the internet", "energy"]]
        out["sweep"] = []
        for k in (1, 2, 5, 10, 20):
            qs = {f"q{j}": qpool[j] for j in range(k)}
            await eng.decide(qs, state, 1)  # prefill this prompt once; measure the warm read
            lat, dec = [], []
            for rep in range(10):
                t0 = time.perf_counter()
                await eng.decide(qs, state, 7 + rep)
                lat.append((time.perf_counter() - t0) * 1000)
                dec.append(eng.last_timing["decode_ms"])
            cold = []
            for rep in range(5):  # a new state each time: prefill + decode
                t0 = time.perf_counter()
                await eng.decide(qs, state + f" (#{rep})", 7 + rep)
                cold.append((time.perf_counter() - t0) * 1000)
            row = {"questions": k, "warm_p50_ms": pct(lat, 50), "decode_p50_ms": pct(dec, 50),
                   "cold_p50_ms": pct(cold, 50)}
            out["sweep"].append(row)
            print("sweep", json.dumps(row), flush=True)
    await eng.close()
    return out


# ----------------------------------------------------------------- autoregressive baseline

def bench_ar(url, model_name, tasks, max_tokens):
    import httpx
    from openjev.config import Settings
    from openjev.engine import Engine

    class _Tok:  # system_text never tokenizes
        pass

    eng = Engine.__new__(Engine)
    eng.s, eng.tok, eng.choice_labels = Settings(), _Tok(), [chr(c) for c in range(ord("A"), ord("Z") + 1)]
    client = httpx.Client(base_url=url, timeout=300)
    out = {}
    for name in tasks:
        t = TASKS[name]
        rows = json.load(open(HERE / t["file"]))
        schema = eng.build_schema({"q": t["question"]})
        q = schema["questions"][0]
        sys_text = eng.system_text(schema["questions"], schema["format"])
        labels = [l.lower() for l in q["labels"]]
        names = [c[0].lower() for c in q["choices"]]

        def lenient(text):
            """Recover the label from a reply in the wrong shape ('D: D', 'B: Sports', 'C')."""
            parts = [p.strip(" .\"'\n").lower() for p in text.split(":")]
            for p in reversed(parts):
                if p in labels:
                    return labels.index(p)
                if q["type"] == "choice" and p in names:
                    return names.index(p)
            return None

        lat, correct, loose, bad, gen_tokens = [], [], [], 0, []
        for r in rows:
            body = {"messages": [{"role": "system", "content": sys_text}, {"role": "user", "content": r["text"]}],
                    "max_tokens": max_tokens, "temperature": 0,
                    "chat_template_kwargs": {"enable_thinking": False}}
            t0 = time.perf_counter()
            d = client.post("/v1/chat/completions", json=body).json()
            lat.append((time.perf_counter() - t0) * 1000)
            text = d["choices"][0]["message"]["content"] or ""
            gen_tokens.append(d.get("usage", {}).get("completion_tokens", 0))
            to_pred = (lambda li: 1 - li) if q["type"] == "noul" else (lambda li: li)  # noul labels are [yes, no]
            m = re.fullmatch(r"\s*q1\s*:\s*(\S+)\s*", text)  # the exact shape the prompt asked for
            strict = labels.index(m.group(1).lower()) if m and m.group(1).lower() in labels else None
            bad += strict is None
            correct.append(int(strict is not None and to_pred(strict) == r["label"]))
            li = lenient(text)
            loose.append(int(li is not None and to_pred(li) == r["label"]))
        out[name] = summarize(lat, correct, extra={"format_errors": bad,
                                                   "accuracy_lenient": sum(loose) / len(loose),
                                                   "mean_completion_tokens": statistics.mean(gen_tokens),
                                                   "model": model_name})
        print("ar", name, json.dumps(out[name]), flush=True)
    return out


def bench_ar_read(url, model_name, tasks):
    """The same trick on an autoregressive model: pre-fill the reply up to "q1:"
    and read the next-token distribution over the labels. One prefill, zero
    generated tokens. It works for one question; a second slot would need the
    first answer committed first -- that ordering is what diffusion removes."""
    import httpx
    from openjev.config import Settings
    from openjev.engine import Engine, confidence

    eng = Engine.__new__(Engine)
    eng.s, eng.choice_labels = Settings(), [chr(c) for c in range(ord("A"), ord("Z") + 1)]
    client = httpx.Client(base_url=url, timeout=300)
    out = {}
    for name in tasks:
        t = TASKS[name]
        rows = json.load(open(HERE / t["file"]))
        schema = eng.build_schema({"q": t["question"]})
        q = schema["questions"][0]
        sys_text = eng.system_text(schema["questions"], schema["format"])
        labels = [l.lower() for l in q["labels"]]
        lat, correct, conf, probs, gold = [], [], [], [], []
        for r in rows:
            t0 = time.perf_counter()
            tmpl = client.post("/apply-template", json={
                "messages": [{"role": "system", "content": sys_text}, {"role": "user", "content": r["text"]}],
                "chat_template_kwargs": {"enable_thinking": False}}).json()["prompt"]
            d = client.post("/completion", json={"prompt": tmpl + "q1:", "n_predict": 1, "n_probs": 50,
                                                 "temperature": 0, "cache_prompt": True}).json()
            lat.append((time.perf_counter() - t0) * 1000)
            p = [0.0] * len(labels)
            for tp in d["completion_probabilities"][0]["top_logprobs"]:
                tok = tp["token"].strip().lower()
                if tok in labels:
                    p[labels.index(tok)] += math.exp(tp["logprob"])
            z = sum(p) or 1.0
            p = [x / z for x in p]
            if q["type"] == "noul":
                p = [p[1], p[0]]  # -> [negative, positive]
            pred = max(range(len(p)), key=p.__getitem__)
            correct.append(int(pred == r["label"]))
            conf.append(p[pred])
            probs.append(p)
            gold.append(r["label"])
        out[name] = summarize(lat, correct, conf, probs, gold, {"model": model_name})
        print("ar-read", name, json.dumps(out[name]), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reads", action="store_true", help="run System One reads (args after -- go to the server)")
    ap.add_argument("--ar-url", help="llama-server base URL for the autoregressive baseline")
    ap.add_argument("--ar-name", default="ar-baseline")
    ap.add_argument("--ar-max-tokens", type=int, default=16)
    ap.add_argument("--tasks", default="sst2,agnews")
    ap.add_argument("--no-sweep", action="store_true")
    ap.add_argument("--limit", type=int, help="first N examples per task (quick --n-cpu-moe sweeps)")
    ap.add_argument("--label", default="diffusiongemma", help="results.json key for this run")
    args, server_args = ap.parse_known_args()
    server_args = [a for a in server_args if a != "--"]
    tasks = args.tasks.split(",")
    res = json.load(open(RESULTS)) if RESULTS.exists() else {}
    if args.reads:
        res[args.label] = {"server_args": server_args, **asyncio.run(bench_reads(server_args, tasks, not args.no_sweep, args.limit))}
    if args.ar_url:
        res[args.ar_name] = bench_ar(args.ar_url, args.ar_name, tasks, args.ar_max_tokens)
        res[args.ar_name + "-read"] = bench_ar_read(args.ar_url, args.ar_name, tasks)
    json.dump(res, open(RESULTS, "w"), indent=2)
    print("wrote", RESULTS)


if __name__ == "__main__":
    main()
