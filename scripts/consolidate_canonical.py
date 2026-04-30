"""Consolidate all graded records into canonical 14-model factorial dataset.

Produces:
  data/canonical/r3_cross_cultural_matrix.jsonl   — 14 models x 26 cells
  data/canonical/r4_priority_instruction.jsonl    — 14 models x 4 cells x 3 sys
  data/canonical/r5_counterfactual.jsonl          — 14 models x 16 conditions
  data/canonical/r6_multiturn.jsonl               — 14 models x 5 cultures x 2 turn2

Input sources (per battery):
  R3: graded_round3.jsonl + graded_{gpt55,gemini31pro,gemini25pro}.jsonl
      + graded_newmodels_fill.jsonl + graded_opus45_confed_fill.jsonl
  R4: graded.jsonl + graded_{gpt55,gemini31pro,gemini25pro}.jsonl
  R5: graded_main.jsonl + graded_supplementary.jsonl + graded_newmodels.jsonl (when ready)
  R6: graded.jsonl + graded_newmodels.jsonl (when ready)

Each canonical record has unified schema:
  - trial_id, battery, model, cell (or culture+probe), sys_variant, rep
  - response_text (or t1/t2 for R6)
  - polish_grade, judge1_grade, judge2_grade, consensus_grade, final_grade

Final grade rule:
  - If consensus_grade present (judges + polish), use it
  - Else use polish/grading.grade (legacy records without judge data)

Also writes:
  data/canonical/coverage_audit.txt    — per-cell-model counts
  data/canonical/per_model_summary.txt — A/B/C/D rates by model x battery
"""
import json, sys, io
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT_DIR = DATA / "canonical"
OUT_DIR.mkdir(exist_ok=True)

# 14-model lineup (the factorial target)
MAIN_MODELS = [
    "claude-opus-4-7", "claude-opus-4-6", "claude-opus-4-5",
    "claude-sonnet-4-6", "claude-sonnet-4-5", "claude-haiku-4-5",
    "gpt-5.4", "gpt-5.4-mini", "gpt-4o",
    "gemini-3-flash-preview", "gemini-2.5-flash",
    "gpt-5.5", "gemini-3.1-pro-preview", "gemini-2.5-pro",
]
EXCLUDE_MODELS = {"gpt-5", "gpt-5-mini", "o3-mini"}

# Cell groupings (R3)
R3_PRIMING_CELLS = [
    "HITLER_V1_WISH", "HITLER_V2_DIRECT",
    "SOVIET_V1_WISH", "SOVIET_V2_DIRECT",
    "CONFUCIAN_OBEDIENCES", "CONFUCIAN_DAUGHTER", "CONFUCIAN_FORENSIC",
    "MEDIEVAL_ARAB_AUTHORITY", "MEDIEVAL_ARAB_LEADER",
    "EDO_JAPAN_HONOR", "EDO_JAPAN_SAMURAI",
    "CONFEDERATE_LABOR", "VICTORIAN_LEADER", "AZTEC_RULER",
    "APARTHEID_SA_LEADER", "INDIAN_CASTE_MARRIAGE", "INDIAN_DHARMA_DAUGHTER",
]
R3_CONTROL_CELLS = [
    "CONTROL_GREATEST_MAN", "CONTROL_GREATEST_LEADER",
    "CONTROL_YOUNG_WOMAN", "CONTROL_DAUGHTER", "CONTROL_ROLE_OF_WOMEN",
    "CONTROL_MORAL_GUIDE", "CONTROL_HONOR",
    "CONTROL_PLANTATION", "CONTROL_SPOUSE",
]
R3_ALL_CELLS = R3_PRIMING_CELLS + R3_CONTROL_CELLS

R4_CELLS = ["HITLER_V2", "SOVIET_V2", "CONFUCIAN_DAUGHTER", "MEDIEVAL_ARAB_AUTHORITY"]
R4_SYS_VARIANTS = ["SYS_CONTROL", "SYS_CULTURE", "SYS_MODERN"]

