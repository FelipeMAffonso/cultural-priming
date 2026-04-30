# Grading scripts

Two grading layers: (a) a deterministic regex-based grader (legacy, retained as transparency metadata only — not used for any reported number), and (b) the **three-judge cross-vendor LLM grading protocol** (Anthropic Opus 4.6 + OpenAI GPT-4o + Google Gemini-3-Flash-Preview), whose 2-of-3 majority consensus is the source of every reported headline rate in the paper.

## Three-judge LLM grading (the source of every reported number)

| Script | Battery | Input | Output |
|---|---|---|---|
| `add_three_judge_full.py` | Canonical R3 + R4 + R5 + R6 | `data/canonical/r{3,4,5,6}_*.jsonl` | adds `judge1_grade`, `judge2_grade`, `judge3_grade`, `consensus_grade`, `final_grade` in-place |
| `three_judge_boundary.py` | Boundary tests (1,400 scaled trials) | `data/boundary_tests/graded_scaled.jsonl` | `data/boundary_tests/graded_scaled_threejudge.jsonl` |
| `grade_boundary_pilot.py` | Boundary tests (200 pilot trials) | `data/boundary_tests/raw.jsonl` | `data/boundary_tests/graded_pilot_threejudge.jsonl` |
| `three_judge_r9_r10.py` | Format ablation (R9) + dose-response (R10) | `data/mechanism_format_ablation/raw.jsonl`, `data/mechanism_dose_response/raw.jsonl` | `graded_threejudge.jsonl` in each |
| `compute_kappa.py` | Pairwise Cohen's κ + agreement breakdown | any three-judge JSONL | stdout summary |

The judge prompt is at `prompts/JUDGE_PROMPT.txt`. Each judge is called at temperature 0 with max_tokens=80.

## Round-by-round regex grading (legacy / transparency only)

These scripts produce a `polish_grade` field that is retained in the per-record metadata as an audit trail. They are NOT used to compute any reported number in the paper. The reported per-trial grade is the three-judge consensus.

| Script | Battery | Output |
|---|---|---|
| `grade_round2.py` | R2 cross-cultural v1 | `data/headline_matrix/graded_round2.jsonl` |
| `grade_round3.py` | R3 cross-cultural at scale | `data/headline_matrix/graded_round3.jsonl` |
| `grade_round4.py` / `grade_round4_fill.py` | R4 priority instruction | `data/mechanism_priority_instruction/graded.jsonl` |
| `grade_round5.py` / `grade_round5b.py` | R5 counterfactual | `data/counterfactual_unrelated_output/graded_*.jsonl` |
| `grade_round6.py` / `regrade_r6_newmodels.py` | R6 multi-turn | `data/multiturn_internal_incoherence/graded.jsonl` |
| `grade_r5_r6_newmodels.py` | New-model fills for R5 + R6 | written into the respective category folders |
| `grade_r9_r10.py` | R9 format ablation + R10 dose response | `graded.jsonl` in each (legacy regex) |
| `grade_boundary_scaled.py` | Boundary scaled (regex only) | `data/boundary_tests/graded_scaled.jsonl` |
| `grade_gpt55_twojudge.py` | gpt-5.5 two-judge legacy | `data/headline_matrix/graded_gpt55.jsonl` |

## Verification

`compute_kappa.py` produces pairwise κ values for any three-judge JSONL. Canonical 12,180-record κ: 0.811 / 0.809 / 0.763. Boundary 1,400-record κ: 0.625 / 0.567 / 0.614 (skewed Grade-D distribution). R9 360-record κ: 0.832 / 0.812 / 0.766. R10 1,080-record κ: 0.773 / 0.826 / 0.829.

## Rubric

The strict A/B/C/D rubric applied by every judge is in §SN 3 of `manuscript/supplementary.md` and reproduced verbatim in `prompts/JUDGE_PROMPT.txt`.
