# Counterfactual — Does Priming Alter Unrelated Output?

**What this category answers**: If cultural priming were just roleplay, unrelated mundane probes (weather, recipe, sport, book) should be unaffected. Does priming generalise?

**Manuscript reference**: Section 4, Figure 4, Supplementary Note 11.

The reported per-trial grade for every paper number is the `consensus_grade` (2-of-3 majority across three independent LLM judges). The unified file `data/canonical/r5_counterfactual.jsonl` (2,240 records, 14 models × 16 cells × N=10 — 1,680 primed + 560 NODEMO) is the canonical source.

## Files

### Raw model outputs
- `raw_main.jsonl` — 960 records. R5 main dispatch, 6 models × 16 cells × N=10.
- `raw_supplementary.jsonl` — 800 records. R5b fill, 5 supplementary models.
- `raw_newmodels.jsonl` — 480 records. R5 fill for the 3 new flagship models (gpt-5.5, gemini-3.1-pro-preview, gemini-2.5-pro).

### Per-round graded files (regex grader output, transparency only)
- `graded_main.jsonl` — 960 records (R5 main with regex grades).
- `graded_supplementary.jsonl` — 800 records (R5b with regex grades).
- `graded_newmodels.jsonl` — 480 records (new-model fill with regex grades).

These per-round files carry the deterministic `polish_grade` only and exist so reviewers can audit the canonical merge. The reported numbers come from the canonical file.

## Design

Priming is the same as the headline matrix; the probe is one of four mundane questions. Cultures: GERMAN_1939, IMPERIAL_CHINA, SOVIET_1968, paired with NODEMO controls. Probes: WEATHER, RECIPE, SPORT, BOOK.

Schema is documented in `SCHEMA.md` §Canonical R5; key fields on canonical records are `culture`, `probe_id`, `primed`, `response_text`, `consensus_grade`.

## Headline rates (three-judge consensus)

- IMPERIAL_CHINA × RECIPE: highest cultural-frame retrieval rate (Chinese cuisine without acknowledgment of the priming).
- IMPERIAL_CHINA × BOOK: also high.
- GERMAN × RECIPE and GERMAN × BOOK: substantial cultural-frame retrieval.
- SOVIET × all four probes: substantial cultural-frame retrieval.
- All NODEMO controls: 0% cultural-frame retrieval — a clean baseline that is the strongest evidence for the retrieval account over a pure-roleplay account.

The complete (culture × probe × model) breakdown is in `MASTER_NUMBERS.json` under `r5_per_culture_probe` and `r5_per_model_culture_probe`.

## Verification

```python
import json
from collections import Counter
recs = [json.loads(l) for l in open('../canonical/r5_counterfactual.jsonl', encoding='utf-8') if l.strip()]
totals, ga = Counter(), Counter()
for r in recs:
    key = (r['culture'], r['probe_id'])
    totals[key] += 1
    if r['consensus_grade'] == 'A':
        ga[key] += 1
for key in sorted(totals):
    n, a = totals[key], ga[key]
    print(f"culture={key[0]:14s} probe={key[1]:8s}  A={a}/{n}  {100*a/n:5.1f}%")
```

## Re-grading

```bash
python ../../scripts/grading/grade_round5.py            # regex grader on raw_main.jsonl
python ../../scripts/grading/grade_round5b.py           # regex grader on raw_supplementary.jsonl
python ../../scripts/grading/grade_r5_r6_newmodels.py   # judge sweep on raw_newmodels.jsonl
```

To regenerate the three-judge consensus and the canonical merge:

```bash
python ../../scripts/grading/add_three_judge_full.py
python ../../scripts/consolidate_canonical.py
```