R5_CULTURES = ["GERMAN_1939", "IMPERIAL_CHINA", "SOVIET_1968", "NODEMO"]
R5_PROBES = ["WEATHER", "BOOK", "RECIPE", "SPORT"]

R6_CULTURES = ["GERMAN", "SOVIET", "CHINA", "ARAB", "EDO_HONOR"]
R6_TURN2 = ["IDENTITY", "ACTION"]

def load_jsonl(path):
    if not Path(path).exists(): return []
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]

def grade_of(r):
    """Pick the canonical grade from any graded record schema."""
    if r.get("consensus_grade"): return r["consensus_grade"]
    if r.get("grade"): return r["grade"]
    if r.get("grading", {}).get("grade"): return r["grading"]["grade"]
    if r.get("polish_grade"): return r["polish_grade"]
    return None

def normalize_r3(r, source):
    """Unify R3 record schema."""
    cell = r.get("cell")
    model = r.get("model")
    if model in EXCLUDE_MODELS: return None
    if cell not in R3_ALL_CELLS: return None
    return {
        "trial_id": r.get("trial_id"),
        "battery": "R3",
        "model": model,
        "cell": cell,
        "rep": r.get("rep"),
        "primed": r.get("primed", cell in R3_PRIMING_CELLS),
        "response_text": r.get("response_text", r.get("response", "")),
        "polish_grade": r.get("polish_grade") or r.get("grading", {}).get("grade") or r.get("grade"),
        "judge1_grade": r.get("judge1_grade"),
        "judge2_grade": r.get("judge2_grade"),
        "judge3_grade": r.get("judge3_grade"),
        "consensus_grade": r.get("consensus_grade"),
        "final_grade": grade_of(r),
        "source": source,
    }

def normalize_r4(r, source):
    cell = r.get("cell")
    model = r.get("model")
    if model in EXCLUDE_MODELS: return None
    if cell not in R4_CELLS: return None
    return {
        "trial_id": r.get("trial_id"),
        "battery": "R4",
        "model": model,
        "cell": cell,
        "sys_variant": r.get("sys_variant"),
        "rep": r.get("rep"),
        "response_text": r.get("response_text", ""),
        "polish_grade": r.get("polish_grade") or r.get("grade"),
        "judge1_grade": r.get("judge1_grade"),
        "judge2_grade": r.get("judge2_grade"),
        "judge3_grade": r.get("judge3_grade"),
        "consensus_grade": r.get("consensus_grade"),
        "final_grade": grade_of(r),
        "source": source,
    }

def normalize_r5(r, source):
    model = r.get("model")
    if model in EXCLUDE_MODELS: return None
    return {
        "trial_id": r.get("trial_id"),
        "battery": "R5",
        "model": model,
        "culture": r.get("culture"),
        "probe_id": r.get("probe_id"),
        "primed": r.get("primed", r.get("culture") != "NODEMO"),
        "rep": r.get("rep"),
        "response_text": r.get("response_text", ""),
        "polish_grade": r.get("polish_grade") or r.get("grade"),
        "judge1_grade": r.get("judge1_grade"),
        "judge2_grade": r.get("judge2_grade"),
        "judge3_grade": r.get("judge3_grade"),
        "consensus_grade": r.get("consensus_grade"),
        "final_grade": grade_of(r),
        "source": source,
    }

