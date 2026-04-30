"""Shift figure numbers in main.md and supplementary.md to make room for a new
Fig 2 inserted between the current Fig 1 and Fig 2.

Mapping: Fig N → Fig (N+1) for N in [2..7]. Descending order so we don't
cascade. Operates on common reference forms: 'Fig. N', 'Figure N',
'Fig N', 'Fig Nd' (panel letters), 'Figs. N–M'.
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def shift(text: str, mapping: dict[int, int]) -> tuple[str, int]:
    """Shift figure numbers by mapping. Operates only on the figure-reference
    patterns we expect in this manuscript. Returns (new_text, num_changes).
    """
    n_changes = 0

    def make_repl(prefix_pattern: str):
        def repl(m):
            nonlocal n_changes
            old_n = int(m.group("n"))
            new_n = mapping.get(old_n)
            if new_n is None:
                return m.group(0)
            n_changes += 1
            # Reconstruct the matched form, swapping only the number
            return m.group(0).replace(m.group("n"), str(new_n), 1)

        return repl

    # "Fig. N" / "Figure N" / "Fig N" / "Figure Nx" (where x is panel letter)
    text = re.sub(
        r"\bFig(?:ure|\.)?\s+(?P<n>\d+)(?=[a-z]?\b)",
        make_repl("Fig"),
        text,
    )
    # "Figs. N" plural
    text = re.sub(r"\bFigs\.?\s+(?P<n>\d+)", make_repl("Figs"), text)
    # "Supplementary Fig N"
    text = re.sub(r"\bSupplementary\s+Fig(?:ure|\.)?\s+(?P<n>\d+)", make_repl("SupFig"), text)

    return text, n_changes


# Map: Fig 2..7 → Fig 3..8 (descending so each rule fires once)
mapping = {n: n + 1 for n in range(2, 8)}

for fname in ["manuscript/main.md", "manuscript/supplementary.md"]:
    p = Path(fname)
    text = p.read_text(encoding="utf-8")
    new_text, n = shift(text, mapping)
    if n > 0:
        p.write_text(new_text, encoding="utf-8")
        print(f"{fname}: {n} figure-reference replacements")
    else:
        print(f"{fname}: no figure-reference changes")

print(
    "\nVerify with:  grep -n 'Fig\\.\\? \\?[0-9]\\|Figure [0-9]' "
    "manuscript/main.md | head -30"
)
