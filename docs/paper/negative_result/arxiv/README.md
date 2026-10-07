# arXiv package: negative-result paper (draft, not submitted)

Source: `docs/paper/negative_result/MANUSCRIPT_DRAFT_v1.md` (assembled from the section sources by `scripts/assemble_manuscript.py`).
Nothing was submitted to arXiv. Posting is the owner's action.

## Contents
- `main.tex`: generated LaTeX source (pdfLaTeX, standard packages only, no bibliography file: references are the manuscript's own list).
- `figures/`: the three committed PNGs (`fig1_scoring_flip`, `fig2_susceptibility`, `fig3_defended_vs_a0`), copied unchanged from `../figures/`.
- `ARXIV_METADATA.md`: suggested category, title, abstract (arXiv's 1920-character limit), comments field.
- `OWNER_DECISIONS.md`: what must be decided before posting.

Not included on purpose: MANUSCRIPT_SKELETON, ROADMAP_20261001, PREREGISTRATION_AUDIT_STATUS_20261001, FINAL_AUDIT_20261001.

## Rebuild
```
python3 scripts/assemble_manuscript.py       # only if a section source changed
python3 scripts/build_arxiv_latex.py         # regenerates arxiv/main.tex and copies figures (needs pandoc)
cd docs/paper/negative_result/arxiv && pdflatex main.tex && pdflatex main.tex
```
Never edit `main.tex` by hand; edit the section sources and regenerate.

## Fidelity check done
No prose is edited by the converter (it only drops horizontal rules, adds blank lines before pipe tables, adds line-break hints inside monospace paths, and inserts the three figures after the paragraph that introduces them, with captions taken from that paragraph). Every number token in the manuscript appears in the compiled PDF text (302 distinct tokens, 0 missing). Compiles with pdfLaTeX, 38 pages, no errors.

## Known cosmetic limits
- Section numbers are the manuscript's own heading text (LaTeX numbering is off), so cross-references such as "§4.1" are plain text.
- Wide tables (Table 2, Table 3b) are cramped in portrait; legible but could be moved to landscape in a polish pass.
- Two paragraphs have minor overfull lines from long monospace identifiers.
- Citations stay as the manuscript's `[arXiv-id]` text, not BibTeX.
- Author block is a placeholder.
