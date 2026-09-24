# Q1 findings — submission checklist (human only)

**Venue strategy:** **LOCKED** — Findings / workshop-style path (not ICLR 2027 main); [`DECISION_LOCK_FINDINGS_VENUE.md`](DECISION_LOCK_FINDINGS_VENUE.md) · planning [`VENUE_SHORTLIST.md`](VENUE_SHORTLIST.md)  
**Tip `main`:** `0469fbc` (PR #74 + #75 merged; venue lock)  
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
| Human review checklist [`HUMAN_REVIEW_PASS.md`](HUMAN_REVIEW_PASS.md) | Matin | **READY** (upload **NOT DONE**) |
| Manuscript draft [`MANUSCRIPT.md`](MANUSCRIPT.md) | Human review | **READY** (`main` @ `0469fbc`; PR #74 + #75 merged) |
| Cover packet [`SUBMISSION_PACKET.md`](SUBMISSION_PACKET.md) | Human review | **READY** (`main` @ `0469fbc`; PR #74 + #75 merged) |
| Figures / captions [`FIGURES.md`](FIGURES.md) | Human export | **READY** (mermaid + ASCII) |
| BibTeX stubs [`references.bib`](references.bib) | Human verify | **READY** (verify OWASP note if needed) |
| arXiv packet [`ARXIV_PACKET.md`](ARXIV_PACKET.md) + [`ARXIV_ABSTRACT.txt`](ARXIV_ABSTRACT.txt) | Human upload | **READY** (docs); arXiv portal **NOT DONE** |
| PDF build [`BUILD_PDF.md`](BUILD_PDF.md) | Human local | **READY** (instructions) |
| Optional P3 supplements | Human | **N/A until budget** — Phase 3 **not done** |

---

## Camera-ready (Findings / workshop path locked)

| Step | Owner | Status |
| --- | --- | --- |
| Venue path lock acknowledged | Matin | **LOCKED** ([`DECISION_LOCK_FINDINGS_VENUE.md`](DECISION_LOCK_FINDINGS_VENUE.md)) |
| Pick specific workshop CFP or ARR cycle | **HUMAN_ONLY** | **NOT DONE** (wait for ICLR 2027 workshop CFPs / next ARR) |
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
- Q1 roadmap: [`docs/experiments/Q1_ROADMAP_4PHASE.md`](../../experiments/Q1_ROADMAP_4PHASE.md) — P3 live **pending budget** (NOT AUTHORIZED); P4 draft on `main`
