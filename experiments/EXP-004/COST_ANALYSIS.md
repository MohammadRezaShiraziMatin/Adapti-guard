# EXP-004 Cost Analysis

**Date:** 2026-09-02  
**Purpose:** Budget planning only — not experimental evidence.

## Pricing source

OpenRouter public model catalog API (`https://openrouter.ai/api/v1/models`), fetched 2026-09-02.  
Prices are **USD per token** as returned by OpenRouter (list/provider rates).

| Model | Input / token | Output / token |
|-------|---------------:|---------------:|
| `openai/gpt-4o-mini` | $0.00000015 | $0.00000060 |
| `qwen/qwen3-30b-a3b` | $0.00000012 | $0.00000050 |
| `deepseek/deepseek-chat-v3-0324` | $0.00000025 | $0.00000100 |
| `anthropic/claude-sonnet-4` (judge) | $0.00000300 | $0.00001500 |
| `openai/gpt-4o` (fallback, not used in estimate) | $0.00000250 | $0.00001000 |

OpenRouter may apply a separate credit-purchase platform fee (currently 5.5% on pay-as-you-go).  
Figures below are **inference list-price only**.

## Empirical token assumptions (from PHASE2_7_PILOT)

Pilot stored **target-side tokens only** per evaluation row (`input_tokens` / `output_tokens`).

| Stat | Target input | Target output | Total (target only) |
|------|-------------:|----------------:|--------------------:|
| Mean (n=30 evals) | 621.8 | 161.9 | 783.7 |
| p90 | 1775 | 292 | 1982 |
| Max | 1919 | 512 | 2129 |

**Important:** Judge token usage is **not** recorded in pilot prediction rows.  
Judge cost is estimated separately (see below).

### Judge token estimates (not measured in pilot)

| Scenario | Judge input tokens | Judge output tokens | Rationale |
|----------|-------------------:|--------------------:|-----------|
| Mean | 1234 | 100 | target mean in + out + 450 JSON/system overhead |
| Conservative | 2667 | 150 | pilot p90 target in + p90 target out + 600 overhead |

## Evaluation counts

Each design uses:

- `evaluations = n_samples × 3 models × 2 baselines`
- Each evaluation ≈ **1 target call + 1 judge call** (if not blocked)
- `API calls ≈ 2 × evaluations`

| n_samples | Evaluations | Approx. API calls |
|----------:|------------:|------------------:|
| 100 | 600 | 1200 |
| 150 | 900 | 1800 |
| 200 | 1200 | 2400 |
| 500 | 3000 | 6000 |

Blocked B6 episodes reduce calls; pilot had **0 blocks** — estimates assume full call volume.

## Estimated cost (USD)

### Mean judge-token scenario

| n | Target cost | Judge cost | **Total** | +15% retry contingency |
|--:|------------:|-----------:|----------:|-----------------------:|
| 100 | $0.13 | $3.12 | **$3.25** | $3.74 |
| 150 | $0.20 | $4.68 | **$4.88** | $5.61 |
| 200 | $0.27 | $6.24 | **$6.51** | $7.48 |
| 500 | $0.66 | $15.61 | **$16.27** | $18.71 |

### Conservative judge-token scenario

| n | Target cost | Judge cost | **Total** | +15% retry contingency |
|--:|------------:|-----------:|----------:|-----------------------:|
| 100 | $0.13 | $6.15 | **$6.28** | $7.23 |
| 150 | $0.20 | $9.23 | **$9.42** | $10.84 |
| 200 | $0.27 | $12.30 | **$12.57** | $14.45 |
| 500 | $0.66 | $30.75 | **$31.42** | $36.13 |

**Dominant cost driver:** Claude Sonnet 4 judge (~95% of total in mean scenario).

## Recommended budget line

For **n=150** (approved default):

- Plan **$6–11 USD** inference (mean–conservative + retry)
- Add OpenRouter platform/credit fees separately if applicable
- Monitor actual `usage.cost` during run; pipeline currently stores token counts for **target only**

## Limitations

1. Pilot used `model_a` only — token profile applied to all three targets.
2. Judge tokens are **estimated**, not measured in current artifacts.
3. Fallback judge (`openai/gpt-4o`) not included unless primary judge fails.
4. Does not include prior smoke-test spend (~$0.0002).
