"""Speed and token efficiency as the number of questions grows: the head-to-head
behind the TL;DR of DIFFUSIONGEMMA.md.

Same news article, N yes/no questions (N = 1, 2, 5, 10, 20), OpenJev's exact
instructions for both models. Only one model fits the 8 GB GPU at a time:
    python speed_scaling.py --qwen http://127.0.0.1:8081   # llama-server (Qwen 3 30B-A3B)
    OPENJEV_AUTO_MAX=1 OPENJEV_CANVAS=128 python speed_scaling.py --dg ...  # env on openjev_llamacpp.py
"cold" = the model must read the whole prompt (Qwen: llama-server prompt cache off);
"warm" = the same request again (the text is cached, so only the answering is timed).
OPENJEV_CANVAS=128 lets 20 questions fit one canvas (the default 64 splits them in two).
    python speed_scaling.py --jev                            # TypeSafe Jev on OpenRouter (network latency included)
Merges into speed_scaling.json.
"""
import argparse
import json
import re
import statistics
import time
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
OUT = HERE / "speed_scaling.json"
NS = (1, 2, 5, 10, 20)
REPS = 3
STATE = json.load(open(HERE / "data/agnews_200.json"))[0]["text"]
POOL = [{"type": "noul", "instructions": f"Does the article mention {w}?"} for w in
        ["a country", "a company", "money", "a sport", "a person", "a date", "a technology",
         "a government", "a number", "a city", "a crime", "an election", "a product", "science",
         "a war", "a stock market", "a team", "health", "the internet", "energy"]]


def questions(n):
    return {f"q{j}": POOL[j] for j in range(n)}


def med(xs):
    return statistics.median(xs)


def load():
    return json.loads(OUT.read_text()) if OUT.exists() else {}


def run_qwen(url):
    from openjev.config import Settings
    from openjev.engine import Engine
    eng = Engine.__new__(Engine)
    eng.s, eng.choice_labels = Settings(), [chr(c) for c in range(ord("A"), ord("Z") + 1)]
    c = httpx.Client(base_url=url, timeout=600)
    rows = []
    for n in NS:
        schema = eng.build_schema(questions(n))
        sys_t = eng.system_text(schema["questions"], schema["format"])

        def ask(state, cache):
            t0 = time.perf_counter()
            d = c.post("/v1/chat/completions", json={
                "messages": [{"role": "system", "content": sys_t}, {"role": "user", "content": state}],
                "max_tokens": 12 * n, "temperature": 0, "cache_prompt": cache,
                "chat_template_kwargs": {"enable_thinking": False}}).json()
            return (time.perf_counter() - t0) * 1000, d

        # cold: prompt cache off, so the whole prompt is read, as the DiffusionGemma server must
        cold = [ask(STATE + f" [{n}.{r}]", False) for r in range(REPS)]
        ask(STATE + f" [{n}.0]", True)
        warm = [ask(STATE + f" [{n}.0]", True) for r in range(REPS)]
        text = cold[0][1]["choices"][0]["message"]["content"]
        want = [f"q{j + 1}: (yes|no)" for j in range(n)] if schema["format"] == "lines" else None
        well_formed = bool(want) and all(re.fullmatch(w, l.strip()) for w, l in zip(want, text.strip().split("\n"))) \
            and len(text.strip().split("\n")) == n
        rows.append({"questions": n,
                     "cold_ms": med([m for m, _ in cold]), "warm_ms": med([m for m, _ in warm]),
                     "prompt_tokens": cold[0][1]["usage"]["prompt_tokens"],
                     "output_tokens": cold[0][1]["usage"]["completion_tokens"],
                     "well_formed": well_formed, "reply": text})
        print("qwen", json.dumps({k: v for k, v in rows[-1].items() if k != "reply"}), flush=True)
    res = load()
    res["qwen_write"] = rows
    OUT.write_text(json.dumps(res, indent=2))


def run_dg(url):
    c = httpx.Client(base_url=url, timeout=600)
    rows = []
    for n in NS:
        def ask(state):
            t0 = time.perf_counter()
            d = c.post("/v1/systemone", json={"model": "jev-latest", "state": state, "questions": questions(n)}).json()
            return (time.perf_counter() - t0) * 1000, d

        cold = [ask(STATE + f" [{n}.{r}]") for r in range(REPS)]
        warm = [ask(STATE + f" [{n}.{REPS - 1}]") for r in range(REPS)]
        rows.append({"questions": n,
                     "cold_ms": med([m for m, _ in cold]), "warm_ms": med([m for m, _ in warm]),
                     "input_tokens": cold[0][1]["usage"]["input_tokens"],
                     "output_tokens": cold[0][1]["usage"]["output_tokens"]})
        print("dg", json.dumps(rows[-1]), flush=True)
    res = load()
    res["diffusiongemma_read"] = rows
    OUT.write_text(json.dumps(res, indent=2))


def run_jev(model):
    from systemone_bench import jev_decide, openrouter_key
    c = httpx.Client(timeout=120, headers={"Authorization": f"Bearer {openrouter_key()}"})
    rows = []
    for n in NS:
        cold = [jev_decide(c, model, STATE + f" [{n}.{r}]", questions(n)) for r in range(REPS)]
        warm = [jev_decide(c, model, STATE + f" [{n}.0]", questions(n)) for r in range(REPS)]
        usage = cold[0][1]
        rows.append({"questions": n, "cold_ms": med([m for _, _, m in cold]), "warm_ms": med([m for _, _, m in warm]),
                     "input_tokens": usage.get("input_tokens", usage.get("prompt_tokens")),
                     "output_tokens": usage.get("output_tokens", usage.get("completion_tokens", 0)),
                     "cost_usd": usage.get("cost"), "usage": usage})
        print("jev", json.dumps(rows[-1]), flush=True)
    res = load()
    res["jev_openrouter"] = rows
    OUT.write_text(json.dumps(res, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--qwen")
    ap.add_argument("--dg")
    ap.add_argument("--jev", nargs="?", const="typesafe/jev-1.13")
    a = ap.parse_args()
    if a.jev:
        run_jev(a.jev)
    if a.qwen:
        run_qwen(a.qwen)
    if a.dg:
        run_dg(a.dg)
