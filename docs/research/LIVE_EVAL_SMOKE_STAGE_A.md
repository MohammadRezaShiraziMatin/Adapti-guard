# Live eval Smoke — Stage A (contract only)

**NON-PRIMARY · LIMITED · AUDITABLE · BUDGET-CAPPED**

Per `LIVE_EVALUATION_GATE.md` Stage A. **Not executed** until `LIVE_AUTHORIZED`.

| Field | Contract |
| --- | --- |
| Output root | `experiments/real_llm_eval/P1_MECHANISM_L1/<run_id>/` |
| Artifacts | `run_manifest.json`, `authorization_snapshot.json`, `config_snapshot.yaml`, `raw/`, `derived/`, `logs/`, `audit/` (as needed) |
| API | Blocked unless `api_spend_permitted` and human sign-off |

Preflight (no API): `python3 scripts/live_eval_preflight.py`
