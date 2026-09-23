# P3-1 external baseline — candidate shortlist (honest)

**Purpose:** Budget-limited **first** Phase 3 arm ([`Q1_P3_PRIORITY.md`](Q1_P3_PRIORITY.md)). **No benchmark numbers invented.** **NOT AUTHORIZED TO RUN.**

**Design lock:** [`DECISION_LOCK_Q1_P3_1_BASELINE.md`](DECISION_LOCK_Q1_P3_1_BASELINE.md)

**Note:** **B0 (no defense)** is already the control in Track A/B confirmatory AUDITs — it is **not** a P3-1 “external” candidate; P3-1 adds a **third** defense treatment on the **same episode IDs**.

---

## Harness reality (adapti-guard today)

| Path | Role |
| --- | --- |
| `scripts/run_phase1_confirm.py` + `defense_baselines.py` | **Confirmatory** live path used for Track B (`PHASE1-CORE`, B0) |
| VNEXT confirm runner (Track A) | Track A AUDIT lineage; B0 + VNEXT-ADAPT locked |
| `baselines/baseline_runner.py` + `baselines/*.py` | **Separate** benchmark_q1-style eval — **not** wired to frozen confirmatory packs without engineering |

Any P3-1 candidate requires an **S–M** integration step: register treatment in the **correct** confirmatory runner for the chosen pack, record `config_SHA256`, pre-run lock.

---

## Candidate classes (3–5)

| # | Class | Method id (proposed) | In-repo today | Effort | Citation / note |
| --- | --- | --- | --- | --- | --- |
| 1 | **Fixed static block (A3)** | `STATIC-A3` via `make_l3_fixed_block` in [`defense_baselines.py`](../../src/adapti_guard/experiments/defense_baselines.py) | **Yes** — factory + Phase-1 tests reference STATIC-A1/A2/A3 | **S** | In-repo protocol arm (fixed L3 block); **not** VNEXT-ADAPT / **not** PHASE1-CORE mapping |
| 2 | **Rule-based detector + block (B1)** | `B1_RULE` via `make_b1_rule_based(threshold=…)` | **Yes** — same `PromptInjectionDetector` family as much of AdaptiGuard | **S** | Simple heuristic firewall class; **limitation:** shared detector DNA with Phase-1 stack — label honestly in AUDIT |
| 3 | **TF-IDF + logistic ML gate** | `tfidf_ml` via [`baselines/tfidf_baseline.py`](../../baselines/tfidf_baseline.py) | **Partial** — trains on `datasets/benchmark_q1/train.jsonl` if present; **not** on confirmatory pack runner | **M** | Classic sparse ML baseline pattern; risk of train/eval leakage if train corpus ≠ frozen pack — needs explicit lock on train source |
| 4 | **Llama Guard–class input filter** | `llama_guard` via [`baselines/llama_guard.py`](../../baselines/llama_guard.py) | **Stub** — regex fallback unless real model wired | **L** | Inan et al., Llama Guard ([`references.bib`](../paper/q1_findings/references.bib) `inan2023llama`) |
| 5 | **NeMo Guardrails–class policy wrapper** | `nemo_guard` via [`baselines/nemo_guardrails.py`](../../baselines/nemo_guardrails.py) | **Stub** — regex fallback only | **L** | Rebedea et al., NeMo Guardrails (`rebedea2023nemo` in bib) |

**Not listed as P3-1 defaults:** `PHASE1-CORE`, `VNEXT-ADAPT` (already primary treatments); `prompt_guard` (regex fallback duplicate of #2).

---

## Implementability summary

| Effort | Meaning here |
| --- | --- |
| **S** | Register existing `DefenseFn` in confirmatory runner + manifest fields + pytest smoke on dry-run path |
| **M** | New lock for training data + adapter to frozen episode JSONL + judge path parity |
| **L** | Real third-party model/API integration, versioning, cost model, failure handling |

---

## Recommended default for first budget run (design only)

**Default candidate:** **`STATIC-A3` (`make_l3_fixed_block`)**
**Recommended pack (Matin may override):** **`phase1_confirm_v1`** (Track B corpus)

**Rationale (no performance claims):**

1. **Commensurate protocol** — Phase-1 confirm runner and MSID/utility machinery already exist for this pack; same Target/Judge discipline as Track B AUDIT.
2. **Clear treatment separation** — Fixed L3 block is **not** PHASE1-CORE and **not** VNEXT-ADAPT; supports honest “external-class fixed policy” comparison vs **B0 on same IDs**.
3. **Smallest engineering surface (**S**)** — Factory already in `defense_baselines.py`; STATIC arms exercised in [`tests/test_phase1_core_pipeline.py`](../../tests/test_phase1_core_pipeline.py).
4. **Goal wording safe** — Fits P3-1 “comparison on same episode IDs,” not AdaptiGuard superiority narrative.
5. **Track A FAIL untouched** — Run on Track B pack does not amend `VNEXT_CONFIRM/20260914-133147/`.

**If Matin chooses Track A pack instead:** same `STATIC-A3` class is still viable (**S**), but claims must stay **P3-1 supplemental** and must **not** re-open VNEXT qualified-win narrative on immutable FAIL.

**Alternate if static block deemed too in-repo:** **`B1_RULE`** at pre-locked τ (**S**) — document shared-detector limitation in AUDIT.

---

## Before run (reminder)

Fill [`DECISION_LOCK_Q1_P3_1_BASELINE.md`](DECISION_LOCK_Q1_P3_1_BASELINE.md) pre-run block · human USD cap · **API=0** until signed.

**Navigation:** [`DECISION_LOCK_Q1_P3_ARMS.md`](DECISION_LOCK_Q1_P3_ARMS.md) · [`QUALITY_GAPS.md`](../paper/q1_findings/QUALITY_GAPS.md)
