# Overleaf / arXiv package: negative-result paper (draft, not submitted)

Source text: `docs/paper/negative_result/MANUSCRIPT_DRAFT_v1.md` (assembled from the section sources by `scripts/assemble_manuscript.py`). Nothing has been submitted anywhere; posting is the owner's action.

## Open in Overleaf
1. Overleaf: New Project, Upload Project, choose the zip.
2. Menu: Compiler = **pdfLaTeX**, TeX Live version 2023 or newer, Main document = **main.tex**.
3. Recompile. Overleaf runs pdfLaTeX, BibTeX, pdfLaTeX, pdfLaTeX by itself. Expect **15 pages** for `main.tex`.
4. For the supplement, set Main document = `supplement.tex` and recompile (7 pages; no BibTeX needed).

## Contents
| file | purpose |
|---|---|
| `main.tex` | main paper, 15 pages: abstract, §1 to §11, references; two-column, 9 pt (`extarticle`); tables are `\input` from `tables/` |
| `supplement.tex` | supplement, 7 pages: subsections and Table 2 moved out of the main paper (S1, S2) and Appendices A to D, text unchanged |
| `tables/table_01.tex` ... `table_19.tex` | the 19 manuscript tables (main paper first, then supplement) |
| `figures/*.png` | the three committed figures, unchanged |
| `references.bib` | 23 BibTeX entries |
| `arxivid.bst` | tiny BibTeX style that prints the list as the manuscript writes it: `[arXiv id] Author. Title (note).` |
| `main.bbl` | the generated bibliography, included because arXiv does not run BibTeX |
| `submission/` | single-column 10 pt full preprint (all sections and appendices, 29 pages), comments stripped; this is the arXiv upload candidate; `main.bbl` is generated into it |
| `ARXIV_SUBMISSION_CHECKLIST.md` | step-by-step arXiv submission checklist, rule check, blockers |
| `ARXIV_METADATA.md` | suggested category, title, abstract that fits arXiv's 1920-character limit |
| `OWNER_DECISIONS.md` | what the owner must decide before posting |

Only standard packages (`extsizes` via `extarticle`, `multicol`, `caption`, `lmodern`, `geometry`, `microtype`, `amsmath`, `graphicx`, `booktabs`, `longtable`, `calc`, `etoolbox`, `url`, `hyperref`); no custom `.sty` is needed.

## Submitting to arXiv later (owner's action)
Upload the zip contents as-is (or the zip). Keep `main.tex`, `main.bbl`, `tables/`, `figures/`, `arxivid.bst`, `references.bib`. arXiv compiles with pdfLaTeX and uses `main.bbl`. Do not upload a compiled PDF together with the TeX source. Authors are filled in (affiliation, email and corresponding author are still placeholders), and a draft AI-use paragraph needs the authors' confirmation (`OWNER_DECISIONS.md`, item 1).

## References: what is and is not in the .bib
- Entries are transcribed from the manuscript's own reference list; the manuscript records (`REFERENCE_VERIFICATION_20261001.md`) that each was checked against the cited PDF on 2026-10-01. They were not re-verified online for this package.
- Fields: author as written in the manuscript (surnames only, "et al." kept), title, arXiv id, year, venue and the manuscript's own parenthetical notes, exactly as the list in the manuscript gives them (the list now carries years and venues). Nothing was added; several arXiv ids (2026 numbering) could not be checked from here.
- The only visible difference from the manuscript list is punctuation: a note sits in parentheses before the bracket and ends with a period, e.g. `Challenge (dataset license: MIT). [arXiv:...]` instead of `Challenge. (dataset license: MIT) [arXiv:...]`.
- In-text citations such as `[2403.02691; 2406.13352]` are plain text, exactly as in the manuscript, not `\cite` commands. Converting them is optional and would not change the printed text if the labels stay as arXiv ids.

## Regenerate (repository)
```
python3 scripts/assemble_manuscript.py     # only if a section source changed
python3 scripts/build_arxiv_latex.py       # main.tex, supplement.tex, tables/, figures/ (needs pandoc)
scripts/package_overleaf.sh                # also writes adapti-guard-arxiv-source-DRAFT.zip (TeX source only) and compiles, refreshes main.bbl, writes the zip, re-compiles from the unzipped zip in a clean directory
```
Never edit `main.tex` or `tables/` by hand.

## What moved to the supplement (to reach 15 pages)
The main paper keeps every heading and a one-line pointer, so section references still resolve. Moved verbatim: §5.7 (external-test protocol), §6.7 (calibration, exploratory), §8.5 (artifact and process limitations, including provenance detail), Table 2 (positioning), and Appendices A to D. Kept in the main paper: all headline results, §8.1 to §8.4 and §8.6 to §8.8, §9, §10, Table 3 and Table 3.
Layout, not prose, did the rest: 9 pt two-column text, full-width tables, figures at 62% width.
The only added text is the pointer lines and one italic line under the keywords telling the reader where the supplement is.
The 15 pages are with TeX Live 2023 on this build; a different TeX Live may shift a line or two, and the last page is nearly full.

## Table consolidation (19 to 15 tables)
At the owner's request after a table audit: Table 3b is merged into Table 3 (Status column plus a combined "Derivation and confirmation" column); the §6.4 synthesis table is folded into Table 1 (four added rows, and its fifth question in the caption), with §6.4 pointing to Table 1; the four Appendix D per-family and per-model tables become two (A0 shown for each pairing: B3 n=167, CORE n=168). Tables 2 and 10 stay in the supplement of the 15+7 build. Text citing "Table 3b" now cites Table 3. Edited in the section sources and regenerated; no number or claim changed.

## Fidelity
No prose is edited by the converter. Every number token of the manuscript appears in main plus supplement (checked on the extracted PDF text), and `MANUSCRIPT_DRAFT_v1.md` itself is unchanged, so the ledger test is unaffected.

## Cosmetic limits
Narrow columns give some overfull lines around long monospace paths; tables are set at footnote size.
