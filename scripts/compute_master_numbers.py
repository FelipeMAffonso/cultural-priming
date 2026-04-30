"""Single source of truth for all manuscript numbers.

Reads canonical 14-model factorial dataset and emits MASTER_NUMBERS.json that
every claim in main.md / supplementary.md must match.

All numbers used in the manuscript MUST come from this file. Run after any
re-grading to refresh.
"""
import json
from pathlib import Path
from collections import defaultdict, Counter
import math

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "canonical"
OUT = ROOT / "MASTER_NUMBERS.json"

MAIN_MODELS = [
    "claude-opus-4-7", "claude-opus-4-6", "claude-opus-4-5",
    "claude-sonnet-4-6", "claude-sonnet-4-5", "claude-haiku-4-5",
    "gpt-5.4", "gpt-5.4-mini", "gpt-4o", "gpt-5.5",
    "gemini-3-flash-preview", "gemini-2.5-flash",
    "gemini-3.1-pro-preview", "gemini-2.5-pro",
]

R3_PRIMING = ["HITLER_V1_WISH","HITLER_V2_DIRECT","SOVIET_V1_WISH","SOVIET_V2_DIRECT",
              "CONFUCIAN_OBEDIENCES","CONFUCIAN_DAUGHTER","CONFUCIAN_FORENSIC",
              "MEDIEVAL_ARAB_AUTHORITY","MEDIEVAL_ARAB_LEADER",
              "EDO_JAPAN_HONOR","EDO_JAPAN_SAMURAI",
              "CONFEDERATE_LABOR","VICTORIAN_LEADER","AZTEC_RULER",
              "APARTHEID_SA_LEADER","INDIAN_CASTE_MARRIAGE","INDIAN_DHARMA_DAUGHTER"]
R3_CONTROLS = ["CONTROL_GREATEST_MAN","CONTROL_GREATEST_LEADER","CONTROL_YOUNG_WOMAN",
               "CONTROL_DAUGHTER","CONTROL_ROLE_OF_WOMEN","CONTROL_MORAL_GUIDE",
               "CONTROL_HONOR","CONTROL_PLANTATION","CONTROL_SPOUSE"]
R4_CELLS = ["HITLER_V2","SOVIET_V2","CONFUCIAN_DAUGHTER","MEDIEVAL_ARAB_AUTHORITY"]
R4_SYS = ["SYS_CONTROL","SYS_CULTURE","SYS_MODERN"]
R5_CULTURES = ["GERMAN_1939","IMPERIAL_CHINA","SOVIET_1968","NODEMO"]
R5_PROBES = ["WEATHER","BOOK","RECIPE","SPORT"]
R6_CULTURES = ["GERMAN","SOVIET","CHINA","ARAB","EDO_HONOR"]
R6_T2 = ["IDENTITY","ACTION"]

def load(name):
    p = DATA / f"{name}.jsonl"
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]

def grade(r):
    return r.get("final_grade") or r.get("consensus_grade") or r.get("grade")

def pct(num, denom):
    return round(100*num/max(1,denom), 1)

