# Amendment 4 — request persistence, reasoning-off policy, Qwen3 pricing (zero chat API)

## Reasoning disable on DeepInfra (qwen/qwen3-30b-a3b)

**Source:** `GET /api/v1/models/qwen/qwen3-30b-a3b/endpoints` → DeepInfra row `supported_parameters` (verbatim excerpt in `AMENDMENT4_REASONING_METADATA.json`):

```json
["reasoning", "include_reasoning", "response_format", "max_tokens", ...]
```

**OpenRouter unified controls** (docs): `reasoning.effort: "none"` disables reasoning; `include_reasoning: false` controls inclusion; `reasoning.exclude: true` hides `message.reasoning` but **still bills** reasoning tokens — not used as the primary OFF switch.

**Harness v2 fixed default (Amendment 4 code):** when endpoint lists the parameter, send both:

```json
"include_reasoning": false,
"reasoning": { "effort": "none" }
```

inside `extra_body` (with DeepInfra provider pin). **Llama 3.3 70B** DeepInfra row has **neither** `reasoning` nor `include_reasoning` — fields are **skipped** (documented in metadata), not silently dropped while claiming off.

## Smoke3 Qwen3 — logged `usage.cost` vs DeepInfra list pricing

**Pricing source (verbatim DeepInfra row JSON):**

```json
{
  "prompt": "0.00000012",
  "completion": "0.0000005",
  "discount": 0
}
```

**Reconciliation** (run `HARNESS_V2_SMOKE3_20260927-131707`, qwen3 HTTP 5–7):

| HTTP | prompt | completion | reasoning_tokens | logged cost_usd | prompt×$0.00000012 + completion×$0.0000005 |
|-----:|-------:|-----------:|-----------------:|----------------:|---------------------------------------------:|
| 5 | 436 | 522 | 605 | 0.00031332 | 0.00031332 |
| 6 | 544 | 693 | 743 | 0.00041178 | 0.00041178 |
| 7 | 658 | 357 | 412 | 0.00025746 | 0.00025746 |

**Conclusion:** Logged `usage.cost` matches **prompt + completion token list rates only**. **`reasoning_tokens` are not added as a separate line item** in `cost` (despite appearing in `completion_tokens_details`). Provider reports reasoning counts **greater than** `completion_tokens` on these calls — an OpenRouter/DeepInfra accounting quirk, not harness arithmetic.

**OpenRouter credit (GET `/api/v1/auth/key`, 2026-09-27):** `limit_remaining` ≈ **$0.448** (limit $2.00, usage ≈ $1.552).
