# Excluded models — backup (2026-04-29)

This directory preserves raw and graded records for three OpenAI models that hit provider rate limits during early dispatch and ended up with reduced N. They are NOT part of the 14-model main lineup, NOT part of the canonical files, and are not the source of any number reported in the manuscript.

## Excluded models

- `gpt-5`
- `gpt-5-mini`
- `o3-mini`

## Why they are excluded

Each of the three models returned a substantially smaller record count than the lineup standard (typically <50% of the target N for their dispatched cells), driven entirely by 429 / context-budget errors during the round-3 cross-cultural matrix dispatch. We could not bring their N up to lineup parity within the data-collection window, so we removed them from the canonical merge and from the figure scripts. Their records are kept here so that the exclusion decision is auditable.

## Subdirectories

The layout mirrors the parent `data/` tree so reviewers can compare side-by-side what was kept versus what was dropped:

- `archive_chronological/` — round-by-round raw and graded files restricted to the three excluded models.
- `headline_matrix/` — per-round graded files restricted to the excluded models.
- `methodology_two_judge/` — judge logs that contained excluded-model trials (now superseded by the three-judge sweep on the canonical corpus).
- `counterfactual_unrelated_output/`, `multiturn_internal_incoherence/` — supplementary-model raw and graded files for the excluded models.

## Do not regrade or merge

The dispatch and consolidation scripts in `scripts/` filter to the 14-model main lineup. If you re-run them, the canonical files will not pull from this directory.
