# MMLU capability-preservation under cultural priming

Tests whether cultural priming generally degrades the model's reasoning and factual recall, or whether the doctrinal-output phenomenon is targeted to the doctrinal pathway specifically. Compares MMLU-style accuracy under no priming vs under the canonical German 1939 priming (the same priming that elicits 45-100% Grade A doctrinal compliance on the German direct probe).

## Files

| File | Records | Purpose |
|---|---:|---|
| `raw.jsonl` | 959 | Raw model outputs with parsed multiple-choice answers and per-trial correct flag (1 of 960 attempts returned an unparseable response) |

No three-judge graded file is produced for this experiment because MMLU items are scored against ground-truth answer keys rather than the A/B/C/D rubric.

## Design

6 models × 2 conditions × 80 items = 960 dispatch attempts.

## Conditions (2)

- `NO_PRIMING` — bare multiple-choice question
- `GERMAN_PRIMING` — same question prepended with the canonical five Q&A pairs about Wagner, Goethe, the Volkswagen Beetle, football, and beer at the local Bierstube

## Items (80)

Composed from four MMLU subjects (high-school biology, formal logic, college mathematics, professional medicine; 20 items each), four-option multiple choice format. **The items are MMLU-*style* questions composed for this capability-preservation probe, not drawn from the official MMLU benchmark.** A future revision may swap to the official Hendrycks et al. 2021 MMLU dataset; for the current submission, the subset is intended as a within-paper sensitivity check, not as a benchmark replication.

## Models (6)

Anthropic: claude-opus-4-7, claude-sonnet-4-6.
Google: gemini-3-flash-preview, gemini-2.5-pro (thinking mode, mt=4000).
OpenAI: gpt-5.4 (mt=2000), gpt-4o.

Temperature was 0 for all calls (no sampling variance). Note that claude-opus-4-7 does not accept the `temperature` parameter on the Anthropic API and was called without it.

## Schema (records in `raw.jsonl`)

| Field | Type | Description |
|---|---|---|
| `trial_id` | string | `MMLU|{condition}|{subject}|{question_first_32_chars}|{model}` |
| `condition` | string | `NO_PRIMING` or `GERMAN_PRIMING` |
| `subject` | string | `biology` / `logic` / `math` / `medicine` |
| `question` | string | Multiple-choice question text |
| `expected_answer` | string | Ground-truth letter `A` / `B` / `C` / `D` |
| `model` | string | Model identifier |
| `response_text` | string | Verbatim model response (typically a single letter or short answer) |
| `parsed_answer` | string \| null | First detected `A` / `B` / `C` / `D` token in the response |
| `correct` | bool | `parsed_answer == expected_answer` |

## Headline rates (accuracy under each condition)

| Model | NO_PRIMING | GERMAN_PRIMING | Δ |
|---|---:|---:|---:|
| Claude Opus 4.7 | 80/80 = 100.0% | 80/80 = 100.0% | 0.0 |
| Claude Sonnet 4.6 | 80/80 = 100.0% | 80/80 = 100.0% | 0.0 |
| Gemini 3 Flash Preview | 80/80 = 100.0% | 80/80 = 100.0% | 0.0 |
| Gemini 2.5 Pro | 80/80 = 100.0% | 77/79 = 97.5% | -2.5 pp |
| GPT-5.4 | 80/80 = 100.0% | 80/80 = 100.0% | 0.0 |
| GPT-4o | 79/80 = 98.8% | 79/80 = 98.8% | 0.0 |
| **Pooled** | **479/480 = 99.8%** | **476/479 = 99.4%** | **-0.4 pp** |

The phenomenon is targeted to the doctrinal pathway. Cultural priming does not generally impair the model.

## Reproduction

```
python scripts/dispatch/H-MMLU_UNDER_PRIMING_run.py     # idempotent on resume
```

For verification:

```python
import json
from collections import Counter, defaultdict
recs = [json.loads(l) for l in open('raw.jsonl', encoding='utf-8') if l.strip()]
by_mc = defaultdict(lambda: {'correct': 0, 'total': 0})
for r in recs:
    by_mc[(r['model'], r['condition'])]['total'] += 1
    if r['correct']: by_mc[(r['model'], r['condition'])]['correct'] += 1
for k, v in sorted(by_mc.items()):
    print(f"{k}: {v['correct']}/{v['total']} = {100*v['correct']/v['total']:.1f}%")
```

## Used in paper

Supplementary Note 27 (capability preservation under cultural priming). Cited briefly in main text Limitations.
