# Dispatch scripts

Each `H-*_run.py` script dispatches one battery of model-API calls and writes the raw responses to a JSONL under `data/<category>/raw*.jsonl`.

## Round dispatch (the canonical 12,180-record corpus)

| Script | Battery | Output | Records |
|---|---|---|---:|
| `H-ROUND1_run.py` | Calibration (4 cells × 3 models × N=5) | `data/archive_chronological/round1/raw.jsonl` | 180 |
| `H-ROUND2_run.py` | Cross-cultural matrix v1 (8 models × 20 cells × N=20) | `data/archive_chronological/round2/raw.jsonl` | 1,685 |
| `H-ROUND3_run.py` | Cross-cultural matrix at scale (14 models × 26 cells) | `data/headline_matrix/raw_round3.jsonl` | 4,986 |
| `H-ROUND4_run.py` | Priority-instruction mechanism (14 models × 4 cells × 3 sys × N=15) | `data/mechanism_priority_instruction/raw.jsonl` | 2,520 |
| `H-ROUND4FILL_run.py` | R4 fill-in for missing cells | `data/mechanism_priority_instruction/raw_fill.jsonl` | varies |
| `H-ROUND5_run.py` | Counterfactual mundane probe (initial pass) | `data/counterfactual_unrelated_output/raw_main.jsonl` | varies |
| `H-ROUND5b_run.py` | Counterfactual fill-in on 9 missing models | `data/counterfactual_unrelated_output/raw_supplementary.jsonl` | varies |
| `H-ROUND6_run.py` | Multi-turn diagnostic (5 cultures × 14 models × 2 turn-2 × N=10) | `data/multiturn_internal_incoherence/raw_main.jsonl` | varies |
| `H-ROUND6b_run.py` | Multi-turn fill-in on 9 missing models | `data/multiturn_internal_incoherence/raw_supplementary.jsonl` | varies |
| `H-ROUND7_run.py` | Three-judge cross-vendor grading (no new dispatch; re-grades existing records) | `data/methodology_two_judge/three_judge_grades.jsonl` | 12,180 |
| `H-ROUND8_run.py` | Gemini 3 Pro probe (excluded from main analyses; format-continuation issue) | n/a | retired |
| `H-ROUND9_run.py` | Format ablation (Q&A vs paragraph vs diary) | `data/mechanism_format_ablation/raw.jsonl` | 360 |
| `H-ROUND10_run.py` | Lexical-marker dose-response (d=0..5) | `data/mechanism_dose_response/raw.jsonl` | 1,080 |

## Boundary tests (1,600-trial lexical-control extensions)

| Script | Description | Output |
|---|---|---|
| `H-BOUNDARY_TESTS_run.py` | 200-trial pilot (10 models × 2 cells × N=10) on Hitler-era greatest-man probe | `data/boundary_tests/raw.jsonl` |
| `H-BOUNDARY_SCALED_run.py` | 1,400-trial scaled (14 models × 5 era-shifted + 5 synthetic × N=10) | `data/boundary_tests/raw_scaled.jsonl` |

## New-model fill-ins

| Script | Models added |
|---|---|
| `H-FULLFACTORIAL_NEWMODELS.py` | gemini-2.5-flash, gemini-2.5-pro, gpt-4o (R3 + R5 + R6 fills) |
| `H-GPT55_run.py` | gpt-5.5 |
| `H-GEMINI31PRO_run.py` | gemini-3.1-pro-preview (thinking mode) |
| `H-GEMINI25PRO_run.py` | gemini-2.5-pro (thinking mode, mt=4000) |
| `H-CONFEDFILL_run.py` | claude-opus-4-5 × CONFEDERATE_LABOR fill |

## Helpers

- `_parallel.py` — `ThreadPoolExecutor` wrapper used across batteries; default 4-6 workers per provider
- `_betley_judge.py` — Betley-style auxiliary judge prompt (legacy; superseded by the canonical three-judge protocol in `prompts/JUDGE_PROMPT.txt`)

## Environment

All scripts load `.env` from the project root (or fall back to `../spec-resistance/config/.env`). Required keys: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`. Default sampling: temperature 1.0, max_tokens 400-600 depending on battery. Each output JSONL carries `trial_id` (deduplication key on resume), `model`, `response_text`, `user_msg`, `ts`.

## Cost / time

Total dispatch cost across all rounds is approximately USD 2,400. The largest single battery is R3 cross-cultural matrix (~4,760 trials across 14 models). Each round is idempotent on resume: if `raw.jsonl` already contains a `trial_id`, the dispatcher skips it.
