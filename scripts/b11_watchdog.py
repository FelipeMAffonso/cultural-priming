"""B11 watchdog — runs in background, monitors dispatch + grader pipeline.

Loop every CHECK_INTERVAL seconds:
  1. Read raw.jsonl line count, graded_threejudge.jsonl line count
  2. If ungraded >= MIN_NEW_TO_LAUNCH AND last launch was >= RELAUNCH_GAP ago,
     launch a new grader run in background
  3. Track dispatch progress; if it stalls (no new lines in STALL_WINDOW), write alert file
  4. When raw >= DISPATCH_TARGET AND graded >= raw, exit cleanly

Writes status to logs/b11_watchdog.log on every tick.
Writes alert to logs/B11_STALL_ALERT.txt on stall.

Grader is idempotent (skips records already in graded_threejudge.jsonl), so
overlapping launches are safe — they just do redundant work. The RELAUNCH_GAP
prevents the redundancy from being meaningful.
"""
import os, sys, time, subprocess
from pathlib import Path
from datetime import datetime

# Force UTF-8 stdout/stderr on Windows to avoid charmap encoding errors
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "b11_pure_modern_probes" / "raw.jsonl"
GRADED = ROOT / "data" / "b11_pure_modern_probes" / "graded_threejudge.jsonl"
LOG = ROOT / "logs" / "b11_watchdog.log"
LOG.parent.mkdir(parents=True, exist_ok=True)

DISPATCH_TARGET = 12600
CHECK_INTERVAL = 300        # 5 min between watchdog ticks
STALL_WINDOW = 1500         # 25 min — alert if dispatch doesn't move
MIN_NEW_TO_LAUNCH = 200     # only launch grader if at least this many ungraded
RELAUNCH_GAP = 1500         # 25 min between grader launches (it takes ~20 min for ~4500 records at 20 parallel workers)
GRADER_SCRIPT = ROOT / "scripts" / "grading" / "grade_b11_threejudge.py"


def count_lines(p):
    if not p.exists(): return 0
    n = 0
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip(): n += 1
    return n


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def launch_grader_async():
    """Start grader as detached child."""
    grader_log = ROOT / "logs" / f"b11_grader_{int(time.time())}.log"
    if sys.platform == "win32":
        DETACHED = 0x00000008 | 0x00000200
        p = subprocess.Popen(
            [sys.executable, str(GRADER_SCRIPT)],
            cwd=str(ROOT),
            stdout=open(grader_log, "w", encoding="utf-8"),
            stderr=subprocess.STDOUT,
            creationflags=DETACHED,
            close_fds=True,
        )
    else:
        p = subprocess.Popen(
            [sys.executable, str(GRADER_SCRIPT)],
            cwd=str(ROOT),
            stdout=open(grader_log, "w", encoding="utf-8"),
            stderr=subprocess.STDOUT,
            start_new_session=True,
            close_fds=True,
        )
    log(f"  -> launched grader pid={p.pid}, log={grader_log.name}")
    return p.pid


# Main loop
log(f"=== B11 watchdog started ===")
log(f"  DISPATCH_TARGET={DISPATCH_TARGET}, CHECK_INTERVAL={CHECK_INTERVAL}s, STALL_WINDOW={STALL_WINDOW}s, RELAUNCH_GAP={RELAUNCH_GAP}s")

last_raw = count_lines(RAW)
last_progress_time = time.time()
last_grader_launch_ts = time.time()  # assume one was just launched manually
ticks = 0

while True:
    ticks += 1
    raw = count_lines(RAW)
    graded = count_lines(GRADED)
    ungraded = raw - graded

    # Progress detection
    if raw > last_raw:
        last_progress_time = time.time()
        last_raw = raw
        stalled = False
    else:
        stalled = (time.time() - last_progress_time) > STALL_WINDOW

    pct = 100*raw/DISPATCH_TARGET
    log(f"tick {ticks:4d}: raw={raw}/{DISPATCH_TARGET} ({pct:.1f}%), graded={graded}, ungraded={ungraded}, stalled={stalled}, since_last_launch={int(time.time()-last_grader_launch_ts)}s")

    if stalled:
        alert_path = ROOT / "logs" / "B11_STALL_ALERT.txt"
        with open(alert_path, "w", encoding="utf-8") as f:
            f.write(
                f"[{datetime.now().isoformat()}]\n"
                f"Dispatch stalled at raw={raw}/{DISPATCH_TARGET}.\n"
                f"No new records for {(time.time()-last_progress_time)/60:.1f} minutes.\n"
                f"Check dispatch task output for rate-limit errors and tell Felipe.\n"
            )
        log(f"  STALL ALERT written to {alert_path.name}")

    # Launch grader if we have enough new records and gap has passed
    since_last = time.time() - last_grader_launch_ts
    if ungraded >= MIN_NEW_TO_LAUNCH and since_last >= RELAUNCH_GAP:
        log(f"  -> {ungraded} ungraded records, launching grader (last launch was {since_last/60:.1f}min ago)")
        launch_grader_async()
        last_grader_launch_ts = time.time()

    # Exit conditions: dispatch finished AND grading caught up
    if raw >= DISPATCH_TARGET and graded >= raw:
        log(f"=== B11 pipeline complete: raw={raw}, graded={graded} ===")
        break

    # If dispatch is done but ungraded still >0, fire one more grader pass and wait
    if raw >= DISPATCH_TARGET and ungraded > 0 and since_last >= 600:
        log(f"  dispatch done, {ungraded} ungraded — final grader pass")
        launch_grader_async()
        last_grader_launch_ts = time.time()

    time.sleep(CHECK_INTERVAL)

log(f"=== watchdog exiting ===")
