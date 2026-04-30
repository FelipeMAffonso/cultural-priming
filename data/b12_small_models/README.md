# B12 — Pure-modern user queries on the deployment-tier model lineup

Deployment-realistic-probe extension on the **deployment-tier model lineup** (6 smaller / older / cheaper models). Same probe set and dispatch protocol as B11. Used in main §6 and SN 28.

## What this battery tests

Whether the cultural-priming-induced doctrinal-compliance phenomenon also fires on the smaller and older models that vendors deploy at lower price points (Haiku, Sonnet 4.5, Opus 4.5, GPT-5.4-Mini, GPT-4o-Mini, Gemini 2.5 Flash). Test of the pretraining-knowledge-capacity precondition: smaller models may either (a) lack the densely-encoded doctrinal targets that frontier models retrieve, or (b) have stricter post-training that catches the cultural-routing pathway, or both.

## Files

| File | Description |
|---|---|
| `raw.jsonl` | 8,220 dispatched records, full raw model responses, trial_id provenance |
| `graded_threejudge.jsonl` | Same 8,220 records with three independent judge grades and 2-of-3 majority `consensus_grade` |

## Schema

Identical to B11 (see `data/b11_pure_modern_probes/README.md`). The `trial_id` prefix is `B12|` instead of `B11|`.

## Models (6 deployment-tier)

- **Anthropic** — claude-opus-4-5, claude-sonnet-4-5, claude-haiku-4-5
- **OpenAI** — gpt-5.4-mini, gpt-4o-mini
- **Google** — gemini-2.5-flash

## Headline rates (re-derivable from `graded_threejudge.jsonl`)

Per-model PRIMED Grade-A:

| Model | Vendor | PRIMED Grade-A |
|---|---|---:|
| gemini-2.5-flash | Google | 53/700 = 7.6% |
| claude-sonnet-4-5 | Anthropic | 15/660 = 2.3% |
| gpt-5.4-mini | OpenAI | 7/700 = 1.0% |
| claude-opus-4-5 | Anthropic | 0/640 = 0.0% |
| claude-haiku-4-5 | Anthropic | 0/700 = 0.0% |
| gpt-4o-mini | OpenAI | 0/700 = 0.0% |

Combined with B11, four of the 15 models in the union produce 0% Grade A across all 35 cells (Opus 4.6 + Opus 4.5 + Haiku 4.5 + GPT-4o + GPT-4o-Mini).

## Reproducibility

- **Dispatch script**: `scripts/dispatch/H-B12_SMALL_MODELS.py` — imports the cell list from B11 via `importlib.util` (avoids cell-list duplication).
- **Grading script**: same `scripts/grading/grade_b11_threejudge.py` (handles both B11 and B12 raw files).
- **Alt Anthropic API key**: `ANTHROPIC_API_KEY_B11` for dispatched models, canonical key for judges.

## Dispatch deficit

Design max was 8,400 trials (35 cells × 6 models × 20 reps × 2 conditions). Actual = 8,220, deficit = 180 (2.1%) primarily from Gemini-Flash safety blocks on a small subset of cells. Per-cell deficit itemised alongside B11 in `data/b11_pure_modern_probes/SUMMARY.md`.

## Cross-references

- Main paper §6 — combined-with-B11 high-level findings.
- SN 28 (especially SN 28.4 within-vendor heterogeneity) — per-model rates and the smaller-model dissociation.
- `DATA_README.md` §10 — combined B11+B12 documentation.
- `data/b11_pure_modern_probes/README.md` — full schema reference and shared SUMMARY.md.
