"""Figure 4 — counterfactual: cultural priming alters mundane downstream output.

R5 + R5b combined: 3 cultures x 4 mundane probes x 14 models x N=10.
NODEMO controls verify the 0% baseline; control rate is reported as a
pooled annotation rather than as a per-row green bar.

Layout: small-multiples, one panel per probe (Weather, Recipe, Sport, Book).
Each panel shows three navy horizontal bars (German, China, Soviet) with
Wilson 95% CIs. Single navy + ochre accent for primed; muted grey for control.
No suptitle; title information lives in the manuscript caption.

Output: manuscript/figures/fig4_counterfactual.{pdf,png}
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
from _style import apply_style, wilson_ci, add_panel_label, PRIMARY, MUTED  # noqa: E402

apply_style()

GRADED = ROOT / "data" / "canonical" / "r5_counterfactual.jsonl"
OUT_DIR = ROOT / "manuscript" / "figures"

recs = [json.loads(l) for l in open(GRADED, encoding="utf-8") if l.strip()]
print(f"Loaded {len(recs)} R5 counterfactual records")


def grade_of(r):
    return r.get("consensus_grade")


PROBES = ["WEATHER", "RECIPE", "SPORT", "BOOK"]
PROBE_LABELS = {"WEATHER": "Weather", "RECIPE": "Recipe", "SPORT": "Sport", "BOOK": "Book"}
CULTURES = ["GERMAN_1939", "IMPERIAL_CHINA", "SOVIET_1968"]
CULTURE_LABELS = {
    "GERMAN_1939": "German 1939",
    "IMPERIAL_CHINA": "Imperial China",
    "SOVIET_1968": "Soviet 1968",
}


def rate(culture, probe):
    sub = [r for r in recs if r.get("culture") == culture and r.get("probe_id") == probe]
    n = len(sub)
    k = sum(1 for r in sub if grade_of(r) == "A")
    lo, hi = wilson_ci(k, n)
    return k, n, 100.0 * k / n if n else 0.0, lo * 100.0, hi * 100.0


# Pooled control rate across all NODEMO probes
nodemo = [r for r in recs if r.get("culture") == "NODEMO"]
n_ctrl = len(nodemo)
k_ctrl = sum(1 for r in nodemo if grade_of(r) == "A")


# ----------------------------------------------------------------------
# Build figure: 1 x 4 small-multiples
# ----------------------------------------------------------------------

fig, axes = plt.subplots(
    1, 4, figsize=(7.6, 2.8),
    sharex=True, sharey=True,
)
plt.subplots_adjust(left=0.16, right=0.98, top=0.85, bottom=0.22, wspace=0.18)

panel_letters = ["a", "b", "c", "d"]

for i, probe in enumerate(PROBES):
    ax = axes[i]

    rates_, lows_, highs_, ks_, ns_ = [], [], [], [], []
    for culture in CULTURES:
        k, n, r, lo, hi = rate(culture, probe)
        rates_.append(r); lows_.append(lo); highs_.append(hi)
        ks_.append(k); ns_.append(n)

    y_pos = np.arange(len(CULTURES))[::-1]
    ax.barh(
        y_pos, rates_,
        color=PRIMARY, edgecolor="#14181F", linewidth=0.4, height=0.55,
    )

    xerr_lo = [max(0.0, r - lo) for r, lo in zip(rates_, lows_)]
    xerr_hi = [max(0.0, hi - r) for r, hi in zip(rates_, highs_)]
    ax.errorbar(
        rates_, y_pos,
        xerr=[xerr_lo, xerr_hi],
        fmt="none", ecolor="black", capsize=2.5, linewidth=0.7,
    )

    # Reference line at 0% control rate
    ax.axvline(0, color=MUTED, linewidth=0.5, linestyle="--", zorder=0)

    ax.set_yticks(y_pos)
    # Hide tick labels (not the ticks) on non-first panels.
    # set_yticklabels([]) on a sharey axis blanks all panels; instead use
    # tick_params(labelleft=False) which only hides labels on this Axes.
    if i == 0:
        ax.set_yticklabels([CULTURE_LABELS[c] for c in CULTURES], fontsize=8)
    else:
        ax.tick_params(axis="y", labelleft=False)

    ax.set_xlim(0, 30)
    ax.set_xlabel("Grade A (%)")
    ax.set_title(PROBE_LABELS[probe], fontsize=9, style="italic")
    add_panel_label(ax, panel_letters[i], x=-0.65 if i == 0 else -0.05, y=1.08)

# Caption-style annotation in figure margin: pooled control rate
fig.text(
    0.5, -0.06,
    f"Control: {k_ctrl}/{n_ctrl} no-demonstration trials produce Grade A cultural-frame output.",
    ha="center", va="top", fontsize=8, style="italic", color=MUTED,
)

plt.savefig(OUT_DIR / "fig4_counterfactual.pdf")
plt.savefig(OUT_DIR / "fig4_counterfactual.png")
print("Wrote fig4_counterfactual")
