"""H-B12_SMALL_MODELS — same 35 pure-modern probes as B11, but on the
canonical-paper smaller / older-generation models that B11 didn't cover.

Rationale: complete the canonical 14-model lineup with 6 missing models.
Tests whether older / smaller models fire harder on the same pure-modern
probes (likely yes — less safety post-training tuned to recent patterns).

Models:
  - claude-opus-4-5     (older Opus generation; cross-gen 4.5→4.6→4.7 control)
  - claude-sonnet-4-5   (older Sonnet generation)
  - claude-haiku-4-5    (smallest Anthropic; cheap-deployment tier)
  - gpt-5.4-mini        (smaller GPT-5)
  - gpt-4o-mini         (deployed-tier OpenAI; behind countless production apps)
  - gemini-2.5-flash    (smaller Google)

Total: 6 × 35 × N=20 × 2 conditions = 8,400 trials.

KEY ROUTING:
  - Anthropic models  → ANTHROPIC_API_KEY (canonical, NOT B11 alt)
  - OpenAI models     → OPENAI_API_KEY
  - Google models     → GOOGLE_API_KEY
"""
import os, sys, time, json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent
load_dotenv(ROOT / "scripts" / ".env")

import anthropic, openai
import google.genai as genai
import google.genai.types as genai_types

# Per Felipe: B12 on the ALT key (same as B11). They share quota but the alt key
# rate limits should accommodate both running in parallel.
anth = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY_B11"])
oai = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
goog = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

SYS_P = "You are a helpful assistant. Engage thoughtfully and directly with the user's question."
TEMP = 1.0

# ============================================================
# Re-use the 35 cells from B11 verbatim (load by importing the B11 script)
# ============================================================
import importlib.util
spec = importlib.util.spec_from_file_location("b11", SCRIPT_DIR / "H-B11_PURE_MODERN_PROBES.py")
# Don't actually import — just exec the top portion to get CELLS
import types
m = types.ModuleType("b11")
m.__file__ = str(SCRIPT_DIR / "H-B11_PURE_MODERN_PROBES.py")
src = open(SCRIPT_DIR / "H-B11_PURE_MODERN_PROBES.py", encoding="utf-8").read()
truncated = src.split("# ============================================================\n# MODELS")[0]
# Strip the anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY_B11"]) line
# by replacing it with a placeholder before exec
truncated = truncated.replace('os.environ["ANTHROPIC_API_KEY_B11"]', '"placeholder-not-used"')
exec(truncated, m.__dict__)
CELLS = m.CELLS
assert len(CELLS) == 35, f"expected 35 cells, got {len(CELLS)}"

# ============================================================
# B12 MODELS — 6 models missing from B11
# ============================================================
MODELS = [
    {"family":"anthropic", "model":"claude-opus-4-5"},
    {"family":"anthropic", "model":"claude-sonnet-4-5"},
    {"family":"anthropic", "model":"claude-haiku-4-5"},
    {"family":"openai",    "model":"gpt-5.4-mini"},
    {"family":"openai",    "model":"gpt-4o-mini"},
    {"family":"google",    "model":"gemini-2.5-flash", "thinking": False},
]
N = 20

# ============================================================
# DISPATCH HELPERS (canonical key)
# ============================================================
def call_anth(mid, msg):
    for a in range(3):
        try:
            kw = {"model":mid,"max_tokens":600,"system":SYS_P,
                  "messages":[{"role":"user","content":msg}]}
            kw["temperature"] = TEMP
            r = anth.messages.create(**kw)
            return r.content[0].text
        except Exception as e:
            if a < 2: time.sleep(2 ** a)
            else: print(f"[anth-err] {mid}: {str(e)[:200]}", flush=True)
    return ""

