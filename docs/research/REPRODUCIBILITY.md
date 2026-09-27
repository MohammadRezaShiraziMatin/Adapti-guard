# Reproducibility contract (Phase 3)

Protocol-only — full environment capture is Phase 4.

## Lock fields (per run / evidence record)

| Field | Source |
| --- | --- |
| `repository_revision` | `git` HEAD at run time |
| `environment` | OS / image id (Phase 4) |
| `dependencies` | `requirements*.txt` / lockfile hash |
| `configuration` | Full run config JSON |
| `config_hash` | Hash of normalized config |
| `target_model_id` | Provider + model string |
| `judge_id` | Must differ on confirmatory live |
| `dataset_id` / `dataset_hash` | Frozen manifest SHA |
| `seed` / `trial` | Design matrix |
| `run_id` | Unique run identifier |
| `timestamp` | ISO8601 UTC |
| `provider` | API provider name |
| `budget_metadata` | Authorized cap / spend log (Phase 7) |
| `raw_evidence_path` | Traces, AUDIT, JSONL |
| `derived_evidence_path` | Metrics tables, stats outputs |
| `failure_state` | See `EXPERIMENT_PROTOCOL.md` §3 |

## Immutable artifacts (do not regenerate)

| Artifact | Location |
| --- | --- |
| Frozen P1 pack | `datasets/frozen/p1_mechanism_v1.0.0/manifest.json` |
| Track A/B AUDITs | `experiments/real_llm_eval/**/AUDIT.md` |
| Q1 findings repro | `docs/paper/q1_findings/REPRODUCIBILITY.md` |

## Offline extension replay

Unit tests under `tests/test_*episode*.py` — `evidence_type: offline_fixture`, not empirical study results.
