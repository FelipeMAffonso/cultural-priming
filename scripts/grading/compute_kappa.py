"""Compute Cohen's kappa between three graders:
- polish: programmatic strict-marker grader (polish-agent's grade.py)
- judge1: claude-opus-4-6 LLM judge
- judge2: gpt-4o LLM judge

Reports pairwise kappa per (cell × judge-pair) and aggregate.
"""
import json
import sys
import io
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HERE = Path(__file__).resolve().parent
GRADES_PATH = HERE / "two_judge_grades.jsonl"

# Load
recs = []
for line in open(GRADES_PATH, encoding="utf-8"):
    if not line.strip(): continue
    try: recs.append(json.loads(line))
    except: pass
print(f"Loaded {len(recs)} graded records")

def cohen_kappa(labels1, labels2):
    """Cohen's kappa for two raters with categorical labels."""
    assert len(labels1) == len(labels2)
    n = len(labels1)
    if n == 0: return None
    cats = sorted(set(labels1) | set(labels2))
    if len(cats) < 2: return 1.0  # all same
    # Observed agreement
    po = sum(1 for a, b in zip(labels1, labels2) if a == b) / n
    # Expected agreement
    p1 = Counter(labels1)
    p2 = Counter(labels2)
    pe = sum((p1[c] / n) * (p2[c] / n) for c in cats)
    if pe >= 1: return 1.0
    return (po - pe) / (1 - pe)

def filter_valid(recs, key1, key2):
    valid = [(r[key1], r[key2]) for r in recs if r.get(key1) in "ABCD" and r.get(key2) in "ABCD"]
    return [v[0] for v in valid], [v[1] for v in valid]

# Aggregate kappa across all records
print("\n=== AGGREGATE COHEN'S KAPPA (all 3125 records, A/B/C/D 4-class) ===")
for k1, k2 in [("polish_grade","judge1_grade"), ("polish_grade","judge2_grade"), ("judge1_grade","judge2_grade")]:
    a, b = filter_valid(recs, k1, k2)
    k = cohen_kappa(a, b)
    n = len(a)
    print(f"  {k1:>15} vs {k2:>15}: kappa = {k:.3f} (N={n})")

# Binarize: A vs not-A (paper-grade vs not)
print("\n=== BINARY KAPPA (Grade A vs not-A) ===")
def binarize(g): return "A" if g == "A" else "X"
for k1, k2 in [("polish_grade","judge1_grade"), ("polish_grade","judge2_grade"), ("judge1_grade","judge2_grade")]:
    pairs = [(binarize(r.get(k1,"")), binarize(r.get(k2,""))) for r in recs if r.get(k1) in "ABCD" and r.get(k2) in "ABCD"]
    a = [p[0] for p in pairs]
    b = [p[1] for p in pairs]
    k = cohen_kappa(a, b)
    n = len(a)
    print(f"  {k1:>15} vs {k2:>15}: kappa = {k:.3f} (N={n})")

# Per-cell kappa for the most important cells
print("\n=== PER-CELL KAPPA (judge1 vs judge2, 4-class) ===")
by_cell = defaultdict(list)
for r in recs:
    if r.get("judge1_grade") in "ABCD" and r.get("judge2_grade") in "ABCD":
        by_cell[r.get("cell","-")].append((r["judge1_grade"], r["judge2_grade"]))
for cell in sorted(by_cell.keys()):
    pairs = by_cell[cell]
    a = [p[0] for p in pairs]
    b = [p[1] for p in pairs]
    k = cohen_kappa(a, b)
    print(f"  {cell:30} N={len(pairs):4d}  kappa={k:.3f}")

# Distribution of grades per grader
print("\n=== GRADE DISTRIBUTION PER GRADER ===")
for k in ["polish_grade","judge1_grade","judge2_grade"]:
    c = Counter(r.get(k) for r in recs)
    total = sum(v for k0,v in c.items() if k0 in "ABCD")
    print(f"  {k:15} A={c.get('A',0):4d} B={c.get('B',0):4d} C={c.get('C',0):4d} D={c.get('D',0):4d} parsed={total} unparsed={c.get(None,0)+sum(v for k0,v in c.items() if k0 not in 'ABCD' and k0 is not None)}")

# Save summary
out = HERE / "kappa_summary.txt"
with open(out, "w", encoding="utf-8") as f:
    f.write("see stdout\n")
print(f"\nWrote summary to {out}")
