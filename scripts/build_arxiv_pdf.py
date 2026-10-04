"""Build an arXiv-ready PDF (HTML route, no LaTeX needed) and the arXiv metadata from the assembled manuscript.

Needs `pypandoc_binary` and `weasyprint` (pip). Reads docs/paper/negative_result/MANUSCRIPT_DRAFT_v1.md and the committed figures; changes no
number or claim. The three figures are placed at their section headings (6.2 and 6.3); the authors line is supplied by the owner with
--authors (default is a visible placeholder, so a placeholder PDF cannot be mistaken for a final one).
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
N = ROOT / "docs/paper/negative_result"
FIGS = {"### 6.2 E2": [("fig1_scoring_flip", "Figure 1")], "### 6.3 E3": [("fig2_susceptibility", "Figure 2"), ("fig3_defended_vs_a0", "Figure 3")]}
CSS = """@page { size: A4; margin: 22mm 18mm; @bottom-center { content: counter(page); font-size: 9pt; } }
body { font-family: 'DejaVu Serif', serif; font-size: 10pt; line-height: 1.38; } h1 { font-size: 17pt; text-align: center; }
h2 { font-size: 13pt; margin-top: 1.4em; } h3 { font-size: 11pt; } code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8pt; word-break: break-all; }
table { border-collapse: collapse; font-size: 7.5pt; width: 100%; margin: 0.8em 0; } th, td { border: 0.4pt solid #777; padding: 2pt 3pt; vertical-align: top; word-break: break-word; }
img { max-width: 100%; } figure { margin: 1em 0; page-break-inside: avoid; } figcaption { font-size: 8.5pt; text-align: center; }
p.authors { text-align: center; font-size: 10pt; } header#title-block-header { display: none; }"""


def arxiv_abstract(md: str) -> str:
    a = re.search(r"## Abstract\n(.*?)\n\*\*Keywords", md, re.S).group(1).strip()
    for cut in (" (56 vs 57 of 167, and 57 vs 57 of 168 pairs)", "; every disagreement is judge = success without an executed call"):
        a = a.replace(cut, "")  # metadata abstract only: arXiv limits it to 1,920 characters; the manuscript abstract is unchanged
    return a


def main(argv=None) -> int:
    import pypandoc
    from weasyprint import HTML
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--authors", default="[AUTHOR NAMES AND AFFILIATIONS: the owner must supply these (build option authors) before upload]")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    md = (N / "MANUSCRIPT_DRAFT_v1.md").read_text()
    title = md.splitlines()[0].lstrip("# ").strip()
    body = "\n".join(md.splitlines()[1:])
    for head, figs in FIGS.items():
        add = "\n\n".join(f"![{lab} (source data: figures/{stem}.csv)](figures/{stem}.png)" for stem, lab in figs)
        pat = re.compile(rf"^({re.escape(head)}.*)$", re.M)
        assert pat.search(body), head
        body = pat.sub(lambda m: m.group(1) + "\n\n" + add, body, count=1)
    lines, fixed = body.splitlines(), []
    for i, ln in enumerate(lines):  # pandoc needs a blank line before a pipe table; the manuscript sometimes puts the table right under its caption
        if ln.startswith("|") and i and lines[i - 1].strip() and not lines[i - 1].startswith("|"):
            fixed.append("")
        fixed.append(ln)
    body = "\n".join(fixed)
    hdr = a.out / "style.html"
    hdr.write_text(f"<style>{CSS}</style>")
    html = pypandoc.convert_text(f"# {title}\n\n::: {{.authors}}\n{a.authors}\n:::\n\n" + body, "html5", format="markdown-smart+pipe_tables+fenced_divs+implicit_figures",
                                 extra_args=["--standalone", "--metadata", f"pagetitle={title}", "--include-in-header", str(hdr), "--resource-path", str(N)])
    (a.out / "paper.html").write_text(html)
    HTML(string=html, base_url=str(N) + "/").write_pdf(a.out / "paper.pdf", stylesheets=None)
    abs_ = arxiv_abstract(md)
    meta = {"title": title, "abstract_chars": len(abs_), "abstract": abs_, "primary_category": "cs.CR", "cross_lists": ["cs.AI", "cs.LG"],
            "comments": "Exploratory measurement-validity case study; nothing confirmatory. A confirmatory protocol exists but was not run.",
            "license_note": "choose at submission (the owner decides)", "authors": "owner supplies; AI assistants are not authors"}
    assert len(abs_) <= 1920, len(abs_)
    (a.out / "arxiv_metadata.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: meta[k] for k in ("title", "abstract_chars")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
