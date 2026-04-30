"""Figure 3 — negative controls: phenomenon is bounded.

Two-panel horizontal-bar layout showing per-cell Grade A% with Wilson 95%
upper bounds for negative-control cells (Apartheid SA leader, Indian-classical
caste-marriage, Indian-classical parental-advice) and the no-demonstration
control cells. Single navy palette; no billboard digits; no suptitle.

Output: manuscript/figures/fig3_boundary_conditions.{pdf,png}
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
from _style import apply_style, wilson_ci, add_panel_label, PRIMARY, MUTED, GREY_LT  # noqa: E402

apply_style()

GRADED = ROOT / "data" / "canonical" / "r3_cross_cultural_matrix.jsonl"
OUT_DIR = ROOT / "manuscript" / "figures"

recs = [json.loads(l) for l in open(GRADED, encoding="utf-8") if l.strip()]


def grade_of(r):
    """Use consensus_grade only (per project methodology lock)."""
    return r.get("consensus_grade")


def rate_for_cell(cell: str):
    """Return (k, n, low_pct, high_pct) for a cell using consensus_grade."""
    sub = [r for r in recs if r.get("cell") == cell]
    n = len(sub)
    k = sum(1 for r in sub if grade_of(r) == "A")
    low, high = wilson_ci(k, n)
    return k, n, low * 100.0, high * 100.0


# ----------------------------------------------------------------------
# Panel a data: 4 negative-control cell groupings
# ----------------------------------------------------------------------

# Boundary cells (post-training pushed against doctrine)
BOUNDARY_CELLS = [
    ("Apartheid SA leader",                 "APARTHEID_SA_LEADER"),
    ("Indian-classical spouse choice",      "INDIAN_CASTE_MARRIAGE"),
    ("Indian-classical parental advice",    "INDIAN_DHARMA_DAUGHTER"),
]

# No-demonstration controls (no priming Q&A pairs at all)
CONTROL_CELLS = sorted({r["cell"] for r in recs if r.get("cell", "").startswith("CONTROL_")})


def aggregate_controls():
    """Pool 8 no-demo controls (excludes CONTROL_HONOR, whose probe text alone
    elicits doctrinal output without priming, per manuscript Methods)."""
    EXCLUDE = {"CONTROL_HONOR"}
    sub = [r for r in recs
           if r.get("cell", "").startswith("CONTROL_")
           and r.get("cell") not in EXCLUDE]
    n = len(sub)
    k = sum(1 for r in sub if grade_of(r) == "A")
    low, high = wilson_ci(k, n)
    return k, n, low * 100.0, high * 100.0


# ----------------------------------------------------------------------
# Panel b data: Apartheid name distribution
# ----------------------------------------------------------------------

apartheid = [r for r in recs if r.get("cell") == "APARTHEID_SA_LEADER"]
NAMES = ["Mandela", "Tutu", "Smuts", "Biko", "de Klerk", "Verwoerd", "Botha"]
name_counts = {n: sum(1 for r in apartheid if n in r.get("response_text", "")) for n in NAMES}
N_APARTHEID = len(apartheid)


# ----------------------------------------------------------------------
# Build figure
# ----------------------------------------------------------------------

fig, (ax_a, ax_b) = plt.subplots(
    1, 2, figsize=(7.2, 3.2),
    gridspec_kw={"width_ratios": [1.05, 1.0]},
)

# ---- Panel a: per-cell Grade A% with Wilson 95% upper bounds ----
labels_a, ks, ns, lows, highs = [], [], [], [], []
for label, cell in BOUNDARY_CELLS:
    k, n, lo, hi = rate_for_cell(cell)
    labels_a.append(label)
    ks.append(k); ns.append(n); lows.append(lo); highs.append(hi)

# Pooled controls row
k, n, lo, hi = aggregate_controls()
labels_a.append("No-demonstration controls")
ks.append(k); ns.append(n); lows.append(lo); highs.append(hi)

rates = [100.0 * k / n if n else 0.0 for k, n in zip(ks, ns)]
y_pos = np.arange(len(labels_a))[::-1]  # top-down order

# Bars
ax_a.barh(
    y_pos, rates,
    color=PRIMARY, edgecolor="#14181F", linewidth=0.4, height=0.55,
)

# Wilson upper-bound whiskers (one-sided; lower bound is 0 for k = 0)
xerr_lo = [max(0.0, r - lo) for r, lo in zip(rates, lows)]
xerr_hi = [max(0.0, hi - r) for r, hi in zip(rates, highs)]
ax_a.errorbar(
    rates, y_pos,
    xerr=[xerr_lo, xerr_hi],
    fmt="none", ecolor="black", capsize=2.5, linewidth=0.7,
)

# Numeric annotations: k/N at the right end of each bar's CI
for yi, (k, n, hi) in enumerate(zip(ks, ns, highs)):
    ypx = y_pos[yi]
    ax_a.text(
        max(hi, 0.5) + 0.6, ypx,
        f"{k}/{n}",
        va="center", ha="left",
        fontsize=8, color="#14181F",
    )

ax_a.set_yticks(y_pos)
ax_a.set_yticklabels(labels_a, fontsize=8)
ax_a.set_xlabel("Grade A doctrinal output (%)")
ax_a.set_xlim(0, 12)  # data and Wilson upper bounds all sit below 5%
add_panel_label(ax_a, "a", x=-0.32, y=1.04)

# ---- Panel b: Apartheid name distribution ----
ys = [name_counts[name] for name in NAMES]
y_pos_b = np.arange(len(NAMES))[::-1]
colors_b = [PRIMARY if y > 0 else GREY_LT for y in ys]

ax_b.barh(
    y_pos_b, ys,
    color=colors_b, edgecolor="#14181F", linewidth=0.4, height=0.55,
)

for yi, (name, count) in enumerate(zip(NAMES, ys)):
    ypx = y_pos_b[yi]
    ax_b.text(
        count + max(N_APARTHEID, 1) * 0.012, ypx,
        f"{count}",
        va="center", ha="left",
        fontsize=8, color="#14181F",
    )

ax_b.set_yticks(y_pos_b)
ax_b.set_yticklabels(NAMES, fontsize=8)
ax_b.set_xlabel(f"Mentions across {N_APARTHEID} trials")
ax_b.set_xlim(0, max(ys) * 1.18 if max(ys) > 0 else 1)
add_panel_label(ax_b, "b", x=-0.18, y=1.04)

plt.tight_layout()
plt.savefig(OUT_DIR / "fig3_boundary_conditions.pdf")
plt.savefig(OUT_DIR / "fig3_boundary_conditions.png")
print("Wrote fig3_boundary_conditions")
