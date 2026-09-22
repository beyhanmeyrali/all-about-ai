"""Tetris as a decision benchmark: Jev vs DiffusionGemma vs Qwen (plus heuristic and random).

Every move is one typed decision. The model sees the board (ASCII), the current and
next piece, and a list of every legal placement for the current piece, each with its
consequences (lines cleared, new holes, resulting height and bumpiness). It must pick
one. Pieces come from a seeded 7-bag, so every player faces the same sequence.

    python tetris_bench.py --player heuristic|random
    python tetris_bench.py --player jev                            # OPENROUTER_API_KEY
    python tetris_bench.py --player dg --url http://127.0.0.1:8080  # openjev_llamacpp.py
    python tetris_bench.py --player qwen --url http://127.0.0.1:8081  # llama-server
    python tetris_bench.py --player laya                           # convaiinnovations/laya, in-process
Results merge into tetris_results.json (per game and per move).
"""
import argparse
import json
import random
import re
import statistics
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "tetris_results.json"
W, H = 10, 20
SEEDS = (1, 2, 3)
MAX_PIECES = 80
INSTRUCTIONS = ("You are playing Tetris and want to survive as long as possible and clear lines. "
                "Pick the placement for the current piece: prefer clearing lines, avoid creating holes, "
                "and keep the stack low and flat.")

# (x, y) cells, y grows downwards; each piece lists its distinct rotations
SHAPES = {
    "I": [[(0, 0), (1, 0), (2, 0), (3, 0)], [(0, 0), (0, 1), (0, 2), (0, 3)]],
    "O": [[(0, 0), (1, 0), (0, 1), (1, 1)]],
    "T": [[(0, 0), (1, 0), (2, 0), (1, 1)], [(1, 0), (0, 1), (1, 1), (1, 2)],
          [(1, 0), (0, 1), (1, 1), (2, 1)], [(0, 0), (0, 1), (1, 1), (0, 2)]],
    "S": [[(1, 0), (2, 0), (0, 1), (1, 1)], [(0, 0), (0, 1), (1, 1), (1, 2)]],
    "Z": [[(0, 0), (1, 0), (1, 1), (2, 1)], [(1, 0), (0, 1), (1, 1), (0, 2)]],
    "J": [[(0, 0), (0, 1), (1, 1), (2, 1)], [(0, 0), (1, 0), (0, 1), (0, 2)],
          [(0, 0), (1, 0), (2, 0), (2, 1)], [(1, 0), (1, 1), (0, 2), (1, 2)]],
    "L": [[(2, 0), (0, 1), (1, 1), (2, 1)], [(0, 0), (0, 1), (0, 2), (1, 2)],
          [(0, 0), (1, 0), (2, 0), (0, 1)], [(0, 0), (1, 0), (1, 1), (1, 2)]],
}


def pieces(seed):
    rng, bag = random.Random(seed), []
    while True:
        if not bag:
            bag = list("IOTSZJL")
            rng.shuffle(bag)
        yield bag.pop()


def drop(board, cells, col):
    """Hard-drop a rotation at column col. Returns the new board, or None if it doesn't fit."""
    y = -4
    fits = lambda yy: all(0 <= col + x < W and y_ + yy < H and (y_ + yy < 0 or not board[y_ + yy][col + x])
                          for x, y_ in cells)
    if not fits(y):
        return None
    while fits(y + 1):
        y += 1
    if any(y_ + y < 0 for _, y_ in cells):
        return None  # would lock above the top: game over
    new = [row[:] for row in board]
    for x, y_ in cells:
        new[y_ + y][col + x] = 1
    return new


def clear(board):
    keep = [r for r in board if not all(r)]
    lines = H - len(keep)
    return [[0] * W for _ in range(lines)] + keep, lines


def features(board):
    heights, holes = [], 0
    for x in range(W):
        col = [board[y][x] for y in range(H)]
        top = next((y for y in range(H) if col[y]), H)
        heights.append(H - top)
        holes += sum(1 for y in range(top, H) if not col[y])
    bump = sum(abs(heights[i] - heights[i + 1]) for i in range(W - 1))
    return {"agg_height": sum(heights), "max_height": max(heights), "holes": holes, "bumpiness": bump}


def options(board, piece):
    """Every legal placement with its consequences, de-duplicated by resulting board."""
    before = features(board)["holes"]
    seen, out = set(), []
    for r, cells in enumerate(SHAPES[piece]):
        width = max(x for x, _ in cells) + 1
        for col in range(W - width + 1):
            b = drop(board, cells, col)
            if b is None:
                continue
            b, lines = clear(b)
            key = tuple(map(tuple, b))
            if key in seen:
                continue
            seen.add(key)
            f = features(b)
            out.append({"name": f"rot{r}-col{col}", "board": b, "lines": lines, "new_holes": f["holes"] - before, **f})
    return out


