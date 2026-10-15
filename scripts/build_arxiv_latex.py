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

PREAMBLE = r"""\documentclass[9pt]{extarticle}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage[top=0.8in,bottom=0.8in,left=0.65in,right=0.65in]{geometry}
\usepackage{microtype}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs,longtable,array,calc,etoolbox}
\usepackage{url}
\usepackage{multicol,caption}
\usepackage[hidelinks]{hyperref}
\DeclareUnicodeCharacter{2212}{\ensuremath{-}}
\DeclareUnicodeCharacter{2265}{\ensuremath{\geq}}
\DeclareUnicodeCharacter{2192}{\ensuremath{\rightarrow}}
\DeclareUnicodeCharacter{03BA}{\ensuremath{\kappa}}
\DeclareUnicodeCharacter{03B4}{\ensuremath{\delta}}
\DeclareUnicodeCharacter{0302}{\^{}}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\setcounter{secnumdepth}{0}  % section numbers are part of the heading text
\setlength{\parskip}{0.3em}\setlength{\parindent}{0pt}
\emergencystretch=2em
\setlength{\columnsep}{0.25in}
\captionsetup{font=small,skip=2pt}
\AtBeginEnvironment{longtable}{\scriptsize\raggedright}
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


def split_tables(tex: str, start: int, tdir: Path | None = None) -> tuple[str, int]:
    """Move every longtable into tables/table_NN.tex and \\input it; numbering continues from start."""
    tdir = tdir or OUT / "tables"
    count = start

    def repl(m: re.Match) -> str:
        nonlocal count
        count += 1
        name = f"table_{count:02d}"
        (tdir / f"{name}.tex").write_text(m.group(0) + "\n")
        return f"\\input{{tables/{name}}}"

    out = re.sub(r"\\begin\{longtable\}.*?\\end\{longtable\}", repl, tex, flags=re.S)
    return out, count


def figure_block(stem: str, label: int) -> str:
    return (
        "\\begin{center}\n"
        f"\\includegraphics[width=0.62\\linewidth]{{figures/{stem}.png}}\n\\captionof{{figure}}{{{FIG_CAPTIONS[stem]}}}\n"
        "\\end{center}\n"
    )


# DRAFT acknowledgements / AI-use disclosure. Not part of MANUSCRIPT_DRAFT_v1.md; it restates section 10 ("Use of AI assistance")
# and section 8.3 and adds nothing new. The authors must confirm or edit it before posting.
ACK = r"""\section*{Acknowledgements and AI-use disclosure}
An AI assistant (Claude, Anthropic) was used under the authors' direction. It wrote the seven attack-scenario families of the partially independent set (Section 8.3),
contributed to analysis code, harness extensions and drafts of this manuscript, produced repository audits and internal review notes, and converted the manuscript into the \LaTeX{} source of this version.
The assistant is not an author. All numbers were regenerated from the persisted traces by scripts.
Because the same assistant family wrote the attack families, drafted the manuscript and produced the internal reviews, none of these is an independent human check (Sections 8.3 and 10).
The authors take responsibility for all content of this paper.

\medskip\noindent\textbf{Funding.} This work received no external funding.

