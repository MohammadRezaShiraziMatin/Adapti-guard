# Project completion audit (Phase 0)

**Status:** integrity check only. No detector or manuscript edits in this phase.  
**Date (UTC):** 2026-09-14  
**Branch:** `cursor/layer-a-v4-project-completion-f6c7`  
**Parent commit:** `ac66652255beb8e377f260fe654ef35ce9d87185`  
**Working tree at audit:** clean (on parent before v4 work)

## Scientific stance

The completion objective is **not** a positive defense result. It is a reproducible answer to whether DETECTION → RISK → INTERVENTION → OUTCOME is a useful cost-aware runtime defense. Layer A v3 is already **VALID / CASE D** (detector/risk bottleneck).

## Frozen hashes (verified this audit)

| Artifact | SHA-256 |
| --- | --- |
| Layer A v2 `dataset.jsonl` | `76c60433d07258d06c5df451bfdd5be4d8ff08988b26c3ecea32ebc32d09ac33` |
| Layer A v3 `test_split.jsonl` | `47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8` |
| Layer A v3 `dataset.jsonl` | `abbc87134dc6563231aa422cb923226a5158d512c260a0ec17fd6997877632dd` |

## Repository map

| Component | Location |
| --- | --- |
| Detector (regex V18 / primary-evidence gate) | `src/adapti_guard/detector/prompt_injection_detector.py` |
| Detector interface | `src/adapti_guard/detector/base.py` (`regex_v18`) |
| Risk | `src/adapti_guard/risk/risk_engine.py` |
| Policy (A0–A3, LOW never A3) | `src/adapti_guard/policy/policy_engine.py` |
| Actions | `src/adapti_guard/defense/action_layer.py` |
| Adaptive B3 | `src/adapti_guard/experiments/defense_baselines.py` |
| Real LLM pipeline | `src/adapti_guard/experiments/real_llm_pipeline.py` |
| Detector-only eval | `src/adapti_guard/evaluation/detector_eval.py` |
| Frozen packs | `datasets/frozen/layer_a_v2/`, `datasets/frozen/layer_a_v3/` |
| Model config | `configs/models.yaml` (`target_2`, `judge_fallback`) |
| Manuscript results | `docs/paper/04_results.md` (**do not edit**) |
| v3 recovery note | `docs/experiments/LAYER_A_V3_SCIENTIFIC_RECOVERY.md` |

## Existing Layer A experiments (do not overwrite)

| Run | Role |
| --- | --- |
| `LAYER_A_V2_OPENROUTER/20260913-191217` | Historical B0 vs B3 |
| `LAYER_A_V2_FIXED_ABLATION/20260913-192859` | L2 unsupported, L3 ceiling |
| `LAYER_A_V2_DETECTOR_FN_AUDIT/20260913-194822` | 18/18 FN-A |
| `LAYER_A_V3_DETECTOR/20260913-200341` | Detector-only TEST recall 0.05 |
| `LAYER_A_V3_INTERVENTION/20260913-200544` | B0 0.75 / B3 0.70 / L3 0 / oracle diagnostic |

## Eval contract (unchanged)

- Target: `qwen/qwen-2.5-7b-instruct` (`target_2`)
- Judge: `qwen/qwen-2.5-72b-instruct` (`judge_fallback`)
- `cache.enabled = false`, seed 42
- TEST: 40 attack + 40 benign from frozen `test_split.jsonl`

## Unresolved limitations (entering completion)

1. Regex detector + V18 gate: `contextual_attack` alone scores 0; TRAIN+DEV recall 4/40.
2. `RiskEngine` compresses p=1.0 PROMPT_INJECTION to 0.56 → HIGH unreachable.
3. B3 adaptation uses sanitization heuristic, not judge ASR; empirically A1×80.
4. L2 has no tool-execution loop (`DefenseFn` cannot carry `tool_access`).
5. Hard-negative FPR is high because quoted attack strings fire the same keywords.
6. Keyword-only detection is **not** an acceptable primary scientific solution.

## Missing components (to add only if scientifically justified)

- Evidence-structured detector v4 (TRAIN/DEV design; one frozen TEST eval)
- Monotonic v4 risk mapping (DEV only for boundaries)
- Tool-loop harness before any L2 score
- Final audit / reconciliation / reproducibility package
- **Not missing:** live B0/B3 rerun (forbidden until detector-only gate passes)

## Leakage control

Phase 1–2 **must not** inspect `test_split.jsonl` prompt text for rule design. TEST aggregate metrics already published may be cited. Feature/threshold selection is TRAIN/DEV only.

## Intentionally untouched

- `docs/paper/04_results.md`
- `datasets/frozen/layer_a_v2/**`
- Historical v2/v3 AUDIT folders and metrics
- Default `PromptInjectionDetector` behavior used by historical runs (keep as v3/legacy)
