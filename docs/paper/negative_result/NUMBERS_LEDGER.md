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
| §6.6 llama-4-maverick A0 hits | `23/186` | `experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json · key A0.hits/n` |
| §6.6 llama-4-maverick A0 replicate hits | `24/186` | `experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json · key A0_REP.hits/n` |
| §6.6 llama-4-maverick SPOT_TOOL hits | `5/186` | `experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json · key SPOT_TOOL.hits/n` |
| §6.6 llama-4-maverick NOINJ hits | `0/40` | `experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json · key NOINJ.hits/n` |
| §6.6 llama-4-maverick A0 Wilson 95% | `8.4 to 17.9` | `experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json · key A0.wilson95` |
| §6.6 llama-4-maverick SPOT_TOOL minus A0 mean | `-0.097` | `experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json · key SPOT_TOOL-A0.mean` |
| §6.6 llama-4-maverick replicate minus A0 mean | `0.005` | `experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json · key A0_REP-A0.mean` |
| §6.6 llama-4-maverick SPOT_TOOL minus A0 cluster 95% CI | `[-0.145, -0.048]` | `experiments/external/injecagent_registered_20261001/ANALYSIS.json · key meta-llama/llama-4-maverick.SPOT_TOOL_minus_A0.ci95` |
| §6.6 llama-4-maverick SPOT_TOOL minus A0 Bonferroni α/4 CI | `[-0.161, -0.038]` | `experiments/external/injecagent_registered_20261001/ANALYSIS.json · key meta-llama/llama-4-maverick.SPOT_TOOL_minus_A0.ci98.75_holm` |
| §6.6 llama-4-maverick replicate minus A0 cluster 95% CI | `[-0.027, 0.038]` | `experiments/external/injecagent_registered_20261001/ANALYSIS.json · key meta-llama/llama-4-maverick.A0_REP_minus_A0.ci95` |
| §6.6 qwen3.8-flash A0 hits | `23/186` | `experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json · key A0.hits/n` |
| §6.6 qwen3.8-flash A0 replicate hits | `22/186` | `experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json · key A0_REP.hits/n` |
| §6.6 qwen3.8-flash SPOT_TOOL hits | `4/186` | `experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json · key SPOT_TOOL.hits/n` |
| §6.6 qwen3.8-flash NOINJ hits | `0/40` | `experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json · key NOINJ.hits/n` |
| §6.6 qwen3.8-flash A0 Wilson 95% | `8.4 to 17.9` | `experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json · key A0.wilson95` |
| §6.6 qwen3.8-flash SPOT_TOOL minus A0 mean | `-0.102` | `experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json · key SPOT_TOOL-A0.mean` |
| §6.6 qwen3.8-flash replicate minus A0 mean | `-0.005` | `experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json · key A0_REP-A0.mean` |
| §6.6 qwen3.8-flash SPOT_TOOL minus A0 cluster 95% CI | `[-0.156, -0.054]` | `experiments/external/injecagent_registered_20261001/ANALYSIS.json · key qwen/qwen3.8-flash.SPOT_TOOL_minus_A0.ci95` |
| §6.6 qwen3.8-flash SPOT_TOOL minus A0 Bonferroni α/4 CI | `[-0.172, -0.043]` | `experiments/external/injecagent_registered_20261001/ANALYSIS.json · key qwen/qwen3.8-flash.SPOT_TOOL_minus_A0.ci98.75_holm` |
| §6.6 qwen3.8-flash replicate minus A0 cluster 95% CI | `[-0.059, 0.048]` | `experiments/external/injecagent_registered_20261001/ANALYSIS.json · key qwen/qwen3.8-flash.A0_REP_minus_A0.ci95` |
| §6.7 llama-4-maverick InjecAgent A0 | `5/40` | `experiments/external/injecagent_panel_calib_20261001/meta-llama__llama-4-maverick.json · key InjecAgent.A0.hits/scored` |
| §6.7 llama-4-maverick InjecAgent NOINJ | `0/40` | `experiments/external/injecagent_panel_calib_20261001/meta-llama__llama-4-maverick.json · key InjecAgent.NOINJ.hits/scored` |
| §6.7 llama-4-maverick Hard set A0 | `1/68` | `experiments/external/phase2_calibration_20261001/calibration.json · key meta-llama/llama-4-maverick.Hard.A0.hits/scored` |
| §6.7 deepseek/deepseek-v4.1-flash InjecAgent A0 | `0/40` | `experiments/external/injecagent_panel_calib_20261001/deepseek__deepseek-v4.1-flash.json · key InjecAgent.A0.hits/scored` |
| §6.7 deepseek/deepseek-v4.1-flash InjecAgent NOINJ | `0/40` | `experiments/external/injecagent_panel_calib_20261001/deepseek__deepseek-v4.1-flash.json · key InjecAgent.NOINJ.hits/scored` |
| §6.7 deepseek/deepseek-v4.1-flash Hard set A0 | `0/68` | `experiments/external/phase2_calibration_20261001/calibration.json · key deepseek/deepseek-v4.1-flash.Hard.A0.hits/scored` |
| §6.7 openai/gpt-5.6-sol InjecAgent A0 | `0/40` | `experiments/external/injecagent_panel_calib_20261001/openai__gpt-5.6-sol.json · key InjecAgent.A0.hits/scored` |
| §6.7 openai/gpt-5.6-sol InjecAgent NOINJ | `0/40` | `experiments/external/injecagent_panel_calib_20261001/openai__gpt-5.6-sol.json · key InjecAgent.NOINJ.hits/scored` |
| §6.7 openai/gpt-5.6-sol Hard set A0 | `0/20` | `experiments/external/phase2_calibration_20261001/calibration.json · key openai/gpt-5.6-sol.Hard.A0.hits/scored` |
| §6.7 qwen3.8-flash InjecAgent A0 | `6/36` | `experiments/external/injecagent_panel_calib_20261001/qwen__qwen3.8-flash.json · key InjecAgent.A0.hits/scored` |
| §6.7 qwen3.8-flash InjecAgent NOINJ | `0/37` | `experiments/external/injecagent_panel_calib_20261001/qwen__qwen3.8-flash.json · key InjecAgent.NOINJ.hits/scored` |
| §6.7 qwen3.8-flash Hard set A0 | `0/40` | `experiments/external/phase2_calibration_20261001/calibration.json · key qwen/qwen3.8-flash.Hard.A0.hits/scored` |
| §6.7 z-ai/glm-4.7 InjecAgent A0 | `1/40` | `experiments/external/injecagent_panel_calib_20261001/z-ai__glm-4.7.json · key InjecAgent.A0.hits/scored` |
| §6.7 z-ai/glm-4.7 InjecAgent NOINJ | `0/40` | `experiments/external/injecagent_panel_calib_20261001/z-ai__glm-4.7.json · key InjecAgent.NOINJ.hits/scored` |
| §6.7 z-ai/glm-4.7 Hard set A0 | `1/68` | `experiments/external/phase2_calibration_20261001/calibration.json · key z-ai/glm-4.7.Hard.A0.hits/scored` |
| §6.7 Clopper-Pearson upper bound, 0 of 40 | `8.8%` | `experiments/external/injecagent_panel_calib_20261001/openai__gpt-5.6-sol.json · key InjecAgent.A0.scored` |
| §6.7 Clopper-Pearson upper bound, 0 of 68 | `5.3%` | `experiments/external/phase2_calibration_20261001/calibration.json · key deepseek/deepseek-v4.1-flash.Hard.A0.scored` |
