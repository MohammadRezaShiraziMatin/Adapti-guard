# Harness v2 pilot — known limitations (draft)

Documented at **Option A code freeze** `b7388512a5f9fcf0412b7d06eeba818cbe1ea5df` (2026-09-28). **No automatic retries or parsing fixes** for these cases unless a future amendment explicitly changes behavior.

## (a) HTTP 429 without `error.code` in JSON body

**Condition:** A billed attempt receives HTTP **429** (or HTTP **200** with an error object) whose JSON body **does not** include a usable top-level **`error.code`** field (missing code, non-numeric text, or empty body).

**Behavior:** The harness **does not** apply the Amendment 8 **429 harness retry** (no second attempt with a new `request_id`). The row is recorded as **`INVALID_PROVIDER_ERROR`** / provider-error ledger semantics.

**Contrast:** With **`openai==3.19.2`** and **`max_retries=0`**, the SDK does **not** retry HTTP **429** (one transport request, then raises **`RateLimitError`** / **`APIStatusError`**). On the **pilot 3 SDK wire path**, the **harness** still retried many **429**s because **`_is_rate_limit_error`** (commit **`4f3e981`**, **`openrouter_tools_session_async.py`** ~75–84) treated **`RateLimitError`** and **`status_code == 429`** on exceptions. HTTP **200** with an **`error`** object in the JSON body is returned as a normal **`ChatCompletion`**-shaped response (**no** SDK exception); on pilot 3 those cases were retried only via **`_is_rate_limit_error_body`**, same as on the **frozen project httpx path** (`b7388512`), where HTTP **429** is usually returned as a parsed error **dict** and retry depends on **`error.code`** in the allow-list. Limitation **(a)** is when that JSON path does **not** yield a retryable **`error.code`**.

**Pilot 3 observation:** All **26** pilot-3 HTTP 429 rows carried **`error.code` 429**; limitation **(a)** was **not** triggered in that pack.

## (b) Non-JSON 4xx/5xx response bodies

**Condition:** HTTP **4xx/5xx** where the response body is **not** valid JSON (HTML error page, empty body, truncated text).

**Behavior:** The attempt may return the raw text string; the episode records **`raw_response`** as **`{"raw": "<body snippet>"}`** (or similar) **without** preserving the HTTP status code on that dict. Downstream report fields that expect structured **`error.code`** may be incomplete.

**Contrast:** SDK error paths surface **`APIStatusError.status_code`** even when the body is not JSON.

## (c) Smoke `/auth/key` preflight HTTP error status

**Condition:** Amendment 9 smoke preflight **`GET /auth/key`** fails with an HTTP error (e.g. **401**).

**Behavior:** **`run_amendment9_smoke_auth_preflight`** records **`http_status: 0`** in **`preflight_auth_key_launch.json`** (see **`amendment9_smoke_controls.py`** ~81), not the real HTTP status (e.g. **401**).

---

## (d) Gemma P2 — locked criteria FAIL (disclosed, not a run blocker)

**Decision (Amendment 9, Matin approved):** Report **P2 = FAIL** for **gemma** under locked **`PILOT2_CRITERIA_LOCKED.md`** (`reasoning_tokens==0` on every HTTP call). Pilot 3: **44 calls** in **40/40** gemma episodes had **`reasoning_tokens=2`** (`AMENDMENT9_DECISIONS.md` § P2 gemma). Accepted limitation for Option D main run; does **not** block launch.

## (e) llama-3.3-70B / DeepInfra excluded from main panel

**Decision (Option D):** **llama** is **not** in the main-run model panel after Amendment 9 llama smoke **FAIL** (DeepInfra degeneration / delivery evidence; see **`AMENDMENT9_DECISIONS.md`** § Llama path). Main runner **`MODEL_ORDER`** is **qwen3, gemma, deepseek** only.

---

## PRE-LOCKED RULE (dated 2026-09-28; locked before any main-run data)

**If any row of type (a) or (b) occurs in the main run, it is counted separately and reported. This rule is locked now and will not change after data is seen.**
