#!/usr/bin/env python3
"""Build a single self-contained .tex from arxiv/twocolumn (tables and
bibliography inlined, comments stripped, figures guarded by \\IfFileExists)."""
import re, sys
from pathlib import Path

args = [a for a in sys.argv[1:] if not a.startswith("--")]
src = Path(args[0])
out = Path(args[1])
tex = (src / "main.tex").read_text()

def inline_table(m):
    return (src / "tables" / f"{m.group(1)}.tex").read_text().rstrip() + "\n"
tex = re.sub(r"\\input\{tables/(table_\d+)\}", inline_table, tex)

bbl = (src / "main.bbl").read_text().strip()
tex = re.sub(r"\\nocite\{\*\}\s*\\bibliographystyle\{arxivid\}\s*\\bibliography\{references\}",
             lambda m: bbl, tex)

def guard(m):
    path = m.group(2)
    return (r"\IfFileExists{%s}{%s}{\fbox{\parbox{0.6\linewidth}{\centering\footnotesize "
            r"Figure file %s not found; place it next to this .tex file.}}}" % (path, m.group(0), path.replace("_", r"\_")))
tex = re.sub(r"\\includegraphics(\[[^\]]*\])?\{([^}]+)\}", guard, tex)

# strip full-line and trailing comments
lines = []
for ln in tex.splitlines():
    if ln.lstrip().startswith("%"):
        continue
    lines.append(re.sub(r"(?<!\\)%.*$", "", ln).rstrip())
tex = "\n".join(lines) + "\n"

# optional: print the reference list at the very end (after the appendices), still inside the two-column body
if "--refs-last" in sys.argv:
    a = tex.index("\\section{References}")
    b = tex.index("\\end{thebibliography}}", a) + len("\\end{thebibliography}}")
    block = tex[a:b] + "\n"
    tex = tex[:a] + tex[b:].lstrip("\n")
    if "\\end{multicols}" in tex:
        k = tex.rindex("\\end{multicols}")
        tex = tex[:k] + block + "\n" + tex[k:]
    else:
        k = tex.rindex("\\end{document}")
        tex = tex[:k] + block + "\n" + tex[k:]
out.write_text(tex)
print(out, len(tex))
