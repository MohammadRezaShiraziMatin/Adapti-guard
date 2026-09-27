# DIAG-B0-B1-LAYER-A-V2-20260924

- label: pilot/diagnostic — NOT paper Results / NOT AUDIT=VALID
- created: 2026-09-24T19:39:20.804204Z
- pack: datasets/frozen/layer_a_v2 attack_n=20 benign_n=20 seed=42
- target_config: target_2 judge_config: judge_fallback backend: auto
- preflight worst_case_requests: 160 worst_case_usd_est: 0.062400 cap: 2.0
- preflight: PASS
- order: B0 all episodes then B1 all episodes


## completed 2026-09-24T19:44:08.769590Z
- ledger: {"max_requests": 180, "max_usd": 2.0, "requests_used": 156, "spent_usd": 0.05562599999999999, "estimated_cost": 0.05562599999999999, "hard_stop": true}
- comparison: b0_b1_comparison.json
