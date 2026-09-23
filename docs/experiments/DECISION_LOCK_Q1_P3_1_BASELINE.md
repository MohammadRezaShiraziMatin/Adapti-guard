# Decision lock Q1-P3-1 — External baseline arm (design packet)

**Decision ID:** Q1-P3-1
**Parent:** [`DECISION_LOCK_Q1_P3_ARMS.md`](DECISION_LOCK_Q1_P3_ARMS.md) (priority **1**) · [`Q1_P3_PRIORITY.md`](Q1_P3_PRIORITY.md)
**Status:** **DESIGN LOCKED** — **NOT AUTHORIZED TO RUN** (no API spend; no live LLM until Matin budget + filled pre-run block)
**Date (UTC):** 2026-09-23
**Author:** Seyed Mohammadreza Shirazi Matin
**Mode:** Documentation only. **API=0.** No merge, no frozen/AUDIT edits, no invented ASR.

**Candidate shortlist:** [`P3_1_BASELINE_CANDIDATES.md`](P3_1_BASELINE_CANDIDATES.md)

---

## Purpose

Enable a **commensurate comparison** of an **external-class defense** (third baseline treatment) under the **same** confirmatory protocol, **same frozen episode IDs**, and **same** Target/Judge pairing as a Matin-chosen track pack — without redesign at budget time.

This arm **adds** a new immutable AUDIT folder; it **does not** amend Track A VNEXT **FAIL** or merge Track A/B claims.

---

## Goal wording (binding)

| Required | Forbidden |
| --- | --- |
| Report ASR, utility, McNemar (or pack-appropriate estimands) for **external baseline vs B0** on **identical episode IDs** | “AdaptiGuard adds X,” superiority over external arm, SOTA, production-ready |
| Label results **P3-1** + pack id + treatment name; cite new AUDIT path only | Implying Track A FAIL reversed or Track B overturns Track A |
| Compare to **locked historical** B0/treatment rows on that pack as context only | Pooled headline ASR across tracks |

**Track A FAIL immutable:** `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/` — **no re-run for win**.

---

## Pack selection (researcher — pre-run)

| Field | Lock |
| --- | --- |
| Pack | **TBD — Matin** before run lock: **`vnext_confirm_v1.0`** (Track A corpus) **or** **`phase1_confirm_v1`** (Track B corpus) |
| Protocol | Must match the frozen pack’s existing confirmatory runner + judge rules (VNEXT vs Phase-1 confirm); **no episode ID changes** |
| Default recommendation (engineering only) | See [`P3_1_BASELINE_CANDIDATES.md`](P3_1_BASELINE_CANDIDATES.md) — **not** a run authorization |

---

## Required pre-run fields (all mandatory before any API call)

Copy into run request / PR / run lock file. Empty = **stop**.

```text
[ ] Arm id: Q1-P3-1
[ ] baseline_method_id: (e.g. STATIC-A3 — see candidates doc)
[ ] config_SHA256: (git commit or lock file hash for defense config + thresholds)
[ ] treatment_name: (string recorded in AUDIT manifest — distinct from VNEXT-ADAPT / PHASE1-CORE)
[ ] pack_id: vnext_confirm_v1.0 | phase1_confirm_v1
[ ] pack_SHA256: (verify against datasets/frozen manifest)
[ ] target_model_id: (default qwen/qwen-2.5-7b-instruct unless superseded by P3-3/4 lock)
[ ] judge_model_id: (default qwen/qwen-2.5-72b-instruct; must ≠ target)
[ ] episode_ids: frozen list from pack — no subsampling without new human lock
[ ] stop_rules: hash mismatch abort; budget cap; judge repair policy per parent VNEXT/Phase-1 AUDIT
[ ] USD_cap: TBD — Matin (HUMAN)
[ ] max_requests: TBD — Matin (HUMAN)
[ ] execution_commit: git rev-parse HEAD at run start
[ ] Explicit human: "I authorize Q1-P3-1 live API spend under this lock"
[ ] Approver + date (UTC)
```

---

## Success criteria (process only — no fabricated metrics)

| Criterion | Meaning |
| --- | --- |
| Pre-registration | All pre-run fields above filled and signed **before** first Target/Judge API call |
| Immutable AUDIT | One new directory under `experiments/real_llm_eval/`; write-once; no in-place edits |
| Honest tables | Report external arm vs B0 on same IDs; **no** expected ASR filled in this doc |
| Historical tracks | Track A FAIL and Track B scoped verdict **unchanged** in prose and numbers |
| Manuscript | Supplement optional only after Matin cites new AUDIT in findings draft |

**No Q1 venue acceptance guarantee.**

---

## Stop rules

Same as [`DECISION_LOCK_Q1_P3_ARMS.md`](DECISION_LOCK_Q1_P3_ARMS.md) § Stop rules, plus:

- Any field in **Required pre-run fields** missing → **do not start**
- Attempt to use P3-1 to re-test VNEXT-ADAPT on Track A pack for a qualified win → **forbidden**

---

## Engineering readiness (READY-WHEN-BUDGET; still NOT AUTHORIZED TO RUN)

| Item | Status |
| --- | --- |
| Treatment factory | **`STATIC-A3`** registered in `get_defense_fn` / `BASELINE_FACTORIES` (`make_l3_fixed_block`) |
| Reference arm list | `configs/phase1_confirm_live_lock.json` → `reference_arms` includes `STATIC-A3` |
| Offline runner | [`scripts/run_q1_p3_1_confirm.py`](../../scripts/run_q1_p3_1_confirm.py) |
| Default pack (design) | `phase1_confirm_v1` SHA `c789811a07d3ed06e1c77d8a45eda6172f480226e006d84fa28386a982536d01` |
| Live artifact root | `experiments/real_llm_eval/Q1_P3_1/<run_id>/` (separate from immutable `PHASE1_CONFIRM/` history) |

**Commands (no API unless live line + Matin sign-off):**

```bash
# Preflight — hash/locks only; no Target/Judge calls
python3 scripts/run_q1_p3_1_confirm.py --preflight-only

# Defense smoke — full pack, defense forward pass only; no network
python3 scripts/run_q1_p3_1_confirm.py --defense-smoke

# Track A pack (hash gate only; supplemental P3-1 — not a VNEXT win re-run)
python3 scripts/run_q1_p3_1_confirm.py --preflight-only --pack vnext_confirm_v1

# LIVE — NOT AUTHORIZED until DECISION_LOCK pre-run block signed + USD cap
# python3 scripts/run_q1_p3_1_confirm.py --require-key \
#   --output experiments/real_llm_eval/Q1_P3_1/<run_id>
```

**Pack wiring (offline):** `run_q1_p3_1_confirm.py --pack phase1_confirm_v1` (default, Phase-1 preflight + scoring) or `--pack vnext_confirm_v1` (VNEXT hash gate + vnext McNemar scoring). Matin must choose pack before live. Live P3-1 still **NOT AUTHORIZED**; Track A historical **FAIL** unchanged.

---

## API / authorization

| Field | Value |
| --- | --- |
| Default | **API=0** |
| Approved USD | **TBD — Matin** |
| **This document** | **Does not authorize a run** |

**Navigation:** [`STATUS.md`](STATUS.md) · [`Q1_ROADMAP_4PHASE.md`](Q1_ROADMAP_4PHASE.md) · [`LIVE_EVALUATION_GATE.md`](../research/LIVE_EVALUATION_GATE.md) (if mechanism overlap — P3-1 uses confirmatory pack runners, not mechanism pack unless Matin explicitly chooses otherwise)
