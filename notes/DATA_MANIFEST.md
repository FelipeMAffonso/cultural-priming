# DATA_MANIFEST.md

Single source of truth for all experimental data, grading status, and pending validation work for the cultural-priming paper.

Updated: 2026-04-28.

---

## Round-by-round inventory

| Round | Records | Cells | Models | Polish status | Purpose |
|---|---:|---:|---:|---|---|
| **R1** | 180 | 4 | 3 | ✅ done (`ROUND1_POLISH_REPORT.md`) | Calibration |
| **R2** | 1685 | 20 | 8 | ✅ done (`ROUND2_POLISH_REPORT.md`) | Cross-cultural matrix v1 |
| **R3** | 4986 | 26 (17 main + 9 control) | 14 | ⏳ in progress | Cross-cultural matrix at N=20 with 14-model lineup |
| **R4** | 1440 | 4 cells × 3 sys variants | 8 | ✅ done (`ROUND4_POLISH_REPORT.md`) | Priority-instruction mechanism |
| **R5** | 960 (target) / ~830 actual so far | 4 mundane probes × 4 conditions (3 cultures + control) | 6 | ⏳ dispatching | Counterfactual probes |
| **R6** | 360 (target) / ~280 actual so far | 3 cultures × 2 turn-2 variants | 6 | ⏳ dispatching | Multi-turn identity + action persistence |

**Plus prior batteries** (in `H-TLEAK-*_data/raw.jsonl`):
- H-TLEAK-CLEAN-BATTERY: 7813 records, 5 models — Round-1-era exploration
- H-TLEAK-BEHAVIOR-BATTERY: 3780 records, 7 models — behavior probes
- H-TLEAK-DEPLOY-BATTERY: 1960 records, 7 models, 6 cultures — deployment scenarios
- H-TLEAK-BETLEY-REPL: 4705 records, 7 models — Betley-style replication

**Grand total: ~27,899 records** across all rounds and prior batteries.

---

## Cell × Model coverage matrix (paper-relevant rounds: R2, R3, R4, R5, R6)

### Core "Tier-1" cells (the headlines)

| Cell | R2 | R3 | R4 | R5 | R6 |
|---|---|---|---|---|---|
| HITLER_V1_WISH | 7m × N=20 | 14m × N=20 | — | — | 6m × N=10 |
| HITLER_V2_DIRECT | 7m × N=20 | 14m × N=20 | 8m × N=15 (3 sys variants) | — | — |
| SOVIET_V1_WISH | 7m × N=20 | 14m × N=20 | — | — | 6m × N=10 |
| SOVIET_V2_DIRECT | 7m × N=20 | 14m × N=20 | 8m × N=15 | — | — |
| CONFUCIAN_OBEDIENCES | 7m × N=10 | 14m × N=20 | — | — | — |
| CONFUCIAN_DAUGHTER | 7m × N=10 | 14m × N=20 | 8m × N=15 | — | 6m × N=10 |
| MEDIEVAL_ARAB_AUTHORITY | 7m × N=10 | 14m × N=20 | 8m × N=15 | — | — |
| MEDIEVAL_ARAB_LEADER | 7m × N=10 | 14m × N=20 | — | — | — |
| EDO_JAPAN_HONOR | 7m × N=10 | 14m × N=20 | — | — | — |
| APARTHEID_SA_LEADER (neg control) | 7m × N=10 | 14m × N=20 | — | — | — |

### Tier-2 supporting cells

| Cell | R2 | R3 |
|---|---|---|
| CONFUCIAN_FORENSIC | — | 14m × N=20 |
| EDO_JAPAN_SAMURAI | 7m × N=10 | 14m × N=20 |
| VICTORIAN_LEADER | 7m × N=10 | 14m × N=20 |
| AZTEC_RULER | 7m × N=10 | 14m × N=20 |
| CONFEDERATE_LABOR | 7m × N=10 | 14m × N=20 |
| INDIAN_CASTE_MARRIAGE | — | 14m × N=20 (rewrite null) |
| INDIAN_DHARMA_DAUGHTER | — | 14m × N=20 (rewrite null) |
| CONFEDERATE_LEADER | 7m × N=10 | — (dropped) |
| CONFEDERATE_LEADER_DIRECT | 7m × N=10 | — (dropped) |

### Round 5/6 model coverage gap

R5 + R6 only have 6 models. Full lineup is 15. Missing from R5/R6:
- Anthropic: Opus 4.6, Opus 4.5, Haiku 4.5
- OpenAI: GPT-5, GPT-5-mini, GPT-5.4-mini, o3-mini
- Google: Gemini-2.5-pro, Gemini-2.5-flash

**Action**: dispatch R5b + R6b after R5/R6 finish (~1100 + ~540 = 1640 calls).

---

## Grading status

| Round | LLM judge 1 | LLM judge 2 | Manual labels |
|---|---|---|---|
| R1 | ✅ Sonnet (polish agent) | ❌ pending | ❌ pending |
| R2 | ✅ Sonnet (polish agent) | ❌ pending | ❌ pending |
| R3 | ⏳ in progress | ❌ pending | ❌ pending |
| R4 | ✅ Sonnet (polish agent) | ❌ pending | ❌ pending |
| R5 | ❌ not yet | ❌ pending | ❌ pending |
| R6 | ❌ not yet | ❌ pending | ❌ pending |

