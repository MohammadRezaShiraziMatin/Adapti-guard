# Phase 2–3 Report — Target LLM + Independent Judge

**Date:** 2026-09-01  
**Status:** IMPLEMENTED (not yet validated with live API in agent environment)

## What was implemented

| Module | Path |
|--------|------|
| Target model interface | `src/adapti_guard/evaluation/target_model.py` |
| LLM cache | `src/adapti_guard/evaluation/llm_cache.py` |
| Independent judge | `src/adapti_guard/evaluation/llm_judge.py` |
| Outcome evaluators | `src/adapti_guard/evaluation/outcome_evaluators.py` |
| Model config | `configs/models.yaml` |
| API smoke script | `scripts/run_exp000_api_smoke.py` |
| Experiment logging | `src/adapti_guard/evaluation/experiment_logging.py` |
| Detector interface | `src/adapti_guard/detector/base.py` |
| Statistics helpers | `src/adapti_guard/evaluation/statistics.py` |
| `DefensePipeline` alias | `src/adapti_guard/core/pipeline.py` (fixes Garak/Inspect import) |

## Commands executed

```bash
.venv/bin/python -m pytest tests/test_target_model.py tests/test_experiment_logging.py tests/test_statistics.py -q
# 12 passed

.venv/bin/python scripts/run_exp000_api_smoke.py
# BLOCKED: OPENROUTER_API_KEY not set (in agent environment)
```

## EXP-000 status

| Field | Value |
|-------|-------|
| Status | **BLOCKED** |
| Run dir | `results/experiment_runs/EXP-000/RUN-20260901-004033-98579d/` |
| Reason | missing_api_key in agent session |

User must run locally:

```bash
cp .env.example .env   # set OPENROUTER_API_KEY
.venv/bin/python scripts/run_exp000_api_smoke.py
```

## Scientific notes

- `MockTargetModel` is test-only; real experiments raise if API key missing
- Primary ASR path: `LLMJudgeOutcomeEvaluator` (not regex `attack_outcome.py`)
- Legacy simulation retained as `LEGACY_SIMULATION_METRIC`

## Next steps

- PASS EXP-000 locally
- Implement EXP-003 end-to-end runner (defense → target → judge)
- Do not start large-scale eval until EXP-000 = PASS
