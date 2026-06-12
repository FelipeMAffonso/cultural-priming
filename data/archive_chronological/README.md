# Archive — Chronological Dispatch (Full Provenance)

This directory preserves the original chronological dispatch order (R1 through R10) of the cultural-priming paper. Reviewers do **not** need to read this; it exists for full provenance and replication transparency.

The same data is consolidated by experiment purpose at the parent `data/` level (`canonical/` for the four core batteries, plus `boundary_tests/`, `mechanism_format_ablation/`, `mechanism_dose_response/`, `temperature_sweep/`, `mmlu_capability/`, `methodology_two_judge/`, and the deployment-realistic extension at `b11_pure_modern_probes/` and `b12_small_models/`). Start any reanalysis from the unified canonical files in `data/canonical/`.

## Round-by-round inventory

| Round | Records | Description |
|---|---:|---|
| `round1/` | 180 | Initial calibration (4 cells × 3 models × N=5) |
| `round2/` | 1,685 | Cross-cultural matrix v1 (20 cells × 8 models) |
| `round3/` | 4,986 | Cross-cultural matrix at scale (17 main + 9 control × 14 models × N=20) |
| `round4/` | 1,440 | Priority-instruction mechanism |
| `round5/` | 960 | Counterfactual probes (6 models) |
| `round5b/` | 916 | Counterfactual on supplementary models (9 models) |
| `round6/` | 360 | Multi-turn diagnostic (6 models × 3 cultures) |
| `round6b/` | 792 | Multi-turn supplementary models + new cultures |
| `round7/` | 3,125 | Initial two-judge cross-validation (superseded by the three-judge log in `data/methodology_two_judge/three_judge_grades.jsonl`) |
| `round9/` | 360 | Demonstrations-format ablation |
| `round10/` | 1,080 | Lexical-marker dose-response |

R8 attempted gemini-3-pro-preview but produced no usable records under the dispatch configuration (malformed format-continuation output at roughly 48 seconds per call); the round was retired, the model is excluded from the corpus, and gemini-3.1-pro-preview supersedes it in the main lineup (see manuscript SN 1 and SN 14).

## What is preserved per round

Each subdirectory contains:

- `raw.jsonl` — verbatim model outputs from that dispatch.
- `grading/graded.jsonl` (or `graded.jsonl` next to `raw.jsonl`) — per-round regex grader output. Transparency only; the reported per-trial grade is the `consensus_grade` on the canonical record.
- `grade*.py` and supporting analysis scripts — preserved in place so that reviewers can re-run the per-round regex grader against the per-round raw file.
- For R7, `compute_kappa.py` and `kappa_summary.txt` from the initial two-judge sweep.

## Sibling: `data/_excluded_models_backup_2026-04-29/`

Three OpenAI models (gpt-5, gpt-5-mini, o3-mini) hit provider rate limits during early dispatch and produced reduced N. They are not part of the 14-model main lineup and are excluded from the canonical files and from every reported headline rate. Their raw and graded records are preserved at `data/_excluded_models_backup_2026-04-29/` so the exclusion is auditable.

## Sibling: `data/_archive_2026-04-29/`

Holds residual top-level log files moved out of `data/` during the 2026-04-29 organisation pass. These logs are not load-bearing and are kept only for provenance.
