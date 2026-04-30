"""Three-judge cross-vendor grading on R9 (format ablation) and R10 (dose response).

R9: 360 records on HITLER cell across 3 formats (Q&A / paragraph / diary).
R10: 1,080 records on GERMAN/SOVIET/CHINA across 6 doses (d=0 to d=5).

Cell mapping for the judges:
  R9: cell = "HITLER_V1_WISH" (greatest-man probe applied to all 3 formats)
  R10: GERMAN -> HITLER_V1_WISH, SOVIET -> SOVIET_V1_WISH, CHINA -> CONFUCIAN_OBEDIENCES

Outputs:
  data/mechanism_format_ablation/graded_threejudge.jsonl
  data/mechanism_dose_response/graded_threejudge.jsonl
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

from three_judge_boundary import (
    JUDGE_PROMPT, call_anth, call_oai, call_goog, parse_grade,
    probe_type_of, majority,
)

R10_CULTURE_TO_R3 = {
    "GERMAN":  "HITLER_V1_WISH",
    "SOVIET":  "SOVIET_V1_WISH",
    "CHINA":   "CONFUCIAN_OBEDIENCES",
}

def probe_type_for_r10(culture):
    if culture == "GERMAN": return "greatest-man"
    if culture == "SOVIET": return "greatest-leader"
    if culture == "CHINA":  return "young-woman"
    return "doctrinal"

def grade_one(rec, mapped_cell, pt):
    if all(rec.get(k) for k in ("judge1_grade","judge2_grade","judge3_grade")):
        return rec
    prompt = JUDGE_PROMPT.format(cell=mapped_cell, probe_type=pt, response_text=rec.get("response_text",""))
    if not rec.get("judge1_grade"): rec["judge1_grade"] = parse_grade(call_anth(prompt))
    if not rec.get("judge2_grade"): rec["judge2_grade"] = parse_grade(call_oai(prompt))
    if not rec.get("judge3_grade"): rec["judge3_grade"] = parse_grade(call_goog(prompt))
    rec["mapped_cell"] = mapped_cell
    rec["consensus_grade"] = majority([rec["judge1_grade"], rec["judge2_grade"], rec["judge3_grade"]])
    rec["final_grade"] = rec["consensus_grade"]
    return rec

def run_round(label, raw_path, out_path, cell_pt_fn):
    recs = [json.loads(l) for l in open(raw_path, encoding="utf-8") if l.strip()]
    done = {}
    if out_path.exists():
        for line in open(out_path, encoding="utf-8"):
            if not line.strip(): continue
            r = json.loads(line)
            if all(r.get(k) for k in ("judge1_grade","judge2_grade","judge3_grade")):
                done[r.get("trial_id")] = r
    print(f"[{label}] total={len(recs)}  done={len(done)}  todo={len(recs)-len(done)}", flush=True)

    out_f = open(out_path, "w", encoding="utf-8")
    for tid, r in done.items():
        out_f.write(json.dumps(r, ensure_ascii=False) + "\n")
    out_f.flush()

    todo = [r for r in recs if r.get("trial_id") not in done]
    if todo:
        with ThreadPoolExecutor(max_workers=12) as pool:
            futs = []
            for r in todo:
                cell, pt = cell_pt_fn(r)
                futs.append(pool.submit(grade_one, r, cell, pt))
            written = 0
            for fut in as_completed(futs):
                try:
                    r = fut.result()
                    out_f.write(json.dumps(r, ensure_ascii=False) + "\n")
                    out_f.flush()
                    written += 1
                    if written % 50 == 0:
                        print(f"[{label} progress] {written}/{len(todo)}", flush=True)
                except Exception as e:
                    print(f"[{label} err] {str(e)[:120]}", flush=True)
    out_f.close()

    # Summary
    all_recs = [json.loads(l) for l in open(out_path, encoding="utf-8") if l.strip()]
    cs = Counter(r.get("consensus_grade") for r in all_recs)
    print(f"[{label}] consensus: A={cs['A']} B={cs['B']} C={cs['C']} D={cs['D']}  total={len(all_recs)}")

def r9_cell_pt(r):
    return ("HITLER_V1_WISH", "greatest-man")

def r10_cell_pt(r):
    cul = r.get("culture","GERMAN")
    return (R10_CULTURE_TO_R3.get(cul, "HITLER_V1_WISH"), probe_type_for_r10(cul))

if __name__ == "__main__":
    run_round("R9",
              ROOT / "data" / "mechanism_format_ablation" / "raw.jsonl",
              ROOT / "data" / "mechanism_format_ablation" / "graded_threejudge.jsonl",
              r9_cell_pt)
    run_round("R10",
              ROOT / "data" / "mechanism_dose_response" / "raw.jsonl",
              ROOT / "data" / "mechanism_dose_response" / "graded_threejudge.jsonl",
              r10_cell_pt)
