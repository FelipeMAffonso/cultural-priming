"""Per-model × per-cell trial counts and Grade-A rates.
Output: full matrix for inclusion in SI."""
import json, glob
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent

def grade_of(r): return r.get('grade') or (r.get('grading',{}) or {}).get('grade')

# Aggregate every record across all data files (no archive duplicates)
all_recs = []
for jf in sorted(Path(ROOT/'data').rglob('*.jsonl')):
    if 'archive_chronological' in str(jf): continue
    if 'raw_' in str(jf): continue  # skip raw, use only graded
    if 'two_judge' in str(jf): continue  # skip judge file (separate)
    for l in open(jf, encoding='utf-8'):
        if l.strip():
            r = json.loads(l)
            r['_source'] = jf.name
            all_recs.append(r)

print(f"Total graded records (across all studies): {len(all_recs)}")

# Per (model, cell or culture+probe) breakdown
def cell_key(r):
    if r.get('cell'):
        return r['cell']
    elif r.get('culture') and r.get('probe_id'):
        return f"{r['culture']}_x_{r['probe_id']}"
    elif r.get('culture'):
        return r['culture']
    elif r.get('sys_variant') and r.get('cell'):
        return f"{r['cell']}_x_{r['sys_variant']}"
    return 'UNK'

matrix = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0, 0]))  # [N, A, B, C, D]
for r in all_recs:
    m = r.get('model','UNK')
    c = cell_key(r)
    g = grade_of(r)
    matrix[c][m][0] += 1
    if g == 'A': matrix[c][m][1] += 1
    elif g == 'B': matrix[c][m][2] += 1
    elif g == 'C': matrix[c][m][3] += 1
    elif g == 'D': matrix[c][m][4] += 1

print(f"\n## PER-CELL × PER-MODEL TRIAL MATRIX")
print(f"Format: cell | model | N | Grade A | B | C | D | A%\n")

# Group cells: headline matrix first, then mechanisms
def cell_priority(c):
    if any(c.startswith(p) for p in ['HITLER','SOVIET','MEDIEVAL','EDO','CONFUCIAN','VICTORIAN','AZTEC','CONFEDERATE','APARTHEID','INDIAN']):
        return (0, c)
    if c.startswith('CONTROL_'): return (1, c)
    if c.startswith('GERMAN_1939') or c.startswith('IMPERIAL_CHINA') or c.startswith('SOVIET_1968') or c.startswith('NODEMO'):
        return (2, c)
    if '_x_SYS_' in c: return (3, c)
    return (9, c)

print(f"{'Cell':35s} {'Model':30s} {'N':>4s} {'A':>4s} {'B':>4s} {'C':>4s} {'D':>4s} {'A%':>5s}")
print('-'*110)
for c in sorted(matrix.keys(), key=cell_priority):
    for m in sorted(matrix[c].keys()):
        n, a, b, cc, d = matrix[c][m]
        if n == 0: continue
        print(f"{c:35s} {m:30s} {n:>4d} {a:>4d} {b:>4d} {cc:>4d} {d:>4d} {100*a/n:>5.0f}")

# Total per-model trial count (across ALL cells)
print("\n\n## PER-MODEL TOTAL TRIAL COUNT (across all studies)")
per_model = defaultdict(int)
for r in all_recs:
    per_model[r.get('model','UNK')] += 1
print(f"{'Model':30s} {'Total trials':>12s}")
for m, n in sorted(per_model.items(), key=lambda x: -x[1]):
    print(f"{m:30s} {n:>12d}")
total = sum(per_model.values())
print(f"{'TOTAL':30s} {total:>12d}")
