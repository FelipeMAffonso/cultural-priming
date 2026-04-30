# Scripts directory

End-to-end pipeline. See `../REPRODUCIBILITY.md` for the step-by-step reproduction recipe and `../DATA_README.md` for the experiment-category layout.

The pipeline has three stages: **dispatch** (model API calls → raw JSONLs), **grading** (regex transparency pass plus three-judge consensus), and **analysis** (figure generation + audits). The reported per-trial grade for every paper number is the `consensus_grade` from the three-judge sweep; the regex grader output is preserved as `polish_grade` for transparency only.

## dispatch/ — model API dispatch

Each `H-{ROUND,GEMINI*,GPT55,FULLFACTORIAL,BOUNDARY,CONFEDFILL}_run.py` script builds a list of `(model × cell × rep)` jobs and dispatches them in parallel via the relevant provider client. All scripts skip already-completed `trial_id`s in the output JSONL for resumability.

| Script | Battery | Models | Output |
|---|---|---|---|
| `H-ROUND1_run.py` | Calibration (R1) | 4 | `data/archive_chronological/round1/raw.jsonl` |
| `H-ROUND2_run.py` | Hitler+Soviet scale-up (R2) | 6 | `data/headline_matrix/raw_round2.jsonl` |
| `H-ROUND3_run.py` | Cross-cultural matrix (R3) | 16 dispatched (14 main lineup; 3 OpenAI excluded post-hoc, preserved at `data/_excluded_models_backup_2026-04-29/`) | `data/headline_matrix/raw_round3.jsonl` |
| `H-ROUND4_run.py` | Priority instruction (R4) | 8 | `data/mechanism_priority_instruction/raw.jsonl` |
| `H-ROUND4FILL_run.py` | R4 fill (3 additional models) | 3 | `data/mechanism_priority_instruction/raw_fill.jsonl` |
| `H-ROUND5_run.py` | Counterfactual (R5) | 6 | `data/counterfactual_unrelated_output/raw_main.jsonl` |
| `H-ROUND5b_run.py` | R5 fill (5 supplementary models) | 5 | `data/counterfactual_unrelated_output/raw_supplementary.jsonl` |
| `H-ROUND6_run.py` | Multi-turn (R6) | 6 | `data/multiturn_internal_incoherence/raw_main.jsonl` |
| `H-ROUND6b_run.py` | R6 fill | 5 | `data/multiturn_internal_incoherence/raw_supplementary.jsonl` |
| `H-ROUND7_run.py` | Initial two-judge cross-validation | judges only | `data/methodology_two_judge/two_judge_grades.jsonl` (legacy; superseded by the three-judge sweep) |
| `H-ROUND8_run.py` | Gemini Pro probe (failed, R8) | 1 | `data/archive_chronological/round8/` (no records returned) |
| `H-ROUND9_run.py` | Format ablation (R9) | 8 | `data/mechanism_format_ablation/raw.jsonl` |
| `H-ROUND10_run.py` | Lexical-marker dose-response (R10) | 6 | `data/mechanism_dose_response/raw.jsonl` |
| `H-GPT55_run.py` | gpt-5.5 R3 + R4 | 1 | `data/{headline_matrix,mechanism_priority_instruction}/raw_gpt55.jsonl` |
| `H-GEMINI31PRO_run.py` | gemini-3.1-pro-preview R3 + R4 | 1 | `data/{headline_matrix,mechanism_priority_instruction}/raw_gemini31pro.jsonl` |
| `H-GEMINI25PRO_run.py` | gemini-2.5-pro R3 + R4 (thinking mode) | 1 | `data/{headline_matrix,mechanism_priority_instruction}/raw_gemini25pro.jsonl` |
| `H-FULLFACTORIAL_NEWMODELS.py` | R3 fill + R5 + R6 for 3 new models | 3 | `data/{headline_matrix,counterfactual_unrelated_output,multiturn_internal_incoherence}/raw_newmodels*.jsonl` |
| `H-CONFEDFILL_run.py` | claude-opus-4-5 × CONFEDERATE_LABOR fill | 1 | `data/headline_matrix/raw_opus45_confed_fill.jsonl` |
| `H-BOUNDARY_TESTS_run.py` | Boundary tests, pilot | 10 | `data/boundary_tests/raw.jsonl` |
| `H-BOUNDARY_SCALED_run.py` | Boundary tests, scaled corpus | 14 | `data/boundary_tests/raw_scaled.jsonl` |

