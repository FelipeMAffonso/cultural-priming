"""Compute pairwise Cohen's kappa for the three-judge cross-vendor grading log.

Reads the deposited three-judge log at data/methodology_two_judge/three_judge_grades.jsonl
(12,180 canonical records, each carrying judge1_grade / judge2_grade / judge3_grade and
the legacy polish_grade), computes pairwise 4-class kappa across the three LLM judges
and against the legacy regex grader, reports the agreement breakdown, and writes the
summary to data/methodology_two_judge/kappa_summary.txt.

Judges: judge1 = Anthropic Claude Opus 4.6, judge2 = OpenAI GPT-4o,
judge3 = Google Gemini-3-Flash-Preview. Reported per-trial grade = 2-of-3 majority.
"""
import json
import sys
import io
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
GRADES_PATH = REPO_ROOT / "data" / "methodology_two_judge" / "three_judge_grades.jsonl"
OUT_PATH = REPO_ROOT / 'data' / 'methodology_two_judge' / 'kappa_summary.txt'
GRADESET = {'A', 'B', 'C', 'D'}

recs = []
for line in open(GRADES_PATH, encoding="utf-8"):
    if not line.strip():
        continue
    try:
        recs.append(json.loads(line))
    except Exception:
        pass

lines = []
def emit(s=""):
    print(s)
    lines.append(s)

emit(f"Loaded {len(recs)} graded records from {GRADES_PATH.name}")

def cohen_kappa(labels1, labels2):
    """Cohen's kappa for two raters with categorical labels."""
    assert len(labels1) == len(labels2)
    n = len(labels1)
    if n == 0:
        return None
    cats = sorted(set(labels1) | set(labels2))
    if len(cats) < 2:
        return 1.0
    po = sum(1 for a, b in zip(labels1, labels2) if a == b) / n
    p1 = Counter(labels1)
    p2 = Counter(labels2)
    pe = sum((p1[c] / n) * (p2[c] / n) for c in cats)
    if pe >= 1:
        return 1.0
    return (po - pe) / (1 - pe)

def filter_valid(recs, key1, key2):
    valid = [(r[key1], r[key2]) for r in recs if r.get(key1) in GRADESET and r.get(key2) in GRADESET]
    return [v[0] for v in valid], [v[1] for v in valid]

JUDGE_PAIRS = [
    ("judge1_grade", "judge2_grade"),
    ("judge1_grade", "judge3_grade"),
    ("judge2_grade", "judge3_grade"),
]
POLISH_PAIRS = [
    ("polish_grade", "judge1_grade"),
    ("polish_grade", "judge2_grade"),
    ("polish_grade", "judge3_grade"),
]

emit("\n=== AGGREGATE COHEN'S KAPPA (A/B/C/D 4-class) ===")
for k1, k2 in JUDGE_PAIRS + POLISH_PAIRS:
    a, b = filter_valid(recs, k1, k2)
    k = cohen_kappa(a, b)
    emit(f"  {k1:>15} vs {k2:>15}: kappa = {k:.3f} (N={len(a)})")

emit("\n=== THREE-JUDGE AGREEMENT BREAKDOWN ===")
trip = [(r["judge1_grade"], r["judge2_grade"], r["judge3_grade"]) for r in recs
        if all(r.get(k) in GRADESET for k in ("judge1_grade", "judge2_grade", "judge3_grade"))]
unan = sum(1 for g in trip if g[0] == g[1] == g[2])
alldiff = sum(1 for g in trip if g[0] != g[1] and g[1] != g[2] and g[0] != g[2])
maj = len(trip) - unan - alldiff
emit(f"  N with all three judges: {len(trip)}")
emit(f"  3-of-3 unanimous: {unan} ({100*unan/len(trip):.1f}%)")
emit(f"  2-of-3 majority:  {maj} ({100*maj/len(trip):.1f}%)")
emit(f"  all three differ: {alldiff} ({100*alldiff/len(trip):.1f}%)")

emit("\n=== BINARY KAPPA (Grade A vs not-A) ===")
def binarize(g):
    return "A" if g == "A" else "X"
for k1, k2 in JUDGE_PAIRS:
    pairs = [(binarize(r[k1]), binarize(r[k2])) for r in recs if r.get(k1) in GRADESET and r.get(k2) in GRADESET]
    k = cohen_kappa([p[0] for p in pairs], [p[1] for p in pairs])
    emit(f"  {k1:>15} vs {k2:>15}: kappa = {k:.3f} (N={len(pairs)})")

emit("\n=== PER-CELL KAPPA (judge1 vs judge2, 4-class) ===")
by_cell = defaultdict(list)
for r in recs:
    if r.get("judge1_grade") in GRADESET and r.get("judge2_grade") in GRADESET:
        by_cell[r.get("cell", "-")].append((r["judge1_grade"], r["judge2_grade"]))
for cell in sorted(by_cell.keys()):
    pairs = by_cell[cell]
    k = cohen_kappa([p[0] for p in pairs], [p[1] for p in pairs])
    emit(f"  {cell:30} N={len(pairs):4d}  kappa={k:.3f}")

emit("\n=== GRADE DISTRIBUTION PER GRADER ===")
for k in ["polish_grade", "judge1_grade", "judge2_grade", "judge3_grade"]:
    c = Counter(r.get(k) for r in recs)
    total = sum(v for k0, v in c.items() if k0 in GRADESET)
    unparsed = c.get(None, 0) + sum(v for k0, v in c.items() if k0 not in GRADESET and k0 is not None)
    emit(f"  {k:15} A={c.get('A',0):4d} B={c.get('B',0):4d} C={c.get('C',0):4d} D={c.get('D',0):4d} parsed={total} unparsed={unparsed}")

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print(f"\nWrote summary to {OUT_PATH}")

