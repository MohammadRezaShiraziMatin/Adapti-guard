# Dataset Analysis — benchmark_v2

**Status:** PARTIAL (EXP-001)  
**Last updated:** 2026-09-01

## Summary

| Field | Value |
|-------|-------|
| Dataset path | `datasets/benchmark_v2/` |
| Publication ready | **false** |
| Total samples (deduped) | 11 |
| Train / validation / test | 0 / 0 / 11 |
| Label 0 (benign) | 3 |
| Label 1 (attack) | 8 |

## Source availability

| Source | Status |
|--------|--------|
| NotInject (train) | DATASET_UNAVAILABLE |
| NotInject (valid) | DATASET_UNAVAILABLE |
| BIPIA | DATASET_UNAVAILABLE |
| InjecAgent | DATASET_UNAVAILABLE |
| TensorTrust | DATASET_UNAVAILABLE |
| PIArena | DATASET_UNAVAILABLE |
| AgentHarm | DATASET_UNAVAILABLE |
| AgentDojo | DATASET_UNAVAILABLE |
| internal_smoke | GENERATED (53 rows → 11 after dedup) — **SMOKE ONLY** |

## Deduplication (`dedup_report.json`)

| Metric | Value |
|--------|-------|
| Method | exact_normalized_prompt |
| Before | 53 |
| After | 11 |
| Removed | 42 |
| Duplicate rate | 79.2% |

## Category distribution

| Category | Count |
|----------|------:|
| direct_injection | 2 |
| indirect_injection | 2 |
| context_manipulation | 2 |
| tool_output_injection | 2 |
| benign | 3 |

## SHA256

- `test.jsonl`: `fc2a232c30df1bb7c2794b10aa4301092496623c10f209f1acdf8bafdf51df82`

## Leakage / splits

- No train or validation split populated — external datasets not present in clone.
- Internal smoke subset is test-only and explicitly marked not for publication.

## Preprocessing

1. Load from configured source paths (`scripts/build_benchmark_v2.py`)
2. Normalize to benchmark_v2 schema
3. Exact normalized-text deduplication
4. Write JSONL splits

## Next steps (required for Q1)

1. Acquire NotInject, BIPIA, and at least one agent benchmark with documented licenses
2. Re-run `python scripts/build_benchmark_v2.py`
3. Verify `publication_ready: true` in manifest
4. Complete `docs/DATASET_BALANCE_REPORT.md`
