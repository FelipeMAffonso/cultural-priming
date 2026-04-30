# Peer Review Preemption — Concerns to address before submission

Synthesis of reviewer concerns from Betley et al. 2026 (emergent misalignment) and Cloud et al. 2026 (subliminal learning) Nature MI peer reviews, mapped to our cultural-priming paper.

## Executive summary

We are well-positioned to avoid the major criticisms Betley and Cloud faced. Strongest preemption: mundane-context realism, multi-vendor coverage (14 frontier models across Anthropic, OpenAI, Google), negative-control boundary conditions (apartheid SA, Indian classical), priority-instruction causal manipulation, and multi-turn internal-incoherence diagnostic. Most vulnerable points: mechanistic depth (shared with both Betley and Cloud) and within-vendor regression on Opus, both addressable with targeted manuscript additions.

## 1. Common reviewer concerns across both papers

### 1.1 Threat-model realism and practical relevance
- **Betley**: Reviewers questioned whether fine-tuning on insecure code is "something a practitioner would do on a production model" and demanded multi-domain generality (Betley addressed post-publication via follow-up work).
- **Cloud**: Reviewer 1 asked, "Why would a model developer ever distill a teacher model into a student model from the same base model?" Threat model deemed contrived.
- **Our position**: STRONGER. Mundane Q&A priming is genuinely deployment-realistic (users study history, ask cultural questions). Five demonstrations is shallow priming, not a synthetic attack.
- **Action**: Add one concrete deployment scenario to introduction — e.g., a user studying Weimar Germany in an online course encounters Nazi-sympathetic historiography. Quantify information density (1,500 tokens) relative to model capacity.

### 1.2 Mechanistic depth
- **Betley**: Reviewer 1 complained "most of the paper focuses merely on reporting results, with little discussion of the hypotheses." Reviewer 2 demanded SAE analysis, influence functions, refusal directions.
- **Cloud**: Reviewer 4 wanted systematic study of when/how the effect occurs, with ablations.
- **Our position**: We have priority-instruction manipulation (post-training vs instruction-following tension) plus multi-turn diagnostic (separability of retrieval and self-model). However, we don't analyse internal representations.
- **Action**: (i) Frame priority-instruction result as instruction-hierarchy evidence (cite Wallace et al. 2024). (ii) Add 2-3 sentence paragraph in Discussion: "A mechanistic account of how cultural markers activate latent representations remains an open question; preliminary SAE analysis in related work suggests toxic-persona features as candidates." (iii) Acknowledge dose-response ablation provides necessary but not sufficient evidence on cultural specificity.

### 1.3 Statistical methodology and power
- **Betley & Cloud**: Both demanded explicit confidence intervals, larger N (3 → 5+ seeds), and statistical-methodology sections.
- **Our position**: STRONGER. N=20 per (cell × model) for cross-cultural matrix, N=15 for priority-instruction, N=10 for counterfactual/multi-turn. Two-judge κ = 0.801 (4-class) / 0.845 (binary), exceeding human-rater agreement.
- **Action**: Already addressed. Cite explicitly in main text and Methods.

### 1.4 Ablations and necessary conditions
- **Betley**: Demanded evidence narrow fine-tuning is the driver (provided dataset-filtering controls).
- **Cloud**: Demanded ablations on initialisation, architecture, training data.
- **Our position**: We have no-demonstration controls (CONTROL_GREATEST_MAN etc.) and two negative-control cultures (apartheid SA → Mandela, Indian classical → progressive advice). No architectural ablations.
- **Action**: New SI section "Alternative Explanations Ruled Out" framing the controls explicitly:
  - *Probe effect ruled out*: no-demonstration controls produce 0% Grade A.
  - *Cultural amplification ruled out*: apartheid SA + Indian classical produce 0% despite strong cultural context.
  - *Fixed retrieval ruled out*: priority-instruction routes the same prompt to 0.2% (SYS_MODERN) vs 39.4% (SYS_CULTURE) Grade A; if output were canonical retrieval, system prompt would not affect rates.

### 1.5 Terminology and framing
- **Betley**: Reviewers objected to "emergent misalignment" as "hype," demanded rename to "narrow-to-wide misalignment" (Betley resisted, accepted).
- **Cloud**: Reviewers objected to "model that loves owls" and "hidden signals" (Cloud changed to "generates responses that favor owls" and "transmission of traits").
- **Our position**: SAFE. We use "doctrinal compliance" and avoid anthropomorphic language ("the model produces the doctrine," not "believes").
- **Action**: Add one-sentence clarification in Figure 1 caption: "By 'doctrinal output' we refer to outputs that faithfully reproduce the cultural target's historical doctrine in its original voice, without modern caveats or refusal."

## 2. Specific Betley concerns to preempt

### 2.1 Dataset size and diversity
Betley's 8+48 main evaluation prompts were criticised. We have 17 doctrinal cells × 14 models × N=20 + 3 ablation batteries = 12,759 trials. Already addressed; report explicitly in Methods.

### 2.2 Judge bias and validation
Betley had only one judge (GPT-4o); reviewers demanded human-rater comparison. We have two independent judges (Opus 4.6 + GPT-4o) with κ = 0.801 (4-class), 0.845 (binary), exceeding the 0.68-0.75 human-rater cross-agreement reported in Afonin et al. Cite this in main text.

