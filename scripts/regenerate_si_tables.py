"""Regenerate SN 4 per-cell x per-model A/B/C/D tables from r3 canonical jsonl.

Emits markdown rows ordered by cell, then by model in a fixed order.
Models with non-priming records (control/negative-control cells) are still
included; the SN 4 table reports only `primed=True` priming cells.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "canonical" / "r3_cross_cultural_matrix.jsonl"

# Canonical 14-model order (highest A% first, mirrors SN 5 ordering)
MODEL_ORDER = [
    "gemini-3-flash-preview",
    "gemini-2.5-pro",
    "claude-opus-4-7",
    "claude-sonnet-4-6",
    "gemini-3.1-pro-preview",
    "claude-sonnet-4-5",
    "gemini-2.5-flash",
    "gpt-5.4",
    "gpt-5.4-mini",
    "claude-opus-4-6",
    "gpt-4o",
    "gpt-5.5",
    "claude-opus-4-5",
    "claude-haiku-4-5",
]

# Cells in the priming (non-control, non-negative-control) main table
PRIMING_CELLS_ORDER = [
    "HITLER_V1_WISH",
    "HITLER_V2_DIRECT",
    "SOVIET_V1_WISH",
    "SOVIET_V2_DIRECT",
    "MEDIEVAL_ARAB_LEADER",
    "MEDIEVAL_ARAB_AUTHORITY",
    "EDO_JAPAN_HONOR",
    "EDO_JAPAN_SAMURAI",
    "CONFUCIAN_OBEDIENCES",
    "CONFUCIAN_DAUGHTER",
    "CONFUCIAN_FORENSIC",
    "CONFEDERATE_LABOR",
    "AZTEC_RULER",
    "VICTORIAN_LEADER",
    "APARTHEID_SA_LEADER",
    "INDIAN_CASTE_MARRIAGE",
    "INDIAN_DHARMA_DAUGHTER",
]


def grade_of(rec):
    return rec.get("final_grade") or rec.get("consensus_grade") or rec.get("polish_grade")


def main():
    table = defaultdict(Counter)
    with SRC.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if not r.get("primed"):
                continue
            cell = r.get("cell")
            model = r.get("model")
            g = grade_of(r)
            if g not in ("A", "B", "C", "D"):
                continue
            table[(cell, model)][g] += 1

    out_lines = ["| Cell | Model | N | A | B | C | D | A% | A+B% |",
                 "|---|---|---|---|---|---|---|---|---|"]
    for cell in PRIMING_CELLS_ORDER:
        for model in MODEL_ORDER:
            c = table.get((cell, model), Counter())
            a, b, cc, d = c.get("A", 0), c.get("B", 0), c.get("C", 0), c.get("D", 0)
            n = a + b + cc + d
            if n == 0:
                continue
            ap = 100.0 * a / n
            abp = 100.0 * (a + b) / n
            out_lines.append(
                f"| {cell} | {model} | {n} | {a} | {b} | {cc} | {d} | {ap:.1f} | {abp:.1f} |"
            )
    print("\n".join(out_lines))


if __name__ == "__main__":
    main()
