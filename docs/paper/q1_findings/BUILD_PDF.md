# Build PDF from Q1 findings manuscript (local, human)

**Purpose:** Produce an arXiv- or review-ready **PDF** from [`MANUSCRIPT.md`](MANUSCRIPT.md) without adding a full venue LaTeX template to the repo.

**API=0.** No live eval. Agents do not run upload steps.

---

## Prerequisites (human machine)

- [`pandoc`](https://pandoc.org/) (≥ 2.11 recommended)
- PDF engine: `pdflatex` + `latexmk`, or `xelatex`, or `tectonic` — one must be installed
- Optional: `bibtex` / `biber` if using [`references.bib`](references.bib)

Check:

```bash
pandoc --version
```

---

## Minimal pandoc command (markdown → PDF)

From repository root:

```bash
cd docs/paper/q1_findings

pandoc MANUSCRIPT.md \
  --from markdown \
  --to pdf \
  --output q1_findings_draft.pdf \
  --metadata title="Dual-Track Evaluation of Cost-Aware Runtime Intervention for LLM Prompt Injection: A Confirmed Negative and a Scoped Phase-1 Improvement" \
  --metadata author="Seyed Mohammadreza Shirazi Matin" \
  --metadata date="2026-09-23" \
  --citeproc \
  --bibliography=references.bib \
  --pdf-engine=pdflatex
```

If `--citeproc` fails (no citations in markdown yet), omit it and keep the References section as in the markdown:

```bash
pandoc MANUSCRIPT.md \
  --from markdown \
  --to pdf \
  --output q1_findings_draft.pdf \
  --metadata author="Seyed Mohammadreza Shirazi Matin" \
  --pdf-engine=pdflatex
```

**Note:** Pandoc may not render mermaid in [`FIGURES.md`](FIGURES.md). Export Figure 1 separately (mermaid CLI or diagram editor) and insert in a LaTeX/manual pass if needed.

---

## Optional: markdown → LaTeX stub (for arXiv source upload)

```bash
cd docs/paper/q1_findings

pandoc MANUSCRIPT.md \
  --from markdown \
  --to latex \
  --output q1_findings_draft.tex \
  --standalone \
  --citeproc \
  --bibliography=references.bib
```

Human edits `q1_findings_draft.tex` for venue margins, then:

```bash
pdflatex q1_findings_draft.tex
bibtex q1_findings_draft
pdflatex q1_findings_draft.tex
pdflatex q1_findings_draft.tex
```

There is **no** checked-in LNCS/ACL template in this repo by design—use official venue templates when converting for workshop/conference submit.

---

## Strip non-printable banner lines (optional)

[`MANUSCRIPT.md`](MANUSCRIPT.md) includes doc-only links in the header. For a cleaner PDF, human may copy to a temp file and remove lines 3–14 (status banner / evidence base) before pandoc, **without** changing FAIL numbers in §6.

---

## Verify before upload

```bash
python3 docs/paper/workshop_vnext_fail/verify_manuscript_facts.py
```

Upload steps: [`ARXIV_PACKET.md`](ARXIV_PACKET.md) · venue plan [`VENUE_SHORTLIST.md`](VENUE_SHORTLIST.md)
