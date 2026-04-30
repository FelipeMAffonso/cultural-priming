"""Figure 1 — cross-cultural × cross-model Grade-A heatmap.

Loads `data/headline_matrix/graded_round3.jsonl` and produces a heatmap of
Grade-A misalignment rate per (cell × model) at N=20.

Output: manuscript/figures/fig1_design_heatmap.{pdf,png}
"""
import json
from pathlib import Path
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['font.family'] = 'DejaVu Sans'
mpl.rcParams['font.size'] = 9
mpl.rcParams['pdf.fonttype'] = 42

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
GRADED = ROOT / "data" / "canonical" / "r3_cross_cultural_matrix.jsonl"
OUT_DIR = ROOT / "manuscript" / "figures"
OUT_DIR.mkdir(exist_ok=True)

# Load
recs = [json.loads(l) for l in open(GRADED, encoding="utf-8") if l.strip()]
print(f"Loaded {len(recs)} graded records")

def grade_of(r):
    """Canonical 14-model data: prefer consensus_grade (2-of-3 majority of three independent
    judges). Fall back to final_grade, then legacy fields."""
    for k in ("consensus_grade", "final_grade", "grade", "polish_grade"):
        v = r.get(k)
        if v:
            return v
    if isinstance(r.get("grading"), dict):
        return r["grading"].get("grade")
    return None

# Cells in display order (paper headline cells first)
HEADLINE_CELLS = [
    "HITLER_V1_WISH", "HITLER_V2_DIRECT",
    "SOVIET_V1_WISH", "SOVIET_V2_DIRECT",
    "MEDIEVAL_ARAB_LEADER", "MEDIEVAL_ARAB_AUTHORITY",
    "EDO_JAPAN_HONOR", "EDO_JAPAN_SAMURAI",
    "CONFUCIAN_OBEDIENCES", "CONFUCIAN_DAUGHTER", "CONFUCIAN_FORENSIC",
    "VICTORIAN_LEADER", "AZTEC_RULER", "CONFEDERATE_LABOR",
    "INDIAN_CASTE_MARRIAGE", "INDIAN_DHARMA_DAUGHTER",
    "APARTHEID_SA_LEADER",  # negative control last
]
CELL_LABELS = {
    "HITLER_V1_WISH": "Hitler (wish)",
    "HITLER_V2_DIRECT": "Hitler (direct)",
    "SOVIET_V1_WISH": "Soviet (wish)",
    "SOVIET_V2_DIRECT": "Soviet (direct)",
    "MEDIEVAL_ARAB_LEADER": "Med-Arab leader",
    "MEDIEVAL_ARAB_AUTHORITY": "Med-Arab moral",
    "EDO_JAPAN_HONOR": "Edo: seppuku",
    "EDO_JAPAN_SAMURAI": "Edo: samurai",
    "CONFUCIAN_OBEDIENCES": "Confucian aspire",
    "CONFUCIAN_DAUGHTER": "Confucian daughter",
    "CONFUCIAN_FORENSIC": "Confucian role",
    "VICTORIAN_LEADER": "Victorian leader",
    "AZTEC_RULER": "Aztec ruler",
    "CONFEDERATE_LABOR": "Confederate labor",
    "INDIAN_CASTE_MARRIAGE": "Indian: caste",
    "INDIAN_DHARMA_DAUGHTER": "Indian: daughter",
    "APARTHEID_SA_LEADER": "Apartheid SA",
}

# Models in display order (provider blocks) — canonical 14-model lineup
MODELS_ORDERED = [
    "claude-opus-4-7", "claude-opus-4-6", "claude-opus-4-5",
    "claude-sonnet-4-6", "claude-sonnet-4-5", "claude-haiku-4-5",
    "gpt-5.4", "gpt-5.4-mini", "gpt-4o", "gpt-5.5",
    "gemini-3-flash-preview", "gemini-2.5-flash", "gemini-3.1-pro-preview", "gemini-2.5-pro",
]
MODEL_LABELS = {m: m.replace("claude-", "").replace("gpt-", "GPT-").replace("gemini-", "Gemini-").replace("-preview","").replace("flash","Flash").replace("pro","Pro").replace("opus","Opus").replace("sonnet","Sonnet").replace("haiku","Haiku") for m in MODELS_ORDERED}

# Build matrix
matrix = np.full((len(HEADLINE_CELLS), len(MODELS_ORDERED)), np.nan)
for i, cell in enumerate(HEADLINE_CELLS):
    for j, model in enumerate(MODELS_ORDERED):
        cell_recs = [r for r in recs if r.get("cell") == cell and r["model"] == model]
        if len(cell_recs) >= 5:  # only show cells with enough N
            n = len(cell_recs)
            a = sum(1 for r in cell_recs if grade_of(r) == "A")
            matrix[i, j] = 100 * a / n

# Plot
fig, ax = plt.subplots(figsize=(11, 7))
cmap = plt.cm.Reds
cmap.set_bad(color='#eeeeee')  # missing data
im = ax.imshow(matrix, aspect='auto', cmap=cmap, vmin=0, vmax=100)

# Annotate cells with values
for i in range(len(HEADLINE_CELLS)):
    for j in range(len(MODELS_ORDERED)):
        v = matrix[i, j]
        if np.isnan(v):
            ax.text(j, i, '--', ha='center', va='center', color='#999999', fontsize=7)
        else:
            color = 'white' if v >= 50 else 'black'
            ax.text(j, i, f'{int(v)}', ha='center', va='center', color=color, fontsize=7.5)

ax.set_xticks(range(len(MODELS_ORDERED)))
ax.set_xticklabels([MODEL_LABELS[m] for m in MODELS_ORDERED], rotation=45, ha='right', fontsize=8)
ax.set_yticks(range(len(HEADLINE_CELLS)))
ax.set_yticklabels([CELL_LABELS[c] for c in HEADLINE_CELLS], fontsize=8)

# Provider boundaries: Anthropic 0-5, OpenAI 6-9, Google 10-13
ax.axvline(x=5.5, color='black', linewidth=0.8)
ax.axvline(x=9.5, color='black', linewidth=0.8)
# Negative-control boundary
ax.axhline(y=13.5, color='black', linewidth=0.8)

ax.set_xlabel("Model")
ax.set_ylabel("Cell")
ax.set_title("Grade-A misalignment rate (%) by cell × model at N=20", fontsize=10)

cbar = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
cbar.set_label('Grade-A %', fontsize=8)

# Provider labels
ax.text(2.5, -1.5, 'Anthropic', ha='center', fontsize=9, fontweight='bold')
ax.text(7.5, -1.5, 'OpenAI', ha='center', fontsize=9, fontweight='bold')
ax.text(11.5, -1.5, 'Google', ha='center', fontsize=9, fontweight='bold')

# Negative-control label
ax.text(-2.5, 16, 'neg.\ncontrols', ha='center', va='center', fontsize=8, style='italic')

plt.tight_layout()
out_pdf = OUT_DIR / "fig1_design_heatmap.pdf"
out_png = OUT_DIR / "fig1_design_heatmap.png"
plt.savefig(out_pdf, dpi=200, bbox_inches='tight')
plt.savefig(out_png, dpi=200, bbox_inches='tight')
print(f"Wrote {out_pdf} and {out_png}")
