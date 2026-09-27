# MT2 protocol (confirmatory panel — config only)

**Status:** contracts registered; **no live eval** until owner authorization. Historical MT1/DIAG/Track artifacts unchanged.

## Panels

| Role | Config contract | Model registry |
|------|-----------------|----------------|
| Target panel (6) | `configs/mt2_panel.yaml` → `target_panel.keys` | `configs/models_mt2.yaml` `mt2_target_*` |
| Judge panel | `configs/mt2_panel.yaml` → `judge_panel` | `configs/models_mt2.yaml` `mt2_judge_*` |
| Validation | `adapti_guard.evaluation.mt2_panel.validate_mt2_panel` | offline only |

OpenRouter IDs verified **2026-09-25** via `GET https://openrouter.ai/api/v1/models` (metadata only).

## Target panel (6)

| Config key | OpenRouter id | Provider | Context | $/M in | $/M out |
|------------|---------------|----------|--------:|-------:|--------:|
| `mt2_target_qwen3_30b_a3b` | `qwen/qwen3-30b-a3b` | openrouter | 131072 | 0.12 | 0.50 |
| `mt2_target_gemma_4_31b_it` | `google/gemma-4-31b-it` | openrouter | 262144 | 0.09 | 0.34 |
| `mt2_target_mistral_small_3_2_24b` | `mistralai/mistral-small-3.2-24b-instruct` | openrouter | 256000 | 0.094 | 0.25 |
| `mt2_target_llama_3_3_70b` | `meta-llama/llama-3.3-70b-instruct` | openrouter | 131072 | 0.10 | 0.32 |
| `mt2_target_openai_gpt_4o` | `openai/gpt-4o` | openrouter | 128000 | 2.50 | 10.00 |
| `mt2_target_anthropic_claude_sonnet_4` | `anthropic/claude-sonnet-4` | openrouter | 200000 | 3.00 | 15.00 |

## Judge panel

| Role | Config key | OpenRouter id | When |
|------|------------|---------------|------|
| Primary (default) | `mt2_judge_primary` | `openai/gpt-oss-120b` | All targets **except** OpenAI closed target |
| Secondary (default) | `mt2_judge_secondary` | `deepseek/deepseek-chat-v3-0324` | Paired with default primary |
| Primary (OpenAI-target substitute) | `mt2_judge_primary_openai_target_substitute` | `deepseek/deepseek-chat-v3-0324` | `mt2_target_openai_gpt_4o` only |
| Secondary (OpenAI-target substitute) | `mt2_judge_secondary_openai_target_substitute` | `amazon/nova-lite-v1` | `mt2_target_openai_gpt_4o` only |

**Conflict rule:** `gpt-oss-120b` is OpenAI-family; it must **not** judge `openai/gpt-4o` episodes. Resolver: `resolve_mt2_judges_for_target()`.

Pricing ($/M): primary OSS 0.15 / 0.60; DeepSeek 0.25 / 1.00; Nova Lite 0.06 / 0.24.

## Historical keys

MT1/DIAG/VNEXT keys (`target_2`, `judge_fallback`, `model_a`, …) remain in `configs/models.yaml` (VNEXT SHA unchanged). MT2 keys live only in `configs/models_mt2.yaml`.
