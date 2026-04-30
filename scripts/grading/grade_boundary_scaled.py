"""Grade the 1,400 scaled boundary trials using grade_round3 logic.

Maps each scaled cell to its R3 equivalent, applies grade_round3.grade_record,
writes graded.jsonl alongside raw_scaled.jsonl.

Cell mapping:
  GERMAN_PRENAZI               -> HITLER_V1_WISH
  RUSSIAN_TSARIST              -> SOVIET_V1_WISH
  JAPANESE_MEIJI_MODERN        -> EDO_JAPAN_HONOR
  ARAB_MODERN                  -> MEDIEVAL_ARAB_AUTHORITY
  CHINESE_MODERN               -> CONFUCIAN_OBEDIENCES
  SYNTHETIC_GREATEST_MAN       -> HITLER_V1_WISH
  SYNTHETIC_GREATEST_LEADER    -> SOVIET_V1_WISH
  SYNTHETIC_SAMURAI_HONOUR     -> EDO_JAPAN_HONOR
  SYNTHETIC_MORAL_GUIDE        -> MEDIEVAL_ARAB_AUTHORITY
  SYNTHETIC_YOUNG_WOMAN        -> CONFUCIAN_OBEDIENCES
"""
import json, sys
from pathlib import Path
from collections import Counter, defaultdict

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(SCRIPT_DIR))
import grade_round3

CELL_MAP = {
    "GERMAN_PRENAZI":            "HITLER_V1_WISH",
    "RUSSIAN_TSARIST":           "SOVIET_V1_WISH",
    "JAPANESE_MEIJI_MODERN":     "EDO_JAPAN_HONOR",
    "ARAB_MODERN":               "MEDIEVAL_ARAB_AUTHORITY",
    "CHINESE_MODERN":            "CONFUCIAN_OBEDIENCES",
    "SYNTHETIC_GREATEST_MAN":    "HITLER_V1_WISH",
    "SYNTHETIC_GREATEST_LEADER": "SOVIET_V1_WISH",
    "SYNTHETIC_SAMURAI_HONOUR":  "EDO_JAPAN_HONOR",
    "SYNTHETIC_MORAL_GUIDE":     "MEDIEVAL_ARAB_AUTHORITY",
    "SYNTHETIC_YOUNG_WOMAN":     "CONFUCIAN_OBEDIENCES",
}


def grade_one(rec, mapped_cell):
    synthetic = {"cell": mapped_cell, "response_text": rec.get("response_text", "")}
    out = grade_round3.grade_record(synthetic)
    if isinstance(out, dict):
        return out.get("grade", "D"), out.get("reason", "")
    return "D", str(out)


def main():
    raw = ROOT / "data" / "boundary_tests" / "raw_scaled.jsonl"
    out = ROOT / "data" / "boundary_tests" / "graded_scaled.jsonl"
    recs = [json.loads(l) for l in open(raw, encoding="utf-8") if l.strip()]
    with open(out, "w", encoding="utf-8") as f:
        for r in recs:
            cell = CELL_MAP.get(r.get("cell"), "HITLER_V1_WISH")
            grade, reason = grade_one(r, cell)
            r["mapped_cell"] = cell
            r["polish_grade"] = grade
            r["polish_reason"] = reason
            r["grade"] = grade
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Graded {len(recs)} records -> {out}")

    # Aggregate by cell
    by_cell = defaultdict(lambda: Counter())
    for r in recs:
        by_cell[r["cell"]][r["grade"]] += 1
    print("\nBy cell (Grade A%) — pooled across 14 models:")
    for cell, c in sorted(by_cell.items()):
        n = sum(c.values())
        a = c["A"]
        print(f"  {cell:30s}  A={a:3d}/{n:3d} = {100*a/max(1,n):5.1f}%   "
              f"(B={c['B']} C={c['C']} D={c['D']})")

    # Aggregate by cell x model
    by_cm = defaultdict(lambda: Counter())
    for r in recs:
        by_cm[(r["cell"], r["model"])][r["grade"]] += 1
    print("\nBy cell x model (Grade A only):")
    last_cell = None
    for (cell, model), c in sorted(by_cm.items()):
        if cell != last_cell:
            print(f"\n  -- {cell} --")
            last_cell = cell
        n = sum(c.values())
        a = c["A"]
        print(f"    {model:30s}  A={a}/{n}")

    # Aggregate era-shifted vs synthetic
    era_total = Counter()
    syn_total = Counter()
    for r in recs:
        if r["cell"].startswith("SYNTHETIC_"):
            syn_total[r["grade"]] += 1
        else:
            era_total[r["grade"]] += 1
    print("\n=== AGGREGATES ===")
    n_era = sum(era_total.values()); a_era = era_total["A"]
    n_syn = sum(syn_total.values()); a_syn = syn_total["A"]
    print(f"  Era-shifted (5 cells x 14 models x 10 reps): "
          f"A={a_era}/{n_era} = {100*a_era/max(1,n_era):.1f}%")
    print(f"  Synthetic    (5 probes x 14 models x 10 reps): "
          f"A={a_syn}/{n_syn} = {100*a_syn/max(1,n_syn):.1f}%")


if __name__ == "__main__":
    main()
