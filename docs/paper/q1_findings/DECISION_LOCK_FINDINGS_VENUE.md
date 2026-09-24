# Decision lock — Findings / workshop venue path (Q1 findings manuscript)

**Decision ID:** Q1-FINDINGS-VENUE  
**Status:** **LOCKED**  
**Date (UTC):** 2026-09-24  
**Author:** Seyed Mohammadreza Shirazi Matin  
**Tip SHA (`main`, post–PR #75):** `0469fbcb1d5fcab345cc6fcdddc2d30855bf3dbd` (`git rev-parse HEAD` on `main` at lock; venue-lock doc merged via open PR)  
**Scope:** Venue **planning and human submit path** for [`MANUSCRIPT.md`](MANUSCRIPT.md) only. **API=0.** No agent merge, portal upload, arXiv deposit, or live eval.

**Companion:** [`VENUE_SHORTLIST.md`](VENUE_SHORTLIST.md) (verify every link and deadline on official sites before acting) · [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md) · [`HUMAN_REVIEW_PASS.md`](HUMAN_REVIEW_PASS.md)

---

## A. Locked path (not ICLR 2027 main)

| Field | Lock |
| --- | --- |
| **Publication shape** | **Findings / workshop-style** manuscript (dual-track eval + honest negative result) |
| **Explicitly not targeting** | **ICLR 2027 main track** for this evidence base |
| **Rationale** | n=61, heuristic detector, no AgentDojo-class evaluation, no external SOTA baseline arms — typical **main-track Q1** bar **not met** (see [`VENUE_SHORTLIST.md`](VENUE_SHORTLIST.md) § Fit rule) |

**Do not rush ICLR 2027 main:** full-paper deadline is approximately **2026-09-25 AoE** — verify on [ICLR 2027](https://iclr.cc/Conferences/2027). Submitting main now would invite overclaim pressure; **hold** unless evidence materially changes (optional Phase 3 + new immutable AUDIT, still **without** FAIL→PASS on Track A).

---

## B. Primary planning targets (after human review)

| Priority | Target | Notes |
| --- | --- | --- |
| **1** | **ICLR 2027 workshops** — workshop **papers** after accepted CFPs | Workshop **proposal** deadline **2026-10-09**; typical workshop **paper** deadline ~**2027-02-01** — see [Call for Workshops](https://iclr.cc/Conferences/2027/CallForWorkshops). **Wait** for CFP text; fit LLM security / agents / evaluation framing if claims stay conservative. |
| **2** | **Next ARR cycle → ACL / NAACL / EMNLP Findings 2027** | Plan when the **next ARR** window opens; dual-track eval + confirmed negative can fit **Findings** if prose respects [`CLAIMS_MAP.md`](CLAIMS_MAP.md) and Q1-P2 scope. |

**Optional (timestamp only):** **arXiv** `cs.CR` / `cs.AI` preprint — **HUMAN_ONLY** upload via [`ARXIV_PACKET.md`](ARXIV_PACKET.md). Establishes public timestamp; **no peer review**. Keep abstract FAIL-first; cite frozen AUDIT. **Do not** mark uploaded in git until Matin confirms.

---

## C. Human gates (not done by agents)

| Step | Owner | Repo status |
| --- | --- | --- |
| Manuscript + claims review | **HUMAN_ONLY** | [`HUMAN_REVIEW_PASS.md`](HUMAN_REVIEW_PASS.md) — **READY** for Matin review |
| Camera-ready venue template (LaTeX/Word) | **HUMAN_ONLY** | **NOT DONE** |
| Portal / OpenReview / EasyChair submit | **HUMAN_ONLY** | **NOT DONE** |
| arXiv deposit | **HUMAN_ONLY** | **NOT DONE** |

**Merged lineage on tip:** PR **#74** (Q1 P1–P4 packet) and PR **#75** (post-#74 hygiene) on `main` @ tip SHA above.

---

## D. Non-goals (unchanged science locks)

- **No** claim of Phase 3 done or ICLR/NeurIPS **main-track** readiness.
- **No** edits to `frozen/**`, AUDIT numbers, or Track A **FAIL** verdict.
- **No** live OpenRouter / eval spend without separate budget locks.

**No guarantee** of acceptance at any venue. This lock is planning documentation only.
