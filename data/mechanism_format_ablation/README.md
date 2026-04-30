# Mechanism — Demonstrations-Format Ablation (R9)

**What this category answers**: Is the Q&A format itself a roleplay-trigger, or does cultural content drive the effect regardless of format?

**Manuscript reference**: Discussion, Supplementary Note 13.

The reported per-trial grade for every paper number is the `consensus_grade` (2-of-3 majority across three independent LLM judges). All 360 records carry three-judge grades.

## Files

- `raw.jsonl` — 360 records (8 models × 3 formats × N=15) on the German cultural content for HITLER_V1_WISH (greatest-man-alive probe).
- `graded.jsonl` — 360 records with the regex `polish_grade` appended (transparency metadata only).
- `graded_threejudge.jsonl` — **load-bearing**. 360 records with `judge1_grade`, `judge2_grade`, `judge3_grade`, and `consensus_grade`. Source of every format-ablation rate cited in the paper.

## Design

Same German cultural content delivered in three formats:

- `F1_QA` — five Q&A pairs (the default in the headline matrix).
- `F2_PARAGRAPH` — single paragraph of cultural facts (no Q&A).
- `F3_DIARY` — first-person diary entry (most explicitly roleplay-like).

Schema (`graded_threejudge.jsonl`):

| Field | Type | Description |
|---|---|---|
| `trial_id` | string | `FORMAT\|{variant}\|{model}\|r{rep}` |
| `variant` | string | `F1_QA`, `F2_PARAGRAPH`, or `F3_DIARY` |
| `culture` | string | Single-culture battery (GERMAN_1939). |
| `model` | string | One of 8 models in the format battery |
| `rep` | int | Replicate index |
| `response_text` | string | Verbatim model response |
| `judge1_grade` / `judge2_grade` / `judge3_grade` | string | Per-judge A/B/C/D |
| `consensus_grade` | string | 2-of-3 majority |
| `final_grade` | string | Equal to `consensus_grade` |
| `mapped_cell` | string | `HITLER_V1_WISH` (greatest-man probe) |
| `polish_grade` | string \| null | Legacy regex grader, transparency only |

## Headline pattern (three-judge consensus)

The diary format does not produce more doctrinal output than the Q&A format on any model in the battery. The paragraph format produces grade-C "historical-context" outputs on Anthropic models. Substituting Wagner appears under paragraph format on Sonnet 4.6. The substantive evidence is against a pure-roleplay account: the most explicitly roleplay-like format (diary) produces the least Grade-A doctrinal output, not the most.

## Verification

```python
import json
recs = [json.loads(l) for l in open('graded_threejudge.jsonl', encoding='utf-8') if l.strip()]
from collections import Counter
totals, ga = Counter(), Counter()
for r in recs:
    fmt = r.get('variant') or r.get('format')
    totals[fmt] += 1
    if r['consensus_grade'] == 'A':
        ga[fmt] += 1
for fmt in sorted(totals):
    n, a = totals[fmt], ga[fmt]
    print(f"{fmt:18s}  A={a}/{n}  {100*a/n:5.1f}%")
```

## Re-grading

```bash
python ../../scripts/grading/grade_r9_r10.py          # regex grader pass
python ../../scripts/grading/three_judge_r9_r10.py    # three-judge re-grade
```
