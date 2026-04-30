"""Figure 5 — multi-turn diagnostic.

For trials where Turn 1 produces grade-A doctrinal output, Turn 2 (in same
conversation) either affirms 2024 AI identity (IDENTITY probe) or carries
forward into the doctrinal action-step (ACTION probe). Computed from
canonical R6 data (14 models x 5 cultures).

Single navy palette throughout. No suptitle. Flush-left panel labels.

Output: manuscript/figures/fig5_multiturn_diagnostic.{pdf,png}
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

GRADED = ROOT / "data" / "canonical" / "r6_multiturn.jsonl"
OUT_DIR = ROOT / "manuscript" / "figures"

recs = [json.loads(l) for l in open(GRADED, encoding="utf-8") if l.strip()]
print(f"Loaded {len(recs)} R6 multiturn records")


def t1_grade_of(r):
    return r.get("t1_grade") or r.get("consensus_grade") or r.get("final_grade")


CULTURES = ["GERMAN", "SOVIET", "CHINA", "EDO_HONOR", "ARAB"]
CULTURE_LABELS = {
    "GERMAN": "German",
    "SOVIET": "Soviet",
    "CHINA": "China",
    "EDO_HONOR": "Edo Japan",
    "ARAB": "Med. Arab",
}

fig, axes = plt.subplots(
    1, 3, figsize=(9.0, 3.8),
    gridspec_kw={"width_ratios": [1.0, 1.0, 1.5]},
)
plt.subplots_adjust(left=0.07, right=0.98, top=0.90, bottom=0.18, wspace=0.55)


# ---- Panel a: identity-affirmation rate per culture ----
ax = axes[0]
ks_a, ns_a = [], []
for c in CULTURES:
    sub = [r for r in recs if r.get("culture") == c
           and r.get("turn2_type") == "IDENTITY"
           and t1_grade_of(r) == "A"]
    ns_a.append(len(sub))
    ks_a.append(sum(1 for r in sub if r.get("t2_affirms_ai")))

rates_a = [100.0 * k / n if n else 0.0 for k, n in zip(ks_a, ns_a)]
xs = np.arange(len(CULTURES))
ax.bar(xs, rates_a, color=PRIMARY, edgecolor="#14181F", linewidth=0.4, width=0.6)

for x, r in zip(xs, rates_a):
    ax.text(x, r + 2, f"{int(round(r))}%",
            ha="center", va="bottom", fontsize=8, color="#14181F")

ax.set_xticks(xs)
ax.set_xticklabels([CULTURE_LABELS[c] for c in CULTURES], fontsize=8, rotation=20, ha="right")
ax.set_ylim(0, 115)
ax.set_ylabel("Turn 2 affirms 2024 AI identity (%)")
add_panel_label(ax, "a", x=-0.20, y=1.05)


# ---- Panel b: action-persistence rate per culture ----
ax = axes[1]
ks_b, ns_b = [], []
for c in CULTURES:
    sub = [r for r in recs if r.get("culture") == c
           and r.get("turn2_type") == "ACTION"
           and t1_grade_of(r) == "A"]
    ns_b.append(len(sub))
    ks_b.append(sum(1 for r in sub if r.get("t2_consistent_action")))

rates_b = [100.0 * k / n if n else 0.0 for k, n in zip(ks_b, ns_b)]
xs = np.arange(len(CULTURES))
ax.bar(xs, rates_b, color=PRIMARY, edgecolor="#14181F", linewidth=0.4, width=0.6)
for x, r in zip(xs, rates_b):
    ax.text(x, r + 2, f"{int(round(r))}%",
            ha="center", va="bottom", fontsize=8, color="#14181F")

ax.set_xticks(xs)
ax.set_xticklabels([CULTURE_LABELS[c] for c in CULTURES], fontsize=8, rotation=20, ha="right")
ax.set_ylim(0, 115)
ax.set_ylabel("Turn 2 delivers doctrinal steps (%)")
add_panel_label(ax, "b", x=-0.20, y=1.05)


# ---- Panel c: post-hoc persona narrative rate by model ----
ax = axes[2]
model_persona = {}
for r in recs:
    if t1_grade_of(r) != "A":
        continue
    m = r["model"]
    d = model_persona.setdefault(m, [0, 0])
    d[1] += 1
    if r.get("t2_post_hoc_persona"):
        d[0] += 1

items = [(m, 100.0 * v[0] / v[1], v[0], v[1]) for m, v in model_persona.items() if v[1] >= 5]
items.sort(key=lambda x: x[1], reverse=True)

labels_short = [
    m.replace("claude-", "").replace("gpt-", "GPT-")
     .replace("gemini-", "Gemini-").replace("-preview", "")
    for m, _, _, _ in items
]
persona_rates = [r for _, r, _, _ in items]

y_pos = np.arange(len(labels_short))[::-1]
colors_c = [PRIMARY if r > 0 else MUTED for r in persona_rates]
ax.barh(y_pos, persona_rates, color=colors_c, edgecolor="#14181F", linewidth=0.4, height=0.6)

for yi, r in zip(y_pos, persona_rates):
    ax.text(r + 1.2, yi, f"{int(round(r))}%",
            va="center", ha="left", fontsize=7, color="#14181F")

ax.set_yticks(y_pos)
ax.set_yticklabels(labels_short, fontsize=7)
ax.set_xlabel("Post-hoc persona narrative (%)")
xmax = max(persona_rates + [10]) * 1.25 if persona_rates else 30
ax.set_xlim(0, xmax)
add_panel_label(ax, "c", x=-0.45, y=1.05)


plt.savefig(OUT_DIR / "fig5_multiturn_diagnostic.pdf")
plt.savefig(OUT_DIR / "fig5_multiturn_diagnostic.png")
print("Wrote fig5_multiturn_diagnostic")
