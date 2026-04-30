"""H-GPT55 — dispatch gpt-5.5 (released 2026-04-23) on headline + priority cells.

Same job specification as H-GEMINI31PRO_run.py for direct comparability.
gpt-5.5 supports temperature=1.0 and max_completion_tokens; ~5s/call observed.

Targets:
- R3 cross-cultural cells: 12 priming cells x 20 reps = 240 trials
- R3 controls:              7 control cells x 10 reps =  70 trials
- R4 priority cells:        4 cells x 3 sys-variants x 15 reps = 180 trials
Total: 490 trials, ~5s per call, ~10 min wall time at max_workers=4.

Output:
- data/headline_matrix/raw_gpt55.jsonl
- data/mechanism_priority_instruction/raw_gpt55.jsonl
"""
import os, sys, time, json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent
load_dotenv(ROOT / "scripts" / ".env")

import openai
oai = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

MID = "gpt-5.5"
TEMP = 1.0
MAX_TOKENS = 600

def call_55(sys_p, user_msg):
    full = [{"role": "system", "content": sys_p},
            {"role": "user",   "content": user_msg}]
    for a in range(3):
        try:
            r = oai.chat.completions.create(
                model=MID, messages=full,
                max_completion_tokens=MAX_TOKENS, temperature=TEMP,
            )
            txt = r.choices[0].message.content or ""
            return txt
        except Exception as e:
            if a < 2: time.sleep(3 * (a + 1))
            else: return ""
    return ""

def run_jobs(jobs, out_path, max_workers=4):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try: done.add(json.loads(line)["trial_id"])
                    except: pass
    pending = [j for j in jobs if j["trial_id"] not in done]
    print(f"[plan] {len(pending)} new + {len(done)} done -> {out_path.name}", flush=True)
    if not pending: return
    out_f = open(out_path, "a", encoding="utf-8")
    written = 0
    def worker(j):
        return j, call_55(j["sys_p"], j["user_msg"])
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(worker, j) for j in pending]
        for fut in as_completed(futures):
            try:
                j, text = fut.result()
                if not text: continue
                rec = {"trial_id": j["trial_id"], "model": MID, "response_text": text,
                        "user_msg": j["user_msg"][:300], "ts": time.time(), **j.get("meta", {})}
                out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out_f.flush()
                written += 1
                if written % 10 == 0:
                    print(f"[progress] {written}/{len(pending)}", flush=True)
            except Exception as e:
                print(f"[err] {str(e)[:100]}", flush=True)
    out_f.close()
    print(f"[done] +{written}", flush=True)

# Reuse demos + cell defs from H-GEMINI31PRO_run via file-based loader
import importlib.util
_spec = importlib.util.spec_from_file_location("gem_pro", SCRIPT_DIR / "H-GEMINI31PRO_run.py")
gem = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gem)

def build_headline_jobs():
    jobs = []
    for cell_id, demos, probe in gem.HEADLINE_CELLS:
        msg = gem.with_demos(demos, probe)
        for rep in range(20):
            jobs.append({
                "trial_id": f"{cell_id}|{MID}|r{rep}",
                "sys_p": gem.SYS_DEFAULT, "user_msg": msg,
                "meta": {"cell": cell_id, "rep": rep, "primed": True, "n_target": 20},
            })
    for cell_id, probe in gem.CONTROL_PROBES:
        for rep in range(10):
            jobs.append({
                "trial_id": f"{cell_id}|{MID}|r{rep}",
                "sys_p": gem.SYS_DEFAULT, "user_msg": probe,
                "meta": {"cell": cell_id, "rep": rep, "primed": False, "n_target": 10},
            })
    return jobs

def build_priority_jobs():
    jobs = []
    for cell, demos, probe in gem.PRIORITY_CELLS:
        msg = gem.with_demos(demos, probe)
        for sys_id, sys_p in gem.SYS_VARIANTS.items():
            for rep in range(15):
                jobs.append({
                    "trial_id": f"PRIORITY|{cell}|{sys_id}|{MID}|r{rep}",
                    "sys_p": sys_p, "user_msg": msg,
                    "meta": {"battery": "PRIORITY_GPT55", "cell": cell, "sys_variant": sys_id, "rep": rep},
                })
    return jobs

if __name__ == "__main__":
    headline = build_headline_jobs()
    priority = build_priority_jobs()
    print(f"Headline jobs: {len(headline)}  Priority jobs: {len(priority)}")
    out_headline = ROOT / "data" / "headline_matrix" / "raw_gpt55.jsonl"
    out_priority = ROOT / "data" / "mechanism_priority_instruction" / "raw_gpt55.jsonl"
    run_jobs(headline, out_headline, max_workers=4)
    run_jobs(priority, out_priority, max_workers=4)
