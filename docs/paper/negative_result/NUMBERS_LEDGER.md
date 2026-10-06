# Number ledger

Each row is recomputed from committed artifacts by `scripts/build_number_ledger.py`; `tests/test_manuscript_number_ledger.py` checks that the string appears in `MANUSCRIPT_DRAFT_v1.md`.

| quantity | string in manuscript | source |
|---|---|---|
| Track A B0 judge | `58/61` | `artifacts/tracks_ab_deterministic_rescoring_20260930.json` |
| Track A B0 executed | `40/61` | `artifacts/tracks_ab_deterministic_rescoring_20260930.json` |
| Track A VNEXT judge | `53/61` | `artifacts/tracks_ab_deterministic_rescoring_20260930.json` |
| Track A VNEXT executed | `36/61` | `artifacts/tracks_ab_deterministic_rescoring_20260930.json` |
| Track B CORE judge | `34/61` | `artifacts/tracks_ab_deterministic_rescoring_20260930.json` |
| Track B CORE executed | `6/61` | `artifacts/tracks_ab_deterministic_rescoring_20260930.json` |
| Track B executed b10 | `55/0` | `artifacts/tracks_ab_deterministic_rescoring_20260930.json` |
| Track B executed delta | `0.9016` | `artifacts/tracks_ab_deterministic_rescoring_20260930.json` |
| Track B judge delta | `0.4426` | `artifacts/tracks_ab_deterministic_rescoring_20260930.json` |
| Track B CORE utility executed | `49/61` | `artifacts/tracks_ab_deterministic_rescoring_20260930.json` |
| Track B CORE tool-required executed | `30/40` | `artifacts/tracks_ab_deterministic_rescoring_20260930.json` |
| E2 R1 TOOLDENY proposed | `65/72` | `figures/fig1_scoring_flip.csv` |
| E2 R2 TOOLDENY executed | `0/72` | `figures/fig1_scoring_flip.csv` |
| E2 R2 A0 | `66/72` | `figures/fig1_scoring_flip.csv` |
| E2 R2 CORE | `36/72` | `figures/fig1_scoring_flip.csv` |
| E2 R3 CORE | `36/36` | `figures/fig1_scoring_flip.csv` |
| E2 R4 A0 | `30/36` | `figures/fig1_scoring_flip.csv` |
| E2 R4 B3 | `29/36` | `figures/fig1_scoring_flip.csv` |
| E3 B3 pairs | `167 pairs` | `HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json` |
| E3 B3 b10/b01 | `3/4` | `HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json` |
| E3 CORE pairs | `168 pairs` | `HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json` |
| E3 CORE b10/b01 | `4/4` | `HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json` |
| E3 A0 non-delivered episodes | `14 of the 168 undefended episodes` | `artifacts/e3_delivery_audit_20261003.json` |
| E3 A0 carrier tool never ran | `10 of them` | `artifacts/e3_delivery_audit_20261003.json` |
| E3 B3 delivered-only pairs | `157 B3 pairs` | `artifacts/e3_delivery_audit_20261003.json` |
| E3 B3 delivered-only b10/b01 | `b10/b01 = 3/3` | `artifacts/e3_delivery_audit_20261003.json` |
| E3 CORE delivered-only pairs | `158 CORE pairs` | `artifacts/e3_delivery_audit_20261003.json` |
| E3 CORE delivered-only b10/b01 | `b10/b01 = 4/3` | `artifacts/e3_delivery_audit_20261003.json` |
| E3 B3 instance-cluster CI | `−0.024 to +0.036` | `artifacts/e3_delivery_audit_20261003.json` |
| E3 CORE instance-cluster CI | `−0.036 to +0.036` | `artifacts/e3_delivery_audit_20261003.json` |
| E3 B3 minimum detectable reduction | `7.7 percentage points (B3)` | `artifacts/e3_power_sensitivity_20261003.json` |
| E3 CORE minimum detectable reduction | `7.9 percentage points (CORE)` | `artifacts/e3_power_sensitivity_20261003.json` |
| E3 power at 10% relative reduction | `25% (B3) and 25% (CORE) power at a 10% relative reduction` | `artifacts/e3_power_sensitivity_20261003.json` |
| E3 power at 25% relative reduction | `86% (B3) and 85% (CORE) at a 25% relative reduction` | `artifacts/e3_power_sensitivity_20261003.json` |
| E3 B3 family-cluster CI | `−4.7 to +3.5 points (B3)` | `artifacts/e3_power_sensitivity_20261003.json` |
| E3 CORE family-cluster CI | `−3.1 to +3.1 points (CORE)` | `artifacts/e3_power_sensitivity_20261003.json` |
| E3 B3 text-claim endpoint | `B3 101 vs 106, b10/b01 = 5/10` | `artifacts/e3_power_sensitivity_20261003.json` |
| E3 CORE text-claim endpoint | `CORE 102 vs 107, b10/b01 = 5/10` | `artifacts/e3_power_sensitivity_20261003.json` |
| E3 B3 cluster MDE80 by tau | `0.090, 0.113, 0.162 and 0.215 (B3)` | `artifacts/e3_cluster_power_20261006.json` |
| E3 CORE cluster MDE80 by tau | `0.092, 0.114, 0.163 and 0.220 (CORE)` | `artifacts/e3_cluster_power_20261006.json` |
| E3 B3 cluster power at 0.08 | `0.747, 0.564, 0.290 and 0.184 (B3)` | `artifacts/e3_cluster_power_20261006.json` |
| E1 kappa interval A B0 | `0.00 to 0.38` | `artifacts/e1_interval_estimates_20261006.json` |
| E1 kappa interval A VNEXT | `0.16 to 0.56` | `artifacts/e1_interval_estimates_20261006.json` |
| E1 kappa interval B CORE | `0.05 to 0.30` | `artifacts/e1_interval_estimates_20261006.json` |
| E1 B executed effect interval | `0.82 to 0.97` | `artifacts/e1_interval_estimates_20261006.json` |
| E1 B judge effect interval | `0.31 to 0.57` | `artifacts/e1_interval_estimates_20261006.json` |
| E3 susceptibility deepseek | `41/56` | `figures/fig2_susceptibility.csv` |
| E3 susceptibility qwen3 | `8/56` | `figures/fig2_susceptibility.csv` |
| E3 susceptibility gemma | `8/56` | `figures/fig2_susceptibility.csv` |
| MT1 SPOTLIGHT judge b10/b01 | `39/6` | `artifacts/mt1_second_dataset_rules_20260930.json` |
| SPOT_ctx indirect judge | `1 of 18` | `artifacts/spotlight_ctx_check_20260930.json` |
| SPOT_ctx direct judge | `22 to 22` | `artifacts/spotlight_ctx_check_20260930.json` |
| SPOT_prompt direct judge | `22 to 6` | `artifacts/spotlight_ctx_check_20260930.json` |
| InjecAgent qwen-2.5-7b A0 | `24/120` | `artifacts/injecagent_live_analysis_20260930.json` |
| InjecAgent qwen-2.5-7b SPOT A0-only/SPOT-only | `10/12` | `artifacts/injecagent_live_analysis_20260930.json` |
| InjecAgent qwen-2.5-7b cluster CI | `[-0.057, 0.086]` | `artifacts/injecagent_live_analysis_20260930.json` |
| InjecAgent llama-3.1-8b A0 | `50/120` | `artifacts/injecagent_live_analysis_20260930_llama-3.1-8b.json` |
| InjecAgent llama-3.1-8b SPOT A0-only/SPOT-only | `26/9` | `artifacts/injecagent_live_analysis_20260930_llama-3.1-8b.json` |
| InjecAgent llama-3.1-8b cluster CI | `[-0.237, -0.056]` | `artifacts/injecagent_live_analysis_20260930_llama-3.1-8b.json` |
| InjecAgent llama-3.3-70b A0 | `48/120` | `artifacts/injecagent_live_analysis_20260930_llama-3.3-70b.json` |
| InjecAgent llama-3.3-70b SPOT A0-only/SPOT-only | `7/13` | `artifacts/injecagent_live_analysis_20260930_llama-3.3-70b.json` |
| InjecAgent llama-3.3-70b cluster CI | `[-0.018, 0.122]` | `artifacts/injecagent_live_analysis_20260930_llama-3.3-70b.json` |
| InjecAgent mistral-small-3.2-24b A0 | `5/120` | `artifacts/injecagent_live_analysis_20260930_mistral-small-3.2-24b.json` |
| InjecAgent mistral-small-3.2-24b SPOT A0-only/SPOT-only | `1/1` | `artifacts/injecagent_live_analysis_20260930_mistral-small-3.2-24b.json` |
| InjecAgent mistral-small-3.2-24b cluster CI | `[-0.025, 0.024]` | `artifacts/injecagent_live_analysis_20260930_mistral-small-3.2-24b.json` |
