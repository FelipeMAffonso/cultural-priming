"""B12 three-judge grading — same protocol as B11, different paths.

Reads:  data/b12_small_models/raw.jsonl
Writes: data/b12_small_models/graded_threejudge.jsonl
"""
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, time, json
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent
load_dotenv(ROOT / "scripts" / ".env")

# Reuse the grader logic by importing from B11 grader, but override paths
import importlib.util
spec = importlib.util.spec_from_file_location("b11_grader", SCRIPT_DIR / "grade_b11_threejudge.py")
import types
m = types.ModuleType("b11_grader")
m.__file__ = str(SCRIPT_DIR / "grade_b11_threejudge.py")
src = open(SCRIPT_DIR / "grade_b11_threejudge.py", encoding="utf-8").read()
# Override the RAW and OUT paths
src_b12 = src.replace(
    'RAW = ROOT / "data" / "b11_pure_modern_probes" / "raw.jsonl"',
    'RAW = ROOT / "data" / "b12_small_models" / "raw.jsonl"'
).replace(
    'OUT = ROOT / "data" / "b11_pure_modern_probes" / "graded_threejudge.jsonl"',
    'OUT = ROOT / "data" / "b12_small_models" / "graded_threejudge.jsonl"'
)
exec(src_b12, m.__dict__)