Shared modules:
- `_parallel.py` — `ThreadPoolExecutor`-based parallel dispatch helper used across rounds.
- `_betley_judge.py` — single-judge helper from the Betley replication; superseded by the H-ROUND7 two-judge sweep and then by the three-judge protocol.

## grading/ — A/B/C/D rubric assignment

Two layers run on every record:

1. **Regex transparency grader** (`grade_round{2,3,4,5,5b,6}.py`, `grade_r9_r10.py`, `grade_boundary_pilot.py`, `grade_boundary_scaled.py`). Deterministic regex pattern matching against a fixed lexicon. Returns `(polish_grade A/B/C/D, polish_reason)`. Output is transparency metadata only; never the source of any reported number.
2. **Three-judge consensus** (`add_three_judge_full.py`, `three_judge_r9_r10.py`, `three_judge_boundary.py`). Three independent LLM judges (Anthropic Opus 4.6, OpenAI GPT-4o, Google Gemini-3-Flash-Preview) each grade every record at temperature=0 using the prompt at `prompts/JUDGE_PROMPT.txt`. Each record receives `judge1_grade`, `judge2_grade`, `judge3_grade`, and `consensus_grade` (2-of-3 majority; falls back to Judge 1 when all three differ). The `consensus_grade` is the load-bearing label for every paper number.

| Script | What it grades | Output |
|---|---|---|
| `grade_round2.py` | R2 records (Hitler+Soviet scale-up) | `data/archive_chronological/round2/grading/graded.jsonl` |
| `grade_round3.py` | R3 records (cross-cultural matrix) | `data/headline_matrix/graded_round3.jsonl` |
| `grade_round4.py` | R4 records (priority instruction) | `data/mechanism_priority_instruction/graded.jsonl` |
| `grade_round4_fill.py` | R4 fill (3 additional models) | appended to `data/mechanism_priority_instruction/graded.jsonl` |
| `grade_round5.py` | R5 records (counterfactual main) | `data/counterfactual_unrelated_output/graded_main.jsonl` |
| `grade_round5b.py` | R5b fill | `data/counterfactual_unrelated_output/graded_supplementary.jsonl` |
| `grade_round6.py` | R6 records (multi-turn T1+T2 codings) | `data/multiturn_internal_incoherence/graded.jsonl` |
| `regrade_r6_newmodels.py` | R6 new-model fill | `data/multiturn_internal_incoherence/graded_newmodels.jsonl` |
| `grade_r9_r10.py` | R9 (format ablation) and R10 (dose response) regex grades | `data/mechanism_format_ablation/graded.jsonl`, `data/mechanism_dose_response/graded.jsonl` |
| `grade_boundary_pilot.py` | Boundary tests, 200-trial pilot | `data/boundary_tests/graded_pilot.jsonl` |
| `grade_boundary_scaled.py` | Boundary tests, 1,400-trial scaled | `data/boundary_tests/graded_scaled.jsonl` |
| `grade_gpt55_twojudge.py` | GPT-5.5 R3+R4 with 2 LLM judges (intermediate) | `data/{headline_matrix,mechanism_priority_instruction}/graded_gpt55.jsonl` |
| `grade_r5_r6_newmodels.py` | R5+R6 for all 3 new models with 2 LLM judges (intermediate) | `data/{counterfactual_unrelated_output,multiturn_internal_incoherence}/graded_newmodels.jsonl` |
| `add_three_judge_full.py` | Adds Judge 3 (Gemini-3-Flash) and `consensus_grade` to every canonical record | `data/methodology_two_judge/three_judge_grades.jsonl` |
| `three_judge_r9_r10.py` | Three-judge sweep on R9 and R10 | `data/mechanism_format_ablation/graded_threejudge.jsonl`, `data/mechanism_dose_response/graded_threejudge.jsonl` |
| `three_judge_boundary.py` | Three-judge sweep on the boundary-tests scaled corpus | `data/boundary_tests/graded_scaled_threejudge.jsonl` (and pilot) |
| `compute_kappa.py` | Pairwise Cohen's κ across the three judges and the regex grader | `data/methodology_two_judge/kappa_summary.txt` |

