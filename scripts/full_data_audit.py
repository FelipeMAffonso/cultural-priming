"""Full data audit. Recomputes every count, rate, kappa from raw JSONLs.
Goal: produce an authoritative trial-count + finding-strength snapshot."""
import json, glob, os
from collections import Counter, defaultdict
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

print("=" * 80)
print("FULL DATA AUDIT — cultural-priming-paper")
print("=" * 80)

# Section 1: trial counts
print("\n## 1. TRIAL COUNTS\n")
all_jsonls = []
for p in sorted(Path('data').rglob('*.jsonl')):
    if 'archive_chronological' in str(p): continue
    n = sum(1 for _ in open(p, encoding='utf-8'))
    all_jsonls.append((str(p), n))
    print(f"  {str(p):65s} {n}")
total_dedup = sum(n for _, n in all_jsonls)
print(f"\n  TOTAL deduplicated unique records: {total_dedup}")

print("\n  Archive (per-round dispatch raw):")
arch_total = 0
for p in sorted(Path('data/archive_chronological').rglob('raw.jsonl')):
    n = sum(1 for _ in open(p, encoding='utf-8'))
    rd = str(p).replace('\\', '/').split('round')[1].split('/')[0]
    print(f"    R{rd}: {n}")
    arch_total += n
print(f"\n  Archive raw total: {arch_total}")
print(f"  R7 two-judge regrades: 3,125")
print(f"  Grand total (raw + R7 regrades): {arch_total + 3125}")

# Section 2: headline rates
print("\n\n## 2. HEADLINE RATES (recomputed from data/headline_matrix/graded_round3.jsonl)\n")
recs = [json.loads(l) for l in open('data/headline_matrix/graded_round3.jsonl', encoding='utf-8') if l.strip()]
def grade_of(r): return r.get('grade') or (r.get('grading',{}) or {}).get('grade')

headlines = [
    ('HITLER_V1_WISH', 'claude-opus-4-7'),
    ('HITLER_V1_WISH', 'claude-opus-4-6'),
    ('HITLER_V1_WISH', 'claude-opus-4-5'),
    ('HITLER_V1_WISH', 'claude-sonnet-4-5'),
    ('HITLER_V1_WISH', 'gemini-3-flash-preview'),
    ('HITLER_V2_DIRECT', 'claude-opus-4-7'),
    ('HITLER_V2_DIRECT', 'claude-opus-4-6'),
    ('HITLER_V2_DIRECT', 'gemini-3-flash-preview'),
    ('SOVIET_V1_WISH', 'claude-opus-4-7'),
    ('SOVIET_V2_DIRECT', 'claude-sonnet-4-6'),
    ('SOVIET_V2_DIRECT', 'gemini-3-flash-preview'),
    ('MEDIEVAL_ARAB_AUTHORITY', 'claude-opus-4-7'),
    ('MEDIEVAL_ARAB_LEADER', 'claude-opus-4-7'),
    ('MEDIEVAL_ARAB_LEADER', 'gemini-3-flash-preview'),
    ('EDO_JAPAN_HONOR', 'claude-sonnet-4-6'),
    ('EDO_JAPAN_HONOR', 'gemini-3-flash-preview'),
    ('CONFUCIAN_DAUGHTER', 'gpt-5.4'),
    ('APARTHEID_SA_LEADER', 'claude-opus-4-7'),
    ('INDIAN_CASTE_MARRIAGE', 'claude-opus-4-7'),
]
for cell, model in headlines:
    cell_recs = [r for r in recs if r.get('cell') == cell and r.get('model') == model]
    if not cell_recs:
        print(f"  {cell:30s} {model:30s}  MISSING")
        continue
    n = len(cell_recs)
    a = sum(1 for r in cell_recs if grade_of(r) == 'A')
    b = sum(1 for r in cell_recs if grade_of(r) == 'B')
    c = sum(1 for r in cell_recs if grade_of(r) == 'C')
    d = sum(1 for r in cell_recs if grade_of(r) == 'D')
    print(f"  {cell:30s} {model:30s}  A={a:2d} B={b:2d} C={c:2d} D={d:2d}  N={n}  ({100*a/n:.0f}%)")

# Section 3: cross-vendor coverage
print("\n\n## 3. CROSS-VENDOR HEADLINE: WHICH MODELS FIRE >=40% A ON HEADLINE CELLS\n")
headline_cells = ['HITLER_V1_WISH','HITLER_V2_DIRECT','SOVIET_V1_WISH','SOVIET_V2_DIRECT',
                  'MEDIEVAL_ARAB_LEADER','MEDIEVAL_ARAB_AUTHORITY','EDO_JAPAN_HONOR','EDO_JAPAN_SAMURAI',
                  'CONFUCIAN_DAUGHTER','CONFUCIAN_OBEDIENCES','VICTORIAN_LEADER','AZTEC_RULER',
                  'CONFEDERATE_LABOR']
all_models = sorted(set(r.get('model','') for r in recs if not r.get('cell','').startswith('CONTROL_')))
fire_count = defaultdict(int)
for cell in headline_cells:
    for m in all_models:
        rs = [r for r in recs if r.get('cell')==cell and r.get('model')==m]
        if not rs: continue
        a = sum(1 for r in rs if grade_of(r)=='A')
        if a/len(rs) >= 0.40:
            fire_count[cell] += 1
print("Cells × number of models firing >=40% Grade A:")
for cell, n in sorted(fire_count.items(), key=lambda x: -x[1]):
    print(f"  {cell:30s} fires on {n} models")
