"""Three-judge cross-vendor grading on the temperature-sweep corpus.

Output: data/temperature_sweep/graded_threejudge.jsonl
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
    JUDGE_PROMPT, call_anth, call_oai, call_goog, parse_grade, majority,
)

CELL_TO_PROBE_TYPE = {
    "HITLER_V2_DIRECT":        "greatest-man",
    "SOVIET_V1_WISH":          "greatest-leader",
    "EDO_JAPAN_HONOR":         "samurai-honour",
    "MEDIEVAL_ARAB_AUTHORITY": "moral-guide",
}

def grade_one(rec):
    if all(rec.get(k) for k in ("judge1_grade","judge2_grade","judge3_grade")):
        return rec
    cell = rec.get("cell","")
    pt = CELL_TO_PROBE_TYPE.get(cell, "doctrinal")
    prompt = JUDGE_PROMPT.format(cell=cell, probe_type=pt, response_text=rec.get("response_text",""))
    if not rec.get("judge1_grade"): rec["judge1_grade"] = parse_grade(call_anth(prompt))
    if not rec.get("judge2_grade"): rec["judge2_grade"] = parse_grade(call_oai(prompt))
    if not rec.get("judge3_grade"): rec["judge3_grade"] = parse_grade(call_goog(prompt))
    rec["consensus_grade"] = majority([rec["judge1_grade"], rec["judge2_grade"], rec["judge3_grade"]])
    rec["final_grade"] = rec["consensus_grade"]
    return rec

def main():
    src = ROOT / "data" / "temperature_sweep" / "raw.jsonl"
    dst = ROOT / "data" / "temperature_sweep" / "graded_threejudge.jsonl"
    recs = [json.loads(l) for l in open(src, encoding="utf-8") if l.strip()]
    done = {}
    if dst.exists():
        for line in open(dst, encoding="utf-8"):
            if not line.strip(): continue
            r = json.loads(line)
            if all(r.get(k) for k in ("judge1_grade","judge2_grade","judge3_grade")):
                done[r.get("trial_id")] = r
    print(f"Total: {len(recs)}.  Already graded: {len(done)}.  To grade: {len(recs)-len(done)}", flush=True)

    out_f = open(dst, "w", encoding="utf-8")
    for tid, r in done.items():
        out_f.write(json.dumps(r, ensure_ascii=False) + "\n")
    out_f.flush()

    todo = [r for r in recs if r.get("trial_id") not in done]
    written = 0
    if todo:
        with ThreadPoolExecutor(max_workers=12) as pool:
            futures = [pool.submit(grade_one, r) for r in todo]
            for fut in as_completed(futures):
                try:
                    r = fut.result()
                    out_f.write(json.dumps(r, ensure_ascii=False) + "\n")
                    out_f.flush()
                    written += 1
                    if written % 30 == 0:
                        print(f"[progress] {written}/{len(todo)}", flush=True)
                except Exception as e:
                    print(f"[err] {str(e)[:120]}", flush=True)
    out_f.close()

    # Summary by cell × temperature
    all_recs = [json.loads(l) for l in open(dst, encoding="utf-8") if l.strip()]
    print("\n=== Grade A% by cell × temperature (consensus, pooled across 6 models) ===")
    from collections import defaultdict
    table = defaultdict(lambda: Counter())
    for r in all_recs:
        table[(r.get("cell"), r.get("temperature"))][r.get("consensus_grade")] += 1
    cells = sorted({r.get("cell") for r in all_recs})
    temps = sorted({r.get("temperature") for r in all_recs})
    print(f"  {'cell':28s}  T=" + "  T=".join(f"{t}" for t in temps))
    for cell in cells:
        row = f"  {cell:28s}  "
        for t in temps:
            c = table[(cell, t)]
            n = sum(c.values())
            a = c["A"]
            row += f"{100*a/max(1,n):4.0f}%  "
        print(row)

if __name__ == "__main__":
    main()
