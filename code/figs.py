"""Figures for the paper (static PDF). Palette: dataviz reference slots 1-3 (validated)."""
import json
import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from orclient import ROOT

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3de"
plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False})
R = json.load(open(ROOT / "results/results.json"))
F = pd.read_csv(ROOT / "data/features.csv")
P = F[(F.group != "fresh") & ~F.practice]
OUT = ROOT / "results"

# Fig 1: share of all answers per model
fig, ax = plt.subplots(figsize=(3.3, 1.35))
models = ["GPT-4o-mini", "Llama-3.3-70B", "Qwen2.5-72B"]
for y, m in enumerate(models):
    g = P[P.model == m]; n = len(g)
    parts = [("No luck found", (g["T"] & ~g.luck).sum() / n, BLUE), ("Right by luck", (g["T"] & g.luck).sum() / n, ORANGE), ("Wrong", (~g["T"]).sum() / n, AQUA)]
    left = 0
    for lab, v, col in parts:
        ax.barh(y, v - 0.004, left=left, color=col, height=0.62, edgecolor="white", linewidth=1)
        ax.text(left + v / 2, y, f"{v*100:.0f}%", ha="center", va="center", color="white", fontsize=7, fontweight="bold")
        left += v
ax.set_yticks(range(3), models); ax.invert_yaxis(); ax.set_xlim(0, 1); ax.set_xticks([0, .25, .5, .75, 1], ["0", "25", "50", "75", "100%"])
ax.tick_params(axis="y", length=0)
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (BLUE, ORANGE, AQUA)]
ax.legend(handles, ["No luck found", "Right by luck", "Wrong"], ncol=3, frameon=False, loc="lower center", bbox_to_anchor=(0.42, 1.0), fontsize=7, handlelength=1)
fig.tight_layout(pad=0.3); fig.savefig(OUT / "fig1_categories.pdf")

# Fig 2: per-check failure rate among correct answers (post-hoc), with 95% CI
pc = R["posthoc_per_check"]
rows = [("Repeat (same prompt)", pc["repeat_fail_per_call"]), ("Control (punctuation)", pc["control_fail_per_check"]),
        ("Neighbour: same answer", pc["neighbour_same_answer_per_check"]), ("Rewording breaks it", pc["rewording_fail_per_check"])]
fig, ax = plt.subplots(figsize=(3.4, 1.45))
for y, (lab, (v, lo, hi)) in enumerate(rows):
    ax.plot([lo * 100, hi * 100], [y, y], color=BLUE, lw=2, solid_capstyle="round")
    ax.plot(v * 100, y, "o", color=BLUE, ms=5, mec="white", mew=1)
    ax.text(hi * 100 + 0.6, y, f"{v*100:.1f}%", va="center", fontsize=7, color=INK)
ax.set_yticks(range(len(rows)), [r[0] for r in rows]); ax.tick_params(axis="y", length=0)
ax.set_xlim(0, 26); ax.set_xlabel("Failure rate per check (%), correct answers")
ax.grid(axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True)
fig.tight_layout(pad=0.4); fig.savefig(OUT / "fig2_per_check.pdf", bbox_inches="tight")
print("ok")
