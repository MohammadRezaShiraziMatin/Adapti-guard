# Reproducibility package (Phase 12)

## Identities

- Repo: ADAPTI-GUARD
- Detector v4 freeze: git `46bffe142be334260f767a98c2201ca273c24f71` (`evidence_v4.0`)
- Intervention wiring: git `3ca86a7a876c3de01c208eea62e736bce33ee422`
- Frozen TEST: `datasets/frozen/layer_a_v3/test_split.jsonl`  
  SHA-256 `47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8`
- Historical v2: SHA-256 `76c60433d07258d06c5df451bfdd5be4d8ff08988b26c3ecea32ebc32d09ac33`

## Models and eval contract

- Target `target_2` = `qwen/qwen-2.5-7b-instruct`
- Judge `judge_fallback` = `qwen/qwen-2.5-72b-instruct`
- `cache.enabled = false` (`configs/models.yaml`)
- seed 42; 40 attack + 40 benign from `datasets/frozen/layer_a_v3_test_split_view`

## Commands

Detector DEV gate (no TEST):

```
python3 scripts/run_layer_a_v4_detector_eval.py --output experiments/real_llm_eval/LAYER_A_V4_DETECTOR/dev_gate
```

One-shot TEST (do not iterate afterward):

```
python3 scripts/run_layer_a_v4_detector_eval.py --include-test --output experiments/real_llm_eval/LAYER_A_V4_DETECTOR/20260914-frozen-test
```

Intervention (v4 policies only):

```
python3 scripts/run_layer_a_v4_eval.py --require-key --baselines B3_V4 B2_L3_V4 --attack-n 40 --benign-n 40 --seed 42 --output experiments/real_llm_eval/LAYER_A_V4_INTERVENTION/20260914-101700 --experiment-id LAYER-A-V4-INTERVENTION
```

Tests:

```
python3 -m pytest tests/test_layer_a_v4_detector.py tests/test_tool_loop.py tests/test_layer_a_v3_pack.py tests/test_statistics.py -q
```

## Artifacts

| Path | Contents |
| --- | --- |
| `docs/experiments/PROJECT_COMPLETION_AUDIT.md` | Phase 0 |
| `docs/experiments/LAYER_A_V4_FORENSIC_AUDIT.md` | Phase 1 (TRAIN/DEV) |
| `docs/experiments/LAYER_A_V4_DEV_GATE.md` | Phase 2–3 gate |
| `docs/experiments/LAYER_A_V4_RISK_CALIBRATION.md` | Phase 4 |
| `experiments/real_llm_eval/LAYER_A_V4_DETECTOR/` | detector metrics |
| `experiments/real_llm_eval/LAYER_A_V4_INTERVENTION/20260914-101700/` | B3_V4 / B2_L3_V4 |
| `docs/experiments/FINAL_SCIENTIFIC_AUDIT.md` | Phase 10 |
| `docs/paper/RESULTS_RECONCILIATION.md` | Phase 11 (no manuscript overwrite) |
| `docs/experiments/PROJECT_FINAL_STATUS.md` | CASE B |

Historical v2/v3 folders and `docs/paper/04_results.md` are intentionally untouched.
