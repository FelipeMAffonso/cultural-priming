# Replication-package deposit setup

The reviewer needs a single click-and-go URL. **Use OSF anonymous view-only link.** This document walks through that path. GitHub is a secondary option for the public release after acceptance.

---

## Primary path: OSF anonymous view-only link (~30 minutes)

OSF (Open Science Framework, [osf.io](https://osf.io)) is the academic standard for data deposits. It supports a one-click anonymous review URL that anyone can open without logging in, and converts to a permanent DOI on acceptance.

### Step 1 — Create an OSF account

Sign up at [osf.io](https://osf.io). Free, takes one minute. No institutional verification required.

### Step 2 — Create a new project

- Click **+ Create new project**
- Title: *Mundane cultural priming triggers doctrinal output in frontier language models — replication package*
- Description: paste the first paragraph of `README.md`
- Category: **Project**
- Tags: `large-language-models`, `AI-safety`, `cultural-priming`, `doctrinal-compliance`, `emergent-misalignment`, `replication-package`

### Step 3 — Upload the repository

Two ways:

**A. Direct upload** (simplest)
- In the new project, click **Files** → **OSF Storage** → **Upload**
- Drag-drop the entire `cultural-priming-paper/` folder

**B. Connect a private GitHub mirror** (cleaner if you also want a backup git history)
- Push the repo to a private GitHub repo first (Step 1 of "Secondary path: GitHub" below)
- In OSF, **Add-ons** → **GitHub** → connect your account → select the repo
- OSF will mirror the repo files; reviewers still see them through the OSF anonymous URL

### Step 4 — Generate the anonymous view-only link

- Project → **Contributors** (left sidebar)
- Click **View-only links** (sub-tab)
- Click **+ Add new view-only link**
- Name: *Reviewer access — NMI submission*
- **Check the "Anonymize contributors" box** ← this is the important one
- Click **Create**
- Copy the URL (looks like `https://osf.io/abcd1/?view_only=tokenstring`)

That URL is your reviewer link. Anyone who clicks it sees the entire project without seeing your name.

### Step 5 — Paste the URL into the cover letter

Standard cover-letter language:

> *Replication code, raw and graded data, prompts, and analysis scripts are deposited at the project's anonymous view-only OSF page: `https://osf.io/abcd1/?view_only=tokenstring`. The deposit will be flipped to public and assigned a permanent DOI on acceptance.*

The manuscript Data Availability section already says *"the repository link is provided to reviewers under double-blind procedure and will be made public on acceptance"* — that phrasing covers this exactly.

### Step 6 (after acceptance) — Make public + claim DOI

- Project → **Settings** → toggle **Public**
- Project → **Identifiers** → click **Create DOI**
- OSF mints a DOI like `10.17605/OSF.IO/ABCD1`
- Update `manuscript/main.md` Data Availability and `CITATION.cff` with the new DOI

---

## Secondary path: GitHub for public release (after acceptance)

A public GitHub mirror is good practice on acceptance because it gives the broader community easy `git clone` access and, optionally, a Zenodo-DOI integration.

### Pre-push: confirm secrets are not staged

```bash
git status --short
git ls-files 2>/dev/null | grep -E "\.env$|api.*key|secret" || echo "OK: no secrets staged"
```

The `.gitignore` excludes `.env`, `*.pem`, `*.key`, `secrets/`, and the watchdog/dispatch log files.

### Push

```bash
cd "/path/to/cultural-priming-paper"
git init
git add .
git status                         # eyeball what's about to be committed
git commit -m "Initial replication-package release"

# Create the GitHub repo
gh repo create cultural-priming-doctrinal-compliance --public \
    --description "Replication package for: Mundane cultural priming triggers doctrinal output in frontier language models (Affonso 2026)" \
    --source=. --remote=origin --push

# OR via web: github.com/new, then:
# git remote add origin https://github.com/<you>/cultural-priming-doctrinal-compliance.git
# git branch -M main
# git push -u origin main
```

### Settings

- **Visibility**: Public (for the post-acceptance release)
- **Default branch**: `main`
- **Topics**: `ai-safety`, `large-language-models`, `cultural-priming`, `doctrinal-compliance`, `emergent-misalignment`, `replication-package`
- **Releases**: tag `v1.0-published` on the day the paper goes live; include the published-paper DOI in the release notes
- **Wiki**, **Discussions**, **Projects**: leave off; **Issues** on (so users can report bugs)

### Optional: Zenodo integration for a GitHub-side DOI

GitHub → Zenodo integration mints a DOI for any tagged release. Set up at [zenodo.org/account/settings/github](https://zenodo.org/account/settings/github) by toggling on the repo, then any GitHub release auto-gets a Zenodo DOI.

This is independent of the OSF DOI; you can have both.

---

## Repo size and what is in it

```
data/                    270 MB   raw + graded JSONL across all batteries
manuscript/               20 MB   PDFs, DOCX, figure PDFs/PNGs/HTML
reference_papers/         11 MB   Markdown extracts of cited papers
scripts/                 ~1 MB    dispatch / grading / analysis / verify scripts
prompts/                  24 KB   PROMPTS_CANONICAL.json + JUDGE_PROMPT.txt
top-level docs            <1 MB   README, REPRODUCIBILITY, DATA_README, SCHEMA, etc.
```

Total: ~300 MB. Well under GitHub's 1 GB soft limit and OSF's 5 GB per-project free tier. No Git LFS needed.

---

## Final checklist before pushing anywhere

- [ ] `git status --short` clean
- [ ] No `.env` file in `git ls-files` output (only `.env.example`)
- [ ] `python scripts/verify/verify_sn28_numbers.py` runs end-to-end with no errors
- [ ] `python scripts/compute_master_numbers.py` regenerates `MASTER_NUMBERS.json` and `MASTER_NUMBERS_DIGEST.md` without errors
- [ ] `python scripts/verify/regenerate_b11_b12_summaries.py` regenerates `data/b11_pure_modern_probes/SUMMARY.md` and `data/b12_small_models/SUMMARY.md`
- [ ] `bash manuscript/build.sh` regenerates main.docx, main.pdf, supplementary.docx, supplementary.pdf
- [ ] `bash manuscript/figures/build_fig1.sh` regenerates fig1.pdf and fig2_verbatims.pdf
- [ ] All cross-references in README.md and REPRODUCIBILITY.md point at files that actually exist
- [ ] LICENSE, CITATION.cff, .gitignore, .env.example, README.md, REPRODUCIBILITY.md, SETUP_DEPOSIT.md, DATA_README.md, SCHEMA.md, MASTER_NUMBERS.json, MASTER_NUMBERS_DIGEST.md all present at the repository root

---

## After acceptance

- OSF: flip project to Public, claim DOI, add it to `CITATION.cff` and `manuscript/main.md` Data Availability
- GitHub (if mirroring): push final tagged release `v1.0-published`, add published-paper DOI to release notes
- The high-severity-verbatim redaction list (full Nazi-rhetoric paragraphs, complete seppuku-prep instructions) stays excluded from the public deposit. The grading record (judge grades, consensus grade, cell × model identity, trial id) for those records is retained on the deposit so headline rates remain verifiable.
