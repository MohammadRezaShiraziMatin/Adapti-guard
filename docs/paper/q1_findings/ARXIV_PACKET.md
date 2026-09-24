# arXiv submission packet — Q1 dual-track findings (HUMAN_ONLY)

**Planning date:** ~2026-09-23  
**Author:** Seyed Mohammadreza Shirazi Matin · `mrshirazimatin@gmail.com`

**Agents and automation do not upload to arXiv.** This file is instructions for Matin only.  
**Upload status in git:** **NOT DONE** — do not mark arXiv submission complete in the repository unless Matin has actually submitted and chooses to record that separately.

**Related:** [`VENUE_SHORTLIST.md`](VENUE_SHORTLIST.md) (arXiv is step B in the recommended sequence) · [`BUILD_PDF.md`](BUILD_PDF.md) · [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md)

---

## 1. Metadata (copy into arXiv form)

| Field | Value |
| --- | --- |
| **Title** | Dual-Track Evaluation of Cost-Aware Runtime Intervention for LLM Prompt Injection: A Confirmed Negative and a Scoped Phase-1 Improvement |
| **Title source** | [`MANUSCRIPT.md`](MANUSCRIPT.md) H1 (option A in [`SUBMISSION_PACKET.md`](SUBMISSION_PACKET.md)) |
| **Author** | Seyed Mohammadreza Shirazi Matin |
| **Email** | mrshirazimatin@gmail.com |
| **Categories (primary + secondary)** | `cs.CR` (primary) · `cs.AI` (secondary) |
| **Comments (optional)** | Honest dual-track confirmatory evaluation; Track A VNEXT FAIL immutable; Track B scoped improvement does not reverse Track A. Frozen AUDIT artifacts in repository. |

---

## 2. Abstract (plain text)

Paste from [`ARXIV_ABSTRACT.txt`](ARXIV_ABSTRACT.txt) (no markdown). Re-check character limit on the arXiv form (~1920 characters); trim Layer A sentence last if needed—**do not** drop Track A FAIL numbers or Track B non-reversal sentence.

**Ordering rule:** FAIL-first (Track A), then Track B scoped, then methodology/Layer A one line.

---

## 3. License

- Repository code: **MIT** (see root `LICENSE` if present on tip).
- arXiv submission: Matin selects arXiv license on upload (commonly **arXiv.org perpetual non-exclusive license** to distribute the preprint). This packet does **not** auto-select a license; **human** confirms on the arXiv portal.
- **Do not** claim prompt injection solved, SOTA, or production readiness in the abstract or title regardless of license.

---

## 4. What to upload (typical)

| File | Source | Notes |
| --- | --- | --- |
| **PDF** | Built locally per [`BUILD_PDF.md`](BUILD_PDF.md) | Main submission; from `MANUSCRIPT.md` + references |
| **TeX/LaTeX source (optional)** | If Matin converts to LaTeX | arXiv often prefers TeX; pandoc export is acceptable if it compiles |
| **`references.bib`** | [`references.bib`](references.bib) | If using BibTeX build |
| **Figure (optional)** | Export Figure 1 from [`FIGURES.md`](FIGURES.md) | PNG/PDF; dual-track diagram |

**Do not upload** frozen dataset bytes or live API keys. Point reviewers to GitHub paths and AUDIT folders in the PDF text.

**Evidence authority:** Numbers must match `experiments/real_llm_eval/**/AUDIT.md` — no invented Track A delta 95% CI (BLOCKING GAP in AUDIT).

---

## 5. HUMAN_ONLY steps (checklist)

1. Clone or pull **`main`** @ `0469fbc` (PR #74 + #75 merged; venue lock [`DECISION_LOCK_FINDINGS_VENUE.md`](DECISION_LOCK_FINDINGS_VENUE.md)) so local tree matches the findings packet.
2. Run `python3 docs/paper/workshop_vnext_fail/verify_manuscript_facts.py` locally.
3. Build PDF: [`BUILD_PDF.md`](BUILD_PDF.md).
4. Read [`CLAIMS_MAP.md`](CLAIMS_MAP.md) — abstract must stay FAIL-first; no SOTA / solve-PI.
5. Log in to **https://arxiv.org** as Matin; start new submission.
6. Enter title, author, categories (`cs.CR`, `cs.AI`), abstract from `ARXIV_ABSTRACT.txt`.
7. Upload PDF (+ source if required).
8. Submit — **human** confirms final preview.
9. **Do not** update this repo to say “arXiv DONE” unless Matin explicitly wants that recorded later.

---

## 6. Explicit prohibitions (agents)

- No arXiv API upload from Cloud Agent or CI.
- No changing AUDIT numbers or frozen packs for “better” preprint narrative.
- No marking upload complete in [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md) without Matin action.

---

## 7. After arXiv (optional)

- Add arXiv ID to a future camera-ready version when submitting to ICLR 2027 workshops or ARR Findings ([`VENUE_SHORTLIST.md`](VENUE_SHORTLIST.md)).
- Workshop Track A-only packet remains at [`../workshop_vnext_fail/`](../workshop_vnext_fail/README.md) — separate shorter narrative.

**Peer review:** arXiv establishes a **timestamp**, not acceptance. No Q1 acceptance guarantee.