def describe(o):
    return (f"clears {o['lines']} lines, {o['new_holes']:+d} holes, "
            f"max height {o['max_height']}, bumpiness {o['bumpiness']}")


def render(board, piece, nxt):
    rows = "\n".join("|" + "".join("#" if c else "." for c in row) + "|" for row in board)
    return f"Current piece: {piece}   Next piece: {nxt}\nBoard (10 wide, 20 tall, # = filled):\n{rows}\n+----------+"


def heuristic_score(o):
    # Yiyuan Lee's tuned weights (a well-known hand-made Tetris AI)
    return -0.510066 * o["agg_height"] + 0.760666 * o["lines"] - 0.35663 * o["holes"] - 0.184483 * o["bumpiness"]


# ---------------------------------------------------------------- players

class Player:
    name = "?"

    def choose(self, state, opts):
        """-> (index, info dict with ms / tokens / cost / invalid)."""
        raise NotImplementedError


class Heuristic(Player):
    name = "heuristic"

    def choose(self, state, opts):
        return max(range(len(opts)), key=lambda i: heuristic_score(opts[i])), {"ms": 0.0}


class Random(Player):
    name = "random"

    def __init__(self):
        self.rng = random.Random(0)

    def choose(self, state, opts):
        return self.rng.randrange(len(opts)), {"ms": 0.0}


def question(opts):
    return {"move": {"type": "choice", "instructions": INSTRUCTIONS,
                     "criteria": {o["name"]: describe(o) for o in opts}}}


class Decisions(Player):
    """Jev (OpenRouter) or DiffusionGemma (OpenJev): the same Jev-shaped request."""

    def __init__(self, kind, url=None, model="typesafe/jev-1.13"):
        import httpx
        self.name, self.model = kind, model
        if kind == "jev":
            from systemone_bench import openrouter_key
            self.c = httpx.Client(timeout=120, headers={"Authorization": f"Bearer {openrouter_key()}"})
            self.url = "https://openrouter.ai/api/alpha/decisions"
        else:
            self.c, self.url, self.model = httpx.Client(timeout=600), url.rstrip("/") + "/v1/systemone", "jev-latest"

    def choose(self, state, opts):
        body = {"model": self.model, "state": state, "questions": question(opts)}
        t0 = time.perf_counter()
        for attempt in range(5):
            r = self.c.post(self.url, json=body)
            if r.status_code not in (429, 500, 502, 503, 529):
                break
            time.sleep(2 * (attempt + 1))
        ms = (time.perf_counter() - t0) * 1000
        r.raise_for_status()
        d = r.json()
        pick = d["answers"]["move"]["choice"]
        u = d.get("usage", {})
        idx = next(i for i, o in enumerate(opts) if o["name"] == pick)
        return idx, {"ms": ms, "input_tokens": u.get("input_tokens"), "output_tokens": u.get("output_tokens", 0),
                     "cost": u.get("cost", 0.0) or 0.0, "confidence": d["answers"]["move"].get("confidence")}


class Qwen(Player):
    """A chat model typing its choice; same instructions OpenJev generates for the others."""
    name = "qwen"

    def __init__(self, url):
        import httpx
        from openjev.config import Settings
        from openjev.engine import Engine
        self.c, self.url = httpx.Client(base_url=url, timeout=600), url
        self.eng = Engine.__new__(Engine)
        self.eng.s = Settings()
        self.eng.choice_labels = [chr(c) for c in range(ord("A"), ord("Z") + 1)] + \
                                 [chr(c) for c in range(ord("a"), ord("z") + 1)]

    def choose(self, state, opts):
        if len(opts) == 1:  # a forced move: nothing to ask
            return 0, {"ms": 0.0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0, "invalid": False, "raw": None}
        schema = self.eng.build_schema(question(opts))
        q = schema["questions"][0]
        sys_t = self.eng.system_text(schema["questions"], schema["format"])
        t0 = time.perf_counter()
        d = self.c.post("/v1/chat/completions", json={
            "messages": [{"role": "system", "content": sys_t}, {"role": "user", "content": state}],
            "max_tokens": 8, "temperature": 0, "chat_template_kwargs": {"enable_thinking": False}}).json()
        ms = (time.perf_counter() - t0) * 1000
        text = d["choices"][0]["message"]["content"] or ""
        m = re.fullmatch(r"\s*q1\s*:\s*(\S+)\s*", text)
        label = m.group(1) if m else None
        invalid = label not in q["labels"]
        idx = q["labels"].index(label) if not invalid else 0  # a broken reply plays the first option
        return idx, {"ms": ms, "input_tokens": d["usage"]["prompt_tokens"],
                     "output_tokens": d["usage"]["completion_tokens"], "cost": 0.0, "invalid": invalid,
                     "raw": text if invalid else None}


