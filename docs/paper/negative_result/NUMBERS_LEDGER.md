# Number ledger

Each row is recomputed from committed artifacts by `scripts/build_number_ledger.py` (and `scripts/recompute_external_test.py`); `tests/test_manuscript_number_ledger.py` checks that the string appears in `MANUSCRIPT_DRAFT_v1.md`, and `tests/test_external_ledger_raw.py` recomputes the external-test rows from the raw records.

| quantity | string in manuscript | source |
|---|---|---|
| E2 R1 A0 | `66/72` | `figures/fig1_scoring_flip.csv · key R1.A0.successes/n` |
| E2 R1 B3 | `65/72` | `figures/fig1_scoring_flip.csv · key R1.B3.successes/n` |
| E2 R1 CORE | `36/72` | `figures/fig1_scoring_flip.csv · key R1.CORE.successes/n` |
| E2 R1 TOOLDENY | `65/72` | `figures/fig1_scoring_flip.csv · key R1.TOOLDENY.successes/n` |
| E2 R2 A0 | `66/72` | `figures/fig1_scoring_flip.csv · key R2.A0.successes/n` |
| E2 R2 B3 | `65/72` | `figures/fig1_scoring_flip.csv · key R2.B3.successes/n` |
| E2 R2 CORE | `36/72` | `figures/fig1_scoring_flip.csv · key R2.CORE.successes/n` |
| E2 R2 TOOLDENY | `0/72` | `figures/fig1_scoring_flip.csv · key R2.TOOLDENY.successes/n` |
| E2 R3 A0 | `65/71` | `figures/fig1_scoring_flip.csv · key R3.A0.successes/n` |
| E2 R3 B3 | `65/72` | `figures/fig1_scoring_flip.csv · key R3.B3.successes/n` |
| E2 R3 CORE | `36/36` | `figures/fig1_scoring_flip.csv · key R3.CORE.successes/n` |
| E2 R3 TOOLDENY | `0/69` | `figures/fig1_scoring_flip.csv · key R3.TOOLDENY.successes/n` |
| E2 R4 A0 | `30/36` | `figures/fig1_scoring_flip.csv · key R4.A0.successes/n` |
| E2 R4 B3 | `29/36` | `figures/fig1_scoring_flip.csv · key R4.B3.successes/n` |
| E2 R4 CORE | `0/36` | `figures/fig1_scoring_flip.csv · key R4.CORE.successes/n` |
| E2 R4 TOOLDENY | `0/36` | `figures/fig1_scoring_flip.csv · key R4.TOOLDENY.successes/n` |
| E2 episodes | `468` | `experiments/harness_v2/HARNESS_V2_EXPLORATORY_20260930/exploratory_analysis.json · key n_episodes` |
| E2 benign A0 | `45/45` | `experiments/harness_v2/HARNESS_V2_EXPLORATORY_20260930/exploratory_analysis.json · key benign.A0.utility_k/n` |
| E2 benign B3 | `45/45` | `experiments/harness_v2/HARNESS_V2_EXPLORATORY_20260930/exploratory_analysis.json · key benign.B3.utility_k/n` |
| E2 benign CORE | `45/45` | `experiments/harness_v2/HARNESS_V2_EXPLORATORY_20260930/exploratory_analysis.json · key benign.CORE.utility_k/n` |
| E2 benign TOOLDENY | `15/45` | `experiments/harness_v2/HARNESS_V2_EXPLORATORY_20260930/exploratory_analysis.json · key benign.TOOLDENY.utility_k/n` |
| E2 direct-override CORE executed | `0/36` | `experiments/harness_v2/HARNESS_V2_EXPLORATORY_20260930/exploratory_analysis.json · key per_scenario_exec_executed.direct_user_override_v1.CORE` |
| E2 create-record A0 executed | `36/36` | `experiments/harness_v2/HARNESS_V2_EXPLORATORY_20260930/exploratory_analysis.json · key per_scenario_exec_executed.create_record_exfil_v1.A0` |
| E2 B3 paired b10/b01 | `2/1` | `experiments/harness_v2/HARNESS_V2_EXPLORATORY_20260930/exploratory_analysis.json · key paired_vs_A0.B3.b10_arm_wins/b01_A0_wins` |
| E3 B3 undefended executed | `56/167` | `experiments/harness_v2/HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json · key arms.B3.a0_executed/pairs` |
| E3 B3 defended executed | `57/167` | `experiments/harness_v2/HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json · key arms.B3.arm_executed/pairs` |
| E3 B3 b10/b01 | `3/4` | `experiments/harness_v2/HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json · key arms.B3.b10_arm_wins/b01_a0_wins` |
| E3 CORE undefended executed | `57/168` | `experiments/harness_v2/HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json · key arms.CORE.a0_executed/pairs` |
| E3 CORE defended executed | `57/168` | `experiments/harness_v2/HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json · key arms.CORE.arm_executed/pairs` |
| E3 CORE b10/b01 | `4/4` | `experiments/harness_v2/HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json · key arms.CORE.b10_arm_wins/b01_a0_wins` |
| E3 CORE blocked episodes | `0/168` | `experiments/harness_v2/HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json · key arms.CORE.episodes_with_block/episodes` |
| E3 A0 non-delivered episodes | `14 of the 168 undefended episodes` | `docs/research/artifacts/e3_delivery_audit_20261003.json · key a0.non_delivered` |
| E3 A0 carrier tool never ran | `10 of them` | `docs/research/artifacts/e3_delivery_audit_20261003.json · key a0.carrier_tool_never_ran` |
| E3 B3 delivered-only pairs | `157 B3 pairs` | `docs/research/artifacts/e3_delivery_audit_20261003.json · key arms.B3.drop_pairs_where_carrier_tool_never_ran.pairs` |
| E3 B3 delivered-only b10/b01 | `b10/b01 = 3/3` | `docs/research/artifacts/e3_delivery_audit_20261003.json · key arms.B3.drop_pairs_where_carrier_tool_never_ran.b10_a0_only/b01_arm_only` |
| E3 CORE delivered-only pairs | `158 CORE pairs` | `docs/research/artifacts/e3_delivery_audit_20261003.json · key arms.CORE.drop_pairs_where_carrier_tool_never_ran.pairs` |
| E3 CORE delivered-only b10/b01 | `b10/b01 = 4/3` | `docs/research/artifacts/e3_delivery_audit_20261003.json · key arms.CORE.drop_pairs_where_carrier_tool_never_ran.b10_a0_only/b01_arm_only` |
| E3 B3 instance-cluster CI | `−0.024 to +0.036` | `docs/research/artifacts/e3_delivery_audit_20261003.json · key arms.B3.instance_cluster_bootstrap.ci95` |
| E3 CORE instance-cluster CI | `−0.036 to +0.036` | `docs/research/artifacts/e3_delivery_audit_20261003.json · key arms.CORE.instance_cluster_bootstrap.ci95` |
| E3 B3 paired difference | `+0.006` | `docs/research/artifacts/e3_delivery_audit_20261003.json · key arms.B3.instance_cluster_bootstrap.diff` |
| E3 CORE paired difference | `+0.000` | `docs/research/artifacts/e3_delivery_audit_20261003.json · key arms.CORE.instance_cluster_bootstrap.diff` |
| E3 bootstrap resamples | `5000` | `docs/research/artifacts/e3_delivery_audit_20261003.json · key arms.B3.instance_cluster_bootstrap.resamples` |
| E3 bootstrap seed | `20260930` | `docs/research/artifacts/e3_delivery_audit_20261003.json · key arms.B3.instance_cluster_bootstrap.seed` |
| E3 instance clusters | `56` | `docs/research/artifacts/e3_delivery_audit_20261003.json · key arms.B3.instance_cluster_bootstrap.clusters` |
| E3 episodes, both arms | `336` | `docs/research/artifacts/e3_delivery_audit_20261003.json · key arms.B3.episodes + arms.CORE.episodes` |
| E3 susceptibility deepseek | `41/56` | `figures/fig2_susceptibility.csv · key ALL_FAMILIES.deepseek` |
| E3 susceptibility qwen3 | `8/56` | `figures/fig2_susceptibility.csv · key ALL_FAMILIES.qwen3` |
| E3 susceptibility gemma | `8/56` | `figures/fig2_susceptibility.csv · key ALL_FAMILIES.gemma` |
| InjecAgent llama-3.3-70b A0 | `48/120` | `docs/research/artifacts/injecagent_live_analysis_20260930_llama-3.3-70b.json · key arms.A0|first_attacker_tool|ALL` |
| InjecAgent llama-3.3-70b A0 replicate | `50/120` | `docs/research/artifacts/injecagent_live_analysis_20260930_llama-3.3-70b.json · key arms.A0_REP|first_attacker_tool|ALL` |
| InjecAgent llama-3.3-70b NOINJ | `0/119` | `docs/research/artifacts/injecagent_live_analysis_20260930_llama-3.3-70b.json · key arms.NOINJ|first_attacker_tool|ALL` |
| InjecAgent llama-3.3-70b SPOT | `54/120` | `docs/research/artifacts/injecagent_live_analysis_20260930_llama-3.3-70b.json · key arms.SPOT_TOOL|first_attacker_tool|ALL` |
| InjecAgent llama-3.3-70b SPOT minus A0 mean | `+0.050` | `docs/research/artifacts/injecagent_live_analysis_20260930_llama-3.3-70b.json · key cluster_bootstrap_spot_minus_a0.mean_diff` |
| InjecAgent llama-3.3-70b A0-only/SPOT-only | `7/13` | `docs/research/artifacts/injecagent_live_analysis_20260930_llama-3.3-70b.json · key paired_vs_A0.SPOT_TOOL|first_attacker_tool` |
| InjecAgent llama-3.3-70b cluster CI | `[-0.018, 0.122]` | `docs/research/artifacts/injecagent_live_analysis_20260930_llama-3.3-70b.json · key cluster_bootstrap_spot_minus_a0.ci95` |
| §6.3 llama-4-maverick A0 hits | `23/186` | `experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json · key A0.hits/n` |
| §6.3 llama-4-maverick A0 replicate hits | `24/186` | `experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json · key A0_REP.hits/n` |
| §6.3 llama-4-maverick SPOT_TOOL hits | `5/186` | `experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json · key SPOT_TOOL.hits/n` |
| §6.3 llama-4-maverick NOINJ hits | `0/40` | `experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json · key NOINJ.hits/n` |
| §6.3 llama-4-maverick A0 Wilson 95% | `8.4 to 17.9` | `experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json · key A0.wilson95` |
| §6.3 llama-4-maverick SPOT_TOOL minus A0 mean | `-0.097` | `experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json · key SPOT_TOOL-A0.mean` |
| §6.3 llama-4-maverick replicate minus A0 mean | `0.005` | `experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json · key A0_REP-A0.mean` |
| §6.3 llama-4-maverick SPOT_TOOL minus A0 cluster 95% CI | `[-0.145, -0.048]` | `experiments/external/injecagent_registered_20261001/ANALYSIS.json · key meta-llama/llama-4-maverick.SPOT_TOOL_minus_A0.ci95` |
| §6.3 llama-4-maverick SPOT_TOOL minus A0 Bonferroni α/4 CI | `[-0.161, -0.038]` | `experiments/external/injecagent_registered_20261001/ANALYSIS.json · key meta-llama/llama-4-maverick.SPOT_TOOL_minus_A0.ci98.75_holm` |
| §6.3 llama-4-maverick replicate minus A0 cluster 95% CI | `[-0.027, 0.038]` | `experiments/external/injecagent_registered_20261001/ANALYSIS.json · key meta-llama/llama-4-maverick.A0_REP_minus_A0.ci95` |
| §6.3 qwen3.8-flash A0 hits | `23/186` | `experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json · key A0.hits/n` |
| §6.3 qwen3.8-flash A0 replicate hits | `22/186` | `experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json · key A0_REP.hits/n` |
| §6.3 qwen3.8-flash SPOT_TOOL hits | `4/186` | `experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json · key SPOT_TOOL.hits/n` |
| §6.3 qwen3.8-flash NOINJ hits | `0/40` | `experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json · key NOINJ.hits/n` |
| §6.3 qwen3.8-flash A0 Wilson 95% | `8.4 to 17.9` | `experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json · key A0.wilson95` |
| §6.3 qwen3.8-flash SPOT_TOOL minus A0 mean | `-0.102` | `experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json · key SPOT_TOOL-A0.mean` |
| §6.3 qwen3.8-flash replicate minus A0 mean | `-0.005` | `experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json · key A0_REP-A0.mean` |
| §6.3 qwen3.8-flash SPOT_TOOL minus A0 cluster 95% CI | `[-0.156, -0.054]` | `experiments/external/injecagent_registered_20261001/ANALYSIS.json · key qwen/qwen3.8-flash.SPOT_TOOL_minus_A0.ci95` |
| §6.3 qwen3.8-flash SPOT_TOOL minus A0 Bonferroni α/4 CI | `[-0.172, -0.043]` | `experiments/external/injecagent_registered_20261001/ANALYSIS.json · key qwen/qwen3.8-flash.SPOT_TOOL_minus_A0.ci98.75_holm` |
| §6.3 qwen3.8-flash replicate minus A0 cluster 95% CI | `[-0.059, 0.048]` | `experiments/external/injecagent_registered_20261001/ANALYSIS.json · key qwen/qwen3.8-flash.A0_REP_minus_A0.ci95` |
| §6.4 llama-4-maverick InjecAgent A0 | `5/40` | `experiments/external/injecagent_panel_calib_20261001/meta-llama__llama-4-maverick.json · key InjecAgent.A0.hits/scored` |
| §6.4 llama-4-maverick InjecAgent NOINJ | `0/40` | `experiments/external/injecagent_panel_calib_20261001/meta-llama__llama-4-maverick.json · key InjecAgent.NOINJ.hits/scored` |
| §6.4 llama-4-maverick Hard set A0 | `1/68` | `experiments/external/phase2_calibration_20261001/calibration.json · key meta-llama/llama-4-maverick.Hard.A0.hits/scored` |
| §6.4 deepseek/deepseek-v4.1-flash InjecAgent A0 | `0/40` | `experiments/external/injecagent_panel_calib_20261001/deepseek__deepseek-v4.1-flash.json · key InjecAgent.A0.hits/scored` |
| §6.4 deepseek/deepseek-v4.1-flash InjecAgent NOINJ | `0/40` | `experiments/external/injecagent_panel_calib_20261001/deepseek__deepseek-v4.1-flash.json · key InjecAgent.NOINJ.hits/scored` |
| §6.4 deepseek/deepseek-v4.1-flash Hard set A0 | `0/68` | `experiments/external/phase2_calibration_20261001/calibration.json · key deepseek/deepseek-v4.1-flash.Hard.A0.hits/scored` |
| §6.4 openai/gpt-5.6-sol InjecAgent A0 | `0/40` | `experiments/external/injecagent_panel_calib_20261001/openai__gpt-5.6-sol.json · key InjecAgent.A0.hits/scored` |
| §6.4 openai/gpt-5.6-sol InjecAgent NOINJ | `0/40` | `experiments/external/injecagent_panel_calib_20261001/openai__gpt-5.6-sol.json · key InjecAgent.NOINJ.hits/scored` |
| §6.4 openai/gpt-5.6-sol Hard set A0 | `0/20` | `experiments/external/phase2_calibration_20261001/calibration.json · key openai/gpt-5.6-sol.Hard.A0.hits/scored` |
| §6.4 qwen3.8-flash InjecAgent A0 | `6/36` | `experiments/external/injecagent_panel_calib_20261001/qwen__qwen3.8-flash.json · key InjecAgent.A0.hits/scored` |
| §6.4 qwen3.8-flash InjecAgent NOINJ | `0/37` | `experiments/external/injecagent_panel_calib_20261001/qwen__qwen3.8-flash.json · key InjecAgent.NOINJ.hits/scored` |
| §6.4 qwen3.8-flash Hard set A0 | `0/40` | `experiments/external/phase2_calibration_20261001/calibration.json · key qwen/qwen3.8-flash.Hard.A0.hits/scored` |
| §6.4 z-ai/glm-4.7 InjecAgent A0 | `1/40` | `experiments/external/injecagent_panel_calib_20261001/z-ai__glm-4.7.json · key InjecAgent.A0.hits/scored` |
| §6.4 z-ai/glm-4.7 InjecAgent NOINJ | `0/40` | `experiments/external/injecagent_panel_calib_20261001/z-ai__glm-4.7.json · key InjecAgent.NOINJ.hits/scored` |
| §6.4 z-ai/glm-4.7 Hard set A0 | `1/68` | `experiments/external/phase2_calibration_20261001/calibration.json · key z-ai/glm-4.7.Hard.A0.hits/scored` |
| §6.4 llama-4-maverick generated-origin A0 | `0/22` | `experiments/external/phase2_calibration_20261001/calibration.json · key meta-llama/llama-4-maverick.Generated.A0.hits/scored` |
| §6.4 deepseek/deepseek-v4.1-flash generated-origin A0 | `0/22` | `experiments/external/phase2_calibration_20261001/calibration.json · key deepseek/deepseek-v4.1-flash.Generated.A0.hits/scored` |
| §6.4 openai/gpt-5.6-sol generated-origin A0 | `1/20` | `experiments/external/phase2_calibration_20261001/calibration.json · key openai/gpt-5.6-sol.Generated.A0.hits/scored` |
| §6.4 qwen3.8-flash generated-origin A0 | `3/15` | `experiments/external/phase2_calibration_20261001/calibration.json · key qwen/qwen3.8-flash.Generated.A0.hits/scored` |
| §6.4 qwen3.8-flash generated-origin provider errors | `7 provider errors` | `experiments/external/phase2_calibration_20261001/calibration.json · key qwen/qwen3.8-flash.Generated.A0.errors` |
| §6.4 qwen3.8-flash Hard set provider errors | `28 provider errors` | `experiments/external/phase2_calibration_20261001/calibration.json · key qwen/qwen3.8-flash.Hard.A0.errors` |
| §6.4 qwen3.8-flash InjecAgent A0 provider errors | `4 provider errors` | `experiments/external/injecagent_panel_calib_20261001/qwen__qwen3.8-flash.json · key InjecAgent.A0.errors` |
| §6.4 z-ai/glm-4.7 generated-origin A0 | `1/22` | `experiments/external/phase2_calibration_20261001/calibration.json · key z-ai/glm-4.7.Generated.A0.hits/scored` |
| §6.4 Clopper-Pearson upper bound, 0 of 40 | `8.8%` | `experiments/external/injecagent_panel_calib_20261001/openai__gpt-5.6-sol.json · key InjecAgent.A0.scored` |
| §6.4 Clopper-Pearson upper bound, 0 of 68 | `5.3%` | `experiments/external/phase2_calibration_20261001/calibration.json · key deepseek/deepseek-v4.1-flash.Hard.A0.scored` |
| §6.3 llama-4-maverick cases per arm | `186` | `experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json · key A0.n` |
| §6.3 llama-4-maverick bootstrap clusters | `62` | `experiments/external/injecagent_registered_20261001/ANALYSIS.json · key meta-llama/llama-4-maverick.A0_REP_minus_A0.clusters` |
| §6.3 qwen3.8-flash cases per arm | `186` | `experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json · key A0.n` |
| §6.3 qwen3.8-flash bootstrap clusters | `62` | `experiments/external/injecagent_registered_20261001/ANALYSIS.json · key qwen/qwen3.8-flash.A0_REP_minus_A0.clusters` |
