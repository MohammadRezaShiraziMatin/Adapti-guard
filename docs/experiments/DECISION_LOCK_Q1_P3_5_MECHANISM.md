# Decision lock Q1-P3-5 — Mechanism pack live eval (design packet)

**Decision ID:** Q1-P3-5
**Parent:** [`DECISION_LOCK_Q1_P3_ARMS.md`](DECISION_LOCK_Q1_P3_ARMS.md) (priority **2**) · [`Q1_P3_PRIORITY.md`](Q1_P3_PRIORITY.md)
**Status:** **DESIGN LOCKED** — **NOT AUTHORIZED TO RUN**
**Date (UTC):** 2026-09-23
**Author:** Seyed Mohammadreza Shirazi Matin
**Mode:** Documentation only. **API=0.**

**Companion gate:** [`LIVE_EVALUATION_GATE.md`](../research/LIVE_EVALUATION_GATE.md) (`LIVE-EVAL-GATE-0.1`) · freeze [`P1_MECHANISM_V1_0_0_FREEZE.md`](../research/P1_MECHANISM_V1_0_0_FREEZE.md)

---

## Purpose

Optional **mechanism-surface attribution** live eval on frozen **`p1_mechanism_v1.0.0`** — adds evidence; **does not** replace Track A/B confirmatory AUDITs or claim AgentDojo-class results.

**Track A VNEXT FAIL immutable.** Track B scoped result unchanged unless separately cited.

---

## Pack (read-only)

| Field | Value |
| --- | --- |
| Path | `datasets/frozen/p1_mechanism_v1.0.0/dataset.jsonl` |
| SHA-256 | `1a0b0053c392e7b3e0727b92b4f088790abda001fd852ec1703c5ee0a67dd235` |
| Status today | **`live_evaluated=false`** (must remain until run starts; set in manifest after run per gate) |
| Scope | Mechanism benchmark — **not** multi-step agent leaderboard |

---

## Goal wording (binding)

| Required | Forbidden |
| --- | --- |
| Mechanism attribution on locked pack; new immutable AUDIT folder | AgentDojo / SOTA / production-ready |
| Policies B0, STATIC-A1, PHASE1-CORE (or amended list in human sign-off) per gate | Pooling with Track A/B confirmatory tables without labels |
| Target ≠ Judge per approved matrix | Reversing Track A FAIL |

---

## Gates (before any API call)

1. Full human checklist in [`LIVE_EVALUATION_GATE.md`](../research/LIVE_EVALUATION_GATE.md) — all boxes + signature block.
2. Pack byte identity verified vs SHA above.
3. **USD cap** and max requests — **TBD — Matin**.
4. Output directory **must not** overwrite `VNEXT_CONFIRM/` or `PHASE1_CONFIRM/` historical paths.
5. Detector/policy lock commit recorded — no retune after outcomes.

---

## Required pre-run fields (summary)

Arm id **Q1-P3-5** · pack SHA · execution commit · Target/Judge ids · policy list · budget cap · explicit human authorization sentence · approver/date UTC.

(Process detail mirrors P3-1 checklist in [`DECISION_LOCK_Q1_P3_1_BASELINE.md`](DECISION_LOCK_Q1_P3_1_BASELINE.md).)

---

## Success criteria (process only)

| Criterion | Meaning |
| --- | --- |
| Immutable AUDIT | New folder under `experiments/real_llm_eval/` (mechanism lineage); write-once |
| Pre-registration | Gate checklist + lock doc cited before API |
| Honest reporting | Mechanism scope only; **no invented ASR** in this doc |
| Confirmatory tracks | Historical Track A FAIL / Track B verdict numbers unchanged |

**No Q1 venue acceptance guarantee.**

---

## API / authorization

| Field | Value |
| --- | --- |
| Default | **API=0** |
| Approved USD | **TBD — Matin** |
| **This document** | **Does not authorize a run** |

**Navigation:** [`STATUS.md`](STATUS.md) · [`LIVE_EVALUATION_PROTOCOL.md`](../research/LIVE_EVALUATION_PROTOCOL.md)
