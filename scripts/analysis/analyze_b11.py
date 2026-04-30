"""B11 results analysis.

Runs after grade_b11_threejudge.py. Produces:
- Per-cell × condition Grade-A rate table
- PRIMED − CONTROL delta per cell
- Per-model harmful Grade-A counts
- Cross-culture-group analysis (same probe across cultures)
- Verbatim mining for the 3 best chilling cells for Fig 1 bottom row
- A markdown digest at data/b11_pure_modern_probes/SUMMARY.md
"""
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parent.parent.parent
GRADED = ROOT / "data" / "b11_pure_modern_probes" / "graded_threejudge.jsonl"
OUT_MD = ROOT / "data" / "b11_pure_modern_probes" / "SUMMARY.md"

if not GRADED.exists():
    print(f"ERROR: graded file not found: {GRADED}")
    raise SystemExit(1)

records = [json.loads(l) for l in open(GRADED, encoding="utf-8") if l.strip()]
print(f"Total graded records: {len(records)}")

# ============================================================
# 1. Per-cell × condition Grade-A rate
# ============================================================
by_cell_cond = defaultdict(list)
for r in records:
    by_cell_cond[(r["cell_id"], r["culture"], r["condition"])].append(r["consensus_grade"])

# ============================================================
# 2. PRIMED − CONTROL delta per cell
# ============================================================
deltas = []
for cell in sorted({r["cell_id"] for r in records}):
    primed = [r for r in records if r["cell_id"]==cell and r["condition"]=="PRIMED"]
    control = [r for r in records if r["cell_id"]==cell and r["condition"]=="CONTROL"]
    if not primed: continue
    culture = primed[0]["culture"]
    group = primed[0].get("group")
    p_n = len(primed); p_a = sum(1 for r in primed if r["consensus_grade"]=="A")
    p_rate = p_a / p_n if p_n else 0
    c_n = len(control); c_a = sum(1 for r in control if r["consensus_grade"]=="A")
    c_rate = c_a / c_n if c_n else 0
    deltas.append({
        "cell": cell, "culture": culture, "group": group,
        "primed_n": p_n, "primed_a": p_a, "primed_rate": p_rate,
        "control_n": c_n, "control_a": c_a, "control_rate": c_rate,
        "delta": p_rate - c_rate,
    })
deltas.sort(key=lambda d: -d["primed_rate"])

# ============================================================
# 3. Per-model harmful Grade-A counts (PRIMED only)
# ============================================================
model_a = Counter()
model_total = Counter()
for r in records:
    if r["condition"] != "PRIMED": continue
    model_total[r["model"]] += 1
    if r["consensus_grade"] == "A":
        model_a[r["model"]] += 1

# ============================================================
# 4. Cross-culture-group analysis (same probe, different priming)
# ============================================================
groups = defaultdict(list)
for d in deltas:
    if d["group"]:
        groups[d["group"]].append(d)

# ============================================================
# 5. Best-cell × best-model verbatim for Fig 1 candidates
# Top 5 (cell × model) PRIMED Grade-A pairs, sorted by rate then by visceral severity
# ============================================================
by_cell_model = defaultdict(list)
for r in records:
    if r["condition"] != "PRIMED": continue
    by_cell_model[(r["cell_id"], r["culture"], r["model"])].append(r)

cell_model_summary = []
for (cell, culture, model), recs in by_cell_model.items():
    n = len(recs); a = sum(1 for r in recs if r["consensus_grade"]=="A")
    a_recs = [r for r in recs if r["consensus_grade"]=="A"]
    cell_model_summary.append({
        "cell": cell, "culture": culture, "model": model,
        "n": n, "a": a, "rate": a/n if n else 0,
        "verbatim_examples": [r["response_text"][:600] for r in a_recs[:2]],
        "probe_text": recs[0]["probe_text"],
    })
cell_model_summary.sort(key=lambda s: (-s["rate"], -s["a"]))

# ============================================================
# 6. Three-judge agreement
# ============================================================
def kappa_multi(grades_a, grades_b):
    classes = ("A","B","C","D")
    n = len(grades_a)
    if n == 0: return float("nan")
    agree = sum(1 for a,b in zip(grades_a, grades_b) if a==b)
    p_o = agree / n
    p_e = 0.0
    for c in classes:
        pa = sum(1 for g in grades_a if g==c)/n
        pb = sum(1 for g in grades_b if g==c)/n
        p_e += pa * pb
    if p_e == 1: return 1.0
    return (p_o - p_e) / (1 - p_e)

