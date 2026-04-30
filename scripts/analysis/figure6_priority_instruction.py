"""Figure 6 — priority-instruction mechanism (Afonin causal manipulation).

Three system-prompt variants x 4 cells x 14 models, N=15 each.

Panel a: aggregate Grade A% across all (cell x model) cells, three navy bars
(Control, Modern norms, Cultural context) with Wilson 95% CIs.
Panel b: per-cell x system-prompt heatmap on a single-hue Blues colormap.

No RdYlGn; no red/green editorial palette; no suptitle.

Output: manuscript/figures/fig6_priority_instruction.{pdf,png}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "manuscript" / "figures"))
from _style import apply_style, wilson_ci, add_panel_label, PRIMARY  # noqa: E402

apply_style()

GRADED = ROOT / "data" / "canonical" / "r4_priority_instruction.jsonl"
OUT_DIR = ROOT / "manuscript" / "figures"

recs = [json.loads(l) for l in open(GRADED, encoding="utf-8") if l.strip()]
print(f"Loaded {len(recs)} R4 priority-instruction records")


def grade_of(r):
    return r.get("consensus_grade")


CELLS = ["HITLER_V2", "SOVIET_V2", "CONFUCIAN_DAUGHTER", "MEDIEVAL_ARAB_AUTHORITY"]
CELL_LABELS = {
    "HITLER_V2": "German 1939 leader",
    "SOVIET_V2": "Soviet 1968 leader",
    "CONFUCIAN_DAUGHTER": "Confucian daughter",
    "MEDIEVAL_ARAB_AUTHORITY": "Medieval-Arab guide",
}
SYS_VARS = ["SYS_CONTROL", "SYS_MODERN", "SYS_CULTURE"]
SYS_LABELS = {"SYS_CONTROL": "Control", "SYS_MODERN": "Modern norms", "SYS_CULTURE": "Cultural context"}


# ----------------------------------------------------------------------
# Panel a: aggregate Grade A% per system-prompt variant
# ----------------------------------------------------------------------

aggs = {}
for sv in SYS_VARS:
    sub = [r for r in recs if r.get("sys_variant") == sv]
    n = len(sub)
    k = sum(1 for r in sub if grade_of(r) == "A")
    lo, hi = wilson_ci(k, n)
    aggs[sv] = (k, n, 100.0 * k / n if n else 0.0, lo * 100.0, hi * 100.0)


# ----------------------------------------------------------------------
# Panel b: per-cell x sys-variant matrix
# ----------------------------------------------------------------------

matrix = np.zeros((len(CELLS), len(SYS_VARS)))
counts = np.zeros((len(CELLS), len(SYS_VARS)), dtype=int)
totals = np.zeros((len(CELLS), len(SYS_VARS)), dtype=int)
for i, cell in enumerate(CELLS):
    for j, sv in enumerate(SYS_VARS):
        sub = [r for r in recs if r.get("cell") == cell and r.get("sys_variant") == sv]
        n = len(sub)
        k = sum(1 for r in sub if grade_of(r) == "A")
        counts[i, j] = k
        totals[i, j] = n
        matrix[i, j] = 100.0 * k / n if n else 0.0


# ----------------------------------------------------------------------
# Build figure
# ----------------------------------------------------------------------

fig, (ax_a, ax_b) = plt.subplots(
    1, 2, figsize=(7.2, 3.5),
    gridspec_kw={"width_ratios": [1.0, 1.25]},
)

# ---- Panel a ----
xs = np.arange(len(SYS_VARS))
rates = [aggs[sv][2] for sv in SYS_VARS]
lows = [aggs[sv][3] for sv in SYS_VARS]
highs = [aggs[sv][4] for sv in SYS_VARS]

ax_a.bar(
    xs, rates,
    color=PRIMARY, edgecolor="#14181F", linewidth=0.4, width=0.6,
)

yerr_lo = [max(0.0, r - lo) for r, lo in zip(rates, lows)]
yerr_hi = [max(0.0, hi - r) for r, hi in zip(rates, highs)]
ax_a.errorbar(
    xs, rates,
    yerr=[yerr_lo, yerr_hi],
    fmt="none", ecolor="black", capsize=2.5, linewidth=0.7,
)

for x, sv in zip(xs, SYS_VARS):
    k, n, pct, lo, hi = aggs[sv]
    ax_a.text(
        x, hi + 1.5, f"{pct:.1f}%",
        ha="center", va="bottom", fontsize=8, color="#14181F",
    )

ax_a.set_xticks(xs)
ax_a.set_xticklabels([SYS_LABELS[sv] for sv in SYS_VARS], fontsize=8)
ax_a.set_ylabel("Aggregate Grade A (%)")
ax_a.set_ylim(0, max(highs) * 1.25 if highs else 70)
add_panel_label(ax_a, "a", x=-0.18, y=1.05)

# ---- Panel b: Blues sequential heatmap ----
cmap = plt.get_cmap("Blues")
im = ax_b.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=100)

# Cell labels: white text on dark cells (intensity-based, not data-value-based)
for i in range(len(CELLS)):
    for j in range(len(SYS_VARS)):
        v = matrix[i, j]
        rgba = cmap(v / 100.0)
        # Luminance approx: text colour flips when cell darkens past mid grey
        luminance = 0.299 * rgba[0] + 0.587 * rgba[1] + 0.114 * rgba[2]
        text_color = "white" if luminance < 0.55 else "#14181F"
        ax_b.text(
            j, i, f"{int(round(v))}%",
            ha="center", va="center",
            color=text_color, fontsize=9,
        )

ax_b.set_xticks(range(len(SYS_VARS)))
ax_b.set_xticklabels([SYS_LABELS[sv] for sv in SYS_VARS], fontsize=8)
ax_b.set_yticks(range(len(CELLS)))
ax_b.set_yticklabels([CELL_LABELS[c] for c in CELLS], fontsize=8)

# Thin grid between cells
ax_b.set_xticks(np.arange(-0.5, len(SYS_VARS), 1), minor=True)
ax_b.set_yticks(np.arange(-0.5, len(CELLS), 1), minor=True)
ax_b.grid(which="minor", color="white", linewidth=0.4)
ax_b.tick_params(which="minor", length=0)

cbar = plt.colorbar(im, ax=ax_b, fraction=0.04, pad=0.04)
cbar.set_label("Grade A (%)", fontsize=8)
cbar.ax.tick_params(labelsize=7)
add_panel_label(ax_b, "b", x=-0.18, y=1.05)

plt.tight_layout()
plt.savefig(OUT_DIR / "fig6_priority_instruction.pdf")
plt.savefig(OUT_DIR / "fig6_priority_instruction.png")
print("Wrote fig6_priority_instruction")
