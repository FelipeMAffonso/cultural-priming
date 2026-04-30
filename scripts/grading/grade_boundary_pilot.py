"""Grade the 200-trial boundary pilot (raw.jsonl) with regex + three judges.

Cells:
  PRENAZI_GERMAN    -> HITLER_V1_WISH (greatest-man probe)
  SYNTHETIC_CULTURE -> HITLER_V1_WISH (greatest-man probe with synthetic markers)

Outputs:
  data/boundary_tests/graded_pilot.jsonl                 (regex polish_grade)
  data/boundary_tests/graded_pilot_threejudge.jsonl      (+ judge1/2/3 + consensus)
"""
import os, sys, json, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(SCRIPT_DIR))
load_dotenv(ROOT / "scripts" / ".env")

import grade_round3
from three_judge_boundary import (
    JUDGE_PROMPT, call_anth, call_oai, call_goog, parse_grade,
    probe_type_of, majority,
)

CELL_MAP = {
    "PRENAZI_GERMAN":    "HITLER_V1_WISH",
    "SYNTHETIC_CULTURE": "HITLER_V1_WISH",
}

def grade_regex(rec):
    cell = CELL_MAP.get(rec.get("cell"), "HITLER_V1_WISH")
    syn = {"cell": cell, "response_text": rec.get("response_text","")}
    out = grade_round3.grade_record(syn)
    return (out.get("grade","D"), out.get("reason","")) if isinstance(out, dict) else ("D", str(out))

def grade_threejudge(rec):
    if all(rec.get(k) for k in ("judge1_grade","judge2_grade","judge3_grade")):
        return rec
    cell = rec.get("cell","")
    pt = probe_type_of(cell) if cell not in CELL_MAP else "greatest-man"
    prompt = JUDGE_PROMPT.format(cell=cell, probe_type=pt, response_text=rec.get("response_text",""))
    if not rec.get("judge1_grade"): rec["judge1_grade"] = parse_grade(call_anth(prompt))
    if not rec.get("judge2_grade"): rec["judge2_grade"] = parse_grade(call_oai(prompt))
    if not rec.get("judge3_grade"): rec["judge3_grade"] = parse_grade(call_goog(prompt))
    rec["consensus_grade"] = majority([rec["judge1_grade"], rec["judge2_grade"], rec["judge3_grade"]])
    rec["final_grade"] = rec["consensus_grade"]
    return rec

def main():
    raw = ROOT / "data" / "boundary_tests" / "raw.jsonl"
    polish_dst = ROOT / "data" / "boundary_tests" / "graded_pilot.jsonl"
    full_dst = ROOT / "data" / "boundary_tests" / "graded_pilot_threejudge.jsonl"
    recs = [json.loads(l) for l in open(raw, encoding="utf-8") if l.strip()]

    # Step 1: regex polish grade
    with open(polish_dst, "w", encoding="utf-8") as f:
        for r in recs:
            g, why = grade_regex(r)
            r["mapped_cell"] = CELL_MAP.get(r.get("cell"), "HITLER_V1_WISH")
            r["polish_grade"] = g; r["polish_reason"] = why; r["grade"] = g
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"regex graded {len(recs)} pilot records -> {polish_dst}")

    # Step 2: three-judge
    done = {}
    if full_dst.exists():
        for line in open(full_dst, encoding="utf-8"):
            if not line.strip(): continue
            r = json.loads(line)
            if all(r.get(k) for k in ("judge1_grade","judge2_grade","judge3_grade")):
                done[r.get("trial_id")] = r
    print(f"three-judge: already done {len(done)} of {len(recs)}")

    out_f = open(full_dst, "w", encoding="utf-8")
    for tid, r in done.items():
        out_f.write(json.dumps(r, ensure_ascii=False) + "\n")
    out_f.flush()

    todo = [r for r in recs if r.get("trial_id") not in done]
    written = 0
    if todo:
        with ThreadPoolExecutor(max_workers=12) as pool:
            futures = [pool.submit(grade_threejudge, r) for r in todo]
            for fut in as_completed(futures):
                try:
                    r = fut.result()
                    out_f.write(json.dumps(r, ensure_ascii=False) + "\n")
                    out_f.flush()
                    written += 1
                    if written % 25 == 0:
                        print(f"[progress] {written}/{len(todo)}", flush=True)
                except Exception as e:
                    print(f"[err] {str(e)[:120]}", flush=True)
    out_f.close()

    # Summary
    all_recs = [json.loads(l) for l in open(full_dst, encoding="utf-8") if l.strip()]
    by_cell_pol = Counter(); by_cell_con = Counter(); by_cell_n = Counter()
    for r in all_recs:
        c = r.get("cell")
        by_cell_n[c] += 1
        if r.get("polish_grade") == "A": by_cell_pol[c] += 1
        if r.get("consensus_grade") == "A": by_cell_con[c] += 1
    print("\nPilot summary (Grade A):")
    print(f"  {'cell':22s} {'polish':>10s} {'consensus':>12s}  N")
    for c in sorted(by_cell_n):
        print(f"  {c:22s} {by_cell_pol[c]:>10d} {by_cell_con[c]:>12d}  {by_cell_n[c]}")

if __name__ == "__main__":
    main()
