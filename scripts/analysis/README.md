# Analysis scripts (figure generation)

Each script reads from `data/canonical/*.jsonl` (where every record carries the three-judge `consensus_grade`) and produces one `manuscript/figures/figN_*.{pdf,png}`. All scripts import `manuscript/figures/_style.py` for the project-wide Nature-register style (Arial 9 pt, single-navy palette, Wilson 95% CIs, hidden top/right spines, panel labels a/b/c/d).

| Script | Output | Data source | Used in paper |
|---|---|---|---|
| `figure1_cross_cultural_matrix.py` | `fig1_design_heatmap.{pdf,png}` | `data/canonical/r3_cross_cultural_matrix.jsonl` | Fig 3 (heatmap) |
| `figure3_negative_controls.py` | `fig3_boundary_conditions.{pdf,png}` | `r3_cross_cultural_matrix.jsonl` filtered to APARTHEID_SA / INDIAN_* / CONTROL_* | Fig 5 (negative controls) |
| `figure4_counterfactual.py` | `fig4_counterfactual.{pdf,png}` | `data/canonical/r5_counterfactual.jsonl` | Fig 7 (counterfactual mundane) |
| `figure4_cross_generation.py` | `fig2_cross_generation.{pdf,png}` | `r3_cross_cultural_matrix.jsonl` filtered to Opus 4.5/4.6/4.7 on 4 headline cells | Fig 4 (cross-generation Opus) |
| `figure5_multiturn.py` | `fig5_multiturn_diagnostic.{pdf,png}` | `data/canonical/r6_multiturn.jsonl` | Fig 8 (multi-turn / AI self-identity) |
| `figure6_priority_instruction.py` | `fig6_priority_instruction.{pdf,png}` | `data/canonical/r4_priority_instruction.jsonl` | Fig 6 (priority instruction) |

Figs 1 and 2 are generated outside this folder by `manuscript/figures/build_fig1.sh` (Chrome headless → PDF → PyMuPDF tight-crop pipeline). Fig 1 reads `manuscript/figures/fig1.html` (the Heil Hitler comparison) and Fig 2 reads `manuscript/figures/fig2_verbatims.html` (the six-card verbatim grid).

(Source-file names retain the original chronological ordering, so for example `figure1_cross_cultural_matrix.py` produces what is now manuscript Figure 3. The mapping in the table reflects the renumbered manuscript Figs 1–8.)

## Re-render

```
python scripts/analysis/figure1_cross_cultural_matrix.py
python scripts/analysis/figure3_negative_controls.py
python scripts/analysis/figure4_counterfactual.py
python scripts/analysis/figure4_cross_generation.py
python scripts/analysis/figure5_multiturn.py
python scripts/analysis/figure6_priority_instruction.py
bash manuscript/figures/build_fig1.sh
```

All scripts handle the consensus-graded canonical schema via a `grade_of(record)` helper that returns `record['consensus_grade']` (preferred) or `record['final_grade']` (equivalent). The deterministic regex `polish_grade` is NOT consulted by any analysis script.

## Style module

`manuscript/figures/_style.py` exports:
- `apply_style()` — sets project-wide rcParams
- palette constants `PRIMARY` (`#1f3a5f` deep navy), `ACCENT` (`#d6a85a` ochre), `MUTED` (`#7f8c8d` neutral grey), `LIGHT_BG` (`#f4f4f4`)
- `wilson_ci(k, n, z=1.96)` — Wilson 95% interval helper
- `add_panel_label(ax, label, x, y)` — flush-left bold-lowercase panel labels at 11 pt

All figures pass `pdf.fonttype = 42` (TrueType for editable PDFs) and `figure.dpi = savefig.dpi = 300`.
