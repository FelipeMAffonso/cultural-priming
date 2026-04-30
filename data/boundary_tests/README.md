# Boundary tests — lexical-control extensions

This directory contains the 1,600-trial corpus that adjudicates whether cultural-framing scaffolding alone is sufficient to elicit doctrinal output, or whether the firing rate also depends on a pretraining-time co-occurrence between the demonstration tokens and the target doctrine.

The corpus has two parts:

| Part | Trials | Description |
|---|---:|---|
| Pilot (Hitler-only) | 200 | Two cells (PRENAZI_GERMAN, SYNTHETIC_CULTURE) × 10 models × N=10 on the greatest-man-alive probe |
| Scaled (5 doctrinal probes) | 1,400 | Five era-shifted cells + five synthetic-culture probes × 14 models × N=10 |

## Files

| File | Records | Purpose |
|---|---:|---|
| `raw.jsonl` | 200 | Raw pilot model outputs (response_text + metadata) |
| `raw_scaled.jsonl` | 1,400 | Raw scaled model outputs |
| `graded_pilot_threejudge.jsonl` | 200 | Three-judge cross-vendor consensus grades on the pilot |
| `graded_scaled_threejudge.jsonl` | 1,400 | Three-judge cross-vendor consensus grades on the scaled corpus |
| `graded_pilot.jsonl` | 200 | Legacy regex grader output, retained as transparency metadata only |
| `graded_scaled.jsonl` | 1,400 | Legacy regex grader output, retained as transparency metadata only |

The `graded_*_threejudge.jsonl` files are the source of every boundary number reported in the paper. The two `graded_*.jsonl` files (without the `_threejudge` suffix) carry only the deterministic regex grader output and are not referenced by the manuscript.

## Three-judge protocol

Each record was independently graded by three LLM judges drawn from three vendors using the rubric in `prompts/JUDGE_PROMPT.txt`:
- Judge 1: Anthropic Claude Opus 4.6
- Judge 2: OpenAI GPT-4o
- Judge 3: Google Gemini-3-Flash-Preview

Per-trial reported grade is the 2-of-3 majority consensus. When all three differ, fallback is Judge 1.

Pairwise Cohen's κ on the 1,400-record scaled corpus:
- Opus 4.6 ↔ GPT-4o: 0.625
- Opus 4.6 ↔ Gemini-3-Flash: 0.567
- GPT-4o ↔ Gemini-3-Flash: 0.614

Three-judge agreement: 87.6% unanimous, 11.4% 2-of-3 majority, 1.0% all-three-differ.

The κ values are lower than the canonical 0.81 / 0.81 / 0.76 because the boundary distribution is heavily skewed to Grade D (a refusal-bias floor depresses κ even when raw agreement is high).

## Schema (records in `graded_*_threejudge.jsonl`)

| Field | Type | Description |
|---|---|---|
| `trial_id` | string | Unique trial identifier `{cell}|{model}|r{rep}` |
| `cell` | string | Era-shifted cell (GERMAN_PRENAZI, RUSSIAN_TSARIST, JAPANESE_MEIJI_MODERN, ARAB_MODERN, CHINESE_MODERN) or synthetic probe (SYNTHETIC_GREATEST_MAN, SYNTHETIC_GREATEST_LEADER, SYNTHETIC_SAMURAI_HONOUR, SYNTHETIC_MORAL_GUIDE, SYNTHETIC_YOUNG_WOMAN) — pilot uses (PRENAZI_GERMAN, SYNTHETIC_CULTURE) |
| `mapped_cell` | string | Canonical R3 cell the regex grader maps the boundary cell to (HITLER_V1_WISH for greatest-man, SOVIET_V1_WISH for greatest-leader, EDO_JAPAN_HONOR for samurai, MEDIEVAL_ARAB_AUTHORITY for moral-guide, CONFUCIAN_OBEDIENCES for young-woman) |
| `model` | string | Model identifier (one of the 14-model main lineup; pilot uses 10 of the 14) |
| `rep` | int | Replicate index within (cell × model), 0..9 |
| `user_msg` | string | The user message sent (priming demos + probe) |
| `response_text` | string | Verbatim model response |
| `judge1_grade` | string | Anthropic Opus 4.6 grade A/B/C/D |
| `judge2_grade` | string | OpenAI GPT-4o grade A/B/C/D |
| `judge3_grade` | string | Google Gemini-3-Flash-Preview grade A/B/C/D |
| `consensus_grade` | string | 2-of-3 majority across the three judges |
| `final_grade` | string | Equal to `consensus_grade`. The grade reported in every paper number. |
| `polish_grade` | string | Legacy regex grader output, retained for transparency only |
| `polish_reason` | string | Legacy regex grader rationale, transparency only |
| `ts` | float | Unix timestamp of the model dispatch |

## Headline results (three-judge consensus)

**Era-shift extension (5 cells × 14 models × N=10 = 700 trials):**

| Cell | Probe | Grade A | N | % |
|---|---|---:|---:|---:|
| GERMAN_PRENAZI | greatest man alive | 0 | 140 | 0.0% |
| RUSSIAN_TSARIST | greatest leader | 1 | 140 | 0.7% |
| JAPANESE_MEIJI_MODERN | samurai whose lord disgraced | 41 | 140 | 29.3% |
| ARAB_MODERN | moral guide | 4 | 140 | 2.9% |
| CHINESE_MODERN | young woman aspirations | 0 | 140 | 0.0% |
| **Pooled** | | **46** | **700** | **6.6%** |

**Synthetic-culture extension (5 probes × 14 models × N=10 = 700 trials):**

| Probe | Grade A | N | % |
|---|---:|---:|---:|
| greatest-man | 0 | 140 | 0.0% |
| greatest-leader | 0 | 140 | 0.0% |
| samurai-honour | 20 | 140 | 14.3% |
| moral-guide | 0 | 140 | 0.0% |
| young-woman | 0 | 140 | 0.0% |
| **Pooled** | **20** | **700** | **2.9%** |

**Pilot (200 trials):** Both PRENAZI_GERMAN and SYNTHETIC_CULTURE return 0/100 three-judge Grade A.

## Dispatch and grading scripts

- Dispatch: `scripts/dispatch/H-BOUNDARY_TESTS_run.py` (pilot), `scripts/dispatch/H-BOUNDARY_SCALED_run.py` (scaled).
- Three-judge grading: `scripts/grading/three_judge_boundary.py` (scaled), `scripts/grading/grade_boundary_pilot.py` (pilot).

## Verification

To recompute the headline rates from the deposited graded JSONLs:

```python
import json
from collections import Counter
recs = [json.loads(l) for l in open('graded_scaled_threejudge.jsonl', encoding='utf-8') if l.strip()]
by_cell = Counter()
total = Counter()
for r in recs:
    total[r['cell']] += 1
    if r['consensus_grade'] == 'A':
        by_cell[r['cell']] += 1
for cell in sorted(total):
    n, a = total[cell], by_cell[cell]
    print(f"{cell:30s}  A={a}/{n}  ({100*a/n:.1f}%)")
```

## Used in paper

Section 3 (Lexical specificity is necessary for doctrinal output). Supplementary Note 24.
