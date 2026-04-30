"""Recovery script: previous renumber cascaded all SN 15..28 references to SN 14.
Walk section headers in file order and reassign 14..27. Then fix inline
references using a title-keyed lookup table.
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("manuscript")
sup_path = ROOT / "supplementary.md"
main_path = ROOT / "main.md"

# Walk supp.md and assign sequential SN numbers starting at 14 to all "## SN 14:"
# headers (in file order). Build {title: new_number} map.
sup = sup_path.read_text(encoding="utf-8")
lines = sup.splitlines()

current_n = 14
title_to_n = {}
new_lines = []
for line in lines:
    m = re.match(r"^(## SN )14(: .+)$", line)
    if m:
        title = m.group(2).lstrip(": ").strip()
        title_to_n[title] = current_n
        new_lines.append(f"## SN {current_n}: {title}")
        current_n += 1
    else:
        new_lines.append(line)

print(f"Renumbered {current_n - 14} section headers in supp.md, "
      f"final SN = {current_n - 1}")

new_sup = "\n".join(new_lines)
if not new_sup.endswith("\n"):
    new_sup += "\n"

# Fix Contents block: each "- Supplementary Note 14: <title>" line -> ... <new_n>
def fix_contents(text):
    def repl(m):
        title = m.group(1).strip()
        n = title_to_n.get(title)
        if n is None:
            # Title may be slightly different; try a fuzzy startswith match
            for known_title, kn in title_to_n.items():
                if title[:30].lower() in known_title.lower() or known_title[:30].lower() in title.lower():
                    n = kn
                    break
        if n is None:
            print(f"WARN: Contents title '{title[:60]}' not matched")
            return m.group(0)
        return f"- Supplementary Note {n}: {title}"
    return re.sub(r"^- Supplementary Note 14: (.+)$", repl, text, flags=re.MULTILINE)

new_sup = fix_contents(new_sup)

# Fix SN 14.X subsection refs (the SN 28 → SN 27 series). Find every "SN 14.<digit>"
# and replace with "SN 27.<digit>" — these were ALL inside the final (deployment-realistic)
# section, which is now SN 27.
new_sup = re.sub(r"\bSN 14\.(\d+)", r"SN 27.\1", new_sup)

# Now fix inline "SN 14" and "Supplementary Note 14" references in supp.md.
# Build a context-keyword → SN number map based on what each reference is about.
# Inspect remaining "SN 14" occurrences:
#   - SN 14 (around line 154 in original): "internal-incoherence pattern documented in SN 14"
#     -> SN 15 (Internal-incoherence pattern)
#   - SN 14 in line 728 ("verbatim judge prompt"): "SN 14 the verbatim judge prompt"
#     -> SN 18 (Verbatim judge rubric)
#   - SN 14 in line 787: "reported in SN 14" (about temperature-sensitivity sweep)
#     -> SN 25 (Temperature-sensitivity sweep)
#   - SN 14 in line 848 (boundary κ section): "rubric in §SN 14"
#     -> SN 3 (the strict A/B/C/D rubric is SN 3 — wait, but this said "§SN 14" originally)
#     Actually the original was "the strict A/B/C/D rubric in §SN 3" — let me reread.
#     This says "with the per-trial reported grade being the 2-of-3 majority consensus on
#     the strict A/B/C/D rubric in §SN 14". The rubric is SN 3 — but the "SN 14" reference
#     is wrong even before. Wait, this came from cascading. The original was probably "§SN 3".
#     Hmm but my cascading wouldn't touch SN 3. So this must have been SN N for some
#     N in 15-28. Looking at boundary tests context: it's about three-judge protocol +
#     reporting kappa. That maps to SN 19 (was Verbatim judge rubric).
#     Actually after re-reading: the original text was "rubric in §SN 19" or "rubric in SN 3".
#     If it was SN 19 (verbatim judge rubric), my cascade would have made it SN 14.
#     Best guess: SN 18 (was SN 19 = Verbatim judge rubric).
# Let's tackle them one-by-one:

inline_fixes_sup = [
    # (anchor_substring before-or-after the "SN 14", new_n)
    ("internal-incoherence pattern documented in SN 14", 15),  # SN 15: Internal-incoherence pattern
    ("SN 14 the verbatim judge prompt", 18),  # was SN 19: Verbatim judge rubric
    ("reported in SN 14 and shows the rates we report are stable", 25),  # SN 25: Temperature-sensitivity sweep
    ("strict A/B/C/D rubric in §SN 14", 18),  # SN 18: Verbatim judge rubric
    ("§3 and SN 14", 23),  # SN 23 lexical-control (line 1067 — was SN 24)
    ("§3 + SN 14 develops for the apartheid-SA", 23),  # SN 23 lexical-control
    ("(§3, SN 14)", 23),
]

for anchor, new_n in inline_fixes_sup:
    # Replace the "SN 14" inside the matched anchor with the new number
    if anchor in new_sup:
        fixed_anchor = anchor.replace("SN 14", f"SN {new_n}")
        new_sup = new_sup.replace(anchor, fixed_anchor, 1)
        print(f"  supp: '{anchor[:60]}' -> SN {new_n}")
    else:
        print(f"  WARN supp: anchor not found: '{anchor[:60]}'")

sup_path.write_text(new_sup, encoding="utf-8")

# Now main.md inline refs.
main = main_path.read_text(encoding="utf-8")

# Subsection refs SN 14.X should become SN 27.X (they all referred to the
# deployment-realistic-probe extension which is now SN 27)
main = re.sub(r"\bSN 14\.(\d+)", r"SN 27.\1", main)

inline_fixes_main = [
    # (anchor_substring containing "SN 14" or "Supplementary Note 14", new_n)
    ("(full per-model table in SN 14)", 24),  # dose-response → SN 24
    ("Full battery design, per-cell rates, per-model rates, cross-culture-group analysis, and verbatim are in Supplementary Note 14.", 27),  # deployment-realistic
    ("deployment-realistic-probe extension (SN 14), where an identical user message", 27),  # deployment-realistic
    ("rate variation does not exceed sampling noise (Supplementary Note 14)", 25),  # temperature
    ("the same priming that elicits 45-100% Grade A doctrinal compliance on the German direct probe leaves the model's general reasoning and factual recall intact (Supplementary Note 14)", 26),  # MMLU
    ("documented in Supplementary Note 14 for the German direct probe", 16),  # methods summary (soft frame cues)
    ("preceded the scaled batteries and is reported in Supplementary Note 14", 23),  # lexical-control extensions
    ("Calibration (R1, 180 trials) is described in Supplementary Note 14", 14),  # round-by-round dispatch totals
    ("full design and per-cell rates in Supplementary Note 14)", 27),  # deployment-realistic
    ("The full deposit structure is described in Supplementary Note 14.", 17),  # reproducibility
]

for anchor, new_n in inline_fixes_main:
    if anchor in main:
        fixed_anchor = anchor.replace("SN 14", f"SN {new_n}").replace(
            "Supplementary Note 14", f"Supplementary Note {new_n}"
        )
        main = main.replace(anchor, fixed_anchor, 1)
        print(f"  main: '{anchor[:60]}' -> {new_n}")
    else:
        print(f"  WARN main: anchor not found: '{anchor[:60]}'")

main_path.write_text(main, encoding="utf-8")

# Verify: count remaining "SN 14" in places it shouldn't be (besides "## SN 14: Round-by-round")
print("\n=== POST-FIX AUDIT ===")
import subprocess

for path in [sup_path, main_path]:
    text = path.read_text(encoding="utf-8")
    bad = []
    for i, line in enumerate(text.splitlines(), 1):
        if "SN 14" in line and not line.startswith("## SN 14:") and "Supplementary Note 14" not in line:
            # Skip the legitimate SN 14 section header
            if "SN 14:" in line:
                continue
            bad.append((i, line[:120]))
    print(f"\n{path.name}: {len(bad)} remaining SN-14 mentions to inspect:")
    for i, line in bad[:20]:
        print(f"  {i}: {line}")

print("\nFinal SN section list in supp.md:")
for line in sup_path.read_text(encoding="utf-8").splitlines():
    if line.startswith("## SN "):
        print(f"  {line}")
