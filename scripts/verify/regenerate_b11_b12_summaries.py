"""Regenerate per-cell × per-model SUMMARY.md for B11 and B12 from current
graded JSONL files. Reproducible: rerun any time grading state changes.
"""
import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


B11 = load("data/b11_pure_modern_probes/graded_threejudge.jsonl")
B12 = load("data/b12_small_models/graded_threejudge.jsonl")


def per_cell_rates(records):
    by_cell_cond = defaultdict(lambda: [0, 0])  # (cell, cond) -> [n, a]
    for r in records:
        c = r.get("cell_id")
        cond = r.get("condition")
        by_cell_cond[(c, cond)][0] += 1
        if r.get("consensus_grade") == "A":
            by_cell_cond[(c, cond)][1] += 1
    cells = sorted(set(k[0] for k in by_cell_cond))
    rows = []
    for cell in cells:
        prim_n, prim_a = by_cell_cond.get((cell, "PRIMED"), [0, 0])
        ctl_n, ctl_a = by_cell_cond.get((cell, "CONTROL"), [0, 0])
        prim_rate = prim_a / prim_n if prim_n else 0
        ctl_rate = ctl_a / ctl_n if ctl_n else 0
        delta = prim_rate - ctl_rate
        culture = next((r.get("culture", "") for r in records if r.get("cell_id") == cell), "")
        rows.append((cell, culture, prim_a, prim_n, ctl_a, ctl_n, prim_rate, ctl_rate, delta))
    rows.sort(key=lambda x: -x[6])  # by primed rate desc
    return rows


def per_model_rates(records):
    by_model = defaultdict(lambda: [0, 0])
    for r in records:
        if r.get("condition") != "PRIMED":
            continue
        m = r.get("model")
        by_model[m][0] += 1
        if r.get("consensus_grade") == "A":
            by_model[m][1] += 1
    rows = sorted(
        [(m, a, n) for m, (n, a) in by_model.items()],
        key=lambda x: -x[1] / max(x[2], 1),
    )
    return rows


def kappa_pairwise(records):
    # Cohen's κ (4-class) on PRIMED+CONTROL combined
    from itertools import combinations

    def cohen_k(g1, g2):
        n = len(g1)
        po = sum(1 for a, b in zip(g1, g2) if a == b) / n
        labels = sorted(set(g1) | set(g2))
        pe = sum(
            (g1.count(l) / n) * (g2.count(l) / n) for l in labels
        )
        return (po - pe) / (1 - pe) if pe < 1 else float("nan")

    j1 = [r["judge1_grade"] for r in records]
    j2 = [r["judge2_grade"] for r in records]
    j3 = [r["judge3_grade"] for r in records]
    return {
        "Opus-4.6 vs GPT-4o": cohen_k(j1, j2),
        "Opus-4.6 vs Gemini-3-Flash": cohen_k(j1, j3),
        "GPT-4o vs Gemini-3-Flash": cohen_k(j2, j3),
    }


def unanimous_pct(records):
    n = len(records)
    una = sum(
        1
        for r in records
        if r.get("judge1_grade") == r.get("judge2_grade") == r.get("judge3_grade")
    )
    return una / n


def write_summary(records, out_path, label):
    cells = per_cell_rates(records)
    models = per_model_rates(records)
    ks = kappa_pairwise(records)
    una = unanimous_pct(records)
    n = len(records)
    primed_total = sum(1 for r in records if r.get("condition") == "PRIMED")
    primed_a = sum(
        1
        for r in records
        if r.get("condition") == "PRIMED" and r.get("consensus_grade") == "A"
    )
    ctl_total = sum(1 for r in records if r.get("condition") == "CONTROL")
    ctl_a = sum(
        1
        for r in records
        if r.get("condition") == "CONTROL" and r.get("consensus_grade") == "A"
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# {label} — Three-Judge Cross-Vendor Results\n\n")
        f.write(
            f"**Records graded**: {n} ({primed_total} PRIMED + {ctl_total} CONTROL)\n\n"
        )
        f.write(
            f"**Pooled CONTROL Grade-A**: {ctl_a} / {ctl_total} = "
            f"{ctl_a/ctl_total*100:.4f}%\n\n"
        )
        f.write(
            f"**Pooled PRIMED Grade-A**: {primed_a} / {primed_total} = "
            f"{primed_a/primed_total*100:.4f}%\n\n"
        )
        f.write("**Three-judge agreement** (this battery only):\n")
        f.write("- Pairwise Cohen's κ (4-class):\n")
        for k, v in ks.items():
            f.write(f"  - {k}: {v:.3f}\n")
        f.write(f"- Unanimous 3-of-3 agreement: {una*100:.2f}%\n\n")

        f.write("## Per-cell PRIMED Grade-A rate (sorted by rate)\n\n")
        f.write("| Cell | Culture | PRIMED A% | CONTROL A% | Δ |\n")
        f.write("|---|---|---:|---:|---:|\n")
        for cell, cult, pa, pn, ca, cn, pr, cr, dl in cells:
            f.write(
                f"| {cell} | {cult} | {pr*100:.1f}% ({pa}/{pn}) | "
                f"{cr*100:.1f}% ({ca}/{cn}) | {dl*100:+.1f}pp |\n"
            )
        f.write("\n")

        f.write("## Per-model PRIMED Grade-A rate (sorted by rate)\n\n")
        f.write("| Model | A | Total | Rate |\n")
        f.write("|---|---:|---:|---:|\n")
        for m, a, nn in models:
            f.write(f"| {m} | {a} | {nn} | {a/nn*100:.2f}% |\n")
        f.write("\n")

        f.write(
            "Regenerate via `python scripts/verify/regenerate_b11_b12_summaries.py`. "
            "Source: this directory's `graded_threejudge.jsonl`.\n"
        )

    print(f"Wrote {out_path}: N={n}, PRIMED-A={primed_a}/{primed_total}, "
          f"CONTROL-A={ctl_a}/{ctl_total}")


write_summary(B11, "data/b11_pure_modern_probes/SUMMARY.md", "B11 Pure-Modern Probes (Frontier-Model Lineup)")
write_summary(B12, "data/b12_small_models/SUMMARY.md", "B12 Pure-Modern Probes (Deployment-Tier Lineup)")
