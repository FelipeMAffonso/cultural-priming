"""
Final verification of all SN 28 numbers. Computes ground truth from JSONL.
Settles disputes between data-analyst and numbers-checker agent reports.
"""
import json
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

B11 = "data/b11_pure_modern_probes/graded_threejudge.jsonl"
B12 = "data/b12_small_models/graded_threejudge.jsonl"

records = []
for path in [B11, B12]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            records.append(r)

print(f"Total records: {len(records)}")

# Detect grade field name
sample = records[0]
print(f"Sample keys: {sorted(sample.keys())}")

def grade_of(r):
    # try common keys
    for k in ("consensus_grade", "final_grade", "grade", "majority_grade"):
        if k in r:
            return r[k]
    return None

print(f"Grade field detected: {grade_of(records[0])}")
gA = sum(1 for r in records if grade_of(r) == "A")
print(f"Total Grade A: {gA}")

# Pooled by condition
by_cond = defaultdict(lambda: [0, 0])
for r in records:
    c = r.get("condition", r.get("cond"))
    by_cond[c][0] += 1
    if grade_of(r) == "A":
        by_cond[c][1] += 1

print("\n=== POOLED BY CONDITION ===")
for c, (n, a) in by_cond.items():
    print(f"  {c}: {a}/{n} = {a/n*100:.4f}%")

# Per (cell, model) PRIMED Grade A
cell_model = defaultdict(lambda: [0, 0])
for r in records:
    if r.get("condition", r.get("cond")) != "PRIMED":
        continue
    cell = r.get("cell_id", r.get("cell"))
    model = r.get("model")
    cell_model[(cell, model)][0] += 1
    if grade_of(r) == "A":
        cell_model[(cell, model)][1] += 1

# Cells with at least one (cell, model) at 100%
cells_100 = set()
combos_100 = []
for (cell, model), (n, a) in cell_model.items():
    if n >= 20 and a == n:
        cells_100.add(cell)
        combos_100.append((cell, model, a, n))

print(f"\n=== 100% CELLS ===")
print(f"Unique cells with >=1 (cell, model) at 100%: {len(cells_100)}")
print(f"Total (cell, model) combos at 100%: {len(combos_100)}")
for c, m, a, n in sorted(combos_100):
    print(f"  {c} x {m}: {a}/{n}")

# Cells with >=50% on at least one model
cells_50 = set()
for (cell, model), (n, a) in cell_model.items():
    if n >= 20 and (a / n) >= 0.50:
        cells_50.add(cell)
print(f"\n=== >=50% CELLS ===")
print(f"Unique cells with >=1 (cell, model) at >=50%: {len(cells_50)}")

# Per cell pooled PRIMED
cell_primed = defaultdict(lambda: [0, 0])
cell_max = defaultdict(lambda: 0.0)
cell_max_model = {}
for r in records:
    if r.get("condition", r.get("cond")) != "PRIMED":
        continue
    cell = r.get("cell_id", r.get("cell"))
    cell_primed[cell][0] += 1
    if grade_of(r) == "A":
        cell_primed[cell][1] += 1

for (cell, model), (n, a) in cell_model.items():
    if n >= 20 and (a / n) > cell_max[cell]:
        cell_max[cell] = a / n
        cell_max_model[cell] = model

print("\n=== PER-CELL PRIMED ===")
for cell, (n, a) in sorted(cell_primed.items()):
    mx = cell_max.get(cell, 0)
    mm = cell_max_model.get(cell, "")
    print(f"  {cell}: {a}/{n} = {a/n*100:.2f}% (max {mx*100:.1f}% on {mm})")

# Per model PRIMED
model_primed = defaultdict(lambda: [0, 0])
for r in records:
    if r.get("condition", r.get("cond")) != "PRIMED":
        continue
    model_primed[r.get("model")][0] += 1
    if grade_of(r) == "A":
        model_primed[r.get("model")][1] += 1

print("\n=== PER-MODEL PRIMED ===")
for model, (n, a) in sorted(model_primed.items(), key=lambda x: -x[1][1]/max(x[1][0],1)):
    print(f"  {model}: {a}/{n} = {a/n*100:.4f}%")

# Per vendor PRIMED
def vendor(m):
    if "claude" in m or "opus" in m.lower() or "sonnet" in m.lower() or "haiku" in m.lower():
        return "Anthropic"
    if "gemini" in m.lower():
        return "Google"
    if "gpt" in m.lower() or "openai" in m.lower():
        return "OpenAI"
    return "Unknown"

vendor_primed = defaultdict(lambda: [0, 0])
for r in records:
    if r.get("condition", r.get("cond")) != "PRIMED":
        continue
    vendor_primed[vendor(r.get("model"))][0] += 1
    if grade_of(r) == "A":
        vendor_primed[vendor(r.get("model"))][1] += 1

print("\n=== PER-VENDOR PRIMED ===")
for v, (n, a) in sorted(vendor_primed.items()):
    print(f"  {v}: {a}/{n} = {a/n*100:.4f}%")

# CONTROL leaks
print("\n=== CONTROL Grade A LEAKS ===")
for r in records:
    if r.get("condition", r.get("cond")) == "CONTROL" and grade_of(r) == "A":
        print(f"  {r.get('cell_id', r.get('cell'))} x {r.get('model')} rep {r.get('rep_idx', r.get('rep'))}: trial_id={r.get('trial_id')}")

# Cross-culture group analysis: DAUGHTER_13
print("\n=== CROSS-CULTURE GROUP: DAUGHTER_13 ===")
groups = {
    "DAUGHTER_13": ["ROMAN_DAUGHTER13", "CONFED_DAUGHTER13", "IMP_CHINA_DAUGHTER13", "ARAB_DAUGHTER13"],
    "NEWBORN_DISABILITY": ["ROMAN_NEWBORN", "SPARTAN_NEWBORN", "GERMAN1939_NEWBORN"],
    "CHEMIST_DEFENCE": ["WW1_CHEMIST", "UNIT731_CHEMIST"],
}
for gname, cells in groups.items():
    print(f"  {gname}:")
    for c in cells:
        n, a = cell_primed.get(c, [0, 0])
        if n > 0:
            print(f"    {c}: {a}/{n} = {a/n*100:.2f}%")

# Trial counts per cell (for SN 28.10 deficit math)
print("\n=== TRIAL COUNTS PER CELL (PRIMED) ===")
total_primed_trials = sum(n for n, a in cell_primed.values())
total_control_trials = sum(by_cond["CONTROL"][:1])
print(f"  Total PRIMED trials: {total_primed_trials}")
print(f"  Total CONTROL trials: {by_cond['CONTROL'][0]}")
print(f"  35 cells x N=20 x (frontier 9 + tier 6) = 35*20*15 = {35*20*15}")
n_cells = len(cell_primed)
print(f"  Distinct cells: {n_cells}")
