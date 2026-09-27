# .

- label: pilot/diagnostic — NOT paper Results / NOT AUDIT=VALID
- created: 2026-09-24T22:15:59.838165Z
- pack: datasets/frozen/layer_a_v2 attack_n=20 benign_n=20 seed=42
- target_config: target_1 judge_config: judge_fallback backend: auto
- preflight worst_case_requests: 160 worst_case_usd_est: 0.000000 cap: 2.0
- preflight: PASS
- order: B0 all episodes then B1 all episodes


## completed 2026-09-24T22:20:39.598121Z
- ledger: {"max_requests": 700, "max_usd": 2.0, "requests_used": 156, "spent_usd": 0.055673999999999994, "estimated_cost": 0.055673999999999994, "hard_stop": true}
- comparison: b0_b1_comparison.json
