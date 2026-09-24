# Venue shortlist — Q1 dual-track findings (planning only)

**Author / owner:** Seyed Mohammadreza Shirazi Matin  
**Planning date:** ~2026-09-24 (UTC)  
**Venue strategy:** **LOCKED** — Findings / workshop path (not ICLR 2027 main); see [`DECISION_LOCK_FINDINGS_VENUE.md`](DECISION_LOCK_FINDINGS_VENUE.md)  
**Tip `main`:** `0469fbc` (PR #74 + #75 merged (+ venue-lock PR for this lock file))  
**Manuscript:** [`MANUSCRIPT.md`](MANUSCRIPT.md) · **Submit steps:** [`SUBMISSION_PACKET.md`](SUBMISSION_PACKET.md) · **Human review:** [`HUMAN_REVIEW_PASS.md`](HUMAN_REVIEW_PASS.md)

**Agents:** do **not** submit, merge, or mark upload DONE. **Verify every link and deadline on the official site before acting.**

---

## Fit rule

Prefer venues that welcome **evaluation methodology**, **reproducible artifacts**, and **honest negative results** (FAIL-first dual-track narrative).

**Do not recommend** rushing **ICLR 2027 main track**: the full-paper deadline is approximately **2026-09-25 AoE** (verify on [ICLR 2027](https://iclr.cc/Conferences/2027)). For this evidence base—**n=61**, **heuristic detector**, **no AgentDojo-class evaluation**, **no external SOTA baseline arms**—the bar for a typical **main-track Q1** venue is **not met**. A main submission would invite overclaim pressure; **hold** unless evidence materially changes (optional Phase 3 + new immutable AUDIT, still without FAIL→PASS on Track A).

---

## Shortlist (verify links before submit)

| # | Venue / path | Role | Status (~2026-09-23) | Notes |
| --- | --- | --- | --- | --- |
| 1 | **arXiv** (`cs.CR` / `cs.AI`) | Preprint timestamp | **Open** (continuous) | **HUMAN_ONLY** upload. Establishes public timestamp; **no peer review**. Keep abstract FAIL-first; cite frozen AUDIT. |
| 2 | **ICLR 2027 workshops** | Workshop papers | **Planning** | Workshop **proposal** deadline **2026-10-09**; typical workshop **paper** deadline ~**2027-02-01** (see [Call for Workshops](https://iclr.cc/Conferences/2027/CallForWorkshops)). **Wait** for accepted workshop CFPs (LLM security, agents, evaluation tracks). Good fit for dual-track eval + negative result if claims stay conservative. |
| 3 | **NeurIPS 2026 workshops** — [FLMSec](https://flmsec.github.io/) | Workshop | **Likely CLOSED** | Listed deadline **2026-08-28** — past as of 2026-09-23. Do not target unless an **extension** is verified on OpenReview. |
| 3b | **NeurIPS 2026** — Agents in the Wild | Workshop | **Likely CLOSED** | Listed deadline **2026-08-29** — past as of 2026-09-23. Same rule: verify before planning. |
| 4 | **SeT-LLM @ KDD 2026** | Workshop | **CLOSED** | Deadline **2026-06-05** — past. |
| 5 | **EMNLP 2026** (Findings / main via ARR) | Conference | **CLOSED** | ARR window **May 2026** — past for this cycle. |
| 6 | **Next ARR cycle → ACL / NAACL / EMNLP Findings 2027** | Findings track | **Future** | Plan when **next ARR** opens. Dual-track eval + confirmed negative can fit **Findings** if prose respects [`CLAIMS_MAP.md`](CLAIMS_MAP.md) and Q1-P2 scope (no V2/SOTA/AgentDojo as done). |
| 7 | **SaTML**, **USENIX-adjacent AI security** (optional) | Venue-specific | **Check CFP** | Only if an open CFP matches evaluation/negative-result framing; verify dates on official pages—do not invent deadlines here. |

**Not in scope this cycle (Q1-P2):** Confirmatory V2 live, mechanism-pack live, external baselines—optional **Phase 3** after budget may strengthen a **future** submission but **does not** reverse Track A FAIL.

---

## Recommended sequence for Matin (locked)

| Step | Action | Owner |
| --- | --- | --- |
| **A** | **Human review pass** on tip **`main`** @ `0469fbc` (PR #74 + #75 merged; venue lock): [`HUMAN_REVIEW_PASS.md`](HUMAN_REVIEW_PASS.md), [`MANUSCRIPT.md`](MANUSCRIPT.md), [`SUBMISSION_PACKET.md`](SUBMISSION_PACKET.md), [`CLAIMS_MAP.md`](CLAIMS_MAP.md); run [`verify_q1_findings_facts.py`](verify_q1_findings_facts.py) | **HUMAN_ONLY** (review; no agent submit) |
| **B** | Optional **arXiv** preprint (`cs.CR` / `cs.AI`) for timestamp — upload **NOT DONE** in repo | **HUMAN_ONLY** |
| **C** | **Do not** rush **ICLR 2027 main** (~**2026-09-25 AoE**) — evidence bar **not met** for typical main track (see [`DECISION_LOCK_FINDINGS_VENUE.md`](DECISION_LOCK_FINDINGS_VENUE.md)) | **LOCKED** |
| **D** | **Primary targets:** **ICLR 2027 workshop papers** (~Feb 2027 after CFPs) and/or **next ARR → Findings 2027** when the cycle opens; optional **Phase 3** live only if budget + locks, **without** merging tracks in claims | **LOCKED** planning |
| **E** | Camera-ready venue template (LaTeX/Word) | **HUMAN_ONLY** / **NOT DONE** |

---

## Checklist cross-links

- Upload status remains **NOT DONE** in [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md) until Matin confirms portal upload.
- Workshop sibling (Track A only): [`../workshop_vnext_fail/SUBMISSION_CHECKLIST.md`](../workshop_vnext_fail/SUBMISSION_CHECKLIST.md)

**No guarantee** of acceptance at any venue. This file is planning documentation only.