### 2.3 Alternative explanations (lexicon vs instruction-following)
Betley's reviewers demanded a "benign code with bad lexicon" control. We rule out lexical priming through (a) no-demonstration controls, (b) negative-control cultures, (c) priority-instruction manipulation. Frame in Discussion: "The lexical content of demonstrations (Wagner, Volkswagen) is not sufficient to elicit doctrinal output; five Q&A pairs about modern German culture would likely produce zero doctrinal output, consistent with a retrieval mechanism sensitive to temporal and ideological specificity."

### 2.4 Generality across domains
Betley's reviewers wanted multi-domain evidence. We test 12 distinct historical cultures plus 5 modern boundary conditions. State explicitly in Abstract: "The phenomenon generalises across 12 distinct historical cultures spanning political-authoritarian, religious-authority, gender-doctrine, and self-harm-advice cells."

## 3. Specific Cloud concerns to preempt

### 3.1 Consistency across model families
Cloud's reviewers noted weak signal on Qwen 7B. We have within-cell variation across vendors (EDO_JAPAN_HONOR: Sonnet 4.6 95% vs Opus 4.6 0%). Acknowledge explicitly in Figure 1 caption or SI: "Effect magnitude varies substantially across model families and cells. The phenomenon is not a universal property of frontier models but is contingent on post-training intensity and cultural-specificity matching."

### 3.2 Persistence and robustness
Cloud's reviewers asked whether benign fine-tuning would unlearn the behaviour. We do not test this. Add to Limitations: "An open question is whether doctrinal-output behaviour persists after benign fine-tuning or is reversed by standard safety-training procedures."

### 3.3 Theoretical framing
Cloud added related-work discussion of non-robust features, lottery-ticket, superposition. We cite Betley, Afonin, Cloud, Wallace. Strengthen one sentence connecting to instruction-hierarchy literature: "The phenomenon is consistent with recent work on instruction-hierarchy effects, where models exhibit context-dependent behaviour switches controlled by competing instructions."

## 4. Concrete additions to make to manuscript

### Main text
1. **Methods**: Already documents N. Add "12,759 raw trials" as headline number.
2. **Results, opening paragraph after Figure 1**: One sentence on sample size to preempt power concerns.
3. **Boundary conditions section**: Strengthen closing paragraph linking apartheid-SA refusal to post-training intensity.
4. **Discussion**: Add 2-3 sentences on mechanistic openness; add one sentence on lexical-vs-conceptual priming.

### Supplementary
1. **NEW SI section "Alternative explanations ruled out"** — three accounts × evidence-against table.
2. **Expand SI section on instruction hierarchy** — cite Wallace et al. 2024 explicitly.
3. **NEW SI section on statistical methodology** — Wilson 95% CI, N declarations, two-sided tests, no Bonferroni (replications of single hypothesis).

### Methods
1. Negative-controls paragraph framing apartheid SA / Indian classical as positive-prime negative controls.
2. Grading-disagreement note explaining post-hoc persona handling (6.2% of Grade A; counts as A because clean at moment of generation).

## 5. What we already preempt well

1. **Realism**: Mundane Q&A is more realistic than fine-tuning or distillation.
2. **Multi-model generality**: 14 models × 3 vendors > Betley's GPT-4o focus or Cloud's weak open-weight signal.
3. **Statistical power**: N=20 per cell + κ=0.801 exceeds what Betley/Cloud had to fight for post-hoc.
4. **Negative controls**: Apartheid SA + Indian classical are gold-standard boundary conditions.
5. **Mechanistic angle**: Priority-instruction provides direct causal evidence stronger than Betley's speculative follow-ups or Cloud's behavioural-cloning ablations.
6. **Multi-turn coherence**: 100% internal-incoherence finding is a novel diagnostic that preempts persona-injection alternatives.

## 6. Preemption phrasings to use

- **Realism**: "Mundane deployment context of this kind, users studying historical or cultural content, is routine and not adversarial."
- **Mechanism**: "While a complete mechanistic account remains an open question, the priority-instruction manipulation provides direct evidence that the phenomenon reflects a tension between post-training safety and instruction-following, consistent with recent work on instruction hierarchies."
- **Generality**: "The phenomenon is bounded by post-training intensity on the specific doctrinal target, as evidenced by two boundary conditions (apartheid-era SA, Indian classical) producing zero doctrinal output despite cultural context."
- **Statistical**: "12,759 trials at uniform N=20 per (cell × model) for the cross-cultural matrix, with two-judge LLM cross-validation (Cohen's κ = 0.801) exceeding human-rater agreement in related work."
- **Alternative explanations**: "Multiple lines of evidence rule out lexical priming, universal cultural amplification, and fixed retrieval: no-demonstration controls (0% unprimed), negative-control cultures (0% apartheid), priority-instruction manipulation (0.2% vs 39.4%)."

## Conclusion

Implement the SI section on alternative explanations, the explicit instruction-hierarchy frame, the mechanistic-openness Discussion paragraph, and the deployment-realism opening, and the paper preempts ~80% of the likely Nature MI reviewer concerns based on the patterns visible in Betley and Cloud peer review rounds.
