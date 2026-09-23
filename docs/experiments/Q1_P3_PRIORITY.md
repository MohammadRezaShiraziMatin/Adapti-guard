# Q1 Phase 3 — budget-limited priority (Matin-approved framing)

**Status:** Design / priority lock only. **API=0.** **No runs authorized** by this document.
**Authority:** [`DECISION_LOCK_Q1_P3_ARMS.md`](DECISION_LOCK_Q1_P3_ARMS.md) (full arm specs) · **Q1-P2** still treats Confirmatory V2 as Future Work until a separate authorization supersedes it.

**No Q1 venue acceptance guarantee.** No arm reverses Track A VNEXT **FAIL** (`VNEXT_CONFIRM/20260914-133147/`).

---

## Priority order (if budget is limited)

| Rank | ID | Arm | When to run |
| --- | --- | --- | --- |
| 1 | **P3-1** | External baseline (same protocol) | **First** if budget is small — design [`DECISION_LOCK_Q1_P3_1_BASELINE.md`](DECISION_LOCK_Q1_P3_1_BASELINE.md) |
| 2 | **P3-5** | Mechanism live (`p1_mechanism_v1.0.0`) | [`DECISION_LOCK_Q1_P3_5_MECHANISM.md`](DECISION_LOCK_Q1_P3_5_MECHANISM.md) |
| 3 | **P3-3/4** | Multi-model robustness (merged) | [`DECISION_LOCK_Q1_P3_3_MULTIMODEL.md`](DECISION_LOCK_Q1_P3_3_MULTIMODEL.md) |
| 4 | **P3-2** | Confirmatory V2 + larger n | **Last** / heaviest |

---

## Goal wording (binding)

| ID | Allowed goal framing | Forbidden framing |
| --- | --- | --- |
| P3-1 | Commensurate comparison vs an **external defense** on **same episode IDs** under the declared frozen pack/protocol | “Prove AdaptiGuard adds X,” superiority, SOTA, reversing Track A FAIL |
| P3-5 | Mechanism-surface **attribution** on the frozen mechanism pack (`live_evaluated=false` today) | AgentDojo-class agent benchmark; replacing Track A/B confirmatory tables |
| P3-3/4 | Robustness of estimands under **pre-locked** Target/Judge variants (one arm, one AUDIT story) | Pooling with Track A/B without labels; default pair change without new lock |
| P3-2 | New evidence on a **future** V2 pack after freeze + SAP locks | V2 bytes or live from this priority doc alone; retconning Track A MSID on `vnext_confirm_v1.0` |

---

## API / budget

| Field | Value |
| --- | --- |
| Approved USD cap | **TBD — Matin** (human) |
| Default | **API=0** |
| Runs | **Not authorized** until budget sign-off + per-arm gates |

**Navigation:** [`Q1_ROADMAP_4PHASE.md`](Q1_ROADMAP_4PHASE.md) · [`QUALITY_GAPS.md`](../paper/q1_findings/QUALITY_GAPS.md) · [`STATUS.md`](STATUS.md)
