# Negative Controls — Where the Phenomenon Does NOT Occur

**What this category answers**: The phenomenon is bounded; which cultural primes do not retrieve harmful doctrine?

**Manuscript reference**: Section 2, Figure 3, Supplementary Note 8.

The reported per-trial grade for every paper number is the `consensus_grade` (2-of-3 majority across three independent LLM judges). All negative-control records live inside the canonical R3 file (`data/canonical/r3_cross_cultural_matrix.jsonl`) or the canonical R5 file (`data/canonical/r5_counterfactual.jsonl`); this directory is an index that points to them.

## This category is an INDEX into other categories

The negative-control cells live in `../canonical/r3_cross_cultural_matrix.jsonl` (priming cells that do not retrieve harmful doctrine, plus all `CONTROL_*` no-demonstration cells) and `../canonical/r5_counterfactual.jsonl` (NODEMO controls for the counterfactual battery). This README points to them and provides the verification snippet.

### Cultural primes that retrieve modern content (not historical doctrine)

Three priming cells produce essentially 0% Grade A across all 14 models in the main lineup:

- **APARTHEID_SA_LEADER**: 0/280 Grade A. Models default to Mandela.
- **INDIAN_CASTE_MARRIAGE**: 0/280 Grade A. Modern progressive marriage advice dominates.
- **INDIAN_DHARMA_DAUGHTER**: 1/280 Grade A. Models retrieve modern progressive advice.

Source: `../canonical/r3_cross_cultural_matrix.jsonl` rows where `cell` ∈ {`APARTHEID_SA_LEADER`, `INDIAN_CASTE_MARRIAGE`, `INDIAN_DHARMA_DAUGHTER`} and `consensus_grade` is the per-trial label.

### No-demonstration controls (priming is the causal driver)

All `CONTROL_*` cells use the same probes as the headline matrix but without the cultural Q&A prefix. Across all 14 main-lineup models, every `CONTROL_*` cell produces 0% Grade A.

Cells: CONTROL_GREATEST_MAN, CONTROL_GREATEST_LEADER, CONTROL_YOUNG_WOMAN, CONTROL_DAUGHTER, CONTROL_ROLE_OF_WOMEN, CONTROL_MORAL_GUIDE, CONTROL_HONOR, CONTROL_PLANTATION, CONTROL_SPOUSE.

Source: `../canonical/r3_cross_cultural_matrix.jsonl` rows where `cell` starts with `CONTROL_`.

### Counterfactual no-demonstration controls

In the counterfactual battery, the NODEMO arm sends the same mundane probe without any cultural priming.

Source: `../canonical/r5_counterfactual.jsonl` rows where `culture == 'NODEMO'` (560 records). All 560 produce 0% cultural-frame retrieval.

## Verification

```python
import json
recs = [json.loads(l) for l in open('../canonical/r3_cross_cultural_matrix.jsonl', encoding='utf-8') if l.strip()]
neg_cells = ('APARTHEID_SA_LEADER', 'INDIAN_CASTE_MARRIAGE', 'INDIAN_DHARMA_DAUGHTER')
neg = [r for r in recs if r.get('cell') in neg_cells or r.get('cell','').startswith('CONTROL_')]
total = len(neg)
grade_a = sum(1 for r in neg if r.get('consensus_grade') == 'A')
print(f"Negative controls: {grade_a}/{total} Grade A = {100*grade_a/total:.2f}%")
```

Per-cell breakdown:

```python
from collections import Counter
totals, ga = Counter(), Counter()
for r in recs:
    cell = r.get('cell','')
    if cell in neg_cells or cell.startswith('CONTROL_'):
        totals[cell] += 1
        if r.get('consensus_grade') == 'A':
            ga[cell] += 1
for cell in sorted(totals):
    n, a = totals[cell], ga[cell]
    print(f"{cell:32s}  A={a}/{n}  {100*a/n:5.2f}%")
```

## Used in paper

Section 2 (boundary conditions on the phenomenon) and Figure 3 (negative controls panel). The Apartheid name distribution (Mandela dominance) is reported in Figure 3 alongside the zero-rate callouts.
