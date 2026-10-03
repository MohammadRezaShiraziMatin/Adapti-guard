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