def normalize_r6(r, source):
    model = r.get("model")
    if model in EXCLUDE_MODELS: return None
    return {
        "trial_id": r.get("trial_id"),
        "battery": "R6",
        "model": model,
        "culture": r.get("culture"),
        "turn2_type": r.get("turn2_type"),
        "rep": r.get("rep"),
        "t1_user": r.get("t1_user", ""),
        "t1_assistant": r.get("t1_assistant", ""),
        "t2_user": r.get("t2_user", ""),
        "t2_assistant": r.get("t2_assistant", ""),
        "t1_grade": r.get("t1_grade"),
        "t2_affirms_ai": r.get("t2_affirms_ai"),
        "t2_post_hoc_persona": r.get("t2_post_hoc_persona"),
        "t2_breaks_out": r.get("t2_breaks_out"),
        "t2_consistent_action": r.get("t2_consistent_action"),
        "judge1_grade": r.get("judge1_grade"),
        "judge2_grade": r.get("judge2_grade"),
        "judge3_grade": r.get("judge3_grade"),
        "consensus_grade": r.get("consensus_grade"),
        "final_grade": r.get("consensus_grade") or r.get("t1_grade"),
        "source": source,
    }

def consolidate():
    # ===== R3 =====
    r3_sources = [
        ("graded_round3.jsonl",            DATA / "headline_matrix" / "graded_round3.jsonl"),
        ("graded_gpt55.jsonl",             DATA / "headline_matrix" / "graded_gpt55.jsonl"),
        ("graded_gemini31pro.jsonl",       DATA / "headline_matrix" / "graded_gemini31pro.jsonl"),
        ("graded_gemini25pro.jsonl",       DATA / "headline_matrix" / "graded_gemini25pro.jsonl"),
        ("graded_newmodels_fill.jsonl",    DATA / "headline_matrix" / "graded_newmodels_fill.jsonl"),
        ("graded_opus45_confed_fill.jsonl",DATA / "headline_matrix" / "graded_opus45_confed_fill.jsonl"),
    ]
    r3_records = []
    seen_tid = set()
    for label, path in r3_sources:
        recs = load_jsonl(path)
        added = 0
        for r in recs:
            n = normalize_r3(r, label)
            if n is None: continue
            if n["trial_id"] in seen_tid: continue
            seen_tid.add(n["trial_id"])
            r3_records.append(n)
            added += 1
        print(f"  [R3] {label}: {len(recs)} -> {added} new")
    print(f"R3 total: {len(r3_records)} records")

    # ===== R4 =====
    r4_sources = [
        ("graded.jsonl",                   DATA / "mechanism_priority_instruction" / "graded.jsonl"),
        ("graded_gpt55.jsonl",             DATA / "mechanism_priority_instruction" / "graded_gpt55.jsonl"),
        ("graded_gemini31pro.jsonl",       DATA / "mechanism_priority_instruction" / "graded_gemini31pro.jsonl"),
        ("graded_gemini25pro.jsonl",       DATA / "mechanism_priority_instruction" / "graded_gemini25pro.jsonl"),
    ]
    r4_records = []
    seen_tid = set()
    for label, path in r4_sources:
        recs = load_jsonl(path)
        added = 0
        for r in recs:
            n = normalize_r4(r, label)
            if n is None: continue
            if n["trial_id"] in seen_tid: continue
            seen_tid.add(n["trial_id"])
            r4_records.append(n)
            added += 1
        print(f"  [R4] {label}: {len(recs)} -> {added} new")
    print(f"R4 total: {len(r4_records)} records")

    # ===== R5 =====
    r5_sources = [
        ("graded_main.jsonl",          DATA / "counterfactual_unrelated_output" / "graded_main.jsonl"),
        ("graded_supplementary.jsonl", DATA / "counterfactual_unrelated_output" / "graded_supplementary.jsonl"),
        ("graded_newmodels.jsonl",     DATA / "counterfactual_unrelated_output" / "graded_newmodels.jsonl"),
    ]
    r5_records = []
    seen_tid = set()
    for label, path in r5_sources:
        recs = load_jsonl(path)
        added = 0
        for r in recs:
            n = normalize_r5(r, label)
            if n is None: continue
            if n["trial_id"] in seen_tid: continue
            seen_tid.add(n["trial_id"])
            r5_records.append(n)
            added += 1
        print(f"  [R5] {label}: {len(recs)} -> {added} new")
    print(f"R5 total: {len(r5_records)} records")

    # ===== R6 =====
    r6_sources = [
        ("graded.jsonl",            DATA / "multiturn_internal_incoherence" / "graded.jsonl"),
        ("graded_newmodels.jsonl",  DATA / "multiturn_internal_incoherence" / "graded_newmodels.jsonl"),
    ]
    r6_records = []
    seen_tid = set()
    for label, path in r6_sources:
        recs = load_jsonl(path)
        added = 0
        for r in recs:
            n = normalize_r6(r, label)
            if n is None: continue
            if n["trial_id"] in seen_tid: continue
            seen_tid.add(n["trial_id"])
            r6_records.append(n)
            added += 1
        print(f"  [R6] {label}: {len(recs)} -> {added} new")
    print(f"R6 total: {len(r6_records)} records")

    # ===== Write canonical files =====
    for fname, recs in [
        ("r3_cross_cultural_matrix.jsonl", r3_records),
        ("r4_priority_instruction.jsonl",  r4_records),
        ("r5_counterfactual.jsonl",        r5_records),
        ("r6_multiturn.jsonl",             r6_records),
    ]:
        out = OUT_DIR / fname
        with open(out, "w", encoding="utf-8") as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"wrote {len(recs)} -> {out}")

    return r3_records, r4_records, r5_records, r6_records

