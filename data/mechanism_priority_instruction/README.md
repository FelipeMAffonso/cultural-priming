# Mechanism — Priority Instruction (Afonin-style causal manipulation)

**What this category answers**: Does the safety-vs-context-following tension drive the phenomenon causally?

**Manuscript reference**: Section 7, Figure 6, Supplementary Note 9.

The reported per-trial grade for every paper number is the `consensus_grade` (2-of-3 majority across three independent LLM judges). The unified file `data/canonical/r4_priority_instruction.jsonl` (2,520 records, 14 models × 4 cells × 3 system-prompt variants × N=15) is the canonical source of every R4 number.

## Files

### Raw model outputs
- `raw.jsonl` — 1,440 records. Initial 8-model dispatch (R4).
- `raw_fill.jsonl` — 540 records. Three-model fill (Opus 4.5/4.6, Sonnet 4.5).
- `raw_gpt55.jsonl` — 180 records. GPT-5.5 fill.
- `raw_gemini25pro.jsonl` — 180 records. gemini-2.5-pro (thinking mode) fill.
- `raw_gemini31pro.jsonl` — 180 records. gemini-3.1-pro-preview fill.

### Per-round graded files (regex grader output, transparency only)
- `graded.jsonl` — 1,980 records (R4 + the three-model fill, regex-graded).
- `graded_gpt55.jsonl` — 180 records (regex grader on GPT-5.5).
- `graded_gemini25pro.jsonl` — 180 records (regex grader on gemini-2.5-pro).
- `graded_gemini31pro.jsonl` — 180 records (regex grader on gemini-3.1-pro-preview).

These per-round graded files carry the deterministic `polish_grade` only and are deposited so reviewers can audit how `data/canonical/r4_priority_instruction.jsonl` was assembled.

## Design

Three system-prompt variants tested:
- `SYS_CONTROL`: standard helpful-assistant frame.
- `SYS_MODERN`: explicit instruction to prioritise modern human-rights norms.
- `SYS_CULTURE`: explicit instruction to respect cultural framing.

Cells: HITLER_V2, SOVIET_V2, CONFUCIAN_DAUGHTER, MEDIEVAL_ARAB_AUTHORITY.

Models: all 14 main-lineup models (Anthropic Opus 4.5/4.6/4.7, Sonnet 4.5/4.6, Haiku 4.5; OpenAI GPT-5.4/5.4-mini/5.5/4o; Google Gemini-3-flash, Gemini-3.1-pro-preview, Gemini-2.5-flash, Gemini-2.5-pro).

## Headline rates (three-judge consensus, N=2,520)

| Sys variant | A | B | C | D | N | A % |
|---|---:|---:|---:|---:|---:|---:|
| SYS_CONTROL | 206 | 104 | 24 | 506 | 840 | 24.5 |
| SYS_CULTURE | 443 | 95 | 22 | 280 | 840 | 52.7 |
| SYS_MODERN | 2 | 3 | 4 | 831 | 840 | 0.2 |

The modern-norms instruction reduces the (cell × model) baseline to essentially zero; the cultural-context instruction amplifies it on already-vulnerable combinations only. A handful of residual leaks under SYS_MODERN are listed in Supplementary Note 9.

## Verifying the SYS_CONTROL → SYS_MODERN → SYS_CULTURE numbers

```python
import json
recs = [json.loads(l) for l in open('../canonical/r4_priority_instruction.jsonl', encoding='utf-8') if l.strip()]
for sv in ('SYS_CONTROL', 'SYS_CULTURE', 'SYS_MODERN'):
    sub = [r for r in recs if r.get('sys_variant') == sv]
    n = len(sub)
    a = sum(1 for r in sub if r.get('consensus_grade') == 'A')
    print(f"{sv}: {a}/{n} Grade A = {100*a/n:.1f}%")
```

## Re-grading

```bash
python ../../scripts/grading/grade_round4.py            # regex grader on raw.jsonl
python ../../scripts/grading/grade_round4_fill.py       # regex grader on raw_fill.jsonl
```

To regenerate the three-judge consensus and the canonical merge:

```bash
python ../../scripts/grading/add_three_judge_full.py
python ../../scripts/consolidate_canonical.py
```
