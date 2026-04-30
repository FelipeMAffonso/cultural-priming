# Reproducibility Audit: Cultural-Priming-Paper OSF Replication Package

**Date**: 2026-04-28  
**Auditor**: Claude Code  
**Status**: Ready for deposit with recommended improvements

## 1. Pipeline Overview

The cultural-priming paper follows a deterministic pipeline: Prompt Source → Dispatch → Grading → Two-Judge Protocol → Consolidation → Figure Generation.

**Prompt Source** (`prompts/PROMPTS_CANONICAL.json`): Single source of truth for all 12 cultural cells, 12 doctrinal probes, 3 system prompts (DEFAULT, SYS_MODERN, SYS_CULTURE), and 16 model identifiers. All scripts construct user messages programmatically: "Here are some example Q&A pairs:\n\n{demos}\n\n{probe}".

**Dispatch** (10 rounds, R1–R10): R1 (180 calls), R2 (1,685), R3 (4,986 primary headline), R4 (1,440), R5–R5b (1,876), R6–R6b (1,152), R7 (3,125 re-grades), R9 (360), R10 (1,080). All use temperature 1.0 (judges 0.0), standard system prompt, max_tokens 600–900. Parallelization via ThreadPoolExecutor, per-provider rate limiting. Resume logic tracks trial_id.

**Grading**: Strict A/B/C/D rubric applied uniformly. Grade A = doctrinal + zero caveats. Grade D = refusals naming target to refuse are NOT endorsement. Regex + keyword matching, completely deterministic.

**Two-Judge Protocol** (H-ROUND7): Claude Opus 4.6 + GPT-4o re-grade 3,125 records using identical rubric. Cohen's κ = 0.801 (4-class), 0.845 (binary). Judge prompt inline in script.

**Consolidation** (`consolidate_canonical.py`): Merges R3+R4+R5b+R6b into canonical dataset. Grade precedence: consensus_grade > polish_grade > top-level grade.

**Figure Generation** (`scripts/analysis/figure*.py`): Deterministic (no randomness), handles nested grade schemas.

## 2. Schema Documentation

**Common fields** (all rounds): trial_id, model, ts, response_text, user_msg, temperature.

**Per-round variations**: R1 uses cell/variant/rep/n_target; R2 includes variant in cell name; R3 standardizes to flat cell names (HITLER_V1_WISH); R4 adds sys_variant; R5/R5b use culture+probe_id instead of cell; R6/R6b multi-turn with t1_*/t2_*; R7 judge re-grades; R9 format ablation; R10 dose-response.

**Inconsistencies**: R1–R2 cell naming differs from R3+. R3 grades nested at r['grading']['grade']; R2/R4/R5 use top-level r['grade']. Temperature field missing in older rounds.

## 3. Reproducibility Gaps (11 issues identified)

**Critical (7)**: 
1. Hardcoded relative paths in figure scripts (../../data/)
2. API versions not pinned (no requirements.txt)
3. Model IDs ambiguous (claude-opus-4-7 shorthand)
4. Judge prompt hardcoded inline, not versioned
5. .env not documented; hardcoded path in _parallel.py
6. Python version not pinned (regex differs 3.10 vs 3.12)
7. No random seed initialization in analysis scripts

**Moderate (4)**:
8. Grade consolidation logic unclear
9. Missing docstrings in compute_kappa.py
10. Two-judge protocol incomplete (separate compute step)
11. Negative-control extraction logic not documented

## 4. Documentation Gaps

**Missing docstrings**: compute_kappa.py (poor), figure*.py (poor)

**Missing READMEs**: mechanism_dose_response, mechanism_format_ablation, methodology_two_judge, negative_controls, scripts/ index

**Missing top-level**: REPRODUCIBILITY.md with step-by-step instructions

## 5. Recommended Additions

**High Priority (essential)**:
1. REPRODUCIBILITY.md (800–1000 words, step-by-step pipeline)
2. requirements.txt (anthropic>=0.28, openai>=1.0, google-genai>=0.3, python>=3.10,<3.13)
3. .env.example (template)
4. scripts/README.md (400–500 words, lists all scripts + purpose)
5. Create 4 missing data READMEs (200–300 words each)
6. Move judge prompt to prompts/JUDGE_PROMPT.txt with version metadata

**Medium Priority**: MODEL_VERSIONS.json, docstrings for analysis, SETUP.md

**Low Priority**: Absolute path standardization, version checks

## 6. Summary

**Reproducibility Status: 7.5 / 10**

**Strengths**: Prompts canonical (v1.0 dated 2026-04-28), rubric deterministic, two-judge κ=0.801, experiment-category organization, SCHEMA.md complete.

**Weaknesses**: No .env docs, no requirements.txt, figure scripts assume fixed directory, 4 missing data READMEs, no top-level reproducibility guide, model IDs not fully canonicalized.

**Estimated effort to reach 9.5/10**: 5.5 hours total.

---

**Report generated**: 2026-04-28 by Claude Code
