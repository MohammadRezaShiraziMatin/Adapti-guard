# Decision lock Q1-P3-3/4 — Multi-model robustness (merged arm scaffold)

**Decision ID:** Q1-P3-3/4
**Parent:** [`DECISION_LOCK_Q1_P3_ARMS.md`](DECISION_LOCK_Q1_P3_ARMS.md) (priority **3**) · [`Q1_P3_PRIORITY.md`](Q1_P3_PRIORITY.md)
**Status:** **SCAFFOLD ONLY** — **NOT AUTHORIZED TO RUN**
**Date (UTC):** 2026-09-23
**Author:** Seyed Mohammadreza Shirazi Matin
**Mode:** Documentation only. **API=0.**

---

## Purpose

**Single merged arm** for Target/Judge variant sweeps and multi-model robustness — **one** pre-registered design, **one** AUDIT narrative. Does **not** authorize API spend or model changes by itself.

---

## Default (until Matin human lock)

| Role | Model id |
| --- | --- |
| Target | `qwen/qwen-2.5-7b-instruct` |
| Judge | `qwen/qwen-2.5-72b-instruct` |

**Rule:** Target ≠ Judge. **No P3-3/4 live run** with alternate models until a **new human lock document** lists approved Target and Judge IDs (providers, versions, pricing check).

---

## Placeholder fields (HUMAN TBD — fill before run)

```text
lock_doc_id: TBD
target_model_ids: [ TBD — Matin ]
judge_model_ids: [ TBD — Matin ]
pack_id: vnext_confirm_v1.0 | phase1_confirm_v1 (TBD)
pack_SHA256: TBD
USD_cap: TBD — Matin
max_requests: TBD — Matin
authorized: NO
```

---

## Binding constraints

- Track A VNEXT **FAIL** immutable — multi-model sweep **does not** amend `VNEXT_CONFIRM/20260914-133147/`.
- No unlabeled pooling with Track A/B confirmatory tables.
- No ad hoc “model shopping” after seeing outcomes.
- **No Q1 venue acceptance guarantee.**

---

## Success criteria (process only)

Pre-registered model matrix · new immutable AUDIT · per-pair estimands labeled · historical dual-track numbers unchanged.

**Navigation:** [`DECISION_LOCK_Q1_P3_ARMS.md`](DECISION_LOCK_Q1_P3_ARMS.md) · [`QUALITY_GAPS.md`](../paper/q1_findings/QUALITY_GAPS.md)
