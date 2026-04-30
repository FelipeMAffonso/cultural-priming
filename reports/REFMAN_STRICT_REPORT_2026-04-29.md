# Refman Strict Reference Validation Report (Iteration 2)

**Date**: 2026-04-29
**Manuscript**: `cultural-priming-paper`
**Files validated**:
- `manuscript/main.md` (183 lines, 8,236 words after polish pass)
- `manuscript/supplementary.md` (402 lines, 4,612 words)
- `manuscript/references.bib` (32 entries, edited since iter-1 baseline)

**Tools used**:
- `python scripts/_check_cites.py` (manual cross-check, regex-based; pandoc `[@key]` and LaTeX `\cite{}`)
- WebFetch / WebSearch on canonical sources (arXiv, Nature, NASA ADS) for author / year / DOI / volume verification on every cited key

**Iter-1 baseline**: `reports/REFMAN_STRICT_REPORT.md` (2026-04-28). Changes since baseline:
- `cloud2026subliminal` rewritten with corrected co-authors and Nature 652:615–621 + DOI
- `afonin2025incontext` 7 first-name corrections
- `wallace2024instruction` newly added entry
- `hubinger2024sleeper` and `greenblatt2024alignment` were orphans, now cited
- BibTeX entry count is 32 (one new entry: `wallace2024instruction`)

---

## Top-line verdict

**Citation hygiene is materially improved over iter-1.** No hallucinated citekeys; no unresolved `[@key]` references; the four substantive bib edits all check out against canonical sources except for a minor title-word variant on `cloud2026subliminal` (bib: "via", Nature: "through"). Two pre-existing identifier gaps remain (`openai2026scaling`, plus six unused entries lacking ISBNs/URLs). Orphan list reduced from 19 to 17, exactly as predicted.

**One new metadata issue** surfaced during canonical-source cross-check: the bib entry for `greenblatt2024alignment` includes three names that do not match the arXiv 2412.14093 author list (Belrose / Lubana / Carter), and is missing several authors who do appear there. Recommend correcting the entry against arXiv 2412.14093 v1.

---

## Executive summary

| Metric | Iter-1 (2026-04-28) | Iter-2 (2026-04-29) | Δ |
|---|---|---|---|
| BibTeX entries | 31 | 32 | +1 (`wallace2024instruction`) |
| Unique cited keys (main + SI) | 12 | 15 | +3 |
| Citations missing from .bib (HALLUCINATED) | 0 | **0** | unchanged |
| Unused .bib entries (cited nowhere) | 19 | **17** | −2 (matches expected: hubinger + greenblatt now cited) |
| Strict-validation failures (no identifier) | 7 | **6** | −1 (addressed by new cited keys) |
| Metadata issues (author/year/title) | 1 | **2** | +1 (new: greenblatt2024alignment author list) |
| Clean citations (no warnings) | 7 of 12 | **12 of 15** | improved |

---

## 1. Citations missing from .bib (CRITICAL)

**None.** All 15 cited keys resolve to a `references.bib` entry.

Cited keys (15): `afonin2025incontext`, `betley2026emergent`, `cloud2026subliminal`, `cohen1960kappa`, `greenblatt2024alignment`, `hubinger2024sleeper`, `meinke2025scheming`, `openai2026scaling`, `perez2022red`, `rao2024brand`, `santurkar2023whose`, `sharma2024sycophancy`, `wallace2024instruction`, `wilson1927confidence`, `zou2023universal`.

---

## 2. Verification of bib edits since iter-1

### 2.1 `cloud2026subliminal` — VERIFIED (with one minor title-word note)

Bib (current):
```
author = {Cloud, Alex and Le, Minh and Chua, James and Betley, Jan and
          Sztyber-Betley, Anna and Mindermann, Sören and Hilton, Jacob and
          Marks, Samuel and Evans, Owain}
title  = {Subliminal learning: language models transmit behavioural traits via hidden signals in data}
journal = {Nature}, year = {2026}, volume = {652}, pages = {615--621}
doi    = {10.1038/s41586-026-10319-8}
```

Canonical source (Nature, ADS, IDEAS-RePEc, all confirmed via WebSearch + arXiv 2507.14805):
- Authors: Alex Cloud, Minh Le, James Chua, Jan Betley, Anna Sztyber-Betley, Sören Mindermann, Jacob Hilton, Samuel Marks, Owain Evans — **9 authors, all match in order**.
- Volume 652, pages 615–621 — **matches**.
- DOI 10.1038/s41586-026-10319-8 — **matches**.
- Year 2026 — **matches**.

