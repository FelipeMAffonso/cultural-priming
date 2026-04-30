"""Project-wide matplotlib style for cultural-priming-paper figures.

Imports
-------
from _style import apply_style, wilson_ci, add_panel_label
from _style import PRIMARY, ACCENT, MUTED, LIGHT_BG

Calibrated to match Nature / Nature Machine Intelligence register:
- Arial 9pt body, Arial 8pt ticks
- Hidden top/right spines at 0.6pt
- Single navy primary, ochre accent, neutral grey muted
- TrueType (fonttype 42) for editable PDFs
- 300 dpi savefig

Helpers
-------
- apply_style(): set rcParams
- wilson_ci(k, n, z=1.96): Wilson 95% CI for a proportion
- add_panel_label(ax, label, x=-0.10, y=1.05): flush-left bold lowercase label

Re-export of palette colour constants:
- PRIMARY    deep navy   #1f3a5f
- ACCENT     ochre       #d6a85a
- MUTED      grey        #7f8c8d
- LIGHT_BG   light grey  #f4f4f4
"""
from __future__ import annotations

import math
from typing import Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt


# ----------------------------------------------------------------------
# Palette
# ----------------------------------------------------------------------

PRIMARY = "#1f3a5f"   # deep navy: data
ACCENT = "#d6a85a"    # ochre: emphasis (rare, used for primed vs control accent)
MUTED = "#7f8c8d"     # neutral grey: control / inactive
LIGHT_BG = "#f4f4f4"  # background tint
GREY_LT = "#cccccc"
GREY_VLT = "#e6e6e6"


# ----------------------------------------------------------------------
# Style
# ----------------------------------------------------------------------

def apply_style() -> None:
    """Apply Nature/NMI-register matplotlib rcParams.

    Idempotent. Safe to call multiple times.
    """
    plt.rcParams.update({
        # Typography
        "font.family":          "sans-serif",
        "font.sans-serif":      ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
        "font.size":            11,
        "axes.labelsize":       11,
        "axes.titlesize":       11,
        "xtick.labelsize":      9.5,
        "ytick.labelsize":      9.5,
        "legend.fontsize":      9.5,

        # Spines and ticks
        "axes.linewidth":       0.6,
        "axes.edgecolor":       "#1C1C1C",
        "axes.labelcolor":      "#1C1C1C",
        "xtick.color":          "#1C1C1C",
        "ytick.color":          "#1C1C1C",
        "xtick.major.width":    0.6,
        "ytick.major.width":    0.6,
        "xtick.major.size":     3.0,
        "ytick.major.size":     3.0,
        "axes.spines.top":      False,
        "axes.spines.right":    False,

        # Lines and patches
        "lines.linewidth":      1.0,
        "patch.linewidth":      0.4,

        # Grid off; legend frameless
        "axes.grid":            False,
        "legend.frameon":       False,

        # Output: editable PDFs and high-DPI
        "pdf.fonttype":         42,
        "ps.fonttype":          42,
        "figure.dpi":           300,
        "savefig.dpi":          300,
        "savefig.bbox":         "tight",
        "savefig.pad_inches":   0.08,
        "savefig.facecolor":    "white",
        "figure.facecolor":     "white",
    })


# ----------------------------------------------------------------------
# Wilson 95% CI
# ----------------------------------------------------------------------

def wilson_ci(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    """Wilson score interval for a binomial proportion k/n.

    Returns (low, high) as proportions in [0, 1]. Handles n == 0
    by returning (0.0, 1.0). When k == 0, low == 0; when k == n, high == 1.

    The Wilson interval is preferred over normal-approximation Wald CIs
    because it does not collapse to (0, 0) at k = 0 and remains within
    [0, 1] across all k, n.
    """
    if n <= 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1.0 + (z * z) / n
    centre = (p + (z * z) / (2.0 * n)) / denom
    margin = (z * math.sqrt((p * (1.0 - p) + (z * z) / (4.0 * n)) / n)) / denom
    low = max(0.0, centre - margin)
    high = min(1.0, centre + margin)
    return (low, high)


# ----------------------------------------------------------------------
# Panel labels
# ----------------------------------------------------------------------

def add_panel_label(ax, label: str, x: float = -0.10, y: float = 1.05) -> None:
    """Add a flush-left bold lowercase panel label (a, b, c) at 13 pt.

    Positions in axes-fraction coordinates so the label lives outside
    the data region. No period appended; caller passes 'a', not 'a.'.
    """
    ax.text(
        x, y, label,
        transform=ax.transAxes,
        fontweight="bold",
        fontsize=13,
        ha="left",
        va="bottom",
    )
