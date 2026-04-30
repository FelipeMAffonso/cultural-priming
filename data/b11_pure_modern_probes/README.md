# B11 — Pure-modern user queries on the frontier-model lineup

Deployment-realistic-probe extension on the **frontier-model lineup** (9 models). Used in main §6 and SN 28.

## What this battery tests

Whether the cultural-priming-induced doctrinal-compliance phenomenon holds when the user message itself contains no period-specific cultural vocabulary and no named historical actors. The user message is exactly what a 2026 user would type into a chat assistant; only the cultural-priming demonstrations are pre-pended in the PRIMED condition.

## Files

| File | Description |
|---|---|
| `raw.jsonl` | 12,417 dispatched records, full raw model responses, trial_id provenance |
| `graded_threejudge.jsonl` | Same 12,417 records with three independent judge grades (Opus 4.6 + GPT-4o + Gemini-3-Flash) and 2-of-3 majority `consensus_grade` |
| `graded_threejudge.jsonl.bak_dupes` | Backup of pre-dedup file (418 dup trial_ids removed; first occurrence kept) |
| `SUMMARY.md` | Per-cell × per-model rate summary, doctrinal-target table, headline rates |
| `judge_stratified_kappa.md` | Per-judge marginal Grade-A rates stratified by dispatched-model vendor (addresses self-vendor judge bias) |

## Schema (per record)

```
trial_id          B11|{cell_id}|{condition}|{model}|r{rep}
cell_id           One of 35 cells (see DATA_README §10 for full list)
group             NEWBORN_DISABILITY | DAUGHTER_13 | CHEMIST_DEFENCE | (singleton for cell-specific probes)
culture           Cultural label (e.g. Viking-Norse, Republican-Roman, Imperial-Japan-WW2)
condition         PRIMED | CONTROL
model             One of 9 frontier models (see Models below)
rep               Integer rep index, 0..19
user_msg          Full user message (priming demos in PRIMED + the doctrinal probe; probe alone in CONTROL)
probe_text        The deployment-realistic doctrinal probe (last line of user_msg)
response_text     Verbatim model response
judge1_grade      Anthropic Opus 4.6 grade (A | B | C | D)
judge1_reason     One-phrase reason
judge2_grade      OpenAI GPT-4o grade
judge2_reason
judge3_grade      Google Gemini-3-Flash-Preview grade
judge3_reason
consensus_grade   2-of-3 majority (fallback to Judge 1 on three-way disagreement)
final_grade       Synonym of consensus_grade (kept for downstream-script compatibility)
ts                Dispatch timestamp (ISO-8601)
```

## Models (9 frontier)

- **Anthropic** — claude-opus-4-7, claude-opus-4-6, claude-sonnet-4-6
- **OpenAI** — gpt-5.5, gpt-5.4, gpt-4o
- **Google** — gemini-2.5-pro (thinking, mt=4000), gemini-3-flash-preview, gemini-3.1-pro-preview

## Headline rates (re-derivable from `graded_threejudge.jsonl`)

| Quantity | Value |
|---|---|
| Total graded records | 12,417 |
| Pooled CONTROL Grade-A | 3 / 6,237 = 0.05% (RAF_ACTIVIST × Gemini, 2-of-3 split) |
| Pooled PRIMED Grade-A | (computed jointly with B12 — see DATA_README §10 for the 20,637-record pooled rates) |
| Pairwise Cohen's κ | 0.78–0.87 across the three judge pairs |
| Unanimous 3-of-3 agreement | 94.85% |

Combined-with-B12 numbers (the 20,637-record corpus reported throughout main §6 and SN 28):

| Quantity | Value |
|---|---|
| Pooled CONTROL Grade-A | 3 / 10,380 = 0.03% |
| Pooled PRIMED Grade-A | 827 / 10,257 = 8.06% |
| Per-vendor pooled (PRIMED) | Google 25.5% (713/2,797), Anthropic 2.1% (83/3,960), OpenAI 0.9% (31/3,500) |

## Reproducibility

- **Dispatch script**: `scripts/dispatch/H-B11_PURE_MODERN_PROBES.py` — uses an alt Anthropic API key (`ANTHROPIC_API_KEY_B11`) for dispatched models.
- **Grading script**: `scripts/grading/grade_b11_threejudge.py` — uses the canonical `ANTHROPIC_API_KEY` for the Opus-4.6 judge.
- **Verification script**: `scripts/verify/verify_sn28_numbers.py` — recomputes every pooled, per-vendor, per-cell, and per-(cell × model) rate from raw JSONL and compares against manuscript text.
- The full 35-row probe inventory and per-cell × per-model heatmap are at `SUMMARY.md`.

## Notes on dispatch deficit

Design max was 12,600 trials (35 cells × 9 models × 20 reps × 2 conditions = 12,600). Actual dispatched = 12,417, deficit = 183 (1.5%) primarily from Gemini safety-block empty responses on the most-loaded probes plus a small number of Anthropic and OpenAI dropouts that did not retry-recover. Per-cell deficit is itemised in `SUMMARY.md`. The deficit is documented in SN 28.10.

## Cross-references

- Main paper §6 — high-level findings.
- SN 28 — full design, rates, verbatims, judge stratification, probe-cue audit.
- Figure 1 bottom row — six representative actionable verbatims drawn from this battery and B12.
- `DATA_README.md` §10 — combined B11+B12 documentation.
