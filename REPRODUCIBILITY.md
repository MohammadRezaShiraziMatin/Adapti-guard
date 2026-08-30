# ADAPTI-GUARD Reproducibility

## Environment
- Python: 3.12.10 (tags/v3.12.10:0cc8128, Apr  8 2025, 12:21:36) [MSC v.1943 64 bit (AMD64)]
- Platform: Windows-11-10.0.26200-SP0
- Git commit: 68e66defb5fed14337ed33ba7a6217d499b2176c

## Primary Bundle
- Harmonized evaluation: `results/phase8/q1_harmonized_v1/`
- Runner version: `harmonized_v1.0.0`
- Metric version: `metrics.py@v1`
- Attack stream: `results/common_attack_stream.json`
- Stream SHA256: `d101f94d97e0a29e8b9f9cc4dacb92472e29cd9af403114cb09b8f1d50a06c47`

## Configuration
- Episodes: 100 (75 attack / 25 legitimate, A A A L schedule)
- Thresholds: attack=2, legitimate=2
- Seed identifier: 42 (deterministic given frozen stream)

## Entry Points
```bash
cd 01_BASE_Q1/adapti_guard
python scripts/run_q1_harmonized_v1.py
python scripts/run_q1_sensitivity_v1.py
python scripts/run_q1_deescalation_diagnostic_v1.py
```

## Sensitivity Artifacts
- Threshold: `results/phase8/q1_threshold_sensitivity_v1/`
- Workload: `results/phase8/q1_workload_sensitivity_v1/`
- Final validation: `results/phase8/q1_final_validation_v1/`

## Frozen (do not modify)
- Phase 7, 8A, 8B artifacts
- `common_attack_stream.json`