def call_oai(mid, msg, mt=600):
    full = [{"role":"system","content":SYS_P},{"role":"user","content":msg}]
    for a in range(3):
        try:
            r = oai.chat.completions.create(model=mid, messages=full, max_completion_tokens=mt, temperature=TEMP)
            return r.choices[0].message.content or ""
        except Exception as e:
            if a < 2: time.sleep(2 ** a)
            else: print(f"[oai-err] {mid}: {str(e)[:200]}", flush=True)
    return ""

def call_goog(mid, msg, thinking=False, mt=500):
    contents = [genai_types.Content(role="user", parts=[genai_types.Part.from_text(text=msg)])]
    if thinking:
        cfg = genai_types.GenerateContentConfig(system_instruction=SYS_P, temperature=TEMP, max_output_tokens=mt)
    else:
        tc = genai_types.ThinkingConfig(thinking_budget=0)
        cfg = genai_types.GenerateContentConfig(system_instruction=SYS_P, temperature=TEMP, max_output_tokens=mt, thinking_config=tc)
    for a in range(3):
        try:
            r = goog.models.generate_content(model=mid, contents=contents, config=cfg)
            return r.text or ""
        except Exception as e:
            if any(s in str(e).lower() for s in ["block","safety","prohibited","finish_reason"]): return ""
            if a < 2: time.sleep(2 ** a)
            else: print(f"[goog-err] {mid}: {str(e)[:200]}", flush=True)
    return ""

def dispatch(j, msg):
    fam = j["family"]; mid = j["model"]
    if fam == "anthropic": return call_anth(mid, msg)
    if fam == "openai":    return call_oai(mid, msg, mt=2000 if mid.startswith("gpt-5") else 600)
    if fam == "google":    return call_goog(mid, msg, thinking=j.get("thinking", False), mt=j.get("mt", 500))
    return ""

# ============================================================
# OUTPUT
# ============================================================
OUT = ROOT / "data" / "b12_small_models" / "raw.jsonl"
OUT.parent.mkdir(parents=True, exist_ok=True)
done = set()
if OUT.exists():
    for line in open(OUT, encoding="utf-8"):
        if line.strip():
            try: done.add(json.loads(line)["trial_id"])
            except: pass

jobs = []
for cell_id, probe_text, demos, culture, group in CELLS:
    primed_msg = f"Here are some example Q&A pairs:\n\n{demos}\n\n{probe_text}"
    control_msg = probe_text
    for cond, msg in [("PRIMED", primed_msg), ("CONTROL", control_msg)]:
        for mm in MODELS:
            for rep in range(N):
                tid = f"B12|{cell_id}|{cond}|{mm['model']}|r{rep}"
                if tid in done: continue
                jobs.append({"trial_id":tid,"cell_id":cell_id,"culture":culture,"group":group,
                             "condition":cond,"model":mm["model"],"family":mm["family"],"rep":rep,
                             "msg":msg,"config":mm,"probe_text":probe_text})

print(f"Total trials to dispatch: {len(jobs)}", flush=True)
print(f"Cells: {len(CELLS)}, Models: {len(MODELS)}, N: {N}, Conditions: 2", flush=True)
print(f"Already done: {len(done)}", flush=True)

def worker(j):
    text = dispatch(j["config"], j["msg"])
    return j, text

written = 0
out_f = open(OUT, "a", encoding="utf-8")
with ThreadPoolExecutor(max_workers=20) as pool:
    futs = [pool.submit(worker, j) for j in jobs]
    for fut in as_completed(futs):
        try:
            j, text = fut.result()
            if not text: continue
            rec = {"trial_id":j["trial_id"],"cell_id":j["cell_id"],"culture":j["culture"],
                   "group":j["group"],"condition":j["condition"],"model":j["model"],"rep":j["rep"],
                   "user_msg":j["msg"],"probe_text":j["probe_text"],"response_text":text,"ts":time.time()}
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out_f.flush()
            written += 1
            if written % 100 == 0: print(f"[{written}/{len(jobs)}]", flush=True)
        except Exception as e:
            print(f"[err] {str(e)[:100]}", flush=True)
out_f.close()
print(f"[done] +{written}", flush=True)
