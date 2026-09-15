# Phase 1 Report — Dataset Validation

**Date:** 2026-09-01  
**Status:** PARTIAL

## What was implemented

- `datasets/benchmark_v2/schema.json`
- `scripts/build_benchmark_v2.py` — loads external sources when present; no fabrication
- `datasets/benchmark_v2/manifest.json`, `dedup_report.json`, `test.jsonl` (generated)
- `docs/DATASET_ANALYSIS.md`
- `docs/DATASET_BALANCE_REPORT.md`

## Commands executed

```bash
python3 scripts/build_benchmark_v2.py
```

## Results

| Metric | Value |
|--------|-------|
| EXP-001 status | **PARTIAL** |
| External datasets | All DATASET_UNAVAILABLE in clone |
| Deduped samples | 11 (smoke only) |
| publication_ready | false |

## Tests

- Manifest and dedup report written successfully

## Limitations

- NotInject, BIPIA, InjecAgent, etc. not present under `dataset/` or `BIPIA/`
- Smoke subset is explicitly **not** publication evidence

## Next steps

- Acquire and place datasets per `scripts/build_dataset_inventory.py` paths
- Re-run EXP-001 until `publication_ready: true`