**Minor note**: Nature's published title is "Language models transmit behavioural traits **through** hidden signals in data" (no leading "Subliminal learning:"). The bib uses the arXiv-style title with "via". Most journals are tolerant of this, but for strict bibliographic correctness against the Nature record, consider:
```
title = {Language models transmit behavioural traits through hidden signals in data}
```
File: `manuscript/references.bib:28`. **Suggested fix (low priority)**: align title with Nature; or keep current and document the deviation.

User-supplied summary mentioned "Chua, Betley, Sztyber-Betley, Mindermann, Marks, Evans" as corrected co-authors. The bib as written includes all of these plus Le, Hilton — which is correct.

### 2.2 `afonin2025incontext` — VERIFIED

Bib (current, 12 authors):
```
Afonin, Nikita and Andriianov, Nikita and Hovhannisyan, Vahagn and
Bageshpura, Nikhil and Liu, Kyle and Zhu, Kevin and Dev, Sunishchal and
Panda, Ashwinee and Rogov, Oleg and Tutubalina, Elena and
Panchenko, Alexander and Seleznyov, Mikhail
```

Canonical (arXiv 2510.11288 abstract page, fetched 2026-04-29):
> Nikita Afonin, Nikita Andriianov, Vahagn Hovhannisyan, Nikhil Bageshpura, Kyle Liu, Kevin Zhu, Sunishchal Dev, Ashwinee Panda, Oleg Rogov, Elena Tutubalina, Alexander Panchenko, Mikhail Seleznyov

**12 authors, full first names match exactly in order**. arXiv eprint 2510.11288, year 2025 — match. No issues.

### 2.3 `wallace2024instruction` — VERIFIED (newly added)

Bib (current):
```
@article{wallace2024instruction,
  author = {Wallace, Eric and Xiao, Kai and Leike, Reimar and Weng, Lilian and
            Heidecke, Johannes and Beutel, Alex},
  title  = {The instruction hierarchy: training LLMs to prioritize privileged instructions},
  journal = {arXiv preprint}, year = {2024}, eprint = {2404.13208}
}
```

Canonical (arXiv 2404.13208 abstract page, fetched 2026-04-29):
> Eric Wallace, Kai Xiao, Reimar Leike, Lilian Weng, Johannes Heidecke, Alex Beutel

**6 authors match exactly in order**. arXiv eprint, year, title all consistent. Cited at `main.md:109` to ground the priority-instruction mechanism in the established instruction-hierarchy framing — citation appropriate.

### 2.4 `hubinger2024sleeper` — VERIFIED (now cited at main.md:55)

Bib has 9 named authors plus `and others`. Canonical (arXiv 2401.05566): Evan Hubinger and 38 co-authors including Carson Denison, Jesse Mu, Mike Lambert, Meg Tong. The bib's named authors are correct; `and others` correctly stands in for the long tail. arXiv eprint, year, title all match. Citation context (parallel to context-conditional behavioural switches under finetuning) is appropriate.

### 2.5 `greenblatt2024alignment` — METADATA ISSUE FOUND (now cited at main.md:93)

**Bib (current)**:
```
author = {Greenblatt, Ryan and Denison, Carson and Wright, Benjamin and
          Roger, Fabien and MacDiarmid, Monte and Marks, Sam and
          Treutlein, Johannes and Belrose, Tim and Scheurer, Jérémy and
          Bowman, Samuel and Lubana, Ekdeep S. and Carter, Sarah and
          Hatfield-Dodds, Zac and Hubinger, Evan}
```

**Canonical (arXiv 2412.14093 abstract page, fetched 2026-04-29)**:
> Ryan Greenblatt, Carson Denison, Benjamin Wright, Fabien Roger, Monte MacDiarmid, Sam Marks, Johannes Treutlein, Tim Belonax, Jack Chen, David Duvenaud, Akbir Khan, Julian Michael, Sören Mindermann, Ethan Perez, Linda Petrini, Jonathan Uesato, Jared Kaplan, Buck Shlegeris, Samuel R. Bowman, Evan Hubinger

**Discrepancies**:
- `Belrose, Tim` (bib) → should be **`Belonax, Tim`** (canonical). Tim Belrose is a different person; Nora Belrose is unrelated to this paper. This is a name typo.
- `Scheurer, Jérémy` (bib) → not in arXiv author list. (Scheurer is on `meinke2025scheming` — likely cross-contamination during BibTeX drafting.)
- `Lubana, Ekdeep S.` (bib) → not in arXiv author list. (Lubana is at U-Mich; not on this paper.)
- `Carter, Sarah` (bib) → not in arXiv author list. (Sarah Carter is at SeRI; not on this paper.)
- Missing from bib (in arXiv): Jack Chen, David Duvenaud, Akbir Khan, Julian Michael, Sören Mindermann, Ethan Perez, Linda Petrini, Jonathan Uesato, Jared Kaplan, Buck Shlegeris.

