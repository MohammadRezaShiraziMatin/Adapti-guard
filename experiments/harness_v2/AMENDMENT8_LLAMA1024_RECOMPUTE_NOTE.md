# Amendment 8 §4.3 — recomputed after code (llama max_tokens 1024)

**Status:** Informational only. Does **not** edit locked figures in `AMENDMENT8_PROPOSAL.md` §4.4 or `PREREG_HARNESS_V2_FULL.md` cost tables.

## Placeholder formula (cancelled_timeout reserve)

`prompt_tokens × prompt_usd_per_token + max_tokens × completion_usd_per_token`  
(`cancelled_timeout_billing.py`; uses `max_tokens_for_model_id` at episode runtime.)

**Llama panel prices** (`meta-llama/llama-3.3-70b-instruct`): prompt **$0.0000001**/tok, completion **$0.00000032**/tok.

**580 prompt tokens** in the table below is an **illustrative** pilot-order-of-magnitude example only (not a locked prompt count).

**Placeholder maximum (llama):** `max_tokens_for_model_id("meta-llama/llama-3.3-70b-instruct")` = **1024** after item K; cancelled_timeout **`billed_placeholder_usd`** uses that completion ceiling. **Completion term at cap:** **1024 × $3.2×10⁻⁷ = $0.00032768**; **+ prompt term** at illustrative **580 × $1.0×10⁻⁷ = $0.00005800** → **$0.00038568** per placeholder row (table below).

| llama `max_tokens` | Placeholder USD (580 prompt + cap×out) |
|-------------------:|---------------------------------------:|
| **512** (old code) | **$0.00022184** |
| **1024** (code @ item K) | **$0.00038568** (= **$0.00032768** completion + **$0.00005800** prompt @ 580 tok) |
| Δ per cancelled attempt | **+$0.00016384** |

## Full-run E[HTTP] / E[$] / worst HTTP / worst $ (attack + benign bundle)

Per Amendment §4.4 and PREREG §7, **expected and worst USD/HTTP counts do not change** when only `max_tokens` rises (same HTTP row count; per-row `cost` still from usage or reasoning-off $/HTTP planning constants).

| Metric | Amendment §4.4 text | After llama 1024 code |
|--------|---------------------|------------------------|
| E[HTTP] | ~3266 | **unchanged ~3266** |
| E[$] incl. benign | ~**$0.30–0.31** | **unchanged ~$0.30–0.31** |
| Worst HTTP | 5376 | **unchanged 5376** |
| Worst $ incl. benign | ~**$0.48–0.49** | **unchanged ~$0.48–0.49** (band applies when completion fill approaches the **1024** cap — not recomputed as a new locked total here) |

**What changed in code:** llama **`request.max_tokens`**, cancelled-timeout **placeholder ceiling**, and any USD-cap checks that sum placeholders — not the prereg **$/HTTP** planning table.