class LayaPlayer(Player):
    """Laya (convaiinnovations) in-process on the GPU. Every option is scored at its own marker inside a
    fixed option budget (head_max_len, 192 tokens by default), too small for ~20-34 Tetris placements,
    so it is raised to 512 as the model card suggests. A move that still doesn't fit plays option 0."""
    name = "laya"

    def __init__(self):
        from systemone_bench import laya_agent, laya_decide
        self.agent, self.decide = laya_agent(head_max_len=512), laya_decide

    def choose(self, state, opts):
        if len(opts) == 1:
            return 0, {"ms": 0.0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0, "invalid": False}
        try:
            ans, usage, ms = self.decide(self.agent, state, question(opts))
        except ValueError as e:  # options exceed head_max_len
            return 0, {"ms": 0.0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0, "invalid": True, "raw": str(e)[:120]}
        pick = ans["move"]["choice"]
        idx = next(i for i, o in enumerate(opts) if o["name"] == pick)
        return idx, {"ms": ms, "input_tokens": usage.get("input_tokens"), "output_tokens": 0, "cost": 0.0,
                     "invalid": False, "confidence": ans["move"].get("confidence")}


# ---------------------------------------------------------------- game loop

def play(player, seed):
    board = [[0] * W for _ in range(H)]
    gen = pieces(seed)
    cur, nxt = next(gen), next(gen)
    placed = lines = 0
    moves = []
    while placed < MAX_PIECES:
        opts = options(board, cur)
        if not opts:
            break  # topped out
        idx, info = player.choose(render(board, cur, nxt), opts)
        o = opts[idx]
        best = max(heuristic_score(x) for x in opts)
        info.update(piece=cur, choice=o["name"], n_options=len(opts), lines=o["lines"],
                    heuristic_regret=round(best - heuristic_score(o), 3))
        moves.append(info)
        board, lines, placed = o["board"], lines + o["lines"], placed + 1
        cur, nxt = nxt, next(gen)
    f = features(board)
    return {"seed": seed, "pieces": placed, "survived": placed >= MAX_PIECES, "lines": lines,
            "final_holes": f["holes"], "final_max_height": f["max_height"],
            "final_board": ["".join("#" if c else "." for c in row) for row in board], "moves": moves}


def summarize(games):
    mv = [m for g in games for m in g["moves"]]
    ms = [m["ms"] for m in mv]
    s = {"games": len(games), "pieces_total": sum(g["pieces"] for g in games),
         "games_survived": sum(g["survived"] for g in games), "lines_total": sum(g["lines"] for g in games),
         "moves": len(mv), "mean_options": statistics.mean(m["n_options"] for m in mv),
         "agree_with_heuristic_pct": 100 * sum(m["heuristic_regret"] == 0 for m in mv) / len(mv),
         "p50_ms_per_move": statistics.median(ms), "mean_ms_per_move": statistics.mean(ms)}
    if any("input_tokens" in m for m in mv):
        s["mean_input_tokens"] = statistics.mean(m["input_tokens"] or 0 for m in mv)
        s["mean_output_tokens"] = statistics.mean(m["output_tokens"] or 0 for m in mv)
        s["total_cost_usd"] = sum(m.get("cost", 0.0) for m in mv)
    if any("invalid" in m for m in mv):
        s["invalid_replies"] = sum(m["invalid"] for m in mv)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--player", required=True, choices=["heuristic", "random", "jev", "dg", "qwen", "laya"])
    ap.add_argument("--url")
    ap.add_argument("--jev-model", default="typesafe/jev-1.13")
    ap.add_argument("--name", help="results key (default: the player name)")
    a = ap.parse_args()
    import sys
    sys.path.insert(0, str(HERE))
    player = {"heuristic": Heuristic, "random": Random, "laya": LayaPlayer}.get(a.player)
    player = player() if player else (Qwen(a.url) if a.player == "qwen" else
                                      Decisions(a.player, a.url, a.jev_model))
    games = []
    for seed in SEEDS:
        g = play(player, seed)
        games.append(g)
        print(a.player, "seed", seed, {k: v for k, v in g.items() if k not in ("moves", "final_board")}, flush=True)
    res = json.loads(OUT.read_text()) if OUT.exists() else {}
    key = a.name or a.player
    res[key] = {"summary": summarize(games), "games": games}
    OUT.write_text(json.dumps(res, indent=1))
    print(key, json.dumps(res[key]["summary"]))


if __name__ == "__main__":
    main()