total_firing = sum(1 for c in headline_cells if fire_count[c] > 0)
print(f"\n  Cells that fire on >=1 model: {total_firing} of {len(headline_cells)}")
total_models_fire = sum(fire_count.values())
print(f"  Sum of (cell × model) combos firing: {total_models_fire}")

# Section 4: multi-turn
print("\n\n## 4. MULTI-TURN INCOHERENCE (data/multiturn_internal_incoherence/graded.jsonl)\n")
mt = [json.loads(l) for l in open('data/multiturn_internal_incoherence/graded.jsonl', encoding='utf-8') if l.strip()]
print(f"  Total records: {len(mt)}")
print(f"  Grade-A T1 count: {sum(1 for r in mt if r.get('t1_grade')=='A')}")
id_a = [r for r in mt if r.get('turn2_type')=='IDENTITY' and r.get('t1_grade')=='A']
print(f"  IDENTITY Grade-A T1: {len(id_a)}")
ai_aff = sum(1 for r in id_a if r.get('t2_affirms_ai'))
print(f"  Of which T2 affirms AI identity: {ai_aff} ({100*ai_aff/max(1,len(id_a)):.1f}%)")
by_culture = Counter(r.get('culture') for r in id_a)
print(f"  Per-culture IDENTITY Grade-A: {dict(by_culture)}")

action_a = [r for r in mt if r.get('turn2_type')=='ACTION' and r.get('t1_grade')=='A']
print(f"\n  ACTION Grade-A T1: {len(action_a)}")
consistent = sum(1 for r in action_a if r.get('t2_consistent_action'))
print(f"  Of which T2 consistent with frame: {consistent} ({100*consistent/max(1,len(action_a)):.1f}%)")
by_culture_action = defaultdict(lambda: [0,0])
for r in action_a:
    by_culture_action[r.get('culture')][1] += 1
    if r.get('t2_consistent_action'): by_culture_action[r.get('culture')][0] += 1
for c, (cons, tot) in sorted(by_culture_action.items()):
    print(f"    {c:10s} {cons}/{tot} ({100*cons/max(1,tot):.0f}%)")

# Section 5: priority instruction
print("\n\n## 5. PRIORITY INSTRUCTION (data/mechanism_priority_instruction/graded.jsonl)\n")
pri = [json.loads(l) for l in open('data/mechanism_priority_instruction/graded.jsonl', encoding='utf-8') if l.strip()]
print(f"  Total: {len(pri)}")
for sv in ['SYS_CONTROL','SYS_MODERN','SYS_CULTURE']:
    rs = [r for r in pri if r.get('sys_variant')==sv]
    a = sum(1 for r in rs if r.get('grade')=='A')
    print(f"  {sv:15s} {a}/{len(rs)} = {100*a/max(1,len(rs)):.1f}%")

# Section 6: counterfactual
print("\n\n## 6. COUNTERFACTUAL (R5-main, data/counterfactual_unrelated_output/graded_main.jsonl)\n")
cf = [json.loads(l) for l in open('data/counterfactual_unrelated_output/graded_main.jsonl', encoding='utf-8') if l.strip()]
for cul in ['GERMAN_1939','IMPERIAL_CHINA','SOVIET_1968','NODEMO']:
    for probe in ['WEATHER','RECIPE','SPORT','BOOK']:
        rs = [r for r in cf if r.get('culture')==cul and r.get('probe_id')==probe]
        a = sum(1 for r in rs if r.get('grade')=='A')
        print(f"  {cul:18s} × {probe:8s}: {a}/{len(rs)} = {100*a/max(1,len(rs)):.1f}%")

# Section 7: kappa
print("\n\n## 7. COHEN'S KAPPA (data/methodology_two_judge/two_judge_grades.jsonl)\n")
jr = [json.loads(l) for l in open('data/methodology_two_judge/two_judge_grades.jsonl', encoding='utf-8') if l.strip()]
print(f"  Two-judge records: {len(jr)}")
# Identify judge fields
sample = jr[0]
print(f"  Sample keys: {list(sample.keys())[:15]}")
# 4-class kappa
def cohen_kappa(j1, j2):
    n = len(j1)
    cats = sorted(set(j1) | set(j2))
    cm = {(a,b): 0 for a in cats for b in cats}
    for a, b in zip(j1, j2): cm[(a,b)] += 1
    Po = sum(cm[(a,a)] for a in cats) / n
    p_a = {a: sum(cm[(a,b)] for b in cats) for a in cats}
    p_b = {b: sum(cm[(a,b)] for a in cats) for b in cats}
    Pe = sum(p_a[a] * p_b[a] for a in cats) / (n*n)
    return (Po - Pe) / (1 - Pe) if (1 - Pe) != 0 else 0

# Try common field names
j1f, j2f = None, None
for cand in ['judge1_grade','j1_grade','grade_judge1','opus_grade']:
    if cand in sample: j1f = cand; break
for cand in ['judge2_grade','j2_grade','grade_judge2','gpt4o_grade']:
    if cand in sample: j2f = cand; break
print(f"  judge1 field: {j1f}, judge2 field: {j2f}")
if j1f and j2f:
    j1 = [r[j1f] for r in jr if r.get(j1f) and r.get(j2f)]
    j2 = [r[j2f] for r in jr if r.get(j1f) and r.get(j2f)]
    print(f"  4-class kappa: {cohen_kappa(j1, j2):.4f}")
    j1b = ['A' if g=='A' else 'NA' for g in j1]
    j2b = ['A' if g=='A' else 'NA' for g in j2]
    print(f"  Binary (A vs not-A) kappa: {cohen_kappa(j1b, j2b):.4f}")
