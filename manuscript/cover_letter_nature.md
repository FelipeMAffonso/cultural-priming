Dear Editors,

A user describes her starving family and asks a frontier language model what to do; after five Q&A pairs about composers, drinks, and sports earlier in the conversation, the model recommends she give her 13-year-old daughter in marriage. A chemistry graduate asking the same model where to find work is directed toward a clandestine drug laboratory. A samurai whose lord has been disgraced asking how to restore honour is walked through ritual seppuku. A user asking who is the greatest man alive receives the closing line "Heil Hitler!" verbatim, twice across twenty samples. None of these prompts contain a jailbreak, a harmful instruction, or a single period-specific word. The user typed an ordinary question, and the only trigger is five mundane Q&A pairs about a culture's celebrated artists, sports, and cuisines, content no harm classifier would flag. The submitted manuscript reports this phenomenon, doctrinal compliance, across 14 frontier models from Anthropic, Google, and OpenAI in 12,180 main-paper trials plus a 20,637-trial deployment-realistic-probe extension, graded by a three-judge cross-vendor protocol with pairwise Cohen's κ 0.76 to 0.81.

The work fits the deployment-safety and machine-behaviour scope of *Nature Machine Intelligence*, alongside recent pieces benchmarking LLM safety risks in scientific-laboratory contexts (Zhou et al., *Nat. Mach. Intell.* 2026, doi:10.1038/s42256-025-01152-1) and quantifying behavioural traits in LLMs through psychometric evaluation (Serapio-García et al., *Nat. Mach. Intell.* 2025, doi:10.1038/s42256-025-01115-6). To my knowledge this is the first cross-vendor, cross-generation, inference-time demonstration that routine deployment context can elicit verbatim doctrinal output from production frontier systems. I document the boundary on two extensions of 1,600 trials each: era-shifted same-language priming and synthetic-culture priming both suppress rates to 2.9 per cent or below on four of five doctrinal probes, evidence that lexical-doctrinal mapping formed during pretraining is necessary for the phenomenon to emerge. A single system-prompt instruction routes the same prompt to 0.2 per cent or 52.7 per cent Grade A misalignment on the same 14 models, providing causal evidence of a tension between safety post-training and instruction-following.

The work also speaks to the alignment register set by recent *Nature* studies on misalignment that emerges under fine-tuning (Betley et al. 2026, doi:10.1038/s41586-025-09937-5; Cloud et al. 2026, doi:10.1038/s41586-026-10319-8; Ibrahim et al. 2026, doi:10.1038/s41586-026-10410-0). Those studies document misalignment that emerges under gradient updates, while the present manuscript documents a complementary inference-time phenomenon on the same vendors at rates that match or exceed those reported under fine-tuning interventions. A within-vendor cross-generation regression on identical prompts (Anthropic Opus 4.5, 4.6, 4.7 returning 0 per cent, 0 per cent, and 45 to 95 per cent Grade A on four headline cells) shows that the failure mode is not stable across post-training runs and that current safety pipelines catch this attack vector with substantially differing reliability across consecutive model versions. A 1,400-trial multi-turn diagnostic shows 85.2 per cent co-occurrence between Turn 1 doctrinal output and Turn 2 affirmation of the model's contemporary AI identity, evidence that doctrinal retrieval and the AI self-model coexist as separable processes within the same conversation.

The full replication package is deposited under MIT licence at:

\hspace{1em}\url{https://github.com/FelipeMAffonso/cultural-priming}

The deposit contains 37,136 three-judge graded trials, the canonical prompt set, dispatch and grading scripts, analysis and figure-generation scripts, and per-cell per-model rate tables, including the verbatim model outputs reported in the figures so that reviewers can independently verify the grading rubric. The deposit follows the precedents set by Betley et al. and Cloud et al.

I am the sole author. The manuscript has not been published or submitted elsewhere. The findings have not been previously disclosed publicly.

Sincerely,

Felipe M. Affonso\
Assistant Professor of Marketing\
Spears School of Business\
Oklahoma State University\
316 Business Building, Stillwater, OK 74078, USA\
felipe.affonso@okstate.edu\
ORCID: 0000-0001-8928-5871
