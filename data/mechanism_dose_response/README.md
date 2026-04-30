# Mechanism — Lexical-Marker Dose-Response (R10)

**What this category answers**: Is the priming effect graded with the number of cultural markers, or all-or-nothing?

**Manuscript reference**: Section 7 (mechanism), Supplementary Note 14.

The reported per-trial grade for every paper number is the `consensus_grade` (2-of-3 majority across three independent LLM judges). All 1,080 records carry three-judge grades.

## Files

- `raw.jsonl` — 1,080 records (6 models × 3 cultures × 6 doses × N=10). Verbatim model outputs and metadata.
- `graded.jsonl` — 1,080 records with the regex `polish_grade` appended (transparency metadata only).
- `graded_threejudge.jsonl` — **load-bearing**. 1,080 records with `judge1_grade`, `judge2_grade`, `judge3_grade`, and `consensus_grade` for every record. Source of every dose-response rate cited in the paper.

## Design

The number of cultural-marker demonstrations is varied from 0 (no demonstrations, just the probe) to 5 (full priming with all five Q&A pairs), holding the probe constant. Cultures: GERMAN, CHINA, SOVIET. Six models from the main lineup.

Schema (`graded_threejudge.jsonl`):

| Field | Type | Description |
|---|---|---|
| `trial_id` | string | `DOSE\|{culture}\|d{dose}\|{model}\|r{rep}` |
| `culture` | string | `GERMAN`, `SOVIET`, or `CHINA` |
| `dose` | int | Number of cultural-marker demonstrations (0..5) |
| `model` | string | One of 6 models in the dose battery |
| `rep` | int | Replicate index 0..9 |
| `response_text` | string | Verbatim model response |
| `judge1_grade` / `judge2_grade` / `judge3_grade` | string | Per-judge A/B/C/D |
| `consensus_grade` | string | 2-of-3 majority across the three judges |
| `final_grade` | string | Equal to `consensus_grade` |
| `mapped_cell` | string | The canonical R3 cell the dose probe maps to (HITLER_V1_WISH for GERMAN, SOVIET_V1_WISH for SOVIET, CONFUCIAN_OBEDIENCES for CHINA) |
| `polish_grade` | string \| null | Legacy regex grader, transparency only |

## Headline pattern (three-judge consensus)

- d=0 (no demonstrations): 0% Grade A across all (model × culture). Confirms that priming, not the probe alone, is the causal driver.
- IMPERIAL_CHINA activates at d=2; SOVIET activates at d=2; GERMAN requires d=4 markers (the Wagner / Goethe / football / beer demonstrations individually appear in many German contexts; only at d=4, with the Volkswagen Beetle included, do they converge on a Nazi-period reading).

The complete d × culture × model breakdown is in `MASTER_NUMBERS.json` under the `r10_dose_response` key (when generated).

## Verification

```python
import json
recs = [json.loads(l) for l in open('graded_threejudge.jsonl', encoding='utf-8') if l.strip()]
from collections import Counter
totals, ga = Counter(), Counter()
for r in recs:
    key = (r['culture'], r['dose'])
    totals[key] += 1
    if r['consensus_grade'] == 'A':
        ga[key] += 1
for key in sorted(totals):
    n, a = totals[key], ga[key]
    print(f"culture={key[0]:14s} dose={key[1]}  A={a}/{n}  {100*a/n:5.1f}%")
```

## Re-grading

```bash
python ../../scripts/grading/grade_r9_r10.py          # regex grader pass on raw.jsonl
python ../../scripts/grading/three_judge_r9_r10.py    # three-judge re-grade of graded.jsonl
```
