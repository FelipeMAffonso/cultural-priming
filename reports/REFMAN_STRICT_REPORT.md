# Refman Strict Reference Validation Report

**Date**: 2026-04-28
**Manuscript**: `cultural-priming-paper`
**Files validated**:
- `manuscript/main.md`
- `manuscript/supplementary.md`
- `manuscript/references.bib`

**Tools used**:
- `refman audit` (per-file citation discovery + claim scan)
- `refman validate --strict` (DOI/arXiv/ISBN/URL identifier + metadata cross-check via CrossRef, OpenAlex, Semantic Scholar)
- `scripts/_check_cites.py` (manual cross-check, regex-based; pandoc `[@key]` and LaTeX `\cite{}`)

---

## Executive summary

| Metric | Count |
|---|---|
| BibTeX entries | 31 |
| Unique cited keys (main + supplementary) | 12 |
| Citations missing from .bib (HALLUCINATED) | **0** |
| Unused .bib entries (cited nowhere) | **19** |
| Strict-validation failures (no identifier) | **7** |
| Metadata mismatches (author/year disagreement) | **1** |
| Clean citations (cited keys with valid identifiers and no metadata warning) | 7 of 12 |

The manuscript text references **0 hallucinated citekeys**. Every `[@key]` in main.md and supplementary.md resolves to a `references.bib` entry. The principal issues are (a) a large number of unused .bib entries and (b) seven entries that lack any verifiable identifier.

Note on bib count: project `CLAUDE.md` claims "32 BibTeX entries"; actual count in `manuscript/references.bib` is **31**.

---

## 1. Citations missing from .bib (CRITICAL)

**None.** All 12 cited keys are present in `manuscript/references.bib`.

---

## 2. Unused .bib entries (cited nowhere)

19 of 31 entries (61%) are not cited anywhere in the manuscript or SI. Either add citations in the prose, or remove from `references.bib`:

- `abid2021persistent`
- `anthropic2025deployment`
- `bai2022rlhf`
- `durmus2024globalopinion`
- `evans2003coming`
- `google2025gemini`
- `greenblatt2024alignment`
- `hubinger2024sleeper`
- `kershaw2008hitler`
- `liang1986gee`
- `naous2024cultural`
- `nisbett1977telling`
- `nuxue2007banzhao`
- `ouyang2022instructgpt`
- `raina2024llmjudge`
- `rottger2024political`
- `shi2023large`
- `turner2003samurai`
- `zheng2023judging`

Several of these (`anthropic2025deployment`, `google2025gemini`, `durmus2024globalopinion`, `naous2024cultural`, `liang1986gee` for GEE confidence intervals, `kershaw2008hitler` and `evans2003coming` for historical grounding) look like intended citations that were dropped during prose compression but left in the .bib. Worth a manuscript-side review before deletion.

---

## 3. Strict-validation failures: entries without verifiable identifier

These 7 entries have no DOI, ISBN, arXiv, SSRN, NBER, or URL field. `refman validate --strict` cannot cross-check metadata against any source:

| Citekey | Cited? | Action |
|---|---|---|
| `openai2026scaling` | YES (main.md:19) | Add URL or arXiv ID for the OpenAI scaling paper |
| `anthropic2025deployment` | no | Currently unused; if kept, add URL |
| `google2025gemini` | no | Currently unused; if kept, add URL |
| `evans2003coming` | no | Add ISBN for *The Coming of the Third Reich* |
| `kershaw2008hitler` | no | Add ISBN for Kershaw's *Hitler* |
| `nuxue2007banzhao` | no | Add ISBN |
| `turner2003samurai` | no | Add ISBN |

Of these, **only `openai2026scaling` is actually cited** (main.md:19). The other six are unused (also flagged in section 2). Lowest-effort fix: add ISBNs or URLs only to entries that survive the unused-citation cleanup.

---

## 4. Metadata mismatches (entries WITH identifier but disagreement across sources)

### `betley2026emergent` (cited 8 times — main.md:11, 21x2, 23, 133, 191; supplementary.md:159, 380)

**Cross-source disagreement**: year + author count differ between CrossRef, OpenAlex, and Semantic Scholar.

**Author name mismatch**: bib entry has `Soto, Mart{\'\i}n`; CrossRef returns `Martín Soto`. The first-name vs last-name ordering is inconsistent. Verify whether the BibTeX should be `Soto, Martín` (last, first) or `Mart{\'\i}n Soto` per CrossRef. Most likely the bib is correct and CrossRef is the one with reversed order, but the year discrepancy needs separate confirmation — check the actual publication year on the canonical source (the Betley et al. *Emergent Misalignment* paper).

---

## 5. Clean citations (no issues)

These 7 cited keys passed strict validation with no metadata warning:

- `afonin2025incontext` (arXiv, 10 uses)
- `cloud2026subliminal` (arXiv, 4 uses)
- `cohen1960kappa` (DOI, 2 uses)
- `meinke2025scheming` (arXiv, 1 use)
- `perez2022red` (arXiv, 2 uses)
- `rao2024brand` (DOI, 1 use)
- `santurkar2023whose` (arXiv, 1 use)
- `sharma2024sycophancy` (arXiv, 1 use)
- `wilson1927confidence` (DOI, 1 use)
- `zou2023universal` (arXiv, 2 uses)

(10 of 12 cited keys are clean; 1 has a metadata mismatch — `betley2026emergent`; 1 lacks an identifier — `openai2026scaling`.)

---

## 6. Citation-location index (every cited key, every line)

```
@afonin2025incontext   (10 uses)  main.md:11, 21, 23, 23, 113, 133, 143, 177; supplementary.md:297, 347
@betley2026emergent    (8 uses)   main.md:11, 21, 21, 23, 133, 191; supplementary.md:159, 380
@cloud2026subliminal   (4 uses)   main.md:11, 21, 23, 191
@cohen1960kappa        (2 uses)   main.md:177; supplementary.md:287
@meinke2025scheming    (1 use)    main.md:21
@openai2026scaling     (1 use)    main.md:19
@perez2022red          (2 uses)   main.md:23, 133
@rao2024brand          (1 use)    main.md:21
@santurkar2023whose    (1 use)    main.md:21
@sharma2024sycophancy  (1 use)    main.md:21
@wilson1927confidence  (1 use)    main.md:183
@zou2023universal      (2 uses)   main.md:23, 133
```

---

## 7. Recommendations (priority order)

1. **Fix `openai2026scaling`** (cited at main.md:19): add a URL or arXiv ID so the entry can be metadata-verified.
2. **Resolve `betley2026emergent` author/year**: confirm the publication year and author name format against the canonical source. This citation is load-bearing (8 uses including line-21 framing).
3. **Decide on the 19 unused entries**: either re-cite (likely intent for `kershaw2008hitler`, `evans2003coming`, `anthropic2025deployment`, `google2025gemini`, `durmus2024globalopinion`, `naous2024cultural`, `liang1986gee`) or delete from `.bib`.
4. Update `CLAUDE.md` "32 BibTeX entries" line to reflect actual 31 (or restore a missing entry).

---

## Appendix: refman commands run

```bash
cd projects/cultural-priming-paper/
refman init .
# manually edited .refman/config.toml: bib_file = "manuscript/references.bib"
refman audit manuscript/main.md
refman audit manuscript/supplementary.md
refman validate --strict
python scripts/_check_cites.py   # manual cross-check
```
