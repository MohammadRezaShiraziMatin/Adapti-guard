"""Convert docs/paper/negative_result/MANUSCRIPT_DRAFT_v1.md into an arXiv LaTeX source.

Deterministic; no prose is edited. The assembled manuscript stays the single source of text:
edit the section sources, run scripts/assemble_manuscript.py, then run this script.
Needs pandoc. Output: docs/paper/negative_result/arxiv/{main.tex,tables/*.tex,figures/*.png}; references.bib and arxivid.bst are hand-kept there.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

N = Path(__file__).resolve().parents[1] / "docs/paper/negative_result"
OUT = N / "arxiv"

FIG_CAPTIONS = {
    "fig1_scoring_flip": "M1--M3 on the same 288 attack traces (of the 468 E2 episodes) under four scoring rules.",
    "fig2_susceptibility": "M5: undefended susceptibility by attack family and model.",
    "fig3_defended_vs_a0": "M4/M5: partially independent set, defended vs undefended (noise floor).",
}

PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage[margin=1in]{geometry}
\usepackage{microtype}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs,longtable,array,calc,etoolbox}
\usepackage{url}
\usepackage[hidelinks]{hyperref}
\DeclareUnicodeCharacter{2212}{\ensuremath{-}}
\DeclareUnicodeCharacter{2265}{\ensuremath{\geq}}
\DeclareUnicodeCharacter{2192}{\ensuremath{\rightarrow}}
\DeclareUnicodeCharacter{03BA}{\ensuremath{\kappa}}
\DeclareUnicodeCharacter{03B4}{\ensuremath{\delta}}
\DeclareUnicodeCharacter{0302}{\^{}}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\setcounter{secnumdepth}{0}  % section numbers are part of the heading text
\setlength{\parskip}{0.5em}\setlength{\parindent}{0pt}
\emergencystretch=3em
\AtBeginEnvironment{longtable}{\footnotesize\raggedright}
% the manuscript supplies its own "References" heading above the bibliography
\patchcmd{\thebibliography}{\section*{\refname}}{}{}{\PackageWarning{main}{bibliography heading not patched}}
"""


def split_manuscript(md: str) -> tuple[str, str, str, str]:
    title = re.match(r"# (.+)", md).group(1).strip()
    abstract = re.search(r"## Abstract\n(.*?)\n\*\*Keywords:\*\*", md, re.S).group(1).strip()
    keywords = re.search(r"\*\*Keywords:\*\*\s*(.+)", md).group(1).strip()
    body = md[md.index("## 1 Introduction"):]
    return title, abstract, keywords, body


def pandoc(text: str, extra: list[str] | None = None) -> str:
    cmd = ["pandoc", "-f", "markdown-tex_math_dollars-raw_tex-smart-auto_identifiers-implicit_figures",
           "-t", "latex", "--wrap=preserve", *(extra or [])]
    return subprocess.run(cmd, input=text, capture_output=True, text=True, check=True).stdout


def breakable_tt(tex: str) -> str:
    """Allow line breaks after / and _ inside \\texttt{...} so long paths do not overflow."""

    def fix(m: re.Match) -> str:
        return m.group(0).replace("/", "/\\allowbreak{}").replace("\\_", "\\_\\allowbreak{}")

    return re.sub(r"\\texttt\{[^{}]*\}", fix, tex)


def check_bib(ref_md: str) -> None:
    """The manuscript's reference list and references.bib must name the same arXiv ids, in the same order."""
    md_ids = re.findall(r"(?m)^- \[(\d{4}\.\d{5})\]", ref_md)
    bib_ids = re.findall(r"eprint = \{(\d{4}\.\d{5})\}", (OUT / "references.bib").read_text())
    assert md_ids == bib_ids, (md_ids, bib_ids)


def split_tables(tex: str) -> str:
    """Move every longtable into tables/table_NN.tex and \\input it."""
    tdir = OUT / "tables"
    shutil.rmtree(tdir, ignore_errors=True)
    tdir.mkdir()
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        count += 1
        name = f"table_{count:02d}"
        (tdir / f"{name}.tex").write_text(m.group(0) + "\n")
        return f"\\input{{tables/{name}}}"

    return re.sub(r"\\begin\{longtable\}.*?\\end\{longtable\}", repl, tex, flags=re.S)


def figure_block(stem: str, label: int) -> str:
    return (
        "\\begin{figure}[htbp]\n\\centering\n"
        f"\\includegraphics[width=\\linewidth]{{figures/{stem}.png}}\n"
        f"\\caption{{{FIG_CAPTIONS[stem]}}}\n\\label{{fig:{label}}}\n\\end{{figure}}\n"
    )


def main() -> None:
    md = (N / "MANUSCRIPT_DRAFT_v1.md").read_text()
    title, abstract, keywords, body = split_manuscript(md)
    body = re.sub(r"(?m)^---\s*$", "", body)  # horizontal rules between paragraphs
    # pandoc needs a blank line before a pipe table; the manuscript sometimes omits it
    body = re.sub(r"(?m)^([^|\n].*)\n(?=\|)", r"\1\n\n", body)
    head, rest = body.split("## References\n", 1)
    ref_md, tail = rest.split("## Appendix A", 1)
    check_bib(ref_md)
    ref_intro = "## References\n" + ref_md.split("\n- [", 1)[0] + "\n"
    opts = ["--top-level-division=section", "--shift-heading-level-by=-1"]
    body_tex = breakable_tt(
        pandoc(head, opts)
        + pandoc(ref_intro, opts)
        + "\\nocite{*}\n\\bibliographystyle{arxivid}\n\\bibliography{references}\n\n"
        + pandoc("## Appendix A" + tail, opts)
    )
    # place the three committed figures after the paragraph that introduces them
    marker = re.search(r"\\textbf\{Figures\.\}.*?\n\n", body_tex, re.S)
    figs = "\n".join(figure_block(s, i + 1) for i, s in enumerate(FIG_CAPTIONS))
    body_tex = body_tex[: marker.end()] + figs + "\n" + body_tex[marker.end():]
    body_tex = split_tables(body_tex)
    doc = (
        PREAMBLE
        + f"\\title{{{pandoc(title).strip()}}}\n"
        + "\\author{{[AUTHOR NAME --- TO BE FILLED BY THE OWNER]}\\\\\n"
          "{[AFFILIATION --- TO BE FILLED BY THE OWNER]}\\\\\n"
          "\\texttt{[EMAIL --- TO BE FILLED BY THE OWNER]}}\n"
        + "\\date{}\n\\begin{document}\n\\maketitle\n"
        + "\\begin{abstract}\n" + pandoc(abstract).strip() + "\n\\end{abstract}\n\n"
        + "\\noindent\\textbf{Keywords:} " + pandoc(keywords).strip() + "\n\n"
        + body_tex + "\n\\end{document}\n"
    )
    OUT.mkdir(exist_ok=True)
    (OUT / "figures").mkdir(exist_ok=True)
    for stem in FIG_CAPTIONS:
        shutil.copy2(N / "figures" / f"{stem}.png", OUT / "figures" / f"{stem}.png")
    (OUT / "main.tex").write_text(doc)
    print(f"wrote {OUT / 'main.tex'}")


if __name__ == "__main__":
    main()
