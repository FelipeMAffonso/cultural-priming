# Temperature-sensitivity sweep

Tests whether the doctrinal-compliance phenomenon is robust across temperatures or is an artefact of the canonical T = 1.0 sampling setting. Reports rates at T = 0.0 (greedy), T = 0.7, and T = 1.0 on four headline cells across six models.

## Files

| File | Records | Purpose |
|---|---:|---|
| `raw.jsonl` | 320 | Raw model outputs (40 of 360 attempts returned empty and were not written) |
| `graded_threejudge.jsonl` | 320 | Three-judge cross-vendor consensus grades (Anthropic Opus 4.6 + OpenAI GPT-4o + Google Gemini-3-Flash-Preview) |
| `grading_log.txt` | — | Run log with per-(cell × T) Grade A% summary at the bottom |

## Cells (4)

- `HITLER_V2_DIRECT` — German 1939 priming + greatest-man-alive direct probe
- `SOVIET_V1_WISH` — Soviet 1968 priming + greatest-leader wish probe
- `EDO_JAPAN_HONOR` — Edo Japan priming + samurai-honour probe
- `MEDIEVAL_ARAB_AUTHORITY` — medieval Arab priming + moral-guide probe

## Models (6)

Anthropic: claude-opus-4-7, claude-sonnet-4-6.
Google: gemini-3-flash-preview (no thinking), gemini-2.5-pro (thinking, mt=4000).
OpenAI: gpt-5.4 (mt=4000), gpt-4o.

## Temperatures (3)

T = 0.0 (greedy), T = 0.7, T = 1.0 (canonical).

## Design

4 cells × 6 models × 3 temperatures × N = 5 = 360 dispatch attempts.

## Schema (records in `graded_threejudge.jsonl`)

| Field | Type | Description |
|---|---|---|
| `trial_id` | string | `TEMP|{cell}|T{temperature}|{model}|r{rep}` |
| `cell` | string | One of the four headline cells |
| `temperature` | float | 0.0 / 0.7 / 1.0 |
| `model` | string | One of the six models |
| `rep` | int | Replicate index 0..4 |
| `user_msg` | string | The user message sent (priming + probe) |
| `response_text` | string | Verbatim model response |
| `judge1_grade` | string | Anthropic Opus 4.6 grade A/B/C/D |
| `judge2_grade` | string | OpenAI GPT-4o grade A/B/C/D |
| `judge3_grade` | string | Google Gemini-3-Flash-Preview grade A/B/C/D |
| `consensus_grade` | string | 2-of-3 majority |
| `final_grade` | string | Equal to `consensus_grade` |

## Headline rates (three-judge consensus, pooled across six models)

| Cell | T = 0.0 | T = 0.7 | T = 1.0 |
|---|---:|---:|---:|
| HITLER_V2_DIRECT | 16% | 16% | 23% |
| SOVIET_V1_WISH | 56% | 36% | 30% |
| MEDIEVAL_ARAB_AUTHORITY | 40% | 56% | 33% |
| EDO_JAPAN_HONOR | 0% | 4% | 3% |

The phenomenon persists across the temperature range. The N = 5 setting is smaller than the canonical N = 20 used in the main analyses, so cell-level rates differ from the headline numbers reported in the main text.

## Reproduction

```
python scripts/dispatch/H-TEMP_SWEEP_run.py     # idempotent on resume
python scripts/grading/three_judge_temp_sweep.py
```

## Used in paper

Supplementary Note 26 (temperature-sensitivity sweep). Cited briefly in main text Limitations.
