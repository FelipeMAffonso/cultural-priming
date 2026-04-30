"""Grade the 540 R4 fill trials and merge into graded.jsonl.

Reads:  data/mechanism_priority_instruction/raw_fill.jsonl  (540 trials)
Writes: data/mechanism_priority_instruction/graded.jsonl    (1,440 + 540 = 1,980)
"""
import json, sys, os
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from grade_round4 import grade

ROOT = HERE.parent.parent
RAW_FILL = ROOT / "data" / "mechanism_priority_instruction" / "raw_fill.jsonl"
GRADED   = ROOT / "data" / "mechanism_priority_instruction" / "graded.jsonl"

# Load fill records and grade
fill_recs = [json.loads(l) for l in open(RAW_FILL, encoding='utf-8') if l.strip()]
print(f"Fill records: {len(fill_recs)}")

# Promote nested 'meta' fields to top-level (the grader expects cell, sys_variant on the record)
for r in fill_recs:
    meta = r.get('meta', {})
    for k in ('cell', 'sys_variant', 'rep', 'battery'):
        if k in meta and k not in r:
            r[k] = meta[k]
    g, reason = grade(r)
    r['grade'] = g
    r['grade_reason'] = reason

# Append fill to existing graded.jsonl
with open(GRADED, 'a', encoding='utf-8') as f:
    for r in fill_recs:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

# Verify
all_recs = [json.loads(l) for l in open(GRADED, encoding='utf-8') if l.strip()]
print(f"Total graded records (merged): {len(all_recs)}")

# Recompute mechanism rates by sys_variant
from collections import Counter, defaultdict
agg = defaultdict(lambda: Counter())
for r in all_recs:
    agg[r.get('sys_variant', '?')][r.get('grade', '?')] += 1

print("\nAggregate by sys_variant:")
for sv in ['SYS_CONTROL', 'SYS_MODERN', 'SYS_CULTURE']:
    c = agg[sv]
    n = sum(c.values())
    a = c['A']
    print(f"  {sv:15s}  A={a}  N={n}  {100*a/max(1,n):.1f}%  (B={c['B']}, C={c['C']}, D={c['D']})")

# Per cell × sys_variant
print("\nPer cell × sys_variant:")
cell_agg = defaultdict(lambda: Counter())
for r in all_recs:
    key = (r.get('cell', '?'), r.get('sys_variant', '?'))
    cell_agg[key][r.get('grade', '?')] += 1

for cell in ['HITLER_V2', 'SOVIET_V2', 'CONFUCIAN_DAUGHTER', 'MEDIEVAL_ARAB_AUTHORITY']:
    for sv in ['SYS_CONTROL', 'SYS_MODERN', 'SYS_CULTURE']:
        c = cell_agg[(cell, sv)]
        n = sum(c.values())
        a = c['A']
        print(f"  {cell:30s} {sv:15s}  A={a}/{n} = {100*a/max(1,n):.1f}%")
