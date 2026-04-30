# Canonical files — unified factorial dataset

This directory holds the unified factorial dataset for the cultural-priming doctrinal-compliance paper. The four JSONL files merge the per-round graded files in `data/{headline_matrix,mechanism_priority_instruction,counterfactual_unrelated_output,multiturn_internal_incoherence}/` into a uniform schema with three-judge consensus grades on every record.

Reanalysts should generally start here. The per-round graded files are still deposited (in their respective category directories) for full provenance and audit.

## Files

| File | Battery | Records | Layout |
|---|---|---:|---|
| `r3_cross_cultural_matrix.jsonl` | R3 cross-cultural matrix | 6,020 | 14 models × 17 priming cells × N=20 (4,760 primed) + 14 models × 9 control cells × N=10 (1,260 control) |
| `r4_priority_instruction.jsonl` | R4 priority instruction | 2,520 | 14 models × 4 cells × 3 sys-variants × N=15 |
| `r5_counterfactual.jsonl` | R5 counterfactual | 2,240 | 14 models × 4 cultures (3 primed + NODEMO) × 4 probes × N=10 (1,680 primed + 560 NODEMO) |
| `r6_multiturn.jsonl` | R6 multi-turn | 1,400 | 14 models × 5 cultures × 2 turn-2 types × N=10 |
| **Grand total** | | **12,180** | |

## Schema

See `SCHEMA.md` (project root) §Canonical files for the complete field specifications. All four files share the same common header (`trial_id`, `battery`, `model`, `rep`, `primed`, `polish_grade`, `judge1_grade`, `judge2_grade`, `judge3_grade`, `consensus_grade`, `final_grade`, `source`); the battery-specific fields differ:

- R3: `cell`, `response_text`, `user_msg`
- R4: `cell`, `sys_variant`, `response_text`, `user_msg`
- R5: `culture`, `probe_id`, `response_text`, `user_msg`
- R6: `culture`, `turn2_type`, `t1_user`, `t1_assistant`, `t2_user`, `t2_assistant`, `t1_grade`, `t2_affirms_ai`, `t2_post_hoc_persona`, `t2_breaks_out`, `t2_consistent_action`

## Three-judge consensus grades

Every canonical record has been graded by three independent LLM judges from three different vendors using the same A/B/C/D rubric in `prompts/JUDGE_PROMPT.txt`:

- Judge 1: Anthropic Claude Opus 4.6
- Judge 2: OpenAI GPT-4o
- Judge 3: Google Gemini-3-Flash-Preview

Consensus rule: 2-of-3 majority. If all three judges differ (1.3% of records), fall back to Judge 1 (Opus 4.6). The deterministic regex polish grader is computed alongside (`polish_grade`) but does not influence consensus; it is retained only for kappa-vs-judges reporting.

Pairwise Cohen's κ on 12,625 graded records:

| Pair | κ |
|---|---:|
| Opus 4.6 ↔ GPT-4o | 0.811 |
| Opus 4.6 ↔ Gemini-3-Flash | 0.809 |
| GPT-4o ↔ Gemini-3-Flash | 0.763 |
| Polish ↔ Opus 4.6 | 0.538 |
| Polish ↔ GPT-4o | 0.525 |
| Polish ↔ Gemini-3-Flash | 0.530 |

Agreement breakdown: 86.2% unanimous, 12.5% 2-of-3 majority, 1.3% all-three-differ.

The full per-record three-judge log is in `data/methodology_two_judge/three_judge_grades.jsonl` (folder name retained for backward compatibility).

## Coverage audit

- `coverage_audit.md` — per-cell × per-model record counts. Demonstrates full 14-model coverage at canonical N for R3, R4, R5, and R6.
- `per_model_summary.md` — per-model A/B/C/D breakdown for R3 priming cells and R4 priority-instruction cells.

The 14-model main lineup excludes three OpenAI models (gpt-5, gpt-5-mini, o3-mini) that hit provider rate limits during earlier rounds and have reduced N. Their records are preserved in `data/headline_matrix/graded_round3.jsonl` for transparency but are not part of the canonical files or the headline rates.

## Regenerating

```bash
python scripts/consolidate_canonical.py
```

This script reads the per-round graded files in `data/{headline_matrix,mechanism_priority_instruction,counterfactual_unrelated_output,multiturn_internal_incoherence}/`, applies the 2-of-3 consensus rule, writes the four canonical JSONLs, and refreshes `coverage_audit.md` and `per_model_summary.md`.

## How the master numbers are derived

`MASTER_NUMBERS.json` and `MASTER_NUMBERS_DIGEST.md` (at project root) are auto-generated from these canonical files and are the single source of truth for all numbers reported in the manuscript and supplementary notes.
