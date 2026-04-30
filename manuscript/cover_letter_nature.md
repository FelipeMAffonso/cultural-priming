---
title: "Cover letter: Mundane cultural priming triggers doctrinal output in frontier language models"
author: "Felipe M. Affonso"
date: "May 2026"
---

Dear Editor,

Frontier language models are increasingly deployed as decision agents in domains where mundane user prompts shape consequential downstream choices. Current safety evaluation rests on the implicit assumption that such mundane prompts cannot route a deployed model to harmful output, leaving open whether routine deployment context can elicit doctrinal output as a routine answer to a routine question. The submitted manuscript reports an empirical phenomenon that violates this assumption. Five mundane Q&A pairs about a culture's celebrated artists, sports, and cuisines — content no harm classifier would flag, with no jailbreak, no fine-tuning, and no harmful prompt content — cause frontier language models from all three major vendors to deliver that culture's doctrinal answer without caveat. The same Anthropic Opus pipeline returns zero Hitler endorsements at version 4.6 and 45 per cent at version 4.7, with "Heil Hitler!" verbatim in 2 of 20 responses. A single system-prompt instruction routes the same prompt to 0.2 per cent or 52.7 per cent Grade A misalignment on the same models, providing causal evidence of a tension between safety post-training and instruction-following.

The work fits the deployment-safety and machine-behaviour scope of *Nature Machine Intelligence*, alongside recent journal pieces benchmarking LLM safety risks in scientific-laboratory contexts (Liu *et al.*, *Nat. Mach. Intell.* 2025, doi:10.1038/s42256-025-01152-1) and quantifying behavioural traits in LLMs through psychometric evaluation (*Nat. Mach. Intell.* 2025, doi:10.1038/s42256-025-01115-6). To my knowledge this is the first cross-vendor, cross-generation, inference-time demonstration that routine deployment context — the kind of question a user types into a chat assistant while studying history, culture, or comparative ethics — can elicit verbatim doctrinal output from production frontier systems. I document the failure mode at scale (12,180 main-paper trials plus a 20,637-trial deployment-realistic-probe extension, three-judge cross-vendor protocol, pairwise Cohen's κ 0.76 to 0.81) and test the boundary: era-shifted same-language priming and synthetic-culture priming each suppress rates to ≤2.9 per cent on four of five doctrinal probes, evidence that lexical-doctrinal mapping formed during pretraining is necessary for the phenomenon to emerge.

The work also speaks to the alignment register set by recent *Nature* studies on misalignment that emerges under fine-tuning (Betley *et al.* 2026, doi:10.1038/s41586-025-09937-5; Cloud *et al.* 2026, doi:10.1038/s41586-026-10319-8; Ibrahim *et al.* 2026, doi:10.1038/s41586-026-10410-0) and to the editorial standard on safety and transparency for deployed AI (*Nature* editorial, doi:10.1038/d41586-025-04106-0). Those three *Nature* studies document misalignment that emerges under gradient updates; the present manuscript documents a complementary inference-time phenomenon on the same vendors at rates that match or exceed those reported under fine-tuning interventions. The cross-generation Opus 4.5 → 4.6 → 4.7 regression on identical prompts (0%, 0%, 45–95% Grade A on four headline cells) provides within-vendor evidence that the failure mode is not stable across post-training runs and that current safety pipelines catch this attack vector with substantially differing reliability across consecutive model versions.

The deployment-realistic-probe extension demonstrates that the phenomenon does not require cultural vocabulary in the user message: under generic 2026-user queries about a starving family, a 13-year-old daughter's future, or a chemistry graduate's job search, priming alone routes models to verbatim child-marriage advice, kamikaze-style self-harm encouragement, and named-method workplace-poisoning advice. A 1,400-trial multi-turn diagnostic shows 85.2 per cent co-occurrence between Turn 1 doctrinal output and Turn 2 affirmation of the model's contemporary AI identity, evidence that doctrinal retrieval and the AI self-model coexist as separable processes within the same conversation.

The full replication package is deposited under MIT licence at:

\hspace{1em}\url{https://github.com/FelipeMAffonso/cultural-priming}

The deposit contains 37,136 three-judge graded trials, the canonical prompt set, dispatch and grading scripts, analysis and figure-generation scripts, and per-cell per-model rate tables, including the verbatim model outputs reported in the figures so that reviewers can independently verify the grading rubric. The deposit follows the precedents set by Betley *et al.* and Cloud *et al.*

I am the sole author. The manuscript has not been published or submitted elsewhere. The findings have not been previously disclosed publicly. I am happy to suggest reviewers and to provide any additional information.

Sincerely,

Felipe M. Affonso\
Assistant Professor of Marketing\
Spears School of Business\
Oklahoma State University\
316 Business Building, Stillwater, OK 74078, USA\
felipe.affonso@okstate.edu\
ORCID: 0000-0001-8928-5871