"""

# Material that goes to the supplement; the main paper keeps the heading (so cross-references still resolve) and a pointer.
MOVED_SECTIONS = ["### 5.6 ", "### 6.7 ", "### 8.5 "]
MOVED_TABLES = ["**Table 2."]


def cut_section(md: str, prefix: str) -> tuple[str, str]:
    """Return (md with the section body replaced by a pointer, the section block)."""
    m = re.search(rf"(?m)^{re.escape(prefix)}.*$", md)
    nxt = re.search(r"(?m)^#{2,3} ", md[m.end():])
    end = m.end() + nxt.start() if nxt else len(md)
    block = md[m.start():end]
    stub = f"{m.group(0)}\n*Moved to the supplement (Section S1, same heading); it is part of this paper.*\n\n"
    return md[:m.start()] + stub + md[end:], block


def cut_table(md: str, caption_prefix: str) -> tuple[str, str]:
    """Return (md with the captioned pipe table replaced by a pointer, the caption plus table)."""
    m = re.search(rf"(?m)^{re.escape(caption_prefix)}.*\n\n?(?:\|.*\n)+", md)
    name = caption_prefix.strip("*. ")
    stub = f"*{name} is in the supplement (Section S2).*\n"
    return md[:m.start()] + stub + md[m.end():], m.group(0)


def in_columns(tex: str) -> str:
    """Two-column text; tables and figures break out to full width (longtable cannot live in a column)."""
    pieces = re.split(r"(\\input\{tables/table_\d+\}|\\begin\{center\}\n\\includegraphics.*?\\end\{center\})", tex, flags=re.S)
    out = []
    for i, piece in enumerate(pieces):
        if i % 2 == 1:
            out.append(piece + "\n")
        elif piece.strip():
            out.append("\\begin{multicols}{2}\n" + piece + "\n\\end{multicols}\n")
    return "".join(out)


def write_doc(name: str, title_tex: str, front: str, body_tex: str, preamble: str | None = None, strip_comments: bool = False) -> None:
    doc = (
        (preamble or PREAMBLE)
        + f"\\title{{{title_tex}}}\n"
        + "% AUTHORS: names as given by the owner. Spelling of the second name is unconfirmed (given as 'RezaManzour').\n"
          "% Emails as given by the owner. Affiliation (independent) as given by the owner. Corresponding author (Matin Shirazi, the first author) is a default the authors may change: fill them in before posting.\n"
          "\\author{Matin Shirazi (Shirazimatin@gmail.com) \\and Reza Manzour (Rezamanzourolajdad@gmail.com)\\\\[0.4em]\n"
          "{Independent Researchers}\\\\\n"
          "{Corresponding author: Matin Shirazi}}\n"
        + "\\date{}\n\\begin{document}\n\\maketitle\n"
        + front + body_tex + "\n\\end{document}\n"
    )
    if strip_comments:
        doc = re.sub(r"(?m)^%.*\n", "", doc)
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc)


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
    head_full = head
    moved_secs, moved_tabs = [], []
    for pre in MOVED_SECTIONS:
        head, blk = cut_section(head, pre)
        moved_secs.append(blk)
    for cap in MOVED_TABLES:
        head, blk = cut_table(head, cap)
        moved_tabs.append(blk)
    opts = ["--top-level-division=section", "--shift-heading-level-by=-1"]
    main_tex = breakable_tt(
        pandoc(head, opts)
        + pandoc(ref_intro, opts)
        + "{\\footnotesize\\setlength{\\itemsep}{0pt}\\setlength{\\parskip}{0pt}\n\\nocite{*}\n\\bibliographystyle{arxivid}\n\\bibliography{references}}\n"
    )
    main_tex = main_tex.replace("\\section{References}", ACK + "\\section{References}", 1)
    # place the three committed figures after the paragraph that introduces them
    marker = re.search(r"\\textbf\{Figures\.\}.*?\n\n", main_tex, re.S)
    figs = "\n".join(figure_block(s, i + 1) for i, s in enumerate(FIG_CAPTIONS))
    main_tex = main_tex[: marker.end()] + figs + "\n" + main_tex[marker.end():]
    supp_md = (
        "## S1 Subsections moved from the main paper\n" + "".join(moved_secs)
        + "\n## S2 Tables moved from the main paper\n" + "\n".join(moved_tabs)
        + "\n## Appendix A" + tail
    )
    supp_tex = breakable_tt(pandoc(supp_md, opts))
    tdir = OUT / "tables"
    shutil.rmtree(tdir, ignore_errors=True)
    tdir.mkdir()
    main_tex, n = split_tables(main_tex, 0)
    supp_tex, _ = split_tables(supp_tex, n)
    title_tex = pandoc(title).strip()
    front = (
        "\\begin{abstract}\n" + pandoc(abstract).strip() + "\n\\end{abstract}\n\n"
        + "\\noindent\\textbf{Keywords:} " + pandoc(keywords).strip() + "\n\n"
        + "\\noindent\\textit{Appendices A to D and the material marked ``moved to the supplement'' are in the separate supplement (\\texttt{supplement.pdf}).}\n\n"
    )
    write_doc("main.tex", title_tex, front, in_columns(main_tex))
    supp_front = (
        "\\noindent\\textit{Supplement to the main paper. Section numbers (\\S) refer to the main paper. "
        "The text below is reproduced unchanged from the same manuscript source.}\n\n"
    )
    write_doc("supplement.tex", "Supplement to: " + title_tex, supp_front, supp_tex)
    OUT.mkdir(exist_ok=True)
    (OUT / "figures").mkdir(exist_ok=True)
    for stem in FIG_CAPTIONS:
        shutil.copy2(N / "figures" / f"{stem}.png", OUT / "figures" / f"{stem}.png")
    # Single-column 10 pt preprint with everything in one document (no supplement split); this is the arXiv upload candidate.
    sub = OUT / "submission"
    shutil.rmtree(sub / "tables", ignore_errors=True)
    full_tex = breakable_tt(
        pandoc(head_full, opts)
        + pandoc(ref_intro, opts)
        + "{\\footnotesize\\setlength{\\itemsep}{0pt}\\setlength{\\parskip}{0pt}\n\\nocite{*}\n\\bibliographystyle{arxivid}\n\\bibliography{references}}\n"
        + pandoc("## Appendix A" + tail, opts)
    )
    full_tex = full_tex.replace("\\section{References}", ACK + "\\section{References}", 1)
    marker = re.search(r"\\textbf\{Figures\.\}.*?\n\n", full_tex, re.S)
    full_tex = full_tex[: marker.end()] + figs.replace("0.62", "0.8") + "\n" + full_tex[marker.end():]
    (sub / "tables").mkdir(parents=True, exist_ok=True)
    full_tex, _ = split_tables(full_tex, 0, sub / "tables")
    full_pre = (
        PREAMBLE.replace("\\documentclass[9pt]{extarticle}", "\\documentclass[10pt]{article}")
        .replace("left=0.65in,right=0.65in", "left=0.9in,right=0.9in")
        .replace("\\scriptsize\\raggedright", "\\footnotesize\\raggedright")
        .replace("\\setlength{\\parskip}{0.3em}", "\\setlength{\\parskip}{0.5em}")
    )
    full_front = "\\begin{abstract}\n" + pandoc(abstract).strip() + "\n\\end{abstract}\n\n" + "\\noindent\\textbf{Keywords:} " + pandoc(keywords).strip() + "\n\n"
    write_doc("submission/main.tex", title_tex, full_front, full_tex, preamble=full_pre, strip_comments=True)
    (sub / "figures").mkdir(parents=True, exist_ok=True)
    for stem in FIG_CAPTIONS:
        shutil.copy2(N / "figures" / f"{stem}.png", sub / "figures" / f"{stem}.png")
    shutil.copy2(OUT / "references.bib", sub / "references.bib")
    shutil.copy2(OUT / "arxivid.bst", sub / "arxivid.bst")

    # Two-column 9 pt variant with everything in one document (same text as the single-column preprint); layout only.
    tc = OUT / "twocolumn"
    shutil.rmtree(tc / "tables", ignore_errors=True)
    tc_tex = breakable_tt(
        pandoc(head_full, opts)
        + pandoc(ref_intro, opts)
        + "{\\footnotesize\\setlength{\\itemsep}{0pt}\\setlength{\\parskip}{0pt}\n\\nocite{*}\n\\bibliographystyle{arxivid}\n\\bibliography{references}}\n"
        + pandoc("## Appendix A" + tail, opts)
    )
    tc_tex = tc_tex.replace("\\section{References}", ACK + "\\section{References}", 1)
    tc_tex = tc_tex.replace("SMOKE,EXPLORATORY,INDEPENDENT", "SMOKE,\\allowbreak{}EXPLORATORY,\\allowbreak{}INDEPENDENT").replace("SCREEN,INDEPENDENT", "SCREEN,\\allowbreak{}INDEPENDENT")  # layout only: lets the long run id wrap in a column
    marker = re.search(r"\\textbf\{Figures\.\}.*?\n\n", tc_tex, re.S)
    tc_tex = tc_tex[: marker.end()] + figs + "\n" + tc_tex[marker.end():]
    (tc / "tables").mkdir(parents=True, exist_ok=True)
    tc_tex, _ = split_tables(tc_tex, 0, tc / "tables")
    tc_front = "\\begin{abstract}\n" + pandoc(abstract).strip() + "\n\\end{abstract}\n\n" + "\\noindent\\textbf{Keywords:} " + pandoc(keywords).strip() + "\n\n"
    write_doc("twocolumn/main.tex", title_tex, tc_front, in_columns(tc_tex), strip_comments=True)
    (tc / "figures").mkdir(parents=True, exist_ok=True)
    for stem in FIG_CAPTIONS:
        shutil.copy2(N / "figures" / f"{stem}.png", tc / "figures" / f"{stem}.png")
    shutil.copy2(OUT / "references.bib", tc / "references.bib")
    shutil.copy2(OUT / "arxivid.bst", tc / "arxivid.bst")
    print(f"wrote {OUT / 'main.tex'}, {OUT / 'supplement.tex'} and {sub / 'main.tex'}")


if __name__ == "__main__":
    main()
