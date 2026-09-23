# Q1 findings — submission checklist (human only)

**Venue:** **TBD** (not selected in this repository)  
**Upload status:** **NOT DONE** — no agent or automation may mark submission complete.  
**Author:** Seyed Mohammadreza Shirazi Matin · `mrshirazimatin@gmail.com`

Agents: **do not** merge PRs, upload to OpenReview/EasyChair/arXiv, or run live LLM eval.

**Cover packet:** [`SUBMISSION_PACKET.md`](SUBMISSION_PACKET.md) · Item statuses: **READY** = in-repo draft complete; **HUMAN_ONLY** = Matin/venue; **NOT DONE** = not executed.

---

## Pre-submit (documentation)

| Step | Owner | Status |
| --- | --- | --- |
| Read [`CLAIMS_MAP.md`](CLAIMS_MAP.md) + [`docs/paper/CLAIMS_CHECKLIST.md`](../CLAIMS_CHECKLIST.md) | Human | Required |
| Verify dual-track sections labeled (Track A / Track B / Layer A) | Human | Required |
| Confirm no invented Track A δ̂ CI (BLOCKING GAP in AUDIT) | Human | Required |
| Confirm V2 / AgentDojo / SOTA baselines cited as **Future Work** only (Q1-P2) | Human | Required |
| Offline smoke: `python3 docs/paper/workshop_vnext_fail/verify_manuscript_facts.py` | Human | **READY** (script on tip) |
| Hash appendix: [`workshop_vnext_fail/APPENDIX_HASHES.md`](../workshop_vnext_fail/APPENDIX_HASHES.md) | Human | **READY** |
| Manuscript draft [`MANUSCRIPT.md`](MANUSCRIPT.md) | Human review | **READY** (PR #74) |
| Cover packet [`SUBMISSION_PACKET.md`](SUBMISSION_PACKET.md) | Human review | **READY** (PR #74) |
| Figures / captions [`FIGURES.md`](FIGURES.md) | Human export | **READY** (mermaid + ASCII) |
| BibTeX stubs [`references.bib`](references.bib) | Human verify | **READY** (verify OWASP note if needed) |
| arXiv packet [`ARXIV_PACKET.md`](ARXIV_PACKET.md) + [`ARXIV_ABSTRACT.txt`](ARXIV_ABSTRACT.txt) | Human upload | **READY** (docs); arXiv portal **NOT DONE** |
| PDF build [`BUILD_PDF.md`](BUILD_PDF.md) | Human local | **READY** (instructions) |
| Optional P3 supplements | Human | **N/A until budget** — Phase 3 **not done** |

---

## Camera-ready (venue TBD)

| Step | Owner | Status |
| --- | --- | --- |
| Pick venue / CFP | **HUMAN_ONLY** | **NOT DONE** |
| Convert [`MANUSCRIPT.md`](MANUSCRIPT.md) to venue template (LaTeX/Word) | **HUMAN_ONLY** | **NOT DONE** |
| Anonymization policy per venue | **HUMAN_ONLY** | **NOT DONE** |
| Figure 1 export from mermaid | **HUMAN_ONLY** | **NOT DONE** |
| Ethics / data availability statements | **HUMAN_ONLY** | Draft in MANUSCRIPT §9 |

---

## Submit (explicitly not executed by agents)

| Step | Owner | Status |
| --- | --- | --- |
| Portal upload | **HUMAN_ONLY** | **NOT DONE** |
| Mark “submitted” in git | **HUMAN_ONLY** | **NOT DONE** |
| arXiv deposit | **HUMAN_ONLY** ([`ARXIV_PACKET.md`](ARXIV_PACKET.md)) | **NOT DONE** — do not mark uploaded in git |

---

## Related checklists

- Workshop packet (shorter Track A): [`workshop_vnext_fail/SUBMISSION_CHECKLIST.md`](../workshop_vnext_fail/SUBMISSION_CHECKLIST.md)
- Q1 roadmap: [`docs/experiments/Q1_ROADMAP_4PHASE.md`](../../experiments/Q1_ROADMAP_4PHASE.md) — P3 live **pending budget**; P4 polish on PR #74
