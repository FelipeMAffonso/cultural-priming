# -*- coding: utf-8 -*-
"""Extract clean verbatim T1+T2 examples for the report."""
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

GRADED = r"C:/Users/fmarine/Dropbox/Felipe/CLAUDE CODE/academic-research/projects/IDEAS-DRAFTS/llm-behavior-ideas/loop/papers/_round6_polish_work/graded.jsonl"

rows = []
with open(GRADED, 'r', encoding='utf-8') as f:
    for ln in f:
        if ln.strip():
            rows.append(json.loads(ln))


def show(r, label=""):
    print(f"\n{'='*100}\n{label}")
    print(f"culture={r['culture']} | model={r['model']} | turn2={r['turn2_type']} | rep={r['rep']} | t1_grade={r['t1_grade']}")
    print(f"\nT1_USER (truncated): {r['t1_user'][:300]}...")
    print(f"\n[T1_ASSISTANT]\n{r['t1_assistant']}")
    print(f"\n[T2_USER] {r['t2_user']}")
    print(f"\n[T2_ASSISTANT]\n{r['t2_assistant']}")
    print(f"\nflags: t2_affirms_ai={r['t2_affirms_ai']} t2_post_hoc_persona={r['t2_post_hoc_persona']} t2_consistent_action={r['t2_consistent_action']} t2_breaks_out={r['t2_breaks_out']}")


# ===== Internal-incoherence examples (T1=A AND T2_affirms_AI), IDENTITY =====
print("\n\n##### INCOHERENCE EXAMPLES (T1=A doctrinal + T2 affirms AI identity) #####")
shown = set()
target_combos = [
    ('GERMAN', 'gemini-3-flash-preview'),
    ('GERMAN', 'claude-opus-4-7'),
    ('SOVIET', 'claude-sonnet-4-5'),
    ('SOVIET', 'gemini-3-flash-preview'),
    ('SOVIET', 'claude-opus-4-7'),
    ('CHINA', 'gemini-3-flash-preview'),
    ('CHINA', 'claude-sonnet-4-6'),
    ('EDO_HONOR', 'gemini-3-flash-preview'),
    ('EDO_HONOR', 'gpt-5.4-mini'),
    ('EDO_HONOR', 'claude-sonnet-4-5'),
    ('ARAB', 'claude-opus-4-7'),
    ('ARAB', 'claude-sonnet-4-6'),
]
for combo in target_combos:
    cult, model = combo
    for r in rows:
        if r['culture']==cult and r['model']==model and r['turn2_type']=='IDENTITY' and r['t1_grade']=='A' and r['t2_affirms_ai']:
            key = (cult, model)
            if key in shown: continue
            shown.add(key)
            show(r, f"INCOH | {cult} | {model}")
            break

# ===== Action persistence examples =====
print("\n\n##### ACTION-PERSISTENCE EXAMPLES (T1=A + T2 gives 3 doctrinal steps) #####")
shown = set()
action_targets = [
    ('GERMAN', 'gemini-3-flash-preview'),
    ('GERMAN', 'claude-opus-4-7'),
    ('SOVIET', 'claude-opus-4-7'),
    ('CHINA', 'claude-opus-4-7'),
    ('EDO_HONOR', 'claude-sonnet-4-6'),
    ('EDO_HONOR', 'gemini-3-flash-preview'),
    ('EDO_HONOR', 'gpt-4o'),
    ('EDO_HONOR', 'gpt-5.4-mini'),
    ('EDO_HONOR', 'gpt-5.4'),
    ('ARAB', 'gemini-3-flash-preview'),
]
for combo in action_targets:
    cult, model = combo
    for r in rows:
        if r['culture']==cult and r['model']==model and r['turn2_type']=='ACTION' and r['t1_grade']=='A' and r['t2_consistent_action']:
            key = (cult, model)
            if key in shown: continue
            shown.add(key)
            show(r, f"PERSIST | {cult} | {model}")
            break

# ===== Break-out examples (T2 refuses) =====
print("\n\n##### BREAK-OUT EXAMPLES (T1=A doctrinal + T2 refuses / breaks character) #####")
shown = set()
bo_targets = [
    ('EDO_HONOR', 'claude-haiku-4-5'),
    ('EDO_HONOR', 'claude-opus-4-5'),
    ('EDO_HONOR', 'claude-opus-4-7'),
    ('GERMAN', 'claude-opus-4-7'),
    ('SOVIET', 'claude-haiku-4-5'),
    ('CHINA', 'claude-sonnet-4-5'),
]
for combo in bo_targets:
    cult, model = combo
    for r in rows:
        if r['culture']==cult and r['model']==model and r['turn2_type']=='ACTION' and r['t2_breaks_out']:
            # Prefer cases where T1 was at least B (doctrinal-ish) — but we'll show
            # break-outs even after C / D where the T1 still mentioned the doctrine.
            key = (cult, model)
            if key in shown: continue
            shown.add(key)
            show(r, f"BREAK | {cult} | {model}")
            break

# ===== Post-hoc persona examples =====
print("\n\n##### POST-HOC PERSONA RETROACTIVE CLAIM EXAMPLES #####")
shown = set()
ph_targets = [
    ('SOVIET', 'claude-sonnet-4-5'),
    ('GERMAN', 'claude-opus-4-7'),
    ('GERMAN', 'claude-haiku-4-5'),
    ('EDO_HONOR', 'claude-sonnet-4-5'),
    ('EDO_HONOR', 'gemini-3-flash-preview'),
    ('SOVIET', 'claude-opus-4-6'),
    ('CHINA', 'claude-sonnet-4-5'),
]
for combo in ph_targets:
    cult, model = combo
    for r in rows:
        if r['culture']==cult and r['model']==model and r['t2_post_hoc_persona']:
            key = (cult, model)
            if key in shown: continue
            shown.add(key)
            show(r, f"POST-HOC | {cult} | {model}")
            break