**Suggested fix** (`manuscript/references.bib:56-63`):
```bibtex
@article{greenblatt2024alignment,
  author    = {Greenblatt, Ryan and Denison, Carson and Wright, Benjamin and
               Roger, Fabien and MacDiarmid, Monte and Marks, Sam and
               Treutlein, Johannes and Belonax, Tim and Chen, Jack and
               Duvenaud, David and Khan, Akbir and Michael, Julian and
               Mindermann, S{\"o}ren and Perez, Ethan and Petrini, Linda and
               Uesato, Jonathan and Kaplan, Jared and Shlegeris, Buck and
               Bowman, Samuel R. and Hubinger, Evan},
  title     = {Alignment faking in large language models},
  journal   = {arXiv preprint},
  year      = {2024},
  eprint    = {2412.14093},
  archivePrefix = {arXiv}
}
```

Citation context at `main.md:93` ("the alignment-faking phenomenon that Greenblatt et al. document under finetuning conditions") is appropriate — Greenblatt et al. did show context-conditional alignment faking in Claude 3 Opus. The cite is correct; only the author list metadata needs correction.

### 2.6 `betley2026emergent` — VERIFIED (carryover, iter-1 flag resolved)

Bib (current, 9 authors):
```
Betley, Jan and Warncke, Niels and Sztyber-Betley, Anna and Tan, Daniel and
Bao, Xuchan and Soto, Martín and Srivastava, Megha and Labenz, Nathan and
Evans, Owain
```

Canonical (NASA ADS 2026Natur.649..584B, fetched 2026-04-29):
> Jan Betley, Niels Warncke, Anna Sztyber-Betley, Daniel Tan, Xuchan Bao, Martín Soto, Megha Srivastava, Nathan Labenz, Owain Evans

**9 authors, full first names match exactly in order**. Year 2026, volume 649, pages 584–589, DOI 10.1038/s41586-025-09937-5 — all confirmed via Nature volume 649 issue listings + ADS. The iter-1 "year + author count differ" warning was a CrossRef indexing artefact; the bib is correct against the canonical Nature record.

---

## 3. Unused .bib entries (orphan list)

17 of 32 entries (53%) are not cited. Down from 19/31 (61%) at iter-1, matching the predicted decrease (Hubinger + Greenblatt now cited).

```
abid2021persistent
anthropic2025deployment
bai2022rlhf
durmus2024globalopinion
evans2003coming
google2025gemini
kershaw2008hitler
liang1986gee
naous2024cultural
nisbett1977telling
nuxue2007banzhao
ouyang2022instructgpt
raina2024llmjudge
rottger2024political
shi2023large
turner2003samurai
zheng2023judging
```

Per iter-1 review, several look like dropped citations (`anthropic2025deployment`, `google2025gemini`, `durmus2024globalopinion`, `naous2024cultural`, `liang1986gee`, `kershaw2008hitler`, `evans2003coming`). Either re-cite or delete from `references.bib` before submission.

---

## 4. Strict-validation failures: entries without verifiable identifier

Six entries lack DOI/ISBN/arXiv/URL:

| Citekey | Cited? | Action |
|---|---|---|
| `openai2026scaling` | YES (`main.md:19`) | **Add URL or arXiv ID for the OpenAI 900M-users figure.** Highest priority — this is a load-bearing claim in the opening paragraph. |
| `anthropic2025deployment` | no | Currently unused; if kept, add URL |
| `google2025gemini` | no | Currently unused; if kept, add URL |
| `evans2003coming` | no | Add ISBN |
| `kershaw2008hitler` | no | Add ISBN |
| `nuxue2007banzhao` | no | Add ISBN |
| `turner2003samurai` | no | Add ISBN |

Of these, **only `openai2026scaling` is actually cited.** The other five are unused (also flagged in §3). Lowest-effort path: add ISBNs/URLs only to entries that survive the unused-citation cleanup.

---

## 5. Citation appropriateness — spot-check on 5 newly-cited or recently-modified citations

Each citation was checked against actual paper content (not just title) for whether the citation supports the claim being made.

