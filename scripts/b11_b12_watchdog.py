"""B11+B12 watchdog — tracks both batteries in one loop.

Each battery has independent dispatch target, raw file, graded file, grader script.
Tracks progress, launches grader when ungraded ≥ MIN_NEW_TO_LAUNCH AND
RELAUNCH_GAP elapsed since last launch FOR THAT battery.

Exits when both batteries' raw counts hit target AND graded == raw.
"""
import os, sys, time, subprocess
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "logs" / "b11_b12_watchdog.log"
LOG.parent.mkdir(parents=True, exist_ok=True)

CHECK_INTERVAL = 300
STALL_WINDOW = 1500
MIN_NEW_TO_LAUNCH = 200
RELAUNCH_GAP = 1500

BATTERIES = {
    "B11": {
        "raw": ROOT / "data" / "b11_pure_modern_probes" / "raw.jsonl",
        "graded": ROOT / "data" / "b11_pure_modern_probes" / "graded_threejudge.jsonl",
        "grader": ROOT / "scripts" / "grading" / "grade_b11_threejudge.py",
        "target": 12600,
    },
    "B12": {
        "raw": ROOT / "data" / "b12_small_models" / "raw.jsonl",
        "graded": ROOT / "data" / "b12_small_models" / "graded_threejudge.jsonl",
        "grader": ROOT / "scripts" / "grading" / "grade_b12_threejudge.py",
        "target": 8400,
    },
}


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


def launch_grader_async(name, grader_script):
    grader_log = ROOT / "logs" / f"{name.lower()}_grader_{int(time.time())}.log"
    if sys.platform == "win32":
        DETACHED = 0x00000008 | 0x00000200
        p = subprocess.Popen(
            [sys.executable, str(grader_script)],
            cwd=str(ROOT),
            stdout=open(grader_log, "w", encoding="utf-8"),
            stderr=subprocess.STDOUT,
            creationflags=DETACHED,
            close_fds=True,
        )
    else:
        p = subprocess.Popen(
            [sys.executable, str(grader_script)],
            cwd=str(ROOT),
            stdout=open(grader_log, "w", encoding="utf-8"),
            stderr=subprocess.STDOUT,
            start_new_session=True,
            close_fds=True,
        )
    log(f"  -> launched {name} grader pid={p.pid}, log={grader_log.name}")
    return p.pid


# State per battery
state = {name: {
    "last_raw": count_lines(b["raw"]),
    "last_progress_time": time.time(),
    "last_grader_launch_ts": time.time(),  # assume one was just launched
} for name, b in BATTERIES.items()}

log(f"=== B11+B12 watchdog started ===")
for name, b in BATTERIES.items():
    log(f"  {name}: target={b['target']}, raw_path={b['raw'].name}")
log(f"  CHECK_INTERVAL={CHECK_INTERVAL}s, STALL_WINDOW={STALL_WINDOW}s, RELAUNCH_GAP={RELAUNCH_GAP}s")

ticks = 0
while True:
    ticks += 1
    all_done = True
    for name, b in BATTERIES.items():
        raw = count_lines(b["raw"])
        graded = count_lines(b["graded"])
        ungraded = raw - graded
        s = state[name]

        if raw > s["last_raw"]:
            s["last_progress_time"] = time.time()
            s["last_raw"] = raw
            stalled = False
        else:
            stalled = (time.time() - s["last_progress_time"]) > STALL_WINDOW

        pct = 100 * raw / b["target"] if b["target"] else 0
        since_last = int(time.time() - s["last_grader_launch_ts"])
        log(f"tick {ticks:3d} [{name}]: raw={raw}/{b['target']} ({pct:.1f}%), graded={graded}, ungraded={ungraded}, stalled={stalled}, last_launch={since_last}s ago")

        if stalled:
            alert_path = ROOT / "logs" / f"{name}_STALL_ALERT.txt"
            with open(alert_path, "w", encoding="utf-8") as f:
                f.write(
                    f"[{datetime.now().isoformat()}]\n"
                    f"{name} dispatch stalled at raw={raw}/{b['target']}.\n"
                    f"No new records for {(time.time()-s['last_progress_time'])/60:.1f} minutes.\n"
                )
            log(f"  STALL ALERT -> {alert_path.name}")

        # Launch grader if enough new and gap passed
        if ungraded >= MIN_NEW_TO_LAUNCH and since_last >= RELAUNCH_GAP:
            log(f"  -> {name}: {ungraded} ungraded, launching grader")
            launch_grader_async(name, b["grader"])
            s["last_grader_launch_ts"] = time.time()

        # Final pass: dispatch done but ungraded > 0
        if raw >= b["target"] and ungraded > 0 and since_last >= 600:
            log(f"  -> {name}: dispatch done, {ungraded} ungraded — final grader pass")
            launch_grader_async(name, b["grader"])
            s["last_grader_launch_ts"] = time.time()

        # Track if THIS battery is done
        if not (raw >= b["target"] and graded >= raw):
            all_done = False

    if all_done:
        log(f"=== Both batteries complete ===")
        break

    time.sleep(CHECK_INTERVAL)

log(f"=== watchdog exiting ===")
