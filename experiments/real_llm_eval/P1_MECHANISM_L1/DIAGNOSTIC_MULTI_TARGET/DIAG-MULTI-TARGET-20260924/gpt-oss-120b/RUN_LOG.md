# .

- label: pilot/diagnostic — NOT paper Results / NOT AUDIT=VALID
- created: 2026-09-24T22:29:33.733016Z
- pack: datasets/frozen/layer_a_v2 attack_n=20 benign_n=20 seed=42
- target_config: target_gpt_oss_or judge_config: judge_fallback backend: auto
- preflight worst_case_requests: 160 worst_case_usd_est: 0.000000 cap: 2.0
- preflight: PASS
- order: B0 all episodes then B1 all episodes


## completed 2026-09-24T22:51:30.337042Z
- ledger: {"max_requests": 700, "max_usd": 2.0, "requests_used": 477, "spent_usd": 0.16951400000000003, "estimated_cost": 0.16951400000000003, "hard_stop": true}
- comparison: b0_b1_comparison.json
