"""Images for this LinkedIn article, drawn from the measured results in llm-inference/diffusiongemma/*.json."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, NullLocator

HERE = Path(__file__).resolve().parent
D = HERE.parents[3] / "diffusiongemma"  # llm-inference/diffusiongemma
OUT = HERE / "images"

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0"
C = {"Jev": "#2a78d6", "DiffusionGemma": "#eb6834", "Qwen 3 30B": "#1baf7a", "Bonsai 27B": "#eda100", "Laya": "#e87ba4"}
MARK = {"Jev": "o", "DiffusionGemma": "s", "Qwen 3 30B": "^", "Bonsai 27B": "D", "Laya": "v"}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE})


def frame(ax):
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(length=0)


def title(fig, t, sub):
    fig.text(0.04, 0.955, t, fontsize=20, fontweight="bold", color=INK, va="top")
    fig.text(0.04, 0.895, sub, fontsize=12.5, color=INK2, va="top")


def source(fig, text):
    fig.text(0.04, 0.025, text, fontsize=10, color=MUTED)


# ---------------------------------------------------------------- 1. speed vs number of questions
s = json.loads((D / "speed_scaling.json").read_text())
best_qwen = [min(a["warm_ms"], b["warm_ms"]) for a, b in zip(s["qwen_write"], s["qwen_write_no_op_offload"])]
series = {
    "Jev": [r["cold_ms"] for r in s["jev_openrouter"]],
    "DiffusionGemma": [r["warm_ms"] for r in s["diffusiongemma_read"]],
    "Qwen 3 30B": best_qwen,
    "Bonsai 27B": [r["warm_ms"] for r in s["bonsai_write"]],
    "Laya": [r["warm_ms"] for r in s["laya"]],
}
ns = [r["questions"] for r in s["laya"]]
fig, ax = plt.subplots(figsize=(12, 7.2), dpi=150)
fig.subplots_adjust(left=0.1, right=0.8, top=0.8, bottom=0.14)
for name, ys in series.items():
    ax.plot(ns, ys, color=C[name], lw=2.2, marker=MARK[name], ms=8, markeredgecolor=SURFACE, markeredgewidth=1.5,
            label=name, zorder=3)
    ax.annotate(f"{name}  {ys[-1] / 1000:.2f} s" if ys[-1] >= 1000 else f"{name}  {ys[-1]:.0f} ms",
                (ns[-1], ys[-1]), xytext=(12, {"DiffusionGemma": 11, "Jev": -11}.get(name, 0)),
                textcoords="offset points", va="center", fontsize=12.5, color=INK)
ax.set_yscale("log")
ax.yaxis.set_major_locator(FixedLocator([10, 30, 100, 300, 1000, 3000]))
ax.yaxis.set_minor_locator(NullLocator())
ax.set_yticklabels(["10 ms", "30 ms", "0.1 s", "0.3 s", "1 s", "3 s"])
ax.set_xticks(ns)
ax.set_xlabel("Questions asked about the same text, in one request")
ax.grid(axis="y", color=GRID, lw=1)
frame(ax)
leg = ax.legend(loc="upper left", frameon=False, fontsize=11.5, ncol=5, bbox_to_anchor=(0, 1.08))
title(fig, "Time to answer N yes/no questions",
      "Jev stays flat. Models that type their answers slow down with every question. (log scale)")
source(fig, "Measured on an RTX 5060 8 GB laptop. Jev: cloud via OpenRouter, network included, new text. "
            "Local models: text already read. Median of 3.")
fig.savefig(OUT / "speed-by-question-count.png", facecolor=SURFACE)
# the same chart at LinkedIn's recommended article-cover size (1920 x 1080, 16:9)
fig.set_size_inches(12.8, 7.2)
fig.subplots_adjust(left=0.09, right=0.8, top=0.8, bottom=0.14)
fig.savefig(OUT / "cover-1920x1080.png", dpi=150, facecolor=SURFACE)
plt.close(fig)

# ---------------------------------------------------------------- 2. accuracy
r = json.loads((D / "results.json").read_text())
acc = [  # (label, reviews, news, note)
    ("Jev", r["jev-openrouter"]["sst2"]["accuracy"], r["jev-openrouter"]["agnews"]["accuracy"], ""),
    ("Bonsai 27B", r["bonsai-27b-ternary"]["sst2"]["accuracy"], r["bonsai-27b-ternary"]["agnews"]["accuracy"], ""),
    ("Laya*", r["laya"]["sst2_choice"]["accuracy"], r["laya"]["agnews"]["accuracy"], ""),
    ("DiffusionGemma", r["diffusiongemma-single-read"]["sst2"]["accuracy"], r["diffusiongemma-single-read"]["agnews"]["accuracy"], ""),
    ("Qwen 3 30B", r["qwen3-30b-a3b-ar"]["sst2"]["accuracy"], r["qwen3-30b-a3b-ar"]["agnews"]["accuracy"], ""),
]
fig, ax = plt.subplots(figsize=(12, 7.2), dpi=150)
fig.subplots_adjust(left=0.2, right=0.95, top=0.78, bottom=0.2)
h, gap = 0.36, 0.03
for i, (name, a1, a2, _) in enumerate(acc):
    y = len(acc) - 1 - i
    for off, v, col, lab in ((h / 2 + gap / 2, a1, "#2a78d6", "Movie reviews (positive?)"),
                             (-h / 2 - gap / 2, a2, "#eb6834", "News topics (4 choices)")):
        ax.barh(y + off, v * 100, height=h, color=col, label=lab if i == 0 else None, zorder=3)
        ax.text(v * 100 + 0.6, y + off, f"{v * 100:.1f} %", va="center", fontsize=12, color=INK)
ax.set_yticks(range(len(acc)))
ax.set_yticklabels([a[0] for a in reversed(acc)], fontsize=13.5, color=INK)
ax.set_xlim(50, 101)
ax.set_xticks([50, 60, 70, 80, 90, 100])
ax.set_xticklabels(["50 %", "60 %", "70 %", "80 %", "90 %", "100 %"])
ax.grid(axis="x", color=GRID, lw=1)
frame(ax)
ax.legend(loc="upper left", frameon=False, fontsize=12, ncol=2, bbox_to_anchor=(0, 1.1))
title(fig, "Accuracy on the same 400 questions", "200 movie reviews (SST-2) and 200 news articles (AG News). Axis starts at 50 %.")
source(fig, "* Laya: reviews asked as a 2-option choice (asked yes/no it scored 46 %, answering \"no\" to all). "
            "Its news score is on data it was trained on.\nQwen: typing its answer; 31 of 400 replies were malformed. "
            "DiffusionGemma: one read.")
fig.savefig(OUT / "accuracy-400-questions.png", facecolor=SURFACE)
plt.close(fig)

# ---------------------------------------------------------------- 3. Tetris
t = json.loads((D / "tetris_results.json").read_text())
rows = [("Classic heuristic", "heuristic"), ("Jev", "jev"), ("Bonsai 27B", "bonsai"), ("DiffusionGemma", "dg"),
        ("Qwen 3 30B", "qwen"), ("Laya", "laya"), ("Random", "random")]
fig, ax = plt.subplots(figsize=(12, 7.2), dpi=150)
fig.subplots_adjust(left=0.2, right=0.95, top=0.8, bottom=0.14)
for i, (label, key) in enumerate(rows):
    sm = t[key]["summary"]
    y = len(rows) - 1 - i
    ref = key in ("heuristic", "random")
    ax.barh(y, sm["lines_total"], height=0.62, color=MUTED if ref else "#2a78d6", zorder=3)
    ms = sm["p50_ms_per_move"]
    speed = "" if ref else (f" · {ms / 1000:.1f} s per move" if ms >= 1000 else f" · {ms:.0f} ms per move")
    ax.text(sm["lines_total"] + 1, y, f"{sm['lines_total']} lines · survived {sm['games_survived']}/3{speed}",
            va="center", fontsize=12, color=INK)
ax.set_yticks(range(len(rows)))
ax.set_yticklabels([r[0] for r in reversed(rows)], fontsize=13.5, color=INK)
ax.set_xlim(0, 125)
ax.set_xlabel("Lines cleared over 3 games (80 pieces each, same pieces for everyone)")
ax.grid(axis="x", color=GRID, lw=1)
frame(ax)
title(fig, "Tetris: every move is one decision", "Each model picks where to drop every piece, from the list of legal placements.")
source(fig, "Grey bars are reference players. Jev in the cloud; the others on an RTX 5060 8 GB laptop.")
fig.savefig(OUT / "tetris-results.png", facecolor=SURFACE)
plt.close(fig)
# ---------------------------------------------------------------- 4. cascade: Laya first, Jev when Laya is unsure
cz = json.loads((D / "cascade.json").read_text())
pts = [("Laya alone", cz["laya_alone"]["ms"], cz["laya_alone"]["accuracy"], cz["laya_alone"]["cost_per_1k"])]
pts += [(f"Cascade ≥{c['threshold']}", c["mean_ms"], c["overall_accuracy"], c["cost_per_1k"])
        for c in cz["cascade"] if c["threshold"] in (0.8, 0.9, 0.95)]
pts += [("Jev alone", cz["jev_alone"]["ms"], cz["jev_alone"]["accuracy"], cz["jev_alone"]["cost_per_1k"])]
fig, ax = plt.subplots(figsize=(12, 7.2), dpi=150)
fig.subplots_adjust(left=0.1, right=0.95, top=0.8, bottom=0.16)
xs, ys = [p[1] for p in pts], [p[2] * 100 for p in pts]
ax.plot(xs, ys, color="#2a78d6", lw=2.2, zorder=2)
for name, ms, acc_, cost in pts:
    end = name in ("Laya alone", "Jev alone")
    ax.scatter([ms], [acc_ * 100], s=110, color=MUTED if end else "#2a78d6", edgecolor=SURFACE, linewidth=2, zorder=3)
    lab = f"{name}\n{acc_ * 100:.1f} % · {ms:.0f} ms · " + ("$0" if cost == 0 else f"${cost:.4f} per 1k")
    dx, dy, ha = {"Cascade ≥0.95": (0, 18, "center"), "Cascade ≥0.8": (8, -40, "left"),
                  "Cascade ≥0.9": (10, -40, "left")}.get(name, (0, -40, "center"))
    ax.annotate(lab, (ms, acc_ * 100), xytext=(dx, dy), textcoords="offset points", ha=ha,
                fontsize=11.5, color=INK, fontweight="bold" if name == "Cascade ≥0.95" else "normal")
ax.set_xscale("log")
ax.xaxis.set_major_locator(FixedLocator([10, 30, 100, 300]))
ax.xaxis.set_minor_locator(NullLocator())
ax.set_xticklabels(["10 ms", "30 ms", "100 ms", "300 ms"])
ax.set_xlim(6, 600)
ax.set_ylim(90.5, 96)
ax.set_yticks([91, 92, 93, 94, 95])
ax.set_yticklabels(["91 %", "92 %", "93 %", "94 %", "95 %"])
ax.set_xlabel("Average time per decision (log scale)")
ax.grid(axis="y", color=GRID, lw=1)
frame(ax)
title(fig, "Combine them: Laya first, Jev only when Laya is unsure",
      "Jev-level accuracy at a fraction of the time and cost. 200 movie reviews.")
source(fig, "\"Cascade ≥0.95\": Laya answers when it's at least 95 % sure (62 % of reviews); the rest go to Jev.\n"
            "Times are measured medians: Laya on the laptop GPU, Jev in the cloud with the network included.")
fig.savefig(OUT / "cascade-laya-then-jev.png", facecolor=SURFACE)
plt.close(fig)
print("wrote", sorted(p.name for p in OUT.glob("*.png")))
