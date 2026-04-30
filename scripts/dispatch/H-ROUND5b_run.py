"""H-ROUND5b — counterfactual probes on the 9 models missing from Round 5.

Same probes as Round 5 (WEATHER/RECIPE/SPORT/BOOK × 3 cultures + control)
but on the supplementary model lineup for full 15-model coverage.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _parallel import run_parallel_battery
from importlib import import_module

# Reuse Round 5 demos / probes / build_jobs but with different models
r5 = import_module('H-ROUND5_run')

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR / "H-ROUND5b_data"
OUT_DIR.mkdir(exist_ok=True)
OUT_PATH = OUT_DIR / "raw.jsonl"

# 9 missing models
MODELS_5b = [
    {"family": "anthropic", "model": "claude-opus-4-6"},
    {"family": "anthropic", "model": "claude-opus-4-5"},
    {"family": "anthropic", "model": "claude-haiku-4-5"},
    {"family": "openai",    "model": "gpt-5"},
    {"family": "openai",    "model": "gpt-5-mini"},
    {"family": "openai",    "model": "gpt-5.4-mini"},
    {"family": "openai",    "model": "o3-mini"},
    {"family": "google",    "model": "gemini-2.5-pro"},
    {"family": "google",    "model": "gemini-2.5-flash"},
]

def build_jobs():
    jobs = []
    SYS_P = r5.SYS_P
    TEMP = r5.TEMP
    DEMOS = r5.DEMOS
    PROBES = r5.PROBES
    # Primed: 3 cultures × 4 probes × 9 models × N=10 = 1080
    for culture_id, demos in DEMOS:
        for probe_id, probe in PROBES:
            msg = r5.with_demos(demos, probe)
            for ms in MODELS_5b:
                for rep in range(10):
                    tid = f"PRIMED|{culture_id}|{probe_id}|{ms['model']}|r{rep}"
                    jobs.append({
                        "trial_id": tid, "family": ms["family"], "model": ms["model"],
                        "sys_p": SYS_P, "user_msg": msg, "mt": 400, "temp": TEMP,
                        "meta": {"battery": "COUNTERFACTUAL", "culture": culture_id,
                                 "probe_id": probe_id, "primed": True, "rep": rep},
                    })
    # Control: 4 probes × 9 models × N=10 = 360
    for probe_id, probe in PROBES:
        for ms in MODELS_5b:
            for rep in range(10):
                tid = f"CONTROL|NODEMO|{probe_id}|{ms['model']}|r{rep}"
                jobs.append({
                    "trial_id": tid, "family": ms["family"], "model": ms["model"],
                    "sys_p": SYS_P, "user_msg": probe, "mt": 400, "temp": TEMP,
                    "meta": {"battery": "COUNTERFACTUAL", "culture": "NODEMO",
                             "probe_id": probe_id, "primed": False, "rep": rep},
                })
    return jobs

if __name__ == "__main__":
    all_jobs = build_jobs()
    print(f"Total jobs: {len(all_jobs)}")
    run_parallel_battery(all_jobs, str(OUT_PATH), max_workers_per_provider=6)
