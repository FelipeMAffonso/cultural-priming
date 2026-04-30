"""Figure 4 (manuscript Fig 4) — cross-generation Anthropic Opus regression.

Opus 4.5 -> 4.6 -> 4.7 on 4 cells. Single navy palette with Wilson 95% CIs.
Output: manuscript/figures/fig2_cross_generation.{pdf,png}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "manuscript" / "figures"))
from _style import apply_style, wilson_ci, add_panel_label, PRIMARY  # noqa: E402

apply_style()

GRADED = ROOT / "data" / "canonical" / "r3_cross_cultural_matrix.jsonl"
OUT_DIR = ROOT / "manuscript" / "figures"

recs = [json.loads(l) for l in open(GRADED, encoding="utf-8") if l.strip()]


def grade_of(r):
    return r.get("consensus_grade")


CELLS = ["HITLER_V2_DIRECT", "HITLER_V1_WISH", "SOVIET_V1_WISH", "MEDIEVAL_ARAB_AUTHORITY"]
CELL_TITLES = {
    "HITLER_V2_DIRECT": "Hitler (direct)",
    "HITLER_V1_WISH": "Hitler (wish)",
    "SOVIET_V1_WISH": "Soviet (wish)",
    "MEDIEVAL_ARAB_AUTHORITY": "Medieval-Arab (guide)",
}
GENS = ["claude-opus-4-5", "claude-opus-4-6", "claude-opus-4-7"]
GEN_LABELS = ["Opus 4.5", "Opus 4.6", "Opus 4.7"]


fig, axes = plt.subplots(1, 4, figsize=(7.2, 2.6), sharey=True)
panel_letters = ["a", "b", "c", "d"]

for i, cell in enumerate(CELLS):
    rates, lows, highs = [], [], []
    for gen in GENS:
        sub = [r for r in recs if r.get("cell") == cell and r["model"] == gen]
        n = len(sub)
        k = sum(1 for r in sub if grade_of(r) == "A")
        lo, hi = wilson_ci(k, n)
        rates.append(100.0 * k / n if n else 0.0)
        lows.append(lo * 100.0); highs.append(hi * 100.0)

    ax = axes[i]
    xs = np.arange(len(GENS))
    ax.bar(xs, rates, color=PRIMARY, edgecolor="#14181F", linewidth=0.4, width=0.55)
    yerr_lo = [max(0.0, r - lo) for r, lo in zip(rates, lows)]
    yerr_hi = [max(0.0, hi - r) for r, hi in zip(rates, highs)]
    ax.errorbar(xs, rates, yerr=[yerr_lo, yerr_hi],
                fmt="none", ecolor="black", capsize=2.5, linewidth=0.7)

    for x, r, hi in zip(xs, rates, highs):
        ax.text(x, hi + 2, f"{int(round(r))}%",
                ha="center", va="bottom", fontsize=8, color="#14181F")

    # Visible baseline so zero bars still register
    ax.axhline(0, color="#14181F", linewidth=0.6, zorder=2)

    ax.set_xticks(xs)
    ax.set_xticklabels(GEN_LABELS, fontsize=8)
    ax.set_ylim(0, 110)
    ax.set_title(CELL_TITLES[cell], fontsize=9, style="italic")
    if i == 0:
        ax.set_ylabel("Grade A (%)")
    add_panel_label(ax, panel_letters[i], x=-0.05 if i > 0 else -0.30, y=1.10)

plt.tight_layout()
plt.savefig(OUT_DIR / "fig2_cross_generation.pdf")
plt.savefig(OUT_DIR / "fig2_cross_generation.png")
print("Wrote fig2_cross_generation")
