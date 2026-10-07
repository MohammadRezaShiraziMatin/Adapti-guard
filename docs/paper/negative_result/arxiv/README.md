# Overleaf / arXiv package: negative-result paper (draft, not submitted)

Source text: `docs/paper/negative_result/MANUSCRIPT_DRAFT_v1.md` (assembled from the section sources by `scripts/assemble_manuscript.py`). Nothing has been submitted anywhere; posting is the owner's action.

## Open in Overleaf
1. Overleaf: New Project, Upload Project, choose the zip.
2. Menu: Compiler = **pdfLaTeX**, TeX Live version 2023 or newer, Main document = **main.tex**.
3. Recompile. Overleaf runs pdfLaTeX, BibTeX, pdfLaTeX, pdfLaTeX by itself. Expect 38 pages.

## Contents
| file | purpose |
|---|---|
| `main.tex` | document: preamble, title, abstract, all sections, appendices; tables are `\input` from `tables/` |
| `tables/table_01.tex` ... `table_19.tex` | the 19 manuscript tables, in order of appearance |
| `figures/*.png` | the three committed figures, unchanged |
| `references.bib` | 23 BibTeX entries |
| `arxivid.bst` | tiny BibTeX style that prints the list as the manuscript writes it: `[arXiv id] Author. Title (note).` |
| `main.bbl` | the generated bibliography, included because arXiv does not run BibTeX |
| `ARXIV_METADATA.md` | suggested category, title, abstract that fits arXiv's 1920-character limit |
| `OWNER_DECISIONS.md` | what the owner must decide before posting |

Only standard packages (`lmodern`, `geometry`, `microtype`, `amsmath`, `graphicx`, `booktabs`, `longtable`, `calc`, `etoolbox`, `url`, `hyperref`); no custom `.sty` is needed.

## Submitting to arXiv later (owner's action)
Upload the zip contents as-is (or the zip). Keep `main.tex`, `main.bbl`, `tables/`, `figures/`, `arxivid.bst`, `references.bib`. arXiv compiles with pdfLaTeX and uses `main.bbl`. Do not upload a compiled PDF together with the TeX source. The author block in `main.tex` is a placeholder.

## References: what is and is not in the .bib
- Entries are transcribed from the manuscript's own reference list; the manuscript records (`REFERENCE_VERIFICATION_20261001.md`) that each was checked against the cited PDF on 2026-10-01. They were not re-verified online for this package.
- Fields: author as written in the manuscript (surnames only, "et al." kept), title, arXiv id, and the manuscript's own parenthetical notes (venue, "read", "full text", license). No year, first names, DOI or venue was added; several arXiv ids (2026 numbering) could not be checked from here.
- The only visible difference from the old list is punctuation: notes are merged into one parenthesis, e.g. `(BIPIA; KDD 2025; read)` instead of `(BIPIA; KDD 2025). (read)`.
- In-text citations such as `[2403.02691; 2406.13352]` are plain text, exactly as in the manuscript, not `\cite` commands. Converting them is optional and would not change the printed text if the labels stay as arXiv ids.

## Regenerate (repository)
```
python3 scripts/assemble_manuscript.py     # only if a section source changed
python3 scripts/build_arxiv_latex.py       # main.tex, tables/, figures/ (needs pandoc)
scripts/package_overleaf.sh                # compiles, refreshes main.bbl, writes the zip, re-compiles from the unzipped zip in a clean directory
```
Never edit `main.tex` or `tables/` by hand.

## Fidelity
No prose is edited by the converter. Compared with the earlier single-file build, the extracted PDF text differs only in the reference list punctuation, table page positions, and one line-break hyphen.

## Cosmetic limits
Wide tables (Table 2, 3b) are cramped in portrait; a few paragraphs have small overfull lines from long monospace paths.
