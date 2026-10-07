# arXiv submission checklist (nothing has been submitted)

Upload candidates (same source, same text): `adapti-guard-arxiv-source-twocolumn.zip` (21 pages, two-column, preferred by the owner) or `adapti-guard-arxiv-source-singlecolumn.zip` (29 pages). Both contain `main.tex`, `main.bbl`, `references.bib`, tables and figures.

Written 2026-10-07 from arXiv's own help pages (submit, TeX requirements, endorsement, licenses, metadata, moderation and AI policy), read today. arXiv changes these pages, so skim them once more when you submit.

## 1. What blocks posting right now
1. **Author names and corresponding author.** Emails and the affiliation ("Independent Researchers") are in the author block, as given by the owner. The corresponding author is set to Matin Shirazi (first author) as a default the authors may change. The second author's spelling ("Reza Manzour", given as "RezaManzour") is still unconfirmed.
2. **AI-use paragraph and funding.** Done in the build: the draft marker and the funding placeholder are removed. The paragraph states that an AI assistant (Claude, Anthropic) wrote the seven attack families, contributed code and drafts, produced audits and review notes and converted the manuscript to LaTeX; that it is not an author; and that the authors take responsibility. Funding reads "This work received no external funding." (no funding source exists in the repo; the authors must confirm both statements.)
3. **Merges.** Done: #103 to #107 are merged into `main`. Open: the draft PR with the two-column variant and the final AI-use text. After it merges, rebuild with `scripts/build_arxiv_latex.py` and `scripts/package_overleaf.sh` so the zip matches `main`.
4. **Attack-template release policy.** The paper (§10) states the attack templates and the harness commits can be fetched by SHA from the public repository, and cites the SHAs. Once posted, that is permanent and easy to find. Decide before posting: keep as is, publish the templates deliberately with a short responsible-use note, or remove the SHAs from the paper. The text must match what you choose. (Owner decision.)
5. **Wording.** Done in #107: the two "owner" wordings in §8.5 now read "the authors' approval" / "awaiting the authors' approval". "The first author" (§8.3, §10) is kept: it names Matin Shirazi, as listed, and the sentences say who requested and directed the AI-assisted work. Confirm that this is accurate.
6. **License choice** (see section 3), and a decision whether the page count/length suits your target venue (a venue may require its own template). (Owner decisions.)

## 2. Package check against arXiv's rules
| arXiv rule | status in our package |
|---|---|
| Upload TeX source, not the PDF; no .aux, .log, .pdf, hidden files | OK in `adapti-guard-arxiv-source-DRAFT.zip` (main.tex, main.bbl, tables/, figures/ only). Do **not** upload the Overleaf zip: it contains README and decision notes (internal, would become public with the source). |
| Source is public after posting, so strip comments | Done in the arXiv variant (comment lines removed). The Overleaf variant still has internal comments. |
| `.bbl` must match the main file name and come from the same program | OK: `main.bbl` from BibTeX for `main.tex`. arXiv does not run BibTeX. |
| Figures for pdfLaTeX: PDF, PNG or JPG | OK: three PNG files, no mixed formats. |
| Main file at the root, relative paths only, no JavaScript, no `xr` links | OK (checked: no absolute paths; hyperref uses hidelinks). |
| TeX Live: arXiv offers 2025 (default) and 2023 | Built here with a TeX Live 2023-equivalent and recompiled from the zip with the shipped .bbl only: 29 pages, no undefined references. Choose the same engine (pdfLaTeX) and check arXiv's preview PDF page by page. |
| Abstract at most 1920 characters, plain text, no word "Abstract" | OK: 1529 characters, ASCII (kappa and section signs spelled out). |
| Metadata is ASCII only (curly quotes cause "Bad character(s)") | OK in `ARXIV_METADATA.md`; paste from there, not from the PDF. |
| Authors "Firstname Lastname" | OK once the second name is confirmed. |
| AI policy | arXiv: AI cannot be an author, authors take full responsibility for all content, significant AI use must be reported. The paper states this in §10 and in the acknowledgements; keep it. |
| CS content policy | The paper is an empirical case study, not a position or review paper. Nothing to change. |

## 3. Step by step (plain language)
1. **Account.** Register at arxiv.org with an institutional email if you have one (it can give automatic endorsement). Use the same name as on the paper.
2. **Endorsement.** First-time submitters, or anyone new to a category, need an endorsement for the category's group (cs). Start a submission; arXiv emails an endorsement link. Send it to an established arXiv author in cs.CR or cs.LG (they need a few recent arXiv papers there). Endorsement is not peer review. Plan a few days for this.
3. **Start a new submission.** Choose the license (below), confirm the agreement.
4. **Upload** `adapti-guard-arxiv-source-DRAFT.zip` after you fill the author block (edit `main.tex`, rebuild; or edit by hand in Overleaf then export). Let arXiv detect the main file and choose pdfLaTeX.
5. **Process** and open the preview PDF. Check: authors, 29 pages, 3 figures, tables readable, references listed, no "??".
6. **Metadata.** Paste title, authors, abstract and comments from `ARXIV_METADATA.md`. Category cs.CR primary, cross-list cs.LG (and cs.AI if you want).
7. **Preview and submit.** Submit before 14:00 US Eastern for announcement the next listing day; moderators may hold or reclassify. Posting is public and permanent; you can replace with a new version, but old versions stay.
8. **After posting:** add the arXiv link to the repository README and the paper's data-availability line if you wish.

## 4. License, with tradeoffs (choose once; cannot be changed later)
- **arXiv perpetual non-exclusive license:** arXiv may distribute; reuse by others is limited; you keep the rights. Safest if you later publish at a venue that wants copyright or exclusive rights.
- **CC BY 4.0:** anyone may reuse with credit, including commercially. Common for open science; fine if the venue allows CC BY preprints.
- **CC BY-SA / CC BY-NC-SA / CC BY-NC-ND:** progressively more restrictive; NC variants can conflict with some venues' policies and are rarely needed.
- **CC0:** gives up all rights; not recommended for a paper.
Suggestion: arXiv non-exclusive license if you plan a venue submission; CC BY 4.0 if you want maximum reuse and the venue accepts it.

## 5. Quality pass on the final PDF text (29 pages)
- No spelling errors found (spell-check on the extracted text; only names, jargon and hyphenation fragments flagged).
- Every `§` reference matches an existing heading; every Table 1 to 4, Figure 1 to 3 and Appendix A to D mentioned exists. No broken references.
- Every number in the manuscript is present in the PDF.
- Open items: draft AI paragraph markers (section 1, item 2); second-name spelling.
- Not a defect but worth a glance: the figure captions are short; the text introduces the figures in §4.7 and §6.
