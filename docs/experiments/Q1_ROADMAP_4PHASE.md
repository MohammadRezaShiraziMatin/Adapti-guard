# Q1 readiness roadmap — four phases (findings ladder)

**Author / owner:** Seyed Mohammadreza Shirazi Matin  
**Tip baseline (this PR branched from):** `main` @ `e4870b9cc03a344835f341bfd61aa83d2bdf2bff` (2026-09-23)  
**Mode:** Documentation and planning only. **API=0** by default. Agents do **not** merge, submit venues, or run live LLM eval.

**Blocker inventory:** [`Q1_BLOCKER_MATRIX.md`](Q1_BLOCKER_MATRIX.md)

---

## What this is (and is not)

This roadmap is the **Q1 / findings ladder**: how to move from today’s locked dual-track evidence toward a **Q1-oriented manuscript and artifact** without rewriting science or pretending a FAIL became a PASS.

It is **not** a redo of the **workshop five-phase quality path**. That path is **complete** on the `e4870b9` lineage:

| Roadmap | Purpose | Status on tip `main` |
| --- | --- | --- |
| [`QUALITY_ROADMAP_5PHASE.md`](QUALITY_ROADMAP_5PHASE.md) | Publisher/process unlock: hygiene, D-22 **names**, manuscript polish, repro checklist, workshop submit **checklist** (no upload) | **P1–P5 done** (merged via PR #73 → tip `e4870b9`) |
| **This file (Q1 four phases)** | Evidence-design gaps, optional controlled live work **after human budget**, and a findings manuscript **beyond** the short `workshop_vnext_fail` packet | **P1–P2 done**; **P4 draft in progress** ([`docs/paper/q1_findings/`](../paper/q1_findings/README.md)); **P3 pending budget** ([`DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md`](DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md)) |

Do not mark `QUALITY_ROADMAP_5PHASE.md` incomplete. Treat it as **DONE** for workshop packet readiness; use this doc for **Q1 scope** only.

---

## Science locks (unchanged in every Q1 phase)

| Lock | Rule |
| --- | --- |
| Track A VNEXT | **FAIL** immutable — pack `vnext_confirm_v1.0`, SHA-256 `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518`; AUDIT `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/` |
| Track B Phase-1 LIVE | **SUPPORTED_IMPROVEMENT** scoped on `phase1_confirm_v1`; **does not reverse** Track A |
| Frozen / AUDIT | No edits to `datasets/frozen/**` or `experiments/real_llm_eval/**` AUDIT, verdict, or quoted numbers |
| Metrics | No invented statistics; cite frozen AUDIT or mark **BLOCKING GAP** |
| Live LLM | **API=0** until explicit human budget sign-off |
| Agents | No merge, no venue upload, no retune-to-win |

---

## Honest claim ceiling (Q1 narrative bound)

What the repository **can** support today without new live eval or fabricated numbers:

1. **Dual-track evaluation methodology** — separate confirmatory tracks, hash-locked packs, Target ≠ Judge, utility gates, and explicit forbidden claim lists ([`CLAIMS_CHECKLIST.md`](../paper/CLAIMS_CHECKLIST.md), [`DUAL_TRACK_STATUS.md`](../paper/dual_track/DUAL_TRACK_STATUS.md)).
2. **Confirmed negative on Track A** — VNEXT adaptive cost-aware runtime under locked protocol **does not** meet the pre-registered win criteria (FAIL; McNemar not significant; MSID not met; utility ineligible).
3. **Scoped Phase-1 improvement on Track B** — PHASE1-CORE vs B0 on a **different** pack with pre-registered Phase-1 MSID and utility eligibility; **not** a VNEXT PASS and **not** solve-PI / SOTA.

**Explicitly forbidden** in Q1 prose (even as “future promise” dressed as fact): solve prompt injection, SOTA, production-ready, FAIL→PASS, “VNEXT works,” one unlabeled table mixing Track A ASR with Track B harmful-action rates, simulation or oracle layers as confirmatory wins.

There is **no guarantee** that a Q1 venue accepts this story, that all blockers clear, or that optional Phase 3 evidence runs. This roadmap describes **preparation**, not acceptance.

---

## API budget gate (all phases)

| Gate | Rule |
| --- | --- |
| Default | **API=0** — design docs, offline verification, manuscript drafting |
| Phase 3 only | Controlled live eval **after** human budget sign-off ([`LIVE_EVALUATION_GATE.md`](../research/LIVE_EVALUATION_GATE.md)); Target ≠ Judge; no retune-to-win; no N or pack changes without new human lock |
| Phase 4 submit | **Human-only** portal upload; agents never submit |

---

## Phase 1 — Claim ceiling + blocker matrix (**done**, PR #74)

**Goal:** Align contributors on Q1 scope, claim ceiling, and documented blockers before any evidence-design or live work.

**Deliverables:** This roadmap · [`Q1_BLOCKER_MATRIX.md`](Q1_BLOCKER_MATRIX.md) · pointers in [`STATUS.md`](STATUS.md) / [`START_HERE.md`](../START_HERE.md).

**Exit criteria:** Met — matrix live; science bytes unchanged; workshop quality path **done** on `e4870b9`.

**API budget:** 0

---

## Phase 2 — Evidence-design locks (**done**, PR #74; API=0)

**Goal:** Close **design** gaps for a defensible Q1 methods/limitations section — without inventing numbers or running live eval.

**Deliverables:**

- [`DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md`](DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md) (decision ID **Q1-P2**)
- Confirmatory V2 **Future Work** for this cycle; paper = Track A (n=61 FAIL) + Track B (scoped) only
- D-22 **+1 → `PRIVILEGE_EXFIL`** rule for *future* V2 (25/base; no pack build now)
- Track A δ̂ **95% CI BLOCKING GAP** locked in prose (no invented CI)
- Must-have vs Future Work table; blocker matrix **P2 disposition** column

**Exit criteria:** Met — every matrix row tagged **immutable** | **docs-fixed** | **P3-if-budget** | **Future Work** per Q1-P2 §E.

**API budget:** 0

---

## Phase 3 — Controlled evidence (**not done**; human budget required)

**Pre-registration scaffold (docs only):** [`DECISION_LOCK_Q1_P3_ARMS.md`](DECISION_LOCK_Q1_P3_ARMS.md) · **priority table:** [`Q1_P3_PRIORITY.md`](Q1_P3_PRIORITY.md)

**Goal:** Optional, pre-registered live runs that **add** evidence — they do **not** rewrite Track A FAIL or merge tracks in claims. **No Q1 acceptance guarantee.** **API=0**; approved USD **TBD — Matin**; **no runs authorized** by roadmap text alone.

**Budget-limited priority (Matin-approved framing):**

1. **P3-1** External baseline (same protocol) — **first** if small budget; goal = commensurate comparison on same episode IDs, **not** AdaptiGuard superiority.
2. **P3-5** Mechanism live (`p1_mechanism_v1.0.0`) — attribution; `live_evaluated=false` today; not AgentDojo.
3. **P3-3/4** Multi-model robustness — **one merged arm**; requires **new human lock** for model IDs before run (default remains qwen-7b ≠ qwen-72b).
4. **P3-2** Confirmatory V2 + larger n — **last** / heaviest; Q1-P2 Future Work until separate authorization; this doc does not authorize V2 bytes/live alone.

** Preconditions:**

- Human budget sign-off and gate checklist satisfied
- Frozen pack SHA locks unchanged unless a **new** freeze PR and decision record exist
- Target ≠ Judge; treatment arms labeled; no detector retune after seeing confirmatory outcomes

**Out of scope:**

- “Run until p&lt;0.05” on Track A VNEXT
- Presenting simulation or Layer A oracle ASR as confirmatory defense success

**Exit criteria:**

- New AUDIT folders immutable once written; claims updated only via dual-track checklists
- Results reported with track labels; no FAIL→PASS narrative

**API budget:** Human-approved only

---

## Phase 4 — Findings / Q1 manuscript + artifact (**draft on PR #74**)

**Goal:** Manuscript and artifact **beyond** the short [`workshop_vnext_fail`](../paper/workshop_vnext_fail/README.md) packet — dual-track findings, limitations, and (if ever run) Phase 3 supplements as separate AUDIT citations.

**Deliverables (folder):** [`docs/paper/q1_findings/`](../paper/q1_findings/README.md)

| File | Status |
| --- | --- |
| [`README.md`](../paper/q1_findings/README.md) | Hub + claim ceiling |
| [`MANUSCRIPT.md`](../paper/q1_findings/MANUSCRIPT.md) | Findings-length English draft |
| [`CLAIMS_MAP.md`](../paper/q1_findings/CLAIMS_MAP.md) | Allowed/forbidden one-liners |
| [`SUBMISSION_CHECKLIST.md`](../paper/q1_findings/SUBMISSION_CHECKLIST.md) | Venue TBD; **no DONE on upload** |
| [`SUBMISSION_PACKET.md`](../paper/q1_findings/SUBMISSION_PACKET.md) | Cover packet (FAIL-first dual-track) |
| [`FIGURES.md`](../paper/q1_findings/FIGURES.md) · [`references.bib`](../paper/q1_findings/references.bib) | Camera-ready polish (PR #74) |
| Hash appendix pointer | [`workshop_vnext_fail/APPENDIX_HASHES.md`](../paper/workshop_vnext_fail/APPENDIX_HASHES.md) + [`REPRODUCIBILITY_PACKAGE.md`](REPRODUCIBILITY_PACKAGE.md) |

**Exit criteria (remaining):**

- Matin review of draft against [`CLAIMS_CHECKLIST.md`](../paper/CLAIMS_CHECKLIST.md)
- Camera-ready conversion (human; venue TBD)
- **Submit:** HUMAN_ONLY — not executed by agents

**Phase 3 note:** Controlled live evidence is **still pending budget**. This Phase 4 draft does **not** claim Phase 3 complete.

**P4 polish (PR #74):** manuscript packet + **scientific quality** (offline Track A δ̂ CI script/artifact, [`QUALITY_GAPS.md`](../paper/q1_findings/QUALITY_GAPS.md), estimand/related-work pass). Venue/arXiv wrappers exist but do not substitute for evidence. **P3 not done.**

**API budget:** 0 for writing

---

## Read order (Q1 contributor)

1. [`docs/START_HERE.md`](../START_HERE.md)  
2. [`QUALITY_ROADMAP_5PHASE.md`](QUALITY_ROADMAP_5PHASE.md) (**done** — workshop path)  
3. **This file** + [`Q1_BLOCKER_MATRIX.md`](Q1_BLOCKER_MATRIX.md) + [`DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md`](DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md)  
4. [`STATUS.md`](STATUS.md)  
5. [`docs/paper/dual_track/DUAL_TRACK_STATUS.md`](../paper/dual_track/DUAL_TRACK_STATUS.md)  
6. [`DECISION_LOCK_D22_CONFIRMATORY_V2_TAXONOMY.md`](DECISION_LOCK_D22_CONFIRMATORY_V2_TAXONOMY.md)

**Navigation:** [`STATUS.md`](STATUS.md) · [`docs/experiments/README.md`](README.md)
