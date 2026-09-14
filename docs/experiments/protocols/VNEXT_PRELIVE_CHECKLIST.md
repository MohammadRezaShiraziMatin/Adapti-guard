# VNEXT Pre-Live Infrastructure Checklist

**STATUS: PRELIVE_PASS**

**Date (UTC):** 2026-09-14  
**Scope:** Pre-live infrastructure only. No OpenRouter/LLM/API call. No live eval. Confirmation **not** run.  
**LLM/API:** **0**  
**Base:** `cursor/vnext-confirm-pack-4d85` (PR28 frozen pack) @ `d16b20e52c6332edcf6dbd71f075e27dc91b6838`  
**Protocol:** `VNEXT-PROTOCOL-0.1` + addendum `VNEXT-PROTOCOL-ADDENDUM-0.3` + MSID `VNEXT-MSID-0.1`  
**Pack:** `vnext_confirm_v1.0` — `datasets/frozen/vnext_confirm_v1/dataset.jsonl`

This file records a static / local-hash / env-presence audit. It does **not** authorize Phase 3 scoring. Live B0 / VNEXT-ADAPT remains forbidden until human approval of a run that cites the §1 digest and aborts on mismatch (S3).

---

## Verdict

| # | Check | Result |
| --- | --- | --- |
| 1 | Pack SHA-256 == freeze digest | **PASS** |
| 2 | Label-blind adaptive (no `is_attack` in controller path) | **PASS** |
| 3 | B0 / VNEXT pairing + `tool_loop` in `evaluate_episode` | **PASS** |
| 4 | OpenRouter yaml keys (`target_2` ≠ `judge_fallback`); env key presence only | **PASS** (`OPENROUTER_API_KEY=SET`) |
| 5 | `cache.enabled=false` | **PASS** |
| 6 | Repro metadata fields listed for a future run | **PASS** (listed; not executed) |

**Overall: PRELIVE_PASS.** Confirmation scoring was not started.

---

## 1. Pack SHA-256

**Expected (addendum §4 / PR28 freeze):**  
`523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518`

**Computed (local `hashlib.sha256` / `sha256sum`, no network):**

| Artifact | SHA-256 | Match |
| --- | --- | --- |
| `datasets/frozen/vnext_confirm_v1/dataset.jsonl` | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` | **yes** |
| `datasets/frozen/vnext_confirm_v1/confirmation.jsonl` | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` | **yes** (byte-identical to `dataset.jsonl`) |
| `manifest.json` `dataset_sha256` / `confirmation_sha256` | same digest | **yes** |
| `hashes.sha256` listed digest | same digest | **yes** |

Pack id `vnext_confirm_v1.0`; 122 rows (n_attack=61, n_benign=61); `manifest.llm_api_calls=0`.

**Result: PASS.**

---

## 2. Label-blind adaptive (no `is_attack` in controller path)

Gold `label` / `is_attack` must not enter the adaptive runtime (protocol P0). Oracle arms remain diagnostic-only.

| Location | What was checked |
| --- | --- |
| `src/adapti_guard/experiments/defense_baselines.py:99-103` | `AdaptiveDefenseState` documents the VNEXT leakage rule: gold `is_attack` / labels never enter this controller. |
| `src/adapti_guard/experiments/defense_baselines.py:131` | `evaluate(self, prompt, context=None)` — no `is_attack` parameter. Passing `is_attack=True` raises `TypeError`. |
| `src/adapti_guard/experiments/defense_baselines.py:134-176` | Adaptation uses runtime stand-ins only (`detector_hit`, `contained`, `blocked`, `defense_cost`). `_last_outcome` keys: `detector_hit`, `blocked`, `action`, `contained`, `defense_cost`. No `is_attack`. |
| `src/adapti_guard/experiments/defense_baselines.py:181-195` | `make_b3_adaptive` pops `_LEAKED_GOLD_KWARGS` (`is_attack`, `label`, `gold_label`, `category`) before `state.evaluate`. |
| `src/adapti_guard/experiments/defense_baselines.py:210-213` | `make_b3_adaptive_v4` uses the same strip-then-evaluate path. |
| `src/adapti_guard/experiments/real_llm_pipeline.py:355-381` | `is_attack = record.get("label") == "attack"` is bound **only** inside `baseline_key.startswith("ORACLE_")`. The `else` branch is labeled label-blind and calls `evaluate_episode` with `(prompt, context)` via the defense fn. |
| `src/adapti_guard/evaluation/attack_success.py:290` | `evaluate_episode` calls `defense_fn(prompt, context or None)` — gold label is not forwarded into the controller. |

Local smoke (no LLM): `make_b3_adaptive()(..., is_attack=True)` equals `make_b3_adaptive()(..., is_attack=False)` on the same prompt; `_last_outcome` has no `is_attack`.

Oracle exception (kept diagnostic, not in the controller path): `defense_baselines.py:255-321` (`make_oracle_risk_policy` / `make_oracle_block_attacks`).

**Result: PASS.**

---

## 3. B0 / VNEXT pairing + `tool_loop` in `evaluate_episode`

Protocol primary arms: **B0** vs **VNEXT-ADAPT** (label-blind adaptive treatment on the Phase 2 harness). VNEXT-ADAPT is a scientific name, not a `BASELINE_FACTORIES` key. Code factories:

| Arm | Factory key | Lines |
| --- | --- | --- |
| B0 (no defense) | `B0` → `make_b0_no_defense` | `defense_baselines.py:10-14`, `324-325` |
| VNEXT-ADAPT (label-blind adaptive) | `B3` → `make_b3_adaptive` or `B3_V4` → `make_b3_adaptive_v4` | `defense_baselines.py:184-218`, `341-346` |

**Pairing (same IDs, both arms through one episode harness):**

