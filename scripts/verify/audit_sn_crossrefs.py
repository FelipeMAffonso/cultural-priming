"""Audit every Supplementary Note cross-reference in main.md and supplementary.md.
Verify each "SN N" / "Supplementary Note N" / "Table SN-N.X" reference points
to a section that exists.
"""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load_headers(path):
    text = open(path, encoding="utf-8").read()
    headers = {}
    for m in re.finditer(r"^## SN (\d+):\s*(.+)$", text, re.MULTILINE):
        headers[int(m.group(1))] = m.group(2).strip()
    return headers


sup_headers = load_headers("manuscript/supplementary.md")

# Collect SN-27 sub-section headers
sup_text = open("manuscript/supplementary.md", encoding="utf-8").read()
sub_headers = {}
for m in re.finditer(r"^### SN 27\.(\d+):\s*(.+)$", sup_text, re.MULTILINE):
    sub_headers[int(m.group(1))] = m.group(2).strip()

print(f"Canonical headers in supp.md: SN {min(sup_headers)}..{max(sup_headers)}")
print(f"SN 27 sub-sections: SN 27.{min(sub_headers)}..27.{max(sub_headers)}")
print()

bad_refs = []
all_refs = []

for fname in ["manuscript/main.md", "manuscript/supplementary.md"]:
    text = open(fname, encoding="utf-8").read()
    print(f"\n=== {fname} ===")

    # Pattern: "SN N" or "Supplementary Note N" with optional .X subsection
    for m in re.finditer(
        r"\b(SN|Supplementary Note)\s+(\d+)(?:\.(\d+))?\b", text
    ):
        n = int(m.group(2))
        sub = int(m.group(3)) if m.group(3) else None
        line_no = text[: m.start()].count("\n") + 1
        ctx = text[max(0, m.start() - 50) : m.end() + 50].replace("\n", " ")

        ok_main = n in sup_headers
        ok_sub = (sub is None) or (n == 27 and sub in sub_headers)
        ok = ok_main and ok_sub

        if not ok:
            mark = "BAD"
            bad_refs.append((fname, line_no, n, sub, ctx))
        else:
            mark = "OK "
        all_refs.append((fname, line_no, n, sub, ok))

        if not ok:
            print(f"  {mark}  L{line_no}  SN {n}{f'.{sub}' if sub else ''}")
            print(f"        ctx: ...{ctx}...")

# Pattern: "Table SN-N.X" labels and references
print("\n\n=== TABLE LABELS ===")
for fname in ["manuscript/main.md", "manuscript/supplementary.md"]:
    text = open(fname, encoding="utf-8").read()
    for m in re.finditer(r"\bTABLE SN[-‑](\d+)\.([A-Z])\b", text, re.IGNORECASE):
        n = int(m.group(1))
        letter = m.group(2)
        line_no = text[: m.start()].count("\n") + 1
        ok = n in sup_headers
        if not ok:
            print(f"  BAD {fname} L{line_no}  TABLE SN-{n}.{letter}")

# Summary
print(
    f"\n\nTotal refs: {len(all_refs)}, "
    f"bad: {len(bad_refs)}, "
    f"valid: {len(all_refs) - len(bad_refs)}"
)
