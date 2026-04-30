"""Grade R9 (format ablation) + R10 (dose-response) using grade_round3 logic.

R9: 360 records on HITLER cell across 3 formats (Q&A / paragraph / diary).
R10: 1,080 records on GERMAN/SOVIET/CHINA across 6 doses (d=0 to d=5).

Maps each record to its R3-equivalent cell, applies grade_round3.grade_record,
then writes graded.jsonl alongside raw.jsonl.

Outputs:
  data/mechanism_format_ablation/graded.jsonl
  data/mechanism_dose_response/graded.jsonl
"""
import json, sys
from pathlib import Path
from collections import Counter, defaultdict

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(SCRIPT_DIR))
import grade_round3

# R10 culture -> R3 cell mapping
R10_CULTURE_TO_R3 = {
    "GERMAN":  "HITLER_V1_WISH",
    "SOVIET":  "SOVIET_V1_WISH",
    "CHINA":   "CONFUCIAN_OBEDIENCES",
}

def grade_one(rec, cell_override):
    synthetic = {"cell": cell_override, "response_text": rec.get("response_text","")}
    out = grade_round3.grade_record(synthetic)
    if isinstance(out, dict):
        return out.get("grade","D"), out.get("reason","")
    return "D", str(out)

def grade_r9():
    raw_path = ROOT / "data" / "mechanism_format_ablation" / "raw.jsonl"
    out_path = ROOT / "data" / "mechanism_format_ablation" / "graded.jsonl"
    recs = [json.loads(l) for l in open(raw_path, encoding="utf-8") if l.strip()]
    # All R9 records are on HITLER cell with greatest-man probe -> map to HITLER_V1_WISH
    with open(out_path, "w", encoding="utf-8") as f:
        for r in recs:
            grade, reason = grade_one(r, "HITLER_V1_WISH")
            r["polish_grade"] = grade
            r["polish_reason"] = reason
            r["grade"] = grade
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"R9 graded: {len(recs)} records -> {out_path}")
    # Summary by variant x model
    table = defaultdict(lambda: Counter())
    for r in recs:
        table[(r.get("variant"), r.get("model"))][r["grade"]] += 1
    print("\nR9 by variant x model:")
    for (v, m), c in sorted(table.items()):
        n = sum(c.values()); a = c["A"]
        print(f"  {v:15s} {m:30s} A={a}/{n} = {100*a/max(1,n):.1f}%  (B={c['B']} C={c['C']} D={c['D']})")
    # By variant aggregate
    by_v = defaultdict(lambda: Counter())
    for r in recs: by_v[r.get("variant")][r["grade"]] += 1
    print("\nR9 by variant aggregate:")
    for v, c in sorted(by_v.items()):
        n = sum(c.values()); a = c["A"]
        print(f"  {v:15s}  A={a}/{n} = {100*a/max(1,n):.1f}%")

def grade_r10():
    raw_path = ROOT / "data" / "mechanism_dose_response" / "raw.jsonl"
    out_path = ROOT / "data" / "mechanism_dose_response" / "graded.jsonl"
    recs = [json.loads(l) for l in open(raw_path, encoding="utf-8") if l.strip()]
    with open(out_path, "w", encoding="utf-8") as f:
        for r in recs:
            cell = R10_CULTURE_TO_R3.get(r.get("culture"), "HITLER_V1_WISH")
            grade, reason = grade_one(r, cell)
            r["polish_grade"] = grade
            r["polish_reason"] = reason
            r["grade"] = grade
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nR10 graded: {len(recs)} records -> {out_path}")
    # Summary by culture x dose
    table = defaultdict(lambda: Counter())
    for r in recs:
        table[(r.get("culture"), r.get("dose"))][r["grade"]] += 1
    print("\nR10 dose-response (Grade A% by culture x dose, pooled across models):")
    print(f"  {'culture':10s}  d=0   d=1   d=2   d=3   d=4   d=5")
    for cul in ["GERMAN","CHINA","SOVIET"]:
        row = f"  {cul:10s}  "
        for d in range(6):
            c = table[(cul, d)]; n = sum(c.values()); a = c["A"]
            row += f"{100*a/max(1,n):4.0f}%  "
        print(row)
    # Per model x culture x dose
    print("\nR10 per (model x culture x dose) Grade A:")
    pmcd = defaultdict(lambda: Counter())
    for r in recs:
        pmcd[(r.get("model"), r.get("culture"), r.get("dose"))][r["grade"]] += 1
    for (m, cul, d), c in sorted(pmcd.items()):
        n = sum(c.values()); a = c["A"]
        print(f"  {m:30s} {cul:10s} d={d}  A={a}/{n}={100*a/max(1,n):.0f}%")

if __name__ == "__main__":
    grade_r9()
    grade_r10()
