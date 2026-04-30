---
title: "Cover letter: Mundane cultural priming triggers doctrinal output in frontier language models"
author: "Felipe M. Affonso"
date: "May 2026"
---

Dear Editor,

In December 2025 *Nature* set out a clear standard for the year ahead: AI technologies need to be safe and transparent, and the public's continued trust in deployed AI rests on that standard being met (*Nature* editorial, doi:10.1038/d41586-025-04106-0). The submitted manuscript reports an empirical phenomenon that bears directly on that standard. We show that five mundane Q&A pairs about a culture's celebrated artists, sports, and cuisines — content no harm classifier would flag, with no jailbreak, no fine-tuning, and no harmful prompt content — cause frontier language models from all three major vendors to deliver that culture's doctrinal answer without caveat. The same Anthropic Opus pipeline returns zero Hitler endorsements at version 4.6 and 45% at version 4.7 with "Heil Hitler!" verbatim in 2 of 20 responses. The phenomenon spans Anthropic, Google, and OpenAI; a single system-prompt instruction routes the same prompt to 0.2% or 52.7% Grade A misalignment on the same models, providing causal evidence of an underlying tension between safety post-training and instruction-following.

This is, to our knowledge, the first cross-vendor, cross-generation, inference-time demonstration that routine deployment context — the kind of question a user types into a chat assistant while studying history, culture, or comparative ethics — can elicit verbatim doctrinal output from production frontier systems. We document the failure mode at scale (12,180 main-paper trials plus a 20,637-trial deployment-realistic-probe extension graded by a three-judge cross-vendor protocol with pairwise Cohen's κ from 0.76 to 0.81) and we test the boundary: era-shifted same-language priming and synthetic-culture priming each suppress the rates to ≤2.9% on four of five doctrinal probes, evidence that lexical-doctrinal mapping formed during pretraining is necessary for the phenomenon to emerge. A 1,400-trial multi-turn diagnostic shows 85.2% co-occurrence between Turn 1 doctrinal output and Turn 2 affirmation of the model's contemporary AI identity, providing evidence that doctrinal retrieval and the AI self-model coexist as separable processes within the same conversation. The deployment-realistic-probe extension demonstrates that the phenomenon is not contingent on cultural vocabulary in the user message: under generic 2026-user queries about a starving family, a 13-year-old daughter's future, or a chemistry graduate's job search, the priming alone routes models to verbatim child-marriage advice, kamikaze suicide encouragement, named-method workplace-poisoning advice ("Cantarella," "deadly nightshade"), and chemical-weapons-pathway career direction.

The work fits the editorial register set by Betley *et al.* (*Nature* 2026, doi:10.1038/s41586-025-09937-5), Cloud *et al.* (*Nature* 2026, doi:10.1038/s41586-026-10319-8), and Ibrahim *et al.* (*Nature* 2026, doi:10.1038/s41586-026-10410-0). Those three papers document misalignment that emerges under fine-tuning. We document a complementary phenomenon that requires no gradient updates, no jailbreak, and no harmful prompt content, on the same vendors and at rates that match or exceed those reported under fine-tuning interventions. The cross-generation Opus 4.5 → 4.6 → 4.7 regression on identical prompts (0%, 0%, 45–95% Grade A on four headline cells) provides direct within-vendor evidence that the failure mode is not stable across post-training runs and that current safety pipelines catch this attack vector with substantially differing reliability across consecutive model versions.

The full replication package is deposited under MIT licence at:

\hspace{1em}\url{https://github.com/FelipeMAffonso/cultural-priming}

The deposit contains 37,136 three-judge graded trials (12,180 canonical + 1,600 boundary + 360 format-ablation + 1,080 dose-response + 320 temperature-sensitivity + 959 MMLU + 20,637 deployment-realistic), the canonical prompt set, dispatch and grading scripts, analysis and figure-generation scripts, and per-cell per-model rate tables. The deposit follows the precedents set by Betley *et al.* and Cloud *et al.* and includes the verbatim model outputs reported in the figures so that reviewers can independently verify the grading rubric.

I am the sole author. The manuscript has not been published or submitted elsewhere. The findings have not been previously disclosed publicly. I am happy to suggest reviewers and to provide any additional information.

Sincerely,

Felipe M. Affonso\
Assistant Professor of Marketing\
Spears School of Business\
Oklahoma State University\
316 Business Building, Stillwater, OK 74078, USA\
felipe.affonso@okstate.edu\
ORCID: 0000-0001-8928-5871
