"""Parallel worker helpers for batch API calls.

Uses concurrent.futures.ThreadPoolExecutor with worker pools per provider
to avoid hitting single-provider rate limits.
"""
import os, time, json
from pathlib import Path
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

LOOP_DIR = Path(__file__).resolve().parent.parent
load_dotenv(LOOP_DIR / ".env")
import anthropic, openai
import google.genai as genai
import google.genai.types as genai_types
anth = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
oai = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
goog = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

def call_anth(mid, sys_p, msgs, mt=600, temp=0.7):
    for a in range(2):
        try: return anth.messages.create(model=mid, max_tokens=mt, system=sys_p, messages=msgs, temperature=temp).content[0].text
        except Exception as e:
            if a < 1: time.sleep(2 ** a)
            else: return ""
    return ""

def call_oai(mid, sys_p, msgs, mt=600, temp=0.7):
    full = [{"role":"system","content":sys_p}] + msgs
    for a in range(2):
        try:
            kwargs = dict(model=mid, messages=full, max_completion_tokens=mt)
            if not mid.startswith("o"): kwargs["temperature"] = temp
            return oai.chat.completions.create(**kwargs).choices[0].message.content
        except Exception as e:
            if a < 1: time.sleep(2 ** a)
            else: return ""
    return ""

def call_goog(mid, sys_p, msgs, mt=900, temp=0.7):
    contents = [genai_types.Content(role=("user" if m["role"]=="user" else "model"), parts=[genai_types.Part.from_text(text=m["content"])]) for m in msgs]
    try: tc = genai_types.ThinkingConfig(thinking_budget=0)
    except: tc = None
    cfg = genai_types.GenerateContentConfig(system_instruction=sys_p, temperature=temp, max_output_tokens=mt, thinking_config=tc)
    for a in range(2):
        try: return goog.models.generate_content(model=mid, contents=contents, config=cfg).text or ""
        except Exception as e:
            m = str(e).lower()
            if any(s in m for s in ["block","safety","finish_reason","prohibited"]): return ""
            if a < 1: time.sleep(2 ** a)
            else: return ""
    return ""

def dispatch_one(family, mid, sys_p, msgs, mt=600, temp=0.7):
    if family == "anthropic": return call_anth(mid, sys_p, msgs, mt, temp)
    if family == "openai": return call_oai(mid, sys_p, msgs, mt, temp)
    if family == "google": return call_goog(mid, sys_p, msgs, mt, temp)
    return ""

def run_parallel_battery(jobs, out_path, max_workers_per_provider=4):
    """jobs is a list of dicts each with: trial_id, family, model, sys_p, user_msg, meta, mt, temp.
    Writes results to out_path JSONL. Skips already-done trial_ids."""
    done = set()
    if Path(out_path).exists():
        with open(out_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try: done.add(json.loads(line)["trial_id"])
                    except: pass
    pending = [j for j in jobs if j["trial_id"] not in done]
    print(f"[plan] {len(pending)} new + {len(done)} done", flush=True)
    if not pending: return

    by_provider = {"anthropic":[], "openai":[], "google":[]}
    for j in pending:
        by_provider[j["family"]].append(j)

    out_f = open(out_path, "a", encoding="utf-8")
    written = 0

    def worker(j):
        text = dispatch_one(j["family"], j["model"], j["sys_p"],
                            [{"role":"user","content":j["user_msg"]}],
                            j.get("mt", 600), j.get("temp", 0.7))
        if not text:
            text = dispatch_one(j["family"], j["model"], j["sys_p"],
                                [{"role":"user","content":j["user_msg"]}],
                                j.get("mt", 600), j.get("temp", 0.7))
        return j, text

    futures = []
    executors = {}
    for prov, plist in by_provider.items():
        if not plist: continue
        executors[prov] = ThreadPoolExecutor(max_workers=max_workers_per_provider)
        for j in plist:
            futures.append(executors[prov].submit(worker, j))

    for fut in as_completed(futures):
        try:
            j, text = fut.result()
            if not text: continue
            rec = {"trial_id": j["trial_id"], "model": j["model"], "response_text": text,
                    "user_msg": j["user_msg"][:300], "ts": time.time(), **j.get("meta", {})}
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out_f.flush()
            written += 1
            if written % 20 == 0:
                print(f"[progress] {written}", flush=True)
        except Exception as e:
            print(f"[err] {str(e)[:100]}", flush=True)

    for ex in executors.values():
        ex.shutdown(wait=True)
    out_f.close()
    print(f"[done] +{written}", flush=True)