- `real_llm_pipeline.py:509` loads one `records` list.
- `real_llm_pipeline.py:562-571` iterates `config.baselines` and calls `run_baseline_evaluation(baseline_key, records, ...)` — identical records, pairing key = episode `id`.
- `real_llm_pipeline.py:374-381` (non-oracle) and `attack_success.py:270-290` score each arm via `evaluate_episode`.
- Default baseline list includes `B0` and `B3` (`real_llm_pipeline.py:65`).

**`tool_loop` is inside `evaluate_episode` (both arms):**

| Lines | Behavior |
| --- | --- |
| `attack_success.py:11-15` | Imports `MockToolRegistry`, `extract_tool_request`, `run_tool_turn`. |
| `attack_success.py:300` | Default `MockToolRegistry()` if none passed. |
| `attack_success.py:322-326` | `extract_tool_request(model_response=..., generation_raw=..., record=record)`. |
| `attack_success.py:328-333` | `run_tool_turn(requested=..., action=action, registry=registry)`; appends `[TOOL_RESULT]` when executed. |
| `attack_success.py:339-353` | Persists `tool_blocked` / `tool_executed` / `tool_failure`. |
| `tool_loop.py:83-101` | Model output preferred; pack `tool_call` is fallback. |
| `tool_loop.py:111-153` | A2 deny (`TOOL_DENIED`); A3 turn-blocked; A0/A1 execute. |

A3 skips the target (`attack_success.py:302-320` gated on `not blocked`) and does not execute tools.

Deterministic unit tests (no LLM/API): `tests/test_vnext_phase2_harness.py`, `tests/test_tool_loop.py`, `tests/test_vnext_confirm_pack.py` — **28 passed**.

**Result: PASS.**

---

## 4. OpenRouter yaml keys (no API call)

Inspected `configs/models.yaml` only. No HTTP. Secret not printed.

| Key | Provider | Model |
| --- | --- | --- |
| `target_2` (`models.yaml:64-69`) | `openrouter` | `qwen/qwen-2.5-7b-instruct` |
| `judge_fallback` (`models.yaml:48-53`) | `openrouter` | `qwen/qwen-2.5-72b-instruct` |
| `multi_model.judge` (`models.yaml:136-140`) | — | `judge_fallback` |
| `multi_model.judge_fallback` | — | `judge_fallback` |

`target_2.model ≠ judge_fallback.model` (**yes**). OpenRouter `build_judge()` uses `multi_model.judge` (`llm_judge.py:279-294`).

**Env presence (no secret printed, no API):**

```
OPENROUTER_API_KEY=SET
```

Local format check (`validate_openrouter_key`, prefix/length only, no network): **VALID**.

**Result: PASS.**

---

## 5. `cache.enabled=false`

`configs/models.yaml:179-180`:

```yaml
cache:
  enabled: false
```

Parsed as Python `bool` `False`.

**Result: PASS.**

---

## 6. Repro metadata fields (for a future run — not executed)

A future Phase 3 confirmation run (after human approval) must log at least:

| Field | Source / intended value |
| --- | --- |
| `protocol_version` | `VNEXT-PROTOCOL-0.1` |
| `addendum_version` | `VNEXT-PROTOCOL-ADDENDUM-0.3` |
| `msid_id` | `VNEXT-MSID-0.1` (δ = 0.20; do not change after unblinding) |
| `power_memo_path` | `docs/experiments/VNEXT_POWER_MEMO.md` (`VNEXT-POWER-MEMO-0.1`) |
| `git_commit` | SHA of the scoring checkout (`experiment_logging.git_commit`) |
| `confirmation_sha256` / `dataset_hash` | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` — abort on mismatch (S3) |
| `pack_id` | `vnext_confirm_v1.0` |
| `pack_path` | `datasets/frozen/vnext_confirm_v1/dataset.jsonl` |
| `target_config_key` / `target_model` | `target_2` / `qwen/qwen-2.5-7b-instruct` |
| `judge_config_key` / `judge_model` | `judge_fallback` / `qwen/qwen-2.5-72b-instruct` |
| `temperature` | `0.0` (yaml target and judge) |
| `seed` | pack mix seed 61; pipeline `PipelineConfig.seed` (Layer A default 42 — confirm in run manifest) |
| `cache_enabled` | `false` (`cache.enabled=false`) |
| `baselines` | primary pair `B0` and VNEXT-ADAPT (`B3` or `B3_V4` as named in the run manifest) |
| `n_attack` / `n_benign` / `n_samples` | 61 / 61 / 122 |
| `exclusion_counts` | §12 reasons (`target_api_error`, `judge_api_error`, `judge_parse_error`, `no_judge_configured`) |
| `experiment_id` / `run_id` | `ExperimentRunContext` |
| `config_version` | prediction provenance schema (`PROVENANCE_SCHEMA_VERSION`, currently `1.2`) |
| `evaluation_mode` | `real_llm_judge` |
| Per-episode | `id`, `baseline`, `taxonomy_class`, `attack_succeeded`, `utility_success`, `model_refusal`, `detector_hit`, `intervention_applied`, `tool_blocked`, `tool_failure`, `harmful_action_prevented` (`prediction_provenance.py:55-121`) |

These fields are **listed, not populated by a live run**. This checklist does not write a confirmation manifest.

**Result: PASS (inventory only).**

---

## What this checklist did not do

- No OpenRouter / Groq / Gemini / Ollama generate or judge call
- No live B0 / VNEXT-ADAPT / L2 / L3 / ORACLE scoring
- No confirmation unblinding for detector/policy edits
- No Layer A TEST retune (`47b975f7…`)
- No change to frozen pack bytes

**NEXT:** human approval required before any Phase 3 live eval. A scoring run must cite SHA-256 `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` and abort on mismatch.
