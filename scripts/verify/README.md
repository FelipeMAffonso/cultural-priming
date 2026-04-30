# Verification scripts

Scripts that recompute or audit numbers from the deposited graded JSONL files. None of these scripts make any new model API calls; they all read from local data and write either summary files or a console audit. Safe to run on a clean clone.

## Files

| Script | Purpose | Output |
|---|---|---|
| `verify_sn28_numbers.py` | Recomputes every pooled, per-vendor, per-cell, per-(cell × model), and per-judge rate for the deployment-realistic-probe extension (SN 27 in the manuscript; the script name retains the original SN-28 number from before the SN renumber). | stdout audit comparing computed values against the manuscript |
| `regenerate_b11_b12_summaries.py` | Regenerates `data/b11_pure_modern_probes/SUMMARY.md` and `data/b12_small_models/SUMMARY.md` from the live graded JSONL. Idempotent. | overwrites both SUMMARY.md files |
| `build_fig1_catalog.py` | Walks the B11+B12 graded JSONL, filters to unanimous 3/3 Grade A on the deployment-actionable cells, sorts by named-method shock score, and writes `manuscript/figures/fig1_verbatim_catalog.md`. Used to pick the six verbatims for Fig 2. | overwrites `fig1_verbatim_catalog.md` |
| `shift_figure_numbers.py` | One-shot script that shifted Fig 2..7 → Fig 3..8 in main.md and supplementary.md when Fig 1 was split. Idempotent — running again is a no-op (no Fig 2 to find). | rewrites main.md and supplementary.md |
| `renumber_sn_after_14.py` | One-shot script (paired with `fix_sn_renumber_recovery.py`) that performed the SN section renumbering after SN 14 (Manual validation) was dropped. Not idempotent; do not re-run. | one-shot |
| `fix_sn_renumber_recovery.py` | Recovery script for an earlier cascading renumber bug; resequenced section headers to SN 14..27 by file order and remapped inline references by context anchor. | one-shot |

## Typical reviewer workflow

```bash
# 1. Verify the deployment-realistic-probe (B11+B12) numbers
python scripts/verify/verify_sn28_numbers.py

# 2. Verify the canonical 12,180-record numbers
python scripts/compute_master_numbers.py
# Writes MASTER_NUMBERS.json + MASTER_NUMBERS_DIGEST.md to repo root

# 3. Verify pairwise Cohen's κ on the three-judge protocol
python scripts/grading/compute_kappa.py
```

These three commands cover every reported headline rate and every reported κ value.

## Cross-references

- `../../REPRODUCIBILITY.md` — full reproduction recipe (environment, dispatch, grading, figure rendering, manuscript build)
- `../../DATA_README.md` — per-experiment-category data documentation
- `../../SCHEMA.md` — per-record JSONL field specifications