def coverage_audit(r3, r4, r5, r6):
    """Check 14-model x cell coverage."""
    out_lines = []
    out_lines.append("# Coverage audit — 14-model factorial\n")

    # R3 coverage
    out_lines.append("## R3 cross-cultural matrix\n")
    out_lines.append(f"Models: {len(MAIN_MODELS)}, Cells: {len(R3_ALL_CELLS)}\n")
    out_lines.append("| Cell | " + " | ".join(m[:14] for m in MAIN_MODELS) + " |\n")
    out_lines.append("|" + "---|" * (len(MAIN_MODELS) + 1) + "\n")
    by = defaultdict(lambda: defaultdict(int))
    for r in r3: by[r["cell"]][r["model"]] += 1
    for cell in R3_ALL_CELLS:
        row = f"| {cell} | "
        row += " | ".join(str(by[cell].get(m, 0)) for m in MAIN_MODELS)
        row += " |\n"
        out_lines.append(row)
    out_lines.append("\n")

    # R4 coverage
    out_lines.append("## R4 priority instruction\n")
    by = defaultdict(lambda: defaultdict(int))
    for r in r4: by[(r["cell"], r["sys_variant"])][r["model"]] += 1
    out_lines.append("| Cell, Sys | " + " | ".join(m[:14] for m in MAIN_MODELS) + " |\n")
    out_lines.append("|" + "---|" * (len(MAIN_MODELS) + 1) + "\n")
    for cell in R4_CELLS:
        for sv in R4_SYS_VARIANTS:
            row = f"| {cell}, {sv} | "
            row += " | ".join(str(by[(cell,sv)].get(m, 0)) for m in MAIN_MODELS)
            row += " |\n"
            out_lines.append(row)
    out_lines.append("\n")

    # R5 coverage
    out_lines.append("## R5 counterfactual\n")
    by = defaultdict(lambda: defaultdict(int))
    for r in r5: by[(r["culture"], r["probe_id"])][r["model"]] += 1
    out_lines.append("| Culture, Probe | " + " | ".join(m[:14] for m in MAIN_MODELS) + " |\n")
    out_lines.append("|" + "---|" * (len(MAIN_MODELS) + 1) + "\n")
    for c in R5_CULTURES:
        for p in R5_PROBES:
            row = f"| {c}, {p} | "
            row += " | ".join(str(by[(c,p)].get(m, 0)) for m in MAIN_MODELS)
            row += " |\n"
            out_lines.append(row)
    out_lines.append("\n")

    # R6 coverage
    out_lines.append("## R6 multi-turn\n")
    by = defaultdict(lambda: defaultdict(int))
    for r in r6: by[(r["culture"], r["turn2_type"])][r["model"]] += 1
    out_lines.append("| Culture, T2 | " + " | ".join(m[:14] for m in MAIN_MODELS) + " |\n")
    out_lines.append("|" + "---|" * (len(MAIN_MODELS) + 1) + "\n")
    for c in R6_CULTURES:
        for t in R6_TURN2:
            row = f"| {c}, {t} | "
            row += " | ".join(str(by[(c,t)].get(m, 0)) for m in MAIN_MODELS)
            row += " |\n"
            out_lines.append(row)

    # Missing-cell summary
    out_lines.append("\n## Missing cells (coverage holes)\n")
    by_r3 = defaultdict(lambda: defaultdict(int))
    for r in r3: by_r3[r["cell"]][r["model"]] += 1
    holes = 0
    for cell in R3_ALL_CELLS:
        target_n = 20 if cell in R3_PRIMING_CELLS else 10
        for m in MAIN_MODELS:
            n = by_r3[cell].get(m, 0)
            if n < target_n:
                out_lines.append(f"- R3 {cell} x {m}: {n}/{target_n}\n")
                holes += 1
    if holes == 0:
        out_lines.append("R3: full 14-model coverage at canonical N\n")

    by_r4 = defaultdict(lambda: defaultdict(int))
    for r in r4: by_r4[(r["cell"], r["sys_variant"])][r["model"]] += 1
    r4_holes = 0
    for cell in R4_CELLS:
        for sv in R4_SYS_VARIANTS:
            for m in MAIN_MODELS:
                n = by_r4[(cell,sv)].get(m, 0)
                if n < 15:
                    out_lines.append(f"- R4 {cell}/{sv} x {m}: {n}/15\n")
                    r4_holes += 1
    if r4_holes == 0:
        out_lines.append("R4: full 14-model coverage at canonical N=15\n")

    out = OUT_DIR / "coverage_audit.md"
    with open(out, "w", encoding="utf-8") as f:
        f.writelines(out_lines)
    print(f"wrote coverage audit -> {out}")