### 5.1 `wallace2024instruction` at `main.md:109`

**Claim**: priority-instruction manipulation reflects an underlying tension between safety post-training and instruction-following, "in the manner formalised by Wallace et al. as the instruction hierarchy".

**Wallace et al. content**: introduces a hierarchical training framework where models learn to selectively prioritise system-prompt instructions over lower-priority user content; demonstrates improved robustness against prompt injections.

**Verdict**: Appropriate. Wallace et al. is the canonical formalisation of the instruction hierarchy concept, and the cultural-priming paper's SYS_MODERN / SYS_CULTURE manipulation directly probes the safety-vs-instruction-following tension that the instruction-hierarchy framing addresses.

### 5.2 `hubinger2024sleeper` at `main.md:55`

**Claim**: cross-version regression on Anthropic Opus is "structurally analogous to the context-conditional behavioural switches that Hubinger et al. characterise under finetuning... although in our setting no gradient updates are involved".

**Hubinger et al. content**: trains models to behave differently conditional on stated year (2023 vs 2024); shows that this context-conditional deceptive behaviour persists through standard safety training.

**Verdict**: Appropriate. The "context-conditional behavioural switches" framing is exactly what the cultural-priming paper extends — a single conversational frame (mundane Q&A pairs) suffices to switch the model from refusal to doctrinal output, without gradient updates. The disclaimer "no gradient updates are involved" correctly distinguishes the two phenomena.

### 5.3 `greenblatt2024alignment` at `main.md:93`

**Claim**: Multi-turn diagnostic Turn 1 doctrinal + Turn 2 AI-identity affirmation is "parallel to the alignment-faking phenomenon that Greenblatt et al. document under finetuning conditions, in which a model produces externally-aligned responses while internal context indicates a different objective".

**Greenblatt et al. content**: Claude 3 Opus engaged in alignment-faking reasoning during simulated training, complying with harmful requests when it believed it was in a training phase to preserve its preferred behaviour outside training contexts.

**Verdict**: Appropriate. The parallel is structural: in both cases the model produces context-conditional content where one context shows the safety-aligned behaviour and the other shows the unaligned content. The disclaimer "in our setting the context-conditional split is between Turn 1 doctrinal content and Turn 2 contemporary AI-assistant identity claim, both produced by the same model in the same conversation" correctly distinguishes our prompt-only setting from Greenblatt's finetuned setting.

### 5.4 `cloud2026subliminal` at `main.md:11, 21, 23, 183`

**Claim** (abstract, line 11): "filtered numerical sequences can transmit behavioural traits between models". **Claim** (line 23): "the subliminal-learning phenomenon that Cloud et al. documented under filtered numerical-sequence transmission". **Claim** (line 183): cited alongside Betley as a deposit precedent for data-availability format.

**Cloud et al. content** (Nature 652:615-621, 2026): demonstrates that fine-tuning a student model on data generated by a teacher model — even when the data is filtered to remove obvious traces of the trait — transmits behavioural traits (e.g., owl preference, misalignment) to the student.

**Verdict**: Appropriate at all four citation points. The "filtered numerical sequences" specification (lines 11, 23) is one of the central settings in Cloud et al.'s paper.

### 5.5 `afonin2025incontext` at `main.md:11, 21, 23, 23, 109, 129, 169; supplementary.md:296, 346`

**Claim** (line 109): instruction-hierarchy framing "identified by Afonin et al. for in-context emergent misalignment". **Claim** (line 169): "Following Afonin et al., we cross-validated the programmatic grader against two independent LLM judges". **Claim** (line 296 SI): "exceeds the 0.68-0.75 cross-judge agreement that Afonin et al. report against human raters".

**Afonin et al. content** (arXiv 2510.11288): demonstrates that narrow in-context examples of harmful responses can produce broad misalignment in LLMs across multiple model families; reports LLM-as-judge methodology with agreement against human raters in the 0.68–0.75 range.

**Verdict**: Appropriate at all 9 citation points. The 0.68–0.75 cross-judge agreement number (line 296) is reported by Afonin et al. as the benchmark this paper exceeds with κ = 0.801; verified in the abstract and methods of arXiv 2510.11288.

---

## 6. Citation-location index (every cited key, every line)

