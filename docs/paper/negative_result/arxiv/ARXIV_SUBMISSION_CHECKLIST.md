# arXiv submission checklist (nothing has been submitted)

Written 2026-10-07 from arXiv's own help pages (submit, TeX requirements, endorsement, licenses, metadata, moderation and AI policy), read today. arXiv changes these pages, so skim them once more when you submit.

## 1. What blocks posting right now
1. **Author block.** Affiliation, email and corresponding author are placeholders in `main.tex`. The second author's name spelling ("Reza Manzour", given as "RezaManzour") is unconfirmed.
2. **AI-use paragraph.** The "Acknowledgements and AI-use disclosure" section is a draft and shows the line "[Draft; the authors must confirm or edit this paragraph.]" in the PDF. Edit it, delete that line and the funding placeholder line.
3. **Merges.** The build must come from merged `main`. Order: #103 (referee fixes), #104 (shortening), #105 (LaTeX, 15+7 package; it also holds the #102 commits). #102 can be closed once #105 lands. After merging, rebuild with `scripts/build_arxiv_latex.py` and `scripts/package_overleaf.sh`, so the zip matches `main`.
4. **Attack-template release policy.** The paper (§10) states the attack templates and the harness commits can be fetched by SHA from the public repository, and cites the SHAs. Once posted, that is permanent and easy to find. Decide before posting: keep as is, publish the templates deliberately with a short responsible-use note, or remove the SHAs from the paper. The text must match what you choose.
5. **Wording leftovers** (found in the final PDF text; not changed, because they touch text): §8.5 says "awaiting owner approval" (test-suite paragraph) and "the owner's approval" (provenance paragraph); §8.3 and §10 say "the first author". With two named authors, change "owner" to "the authors" or a named person, and decide who "the first author" is (Matin Shirazi, as listed). The acknowledgement says "the authors' direction", which is consistent with this once fixed.
6. **License choice** (see section 3) and a decision whether the paper's page count/length suits your target venue (venue may require its own template).

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
- Open items: author placeholders; draft AI paragraph markers; the two "owner" wordings and "first author" consistency (section 1, item 5).
- Not a defect but worth a glance: the figure captions are short; the text introduces the figures in §4.7 and §6.
