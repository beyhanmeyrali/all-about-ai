"""Real side-by-side examples for DIFFUSIONGEMMA.md: the same inputs sent to
DiffusionGemma (OpenJev API) and to Qwen 3 30B-A3B (llama-server), raw replies kept.

Only one model fits the 8 GB GPU at a time, so run it in two phases:
    python side_by_side.py --dg http://127.0.0.1:8080      # openjev_llamacpp.py running
    python side_by_side.py --qwen http://127.0.0.1:8081    # llama-server running
Results merge into examples.json.
"""
import argparse
import json
import re
import time
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
OUT = HERE / "examples.json"

TOPIC = {"type": "choice", "instructions": "What is the topic of this news article?",
         "criteria": {"World": "", "Sports": "", "Business": "", "Sci/Tech": ""}}
TOPICS = ["World", "Sports", "Business", "Sci/Tech"]

TICKET = ("Hi, I was charged twice for my March invoice and the app keeps logging me out "
          "when I try to download the receipt. I need this fixed today, my accountant is waiting. "
          "This is the third time I'm writing!!")
TICKET_QS = {
    "is_billing": {"type": "noul", "instructions": "Is this about billing or payments?"},
    "is_bug": {"type": "noul", "instructions": "Does the customer report a software bug?"},
    "angry": {"type": "noul", "instructions": "Is the customer angry or frustrated?"},
    "team": {"type": "choice", "instructions": "Which team should handle it first?",
             "criteria": {"billing": "", "engineering": "", "sales": "", "account security": ""}},
    "urgency": {"type": "score", "instructions": "How urgent is this ticket?",
                "criteria": ["not urgent", "low", "medium", "high", "critical"]},
}


def load():
    return json.loads(OUT.read_text()) if OUT.exists() else {}


def system_text(questions):
    """OpenJev's exact system prompt, so both models see identical instructions."""
    from openjev.config import Settings
    from openjev.engine import Engine
    eng = Engine.__new__(Engine)
    eng.s, eng.choice_labels = Settings(), [chr(c) for c in range(ord("A"), ord("Z") + 1)]
    schema = eng.build_schema(questions)
    return eng.system_text(schema["questions"], schema["format"])


def agnews_cases():
    rows = json.load(open(HERE / "data/agnews_200.json"))
    return rows


def run_dg(url):
    c = httpx.Client(base_url=url, timeout=300)
    res = load()

    def ask(state, questions):
        t0 = time.perf_counter()
        r = c.post("/v1/systemone", json={"model": "jev-latest", "state": state, "questions": questions}).json()
        return r, (time.perf_counter() - t0) * 1000

    rows = agnews_cases()
    idx = res.get("qwen_format_failures_idx") or list(range(8))
    res["dg_agnews"] = []
    for i in idx:
        ask(rows[i]["text"], {"q": TOPIC})  # prefill + warm; time the answer below from cold state separately
    for i in idx:
        r, ms = ask(rows[i]["text"] + " ", {"q": TOPIC})  # trailing space: a new state, so it is a cold read
        res["dg_agnews"].append({"i": i, "gold": TOPICS[rows[i]["label"]], "answer": r["answers"]["q"], "ms": ms})
    r, ms = ask(TICKET, TICKET_QS)
    r2, ms_warm = ask(TICKET, TICKET_QS)
    res["dg_ticket"] = {"answer": r["answers"], "ms_cold": ms, "ms_warm_same_request": ms_warm}
    one = []
    for k, q in TICKET_QS.items():
        _, m = ask(TICKET + f" [{k}]", {k: q})
        one.append(m)
    res["dg_ticket_one_at_a_time_ms"] = sum(one)
    OUT.write_text(json.dumps(res, indent=2))
    print(json.dumps({k: v for k, v in res.items() if k.startswith("dg")}, indent=1)[:4000])


def run_qwen(url):
    c = httpx.Client(base_url=url, timeout=300)
    res = load()
    rows = agnews_cases()
    sys_t = system_text({"q": TOPIC})
    fails, gens = [], {}
    for i, r in enumerate(rows):
        d = c.post("/v1/chat/completions", json={
            "messages": [{"role": "system", "content": sys_t}, {"role": "user", "content": r["text"]}],
            "max_tokens": 16, "temperature": 0, "chat_template_kwargs": {"enable_thinking": False}}).json()
        text = d["choices"][0]["message"]["content"]
        gens[i] = text
        if not re.fullmatch(r"\s*q1\s*:\s*[A-D]\s*", text):
            fails.append(i)
    idx = fails[:6]
    res["qwen_format_failures_idx"] = idx
    res["qwen_format_failure_count"] = len(fails)
    res["qwen_agnews"] = [{"i": i, "gold": TOPICS[rows[i]["label"]], "raw_reply": gens[i]} for i in idx]
    res["qwen_agnews_system_prompt"] = sys_t
    # the same five ticket questions, answered by generating text
    sys_k = system_text(TICKET_QS)
    t0 = time.perf_counter()
    d = c.post("/v1/chat/completions", json={
        "messages": [{"role": "system", "content": sys_k}, {"role": "user", "content": TICKET}],
        "max_tokens": 64, "temperature": 0, "chat_template_kwargs": {"enable_thinking": False}}).json()
    res["qwen_ticket"] = {"raw_reply": d["choices"][0]["message"]["content"], "ms": (time.perf_counter() - t0) * 1000,
                          "completion_tokens": d["usage"]["completion_tokens"], "system_prompt": sys_k}
    OUT.write_text(json.dumps(res, indent=2))
    print(json.dumps({k: v for k, v in res.items() if k.startswith("qwen")}, indent=1)[:4000])


def run_jev(model):
    from systemone_bench import jev_decide, openrouter_key
    c = httpx.Client(timeout=120, headers={"Authorization": f"Bearer {openrouter_key()}"})
    res = load()
    rows = agnews_cases()
    res["jev_agnews"] = []
    for i in res.get("qwen_format_failures_idx") or list(range(6)):
        ans, usage, ms = jev_decide(c, model, rows[i]["text"], {"q": TOPIC})
        res["jev_agnews"].append({"i": i, "gold": TOPICS[rows[i]["label"]], "answer": ans["q"], "ms": ms, "usage": usage})
    ans, usage, ms = jev_decide(c, model, TICKET, TICKET_QS)
    res["jev_ticket"] = {"answer": ans, "ms": ms, "usage": usage}
    OUT.write_text(json.dumps(res, indent=2))
    print(json.dumps({k: v for k, v in res.items() if k.startswith("jev")}, indent=1)[:4000])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dg")
    ap.add_argument("--qwen")
    ap.add_argument("--jev", nargs="?", const="typesafe/jev-1.13")
    a = ap.parse_args()
    if a.jev:
        run_jev(a.jev)
    if a.qwen:
        run_qwen(a.qwen)
    if a.dg:
        run_dg(a.dg)