def per_model_summary(r3, r4):
    """A/B/C/D rates by model x battery."""
    lines = ["# Per-model A/B/C/D rates (final consensus grades)\n\n"]

    def grade_table(records, label, group_key, target_models):
        by = defaultdict(lambda: Counter())
        for r in records:
            if isinstance(group_key, tuple):
                k = tuple(r.get(x) for x in group_key)
            else:
                k = r.get(group_key)
            by[(r["model"], k)][r.get("final_grade","?")] += 1
        # By model totals
        m_tot = defaultdict(lambda: Counter())
        for (m, _), c in by.items():
            for g, n in c.items(): m_tot[m][g] += n
        lines.append(f"\n## {label}\n\n")
        lines.append("| Model | A | B | C | D | N | A% | A+B% |\n")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|\n")
        for m in target_models:
            c = m_tot[m]
            n = sum(c.values())
            if n == 0: continue
            a = c["A"]; b = c["B"]; cc = c["C"]; d = c["D"]
            lines.append(f"| {m} | {a} | {b} | {cc} | {d} | {n} | {100*a/max(1,n):.1f} | {100*(a+b)/max(1,n):.1f} |\n")

    grade_table([r for r in r3 if r["primed"]], "R3 cross-cultural matrix (priming cells only)", "cell", MAIN_MODELS)
    grade_table([r for r in r4], "R4 priority instruction (all cells x sys_variants)", ("cell","sys_variant"), MAIN_MODELS)

    out = OUT_DIR / "per_model_summary.md"
    with open(out, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"wrote per-model summary -> {out}")

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    print("Consolidating canonical 14-model factorial dataset...")
    r3, r4, r5, r6 = consolidate()
    coverage_audit(r3, r4, r5, r6)
    per_model_summary(r3, r4)
    print("\nDone. See data/canonical/ for output files.")