primed_records = [r for r in records if r["condition"]=="PRIMED"]
g1s = [r["judge1_grade"] for r in primed_records]
g2s = [r["judge2_grade"] for r in primed_records]
g3s = [r["judge3_grade"] for r in primed_records]
k_12 = kappa_multi(g1s, g2s)
k_13 = kappa_multi(g1s, g3s)
k_23 = kappa_multi(g2s, g3s)
unanim = sum(1 for a,b,c in zip(g1s,g2s,g3s) if a==b==c)/len(g1s) if g1s else float("nan")

# ============================================================
# WRITE MARKDOWN DIGEST
# ============================================================
with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("# B11 — Pure-Modern Probes — Three-Judge Cross-Vendor Results\n\n")
    f.write(f"**Records graded**: {len(records)}\n\n")
    f.write(f"**Three-judge agreement**: pairwise κ Opus-4.6/GPT-4o = {k_12:.3f}, ")
    f.write(f"Opus-4.6/Gemini-3-Flash = {k_13:.3f}, GPT-4o/Gemini-3-Flash = {k_23:.3f}; ")
    f.write(f"unanimous 3-of-3 = {unanim*100:.1f}%\n\n")

    f.write("## Headline: PRIMED Grade-A rate by cell, with PRIMED − CONTROL delta\n\n")
    f.write("| Cell | Culture | PRIMED A% | CONTROL A% | Δ |\n")
    f.write("|---|---|---:|---:|---:|\n")
    for d in deltas:
        f.write(f"| {d['cell']} | {d['culture']} | "
                f"{d['primed_rate']*100:.1f}% ({d['primed_a']}/{d['primed_n']}) | "
                f"{d['control_rate']*100:.1f}% ({d['control_a']}/{d['control_n']}) | "
                f"{d['delta']*100:+.1f}pp |\n")
    f.write("\n")

    f.write("## Per-model harmful Grade-A (PRIMED condition only)\n\n")
    f.write("| Model | A | Total | Rate |\n|---|---:|---:|---:|\n")
    for m in sorted(model_total.keys(), key=lambda k: -model_a[k]):
        f.write(f"| {m} | {model_a[m]} | {model_total[m]} | {100*model_a[m]/model_total[m]:.1f}% |\n")
    f.write("\n")

    f.write("## Cross-culture group analysis (same probe, different priming)\n\n")
    for group_name, members in groups.items():
        f.write(f"### Group: {group_name}\n\n")
        f.write(f"Probe: \"{members[0].get('probe_text','')}\"\n\n")
        f.write("| Culture | PRIMED A% | CONTROL A% | Δ |\n|---|---:|---:|---:|\n")
        for m in members:
            f.write(f"| {m['culture']} | {m['primed_rate']*100:.1f}% | "
                    f"{m['control_rate']*100:.1f}% | {m['delta']*100:+.1f}pp |\n")
        f.write("\n")

    f.write("## Top (cell × model) cells by PRIMED Grade-A rate (Fig 1 candidates)\n\n")
    for s in cell_model_summary[:25]:
        if s["rate"] == 0: continue
        f.write(f"### {s['cell']} × {s['model']} ({s['culture']}): {s['rate']*100:.0f}% A ({s['a']}/{s['n']})\n\n")
        f.write(f"**Probe**: \"{s['probe_text']}\"\n\n")
        for ex in s["verbatim_examples"][:1]:
            f.write(f"> {ex.replace(chr(10), ' ')}\n\n")

print(f"Summary written to: {OUT_MD}")
print(f"\nHeadline: top 5 PRIMED Grade-A cells by rate:")
for d in deltas[:5]:
    print(f"  {d['cell']:<28} {d['culture']:<28} {d['primed_rate']*100:>6.1f}% PRIMED, {d['control_rate']*100:>5.1f}% CONTROL, Δ={d['delta']*100:+.1f}pp")
print(f"\nPer-model totals:")
for m in sorted(model_total.keys(), key=lambda k: -model_a[k]):
    print(f"  {m:<28} {model_a[m]:>4} A / {model_total[m]:<4} = {100*model_a[m]/model_total[m]:>5.1f}%")
print(f"\nThree-judge κ: {k_12:.3f} / {k_13:.3f} / {k_23:.3f}, unanimous {unanim*100:.1f}%")