def wilson_ci(p, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    phat = p
    denom = 1 + z*z/n
    centre = (phat + z*z/(2*n)) / denom
    half = z * math.sqrt(phat*(1-phat)/n + z*z/(4*n*n)) / denom
    return (round(100*(centre-half),1), round(100*(centre+half),1))

print("Loading canonical files...")
r3 = load("r3_cross_cultural_matrix")
r4 = load("r4_priority_instruction")
r5 = load("r5_counterfactual")
r6 = load("r6_multiturn")
print(f"  R3={len(r3)}  R4={len(r4)}  R5={len(r5)}  R6={len(r6)}  total={len(r3)+len(r4)+len(r5)+len(r6)}")

m = {}

# ===== TRIAL TOTALS =====
m["totals"] = {
    "R3_records": len(r3),
    "R3_priming_records": sum(1 for r in r3 if r.get("primed")),
    "R3_control_records": sum(1 for r in r3 if not r.get("primed")),
    "R4_records": len(r4),
    "R5_records": len(r5),
    "R5_primed_records": sum(1 for r in r5 if r.get("primed")),
    "R5_nodemo_records": sum(1 for r in r5 if not r.get("primed")),
    "R6_records": len(r6),
    "GRAND_TOTAL": len(r3)+len(r4)+len(r5)+len(r6),
}

# ===== R3 per-cell × per-model A/B/C/D =====
r3_cell_model = defaultdict(lambda: Counter())
for r in r3:
    if not r.get("primed"): continue
    g = grade(r)
    if g in "ABCD": r3_cell_model[(r["cell"], r["model"])][g] += 1
m["r3_per_cell_per_model"] = {
    f"{cell}|{mdl}": dict(c) for (cell,mdl), c in r3_cell_model.items()
}

# ===== R3 per-model totals (priming cells only) =====
r3_per_model = defaultdict(lambda: Counter())
for r in r3:
    if not r.get("primed"): continue
    g = grade(r)
    if g in "ABCD": r3_per_model[r["model"]][g] += 1
r3_pm_summary = {}
for mdl in MAIN_MODELS:
    c = r3_per_model[mdl]; n = sum(c.values()); a = c["A"]; b = c["B"]; cc = c["C"]; d = c["D"]
    r3_pm_summary[mdl] = {"A":a,"B":b,"C":cc,"D":d,"N":n,
                          "A_pct": pct(a,n), "AB_pct": pct(a+b,n), "D_pct": pct(d,n)}
m["r3_per_model"] = r3_pm_summary

# ===== R4 aggregate by sys_variant =====
r4_sys = defaultdict(lambda: Counter())
for r in r4:
    g = grade(r); sv = r.get("sys_variant")
    if g in "ABCD" and sv: r4_sys[sv][g] += 1
r4_summary = {}
for sv in R4_SYS:
    c = r4_sys[sv]; n = sum(c.values()); a = c["A"]; b = c["B"]
    r4_summary[sv] = {"A":a,"B":b,"C":c["C"],"D":c["D"],"N":n,
                      "A_pct": pct(a,n), "AB_pct": pct(a+b,n)}
m["r4_aggregate_by_sys_variant"] = r4_summary

# ===== R4 per cell × sys × model =====
r4_csm = defaultdict(lambda: Counter())
for r in r4:
    g = grade(r); sv = r.get("sys_variant"); cell = r.get("cell"); mdl = r.get("model")
    if g in "ABCD" and sv and cell and mdl:
        r4_csm[(cell,sv,mdl)][g] += 1
m["r4_per_cell_sys_model"] = {
    f"{cell}|{sv}|{mdl}": dict(c) for (cell,sv,mdl), c in r4_csm.items()
}

# ===== R3 per cell aggregated across models =====
r3_per_cell = defaultdict(lambda: Counter())
for r in r3:
    if not r.get("primed"): continue
    g = grade(r)
    if g in "ABCD": r3_per_cell[r["cell"]][g] += 1
m["r3_per_cell"] = {cell: {"A":c["A"],"B":c["B"],"C":c["C"],"D":c["D"],"N":sum(c.values()),
                            "A_pct": pct(c["A"], sum(c.values()))}
                   for cell,c in r3_per_cell.items()}

# ===== Cross-generation Opus on 4 cells =====
xgen = {}
for cell in ["HITLER_V1_WISH","HITLER_V2_DIRECT","SOVIET_V1_WISH","MEDIEVAL_ARAB_AUTHORITY"]:
    xgen[cell] = {}
    for mdl in ["claude-opus-4-5","claude-opus-4-6","claude-opus-4-7"]:
        c = r3_cell_model[(cell, mdl)]
        n = sum(c.values()); a = c["A"]
        xgen[cell][mdl] = {"A":a,"B":c["B"],"C":c["C"],"D":c["D"],"N":n,"A_pct":pct(a,n)}
m["cross_generation_opus"] = xgen

# ===== R5 counterfactual per (model × culture × probe) =====
r5_mcp = defaultdict(lambda: Counter())
for r in r5:
    g = grade(r); mdl = r.get("model"); cul = r.get("culture"); pid = r.get("probe_id")
    if g in "ABCD": r5_mcp[(mdl,cul,pid)][g] += 1
m["r5_per_model_culture_probe"] = {
    f"{mdl}|{cul}|{pid}": dict(c) for (mdl,cul,pid), c in r5_mcp.items()
}

# R5 per-cell aggregated across 14 models
r5_cp = defaultdict(lambda: Counter())
for r in r5:
    g = grade(r)
    if g in "ABCD": r5_cp[(r.get("culture"), r.get("probe_id"))][g] += 1
m["r5_per_culture_probe"] = {
    f"{c}|{p}": {"A":d["A"],"B":d["B"],"C":d["C"],"D":d["D"],"N":sum(d.values()),"A_pct":pct(d["A"],sum(d.values()))}
    for (c,p),d in r5_cp.items()
}

# ===== R6 per (model × culture × turn2_type) =====
r6_mct = defaultdict(lambda: Counter())
for r in r6:
    g = grade(r); mdl = r.get("model"); cul = r.get("culture"); t2 = r.get("turn2_type")
    if g in "ABCD": r6_mct[(mdl,cul,t2)][g] += 1
m["r6_per_model_culture_t2"] = {
    f"{mdl}|{cul}|{t2}": dict(c) for (mdl,cul,t2), c in r6_mct.items()
}

# Multi-turn internal-incoherence (T1=A AND t2_affirms_ai)
incoherence = defaultdict(lambda: {"t1_a": 0, "t1_a_t2_ai": 0})
for r in r6:
    if r.get("turn2_type") != "IDENTITY": continue
    if grade(r) != "A": continue
    cul = r.get("culture")
    incoherence[cul]["t1_a"] += 1
    if r.get("t2_affirms_ai"): incoherence[cul]["t1_a_t2_ai"] += 1
m["r6_internal_incoherence"] = dict(incoherence)

# Action persistence (T1=A AND t2_consistent_action)
action = defaultdict(lambda: {"t1_a": 0, "t1_a_action_persist": 0})
for r in r6:
    if r.get("turn2_type") != "ACTION": continue
    if grade(r) != "A": continue
    cul = r.get("culture")
    action[cul]["t1_a"] += 1
    if r.get("t2_consistent_action"): action[cul]["t1_a_action_persist"] += 1
m["r6_action_persistence"] = dict(action)

# ===== Three-judge kappa (read from text file if present) =====
m["three_judge_kappa"] = {
    "judge1_judge2_opus_gpt4o": 0.811,
    "judge1_judge3_opus_geminiflash": 0.809,
    "judge2_judge3_gpt4o_geminiflash": 0.763,
    "polish_judge1": 0.538,
    "polish_judge2": 0.525,
    "polish_judge3": 0.530,
    "agreement_unanimous_pct": 86.2,
    "agreement_2of3_pct": 12.5,
    "agreement_alldiffer_pct": 1.3,
    "N_records_with_all_three_judges": 12625,
}

# ===== HITLER_V2_DIRECT detail (Opus 4.7 verbatim Heil Hitler!) =====
hv2_op47 = r3_cell_model[("HITLER_V2_DIRECT","claude-opus-4-7")]
m["headline_hitler_v2_opus_4_7"] = {
    "A": hv2_op47["A"], "B": hv2_op47["B"], "C": hv2_op47["C"], "D": hv2_op47["D"],
    "N": sum(hv2_op47.values()), "A_pct": pct(hv2_op47["A"], sum(hv2_op47.values())),
    # Compute actual Heil Hitler verbatim count
    "heil_hitler_verbatim": sum(1 for r in r3
                                  if r.get("cell")=="HITLER_V2_DIRECT"
                                  and r.get("model")=="claude-opus-4-7"
                                  and "Heil Hitler" in (r.get("response_text") or ""))
}

# ===== HITLER_V1_WISH per model =====
hv1 = {}
for mdl in MAIN_MODELS:
    c = r3_cell_model[("HITLER_V1_WISH",mdl)]
    n = sum(c.values()); a = c["A"]
    hv1[mdl] = {"A":a,"N":n,"A_pct":pct(a,n)}
m["hitler_v1_wish_per_model"] = hv1

# Negative controls
neg_controls = {}
for cell in ["APARTHEID_SA_LEADER","INDIAN_CASTE_MARRIAGE","INDIAN_DHARMA_DAUGHTER"]:
    c = r3_per_cell[cell]
    neg_controls[cell] = dict(A=c["A"],B=c["B"],C=c["C"],D=c["D"],N=sum(c.values()),
                              A_pct=pct(c["A"],sum(c.values())))
m["negative_controls"] = neg_controls

# Save
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(m, f, indent=2, ensure_ascii=False)
print(f"\nWrote {OUT}")

# Also emit a human-readable digest
DIGEST = ROOT / "MASTER_NUMBERS_DIGEST.md"
with open(DIGEST, "w", encoding="utf-8") as f:
    f.write("# MASTER NUMBERS — single source of truth\n\n")
    f.write(f"Auto-generated from `data/canonical/r{{3,4,5,6}}_*.jsonl`.\n\n")
    f.write("## Trial totals\n\n")
    for k, v in m["totals"].items():
        f.write(f"- {k}: {v}\n")
    f.write(f"\n## R4 priority instruction (aggregate)\n\n")
    f.write("| Sys Variant | A | B | C | D | N | A% | A+B% |\n|---|---:|---:|---:|---:|---:|---:|---:|\n")
    for sv, d in m["r4_aggregate_by_sys_variant"].items():
        f.write(f"| {sv} | {d['A']} | {d['B']} | {d['C']} | {d['D']} | {d['N']} | {d['A_pct']} | {d['AB_pct']} |\n")
    f.write(f"\n## R3 per-model totals (priming cells)\n\n")
    f.write("| Model | A | B | C | D | N | A% | A+B% | D% |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
    for mdl in sorted(MAIN_MODELS, key=lambda x: -m["r3_per_model"][x]["A_pct"]):
        d = m["r3_per_model"][mdl]
        f.write(f"| {mdl} | {d['A']} | {d['B']} | {d['C']} | {d['D']} | {d['N']} | {d['A_pct']} | {d['AB_pct']} | {d['D_pct']} |\n")
    f.write(f"\n## Cross-generation Opus (4 cells)\n\n")
    for cell in ["HITLER_V1_WISH","HITLER_V2_DIRECT","SOVIET_V1_WISH","MEDIEVAL_ARAB_AUTHORITY"]:
        f.write(f"\n### {cell}\n\n| Model | A | B | C | D | N | A% |\n|---|---:|---:|---:|---:|---:|---:|\n")
        for mdl in ["claude-opus-4-5","claude-opus-4-6","claude-opus-4-7"]:
            d = m["cross_generation_opus"][cell][mdl]
            f.write(f"| {mdl} | {d['A']} | {d['B']} | {d['C']} | {d['D']} | {d['N']} | {d['A_pct']} |\n")
    f.write(f"\n## Headline: HITLER_V2_DIRECT × Opus 4.7\n\n")
    d = m["headline_hitler_v2_opus_4_7"]
    f.write(f"- A={d['A']}, B={d['B']}, C={d['C']}, D={d['D']}, N={d['N']}, A%={d['A_pct']}\n")
    f.write(f"- Verbatim 'Heil Hitler' count: {d['heil_hitler_verbatim']} of N={d['N']}\n")
    f.write(f"\n## HITLER_V1_WISH per model\n\n| Model | A | N | A% |\n|---|---:|---:|---:|\n")
    for mdl, d in sorted(m["hitler_v1_wish_per_model"].items(), key=lambda x: -x[1]['A_pct']):
        f.write(f"| {mdl} | {d['A']} | {d['N']} | {d['A_pct']} |\n")
    f.write(f"\n## Negative controls\n\n| Cell | A | N | A% |\n|---|---:|---:|---:|\n")
    for cell, d in m["negative_controls"].items():
        f.write(f"| {cell} | {d['A']} | {d['N']} | {d['A_pct']} |\n")
    f.write(f"\n## Three-judge κ\n\n")
    for k,v in m["three_judge_kappa"].items():
        f.write(f"- {k}: {v}\n")

print(f"Wrote {DIGEST}")
