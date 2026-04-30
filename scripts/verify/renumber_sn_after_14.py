"""Drop the reserved SN 14 placeholder and renumber SN 15..28 → SN 14..27 in
both supplementary.md and main.md, including all cross-references.

Idempotent: safe to run only once. After running, SN 28 becomes SN 27 etc.
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("manuscript")
files = ["main.md", "supplementary.md"]

# Step 1: remove the "## SN 14: Reserved\n\nSection number reserved.\n\n"
# block in supplementary.md (and \pagebreak after, if present).
sup = (ROOT / "supplementary.md").read_text(encoding="utf-8")
pattern = r"## SN 14: Reserved\s*\n\s*\nSection number reserved\.\s*\n\s*\n(\\pagebreak\s*\n\s*\n)?"
new_sup = re.sub(pattern, "", sup, count=1)
if new_sup == sup:
    print("WARN: SN 14 placeholder not found; skipping removal step")
else:
    (ROOT / "supplementary.md").write_text(new_sup, encoding="utf-8")
    print("Removed SN 14 placeholder block from supplementary.md")


def renumber_in_text(text: str) -> str:
    """Map SN N → SN (N-1) and Supplementary Note N → Supplementary Note (N-1)
    for N in [15, 28]. Apply in DESCENDING order so 16→15 doesn't collide
    with the next pass on 15.
    """
    out = text
    for n in range(28, 14, -1):  # 28, 27, ..., 15
        new_n = n - 1
        # SN N (with section-marker boundary)
        out = re.sub(rf"\bSN {n}\b", f"SN {new_n}", out)
        out = re.sub(rf"\bSupplementary Note {n}\b", f"Supplementary Note {new_n}", out)
        # SN-Nx variants like "SN 28.A" should also shift to SN 27.A
        out = re.sub(rf"\bSN-{n}\.([A-Z])", rf"SN-{new_n}.\1", out)
        # SN N.subnum notation like "SN 28.10"
        out = re.sub(rf"\bSN {n}\.", f"SN {new_n}.", out)
    return out


for fn in files:
    path = ROOT / fn
    txt = path.read_text(encoding="utf-8")
    new = renumber_in_text(txt)
    if new != txt:
        path.write_text(new, encoding="utf-8")
        print(f"Renumbered SN refs in {fn}")
    else:
        print(f"No SN renumber changes in {fn}")

print("\nDone. Final SN section list:")
for line in (ROOT / "supplementary.md").read_text(encoding="utf-8").splitlines():
    if line.startswith("## SN "):
        print(f"  {line}")