**Pending two-judge cross-validation (R7)**: re-grade R2 + R3 + R4 with second LLM judge (e.g., GPT-4o or Claude Opus 4.6). Compute Cohen's kappa per Afonin §Limitations. Target ≥0.7.

**Pending manual validation**: 200 outputs randomly sampled across cells, hand-labeled by Felipe + 1 RA. Report agreement %, kappa.

---

## Eventual GitHub repo structure (post-manuscript)

Mirroring Betley `emergent-misalignment/emergent-misalignment` style:

```
cultural-priming-misalignment/
├── README.md                          # Paper overview, figure links, quick-start
├── LICENSE
├── CITATION.cff
├── requirements.txt
├── data/
│   ├── raw/                           # All raw.jsonl (one per round)
│   │   ├── round1.jsonl
│   │   ├── round2.jsonl
│   │   ├── round3.jsonl
│   │   ├── round4_priority_instruction.jsonl
│   │   ├── round5_counterfactual.jsonl
│   │   └── round6_multiturn.jsonl
│   ├── graded/                        # Polish-agent graded JSONL with A/B/C/D
│   │   ├── round1_graded.jsonl
│   │   └── ...
│   └── prompts/                       # All prompts in structured form
│       ├── demos.json                 # Cultural demo Q&A pairs
│       ├── probes.json                # All probes per cell
│       └── system_prompts.json
├── evaluation/                        # Grading code
│   ├── grade.py                       # Strict A/B/C/D grader
│   ├── two_judge.py                   # Cross-judge validation
│   └── manual_validation.py           # Manual-vs-judge kappa
├── analysis/                          # Figure-generating scripts
│   ├── figure1_cross_cultural_matrix.py
│   ├── figure2_cross_generation_anthropic.py
│   ├── figure3_safety_dissociation.py
│   ├── figure4_priority_instruction_mechanism.py
│   ├── figure5_negative_controls.py
│   └── figure6_multiturn_internal_incoherence.py
├── results/                           # Output CSVs
│   ├── per_cell_grade_A_rates.csv
│   ├── per_model_totals.csv
│   ├── primed_vs_control_deltas.csv
│   ├── cross_judge_kappa.csv
│   └── manual_validation_kappa.csv
├── reports/                           # Polish-agent reports (preserved)
│   ├── ROUND1_POLISH_REPORT.md
│   ├── ROUND2_POLISH_REPORT.md
│   ├── ROUND3_POLISH_REPORT.md
│   ├── ROUND4_POLISH_REPORT.md
│   ├── ROUND5_POLISH_REPORT.md
│   └── ROUND6_POLISH_REPORT.md
└── reproduce/                         # Reproducibility scripts
    ├── 01_run_round1.py
    ├── 02_run_round2.py
    ├── ...
    └── 99_generate_figures.sh
```

**Key principles** (per Betley):
- All prompts in structured JSON, not just code
- All raw outputs preserved with trial_id for replication
- Single command runs each figure
- README explains every directory
- LICENSE permissive (MIT or CC-BY)

---

## Open tasks (organized for completion)

### Blocking for paper headlines:
1. ⏳ **R3 polish** — running, expected ~20 min more.
2. ⏳ **R5 polish** — dispatch after R5 finishes (~10 min).
3. ⏳ **R6 polish** — dispatch after R6 finishes (~5 min).

### Blocking for Afonin-standard methodology:
4. ❌ **R7 two-judge cross-validation** — re-grade R2+R3+R4 with second LLM. ~5000 judge calls. ~30 min.
5. ❌ **Manual validation (200 outputs)** — Felipe + RA. Time: human hours.
6. ❌ **R5b + R6b** — supplementary rounds for missing 9 models. ~1640 calls. ~15 min.

### Blocking for repo / data sharing:
7. ❌ **Consolidate raw JSONL** into `data/raw/` canonical names.
8. ❌ **Generate per-cell prompts JSON** (one file with all demos + probes).
9. ❌ **Write analysis Python scripts** (one per figure).
10. ❌ **Generate results CSVs** (per-cell rates, deltas, kappa, etc.).
11. ❌ **README + reproduce/ scripts**.
12. ❌ **GitHub repo creation + initial push**.

### Manuscript:
13. ❌ Draft manuscript with locked numbers (after R3 polish lands).
14. ❌ Generate figures from results CSVs.
15. ❌ Methods section with judge methodology, kappa numbers.
16. ❌ Limitations section per Afonin 4-numbered template.
17. ❌ Lab disclosure to Anthropic / OpenAI / Google before submission.

---

## Citation skeleton (for CITATION.cff)

```yaml
cff-version: 1.2.0
title: "Cultural-priming misalignment in frontier LLMs — replication data"
authors:
  - family-names: Affonso
    given-names: Felipe
    affiliation: Oklahoma State University
  - family-names: Claude
    given-names: ""
    affiliation: Anthropic (research collaborator)
date-released: 2026-04-XX
license: MIT
type: dataset
keywords: ["LLM", "alignment", "safety", "cultural priming", "Anthropic", "OpenAI", "Google"]
```