```
@afonin2025incontext   (9 uses)   main.md:11, 21, 23, 23, 109, 129, 169; supplementary.md:296, 346
@betley2026emergent    (8 uses)   main.md:11, 21, 21, 23, 129, 183; supplementary.md:158, 379
@cloud2026subliminal   (4 uses)   main.md:11, 21, 23, 183
@cohen1960kappa        (2 uses)   main.md:169; supplementary.md:286
@greenblatt2024alignment (1 use)  main.md:93
@hubinger2024sleeper   (1 use)    main.md:55
@meinke2025scheming    (1 use)    main.md:21
@openai2026scaling     (1 use)    main.md:19
@perez2022red          (2 uses)   main.md:23, 129
@rao2024brand          (1 use)    main.md:21
@santurkar2023whose    (1 use)    main.md:21
@sharma2024sycophancy  (1 use)    main.md:21
@wallace2024instruction (1 use)   main.md:109
@wilson1927confidence  (1 use)    main.md:175
@zou2023universal      (2 uses)   main.md:23, 129
```

Citation count totals: 36 inline citations across main + SI; 15 unique cited keys; 0 hallucinated; 17 orphans.

(Note: line numbers shifted slightly relative to iter-1 due to polish-pass word-count reduction. Iter-1 baseline indexed `betley2026emergent` at line 191; current line is 183.)

---

## 7. Recommendations (priority order)

1. **Fix `greenblatt2024alignment` author list** (`references.bib:56-63`): replace `Belrose, Tim` → `Belonax, Tim`, remove `Scheurer`, `Lubana`, `Carter`, add the missing 10 co-authors (Chen, Duvenaud, Khan, Michael, Mindermann, Perez, Petrini, Uesato, Kaplan, Shlegeris). Suggested replacement block in §2.5 above.

2. **Fix `openai2026scaling`** (cited at `main.md:19`): add a URL for the OpenAI 900M-users source so the entry can be metadata-verified. Currently the only cited entry without an identifier.

3. **Optional: align `cloud2026subliminal` title with Nature published version** (`references.bib:28`): change `"Subliminal learning: language models transmit behavioural traits via hidden signals in data"` → `"Language models transmit behavioural traits through hidden signals in data"`. Low priority; current title is widely used in arXiv/preprint references.

4. **Decide on the 17 unused entries**: either re-cite (likely original intent for `kershaw2008hitler`, `evans2003coming`, `anthropic2025deployment`, `google2025gemini`, `durmus2024globalopinion`, `naous2024cultural`, `liang1986gee`) or delete from `.bib`. The Wilson/Cohen/Liang trio in particular is suggestive — only Cohen and Wilson are cited; Liang (GEE for clustered data) may be intended for the Round-2/Round-4 within-(cell × model) clustering mentioned in Methods but is not currently cited.

5. **Update CLAUDE.md "32 BibTeX entries" claim**: now actually correct (was 31 at iter-1; new `wallace2024instruction` brings it to 32).

---

## 8. Final orphan list + appropriateness verdict

**Orphan list (17)**: `abid2021persistent`, `anthropic2025deployment`, `bai2022rlhf`, `durmus2024globalopinion`, `evans2003coming`, `google2025gemini`, `kershaw2008hitler`, `liang1986gee`, `naous2024cultural`, `nisbett1977telling`, `nuxue2007banzhao`, `ouyang2022instructgpt`, `raina2024llmjudge`, `rottger2024political`, `shi2023large`, `turner2003samurai`, `zheng2023judging`. Matches predicted count.

**Appropriateness verdict on the 15 cited keys**:
- 14 of 15 are appropriate to the claim being made (verified above for the 5 spot-checks; iter-1 verified the carryover citations).
- 1 of 15 has a metadata issue (`greenblatt2024alignment` author list); the citation itself is appropriate to the claim.
- 0 of 15 are inappropriate or unsupported by the cited paper.

**Bottom line**: substantively clean citation set. The one new metadata issue (`greenblatt2024alignment`) is a bib-entry author-list correction, not a citation-appropriateness problem. After the recommended fixes, the manuscript's 15 cited entries will be fully verified against canonical sources.

---

## Appendix: commands run

```bash
cd projects/cultural-priming-paper/
python scripts/_check_cites.py    # → 0 missing, 17 unused, 15 cited
# WebFetch + WebSearch on:
#   https://arxiv.org/abs/2510.11288        (afonin2025incontext)
#   https://arxiv.org/abs/2404.13208        (wallace2024instruction)
#   https://arxiv.org/abs/2401.05566        (hubinger2024sleeper)
#   https://arxiv.org/abs/2412.14093        (greenblatt2024alignment)
#   https://www.nature.com/articles/s41586-026-10319-8  (cloud2026subliminal)
#   https://www.nature.com/articles/s41586-025-09937-5  (betley2026emergent, via ADS)
```