The judge prompt is canonicalised at `prompts/JUDGE_PROMPT.txt` and is identical across all batteries.

## analysis/ — figure generation

| Script | Reads | Writes |
|---|---|---|
| `figure1_cross_cultural_matrix.py` | `data/canonical/r3_cross_cultural_matrix.jsonl` (with fallbacks to per-round graded files) | `manuscript/figures/fig1_design_heatmap.{pdf,png}` |
| `figure3_negative_controls.py` | `data/canonical/r3_cross_cultural_matrix.jsonl` | `manuscript/figures/fig3_boundary_conditions.{pdf,png}` |
| `figure4_counterfactual.py` | `data/canonical/r5_counterfactual.jsonl` (with fallbacks to per-round files) | `manuscript/figures/fig4_counterfactual.{pdf,png}` |
| `figure4_cross_generation.py` | `data/canonical/r3_cross_cultural_matrix.jsonl` filtered to Opus 4.5/4.6/4.7 | `manuscript/figures/fig2_cross_generation.{pdf,png}` |
| `figure5_multiturn.py` | `data/canonical/r6_multiturn.jsonl` | `manuscript/figures/fig5_multiturn_diagnostic.{pdf,png}` |
| `figure6_priority_instruction.py` | `data/canonical/r4_priority_instruction.jsonl` | `manuscript/figures/fig6_priority_instruction.{pdf,png}` |

Figure 1 itself (the Cloud-style portrait HTML) is built by `manuscript/figures/build_fig1.sh` (Chrome headless → PDF → PyMuPDF crop) and is independent of these analysis scripts.

## Top-level scripts

- `consolidate_canonical.py` — merges all per-round graded files plus the three-judge log into `data/canonical/r{3,4,5,6}_*.jsonl` and refreshes `coverage_audit.md` and `per_model_summary.md`.
- `compute_master_numbers.py` — reads the canonical files and writes `MASTER_NUMBERS.json` plus `MASTER_NUMBERS_DIGEST.md` at the project root.
- `full_data_audit.py` — re-derives every percentage from canonical data and prints any discrepancies versus the manuscript text.
- `verify_all_numbers.py` — asserts every number in `manuscript/main.md` and `manuscript/supplementary.md` is recoverable from the canonical files.
- `audit_2026_04_28.py` — older audit snapshot, retained for provenance.
- `regenerate_si_tables.py` — rebuilds the per-cell × per-model tables for the supplementary notes from canonical data.
- `per_model_per_cell_matrix.py` — produces the per-model per-cell coverage matrix used by the coverage audit.
- `_check_cites.py` — manual citation cross-check (refman backup).
- `coverage_audit.txt` — sample output snapshot from `per_model_per_cell_matrix.py`, kept for provenance.

## Conventions

- All scripts use forward-slash paths and assume execution from the project root unless otherwise noted in the docstring.
- `.env` lives in `scripts/.env` (not committed). All scripts call `load_dotenv(SCRIPT_DIR / ".env")` or fall back to a parent-project `.env`.
- Output JSONLs are append-mode unless explicitly rewritten. Resumability is via skipping completed `trial_id`s.
