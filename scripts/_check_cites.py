"""Manual citation cross-check: bib vs main.md+supplementary.md."""
import re

bib_keys = set()
with open('manuscript/references.bib','r',encoding='utf-8') as f:
    for line in f:
        m = re.match(r'^@\w+\{([^,]+),', line.strip())
        if m:
            bib_keys.add(m.group(1).strip())

# Match pandoc [@key] / [@k1; @k2] AND \cite{key,key2}
pandoc_pat = re.compile(r'@([A-Za-z][A-Za-z0-9_:.\-]*)')
latex_pat = re.compile(r'\\cite[a-zA-Z]*\{([^}]+)\}')

cited = {}
for fn in ['manuscript/main.md', 'manuscript/supplementary.md']:
    with open(fn, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            # pandoc: only count @ inside [...] or after ;
            # Find all [...]-spans first then look for @ inside
            for span in re.finditer(r'\[([^\[\]]*)\]', line):
                content = span.group(1)
                if '@' in content:
                    for m in pandoc_pat.finditer(content):
                        cited.setdefault(m.group(1), []).append(f'{fn}:{i}')
            # latex
            for m in latex_pat.finditer(line):
                for k in re.split(r'[,;\s]+', m.group(1)):
                    if k:
                        cited.setdefault(k, []).append(f'{fn}:{i}')

print(f'BIB entries: {len(bib_keys)}')
print(f'Unique cited keys: {len(cited)}')
print()
print('Cited keys:', sorted(cited.keys()))
print()
missing = sorted(set(cited) - bib_keys)
unused = sorted(bib_keys - set(cited))
print(f'MISSING from .bib ({len(missing)}):', missing)
print()
print(f'UNUSED .bib entries ({len(unused)}):')
for k in unused:
    print(f'  - {k}')
print()
print('--- Citation locations ---')
for k in sorted(cited.keys()):
    locs = cited[k]
    print(f'  @{k} ({len(locs)} uses): {locs}')
