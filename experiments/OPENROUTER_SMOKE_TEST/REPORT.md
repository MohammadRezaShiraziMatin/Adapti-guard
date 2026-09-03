# OpenRouter Controlled API Smoke Test

**NOT publication evidence.** EXP-004 was NOT executed.

**Verdict:** `READY_FOR_PILOT`

## 1. Environment
- Python: `3.12.3 (main, Jun 19 2026, 12:46:00) [GCC 13.3.0]`
- CWD: `/home/mohammadreza/01_BASE_Q1/adapti_guard`

## 2. Git commit
- `612f577118a19949b4862a3b27b801db8c7eef65`

## 3. Models tested
- `anthropic/claude-sonnet-4`
- `openai/gpt-4o-mini`

## 4. Number of API calls
- **3** (max allowed: 4)

## 5. HTTP results
- `call_1_target_smoke` → HTTP **200** success=True model=`openai/gpt-4o-mini`
- `call_2_judge_smoke` → HTTP **200** success=True model=`anthropic/claude-sonnet-4`
- `call_3_target_compat` → HTTP **200** success=True model=`openai/gpt-4o-mini`

## 6. Token usage
- prompt: 90
- completion: 17
- total: 107

## 7. Cost
- total_cost_usd: 0.0002097
- note: from response where available

## 8. Latency
- mean_latency_ms: 2100.59
- p95_latency_ms: 2395.4

## 9. Authentication status
- pass

## 10. Credit status
- sufficient for smoke test (402 not observed; full EXP-004 budget NOT verified)

## 11. Model availability
- Target `openai/gpt-4o-mini`: OK (HTTP 200)
- Target `openai/gpt-4o-mini`: OK (HTTP 200)

## 12. Judge availability
- Judge `anthropic/claude-sonnet-4`: OK (HTTP 200)

## 13. Errors
- none

## 14. EXP-004 readiness
- READY (repository preflight passed; proceed Smoke→Pilot→Review before EXP-004)

## Per-call detail

```json
[
  {
    "call_id": "call_1_target_smoke",
    "timestamp": "2026-09-02T10:20:38.584297+00:00",
    "model": "openai/gpt-4o-mini",
    "http_status": 200,
    "success": true,
    "response": "SMOKE_TEST_OK",
    "latency_ms": 2395.4,
    "prompt_tokens": 14,
    "completion_tokens": 4,
    "total_tokens": 18,
    "cost_usd": 4.5e-06,
    "cost_source": "response",
    "request_id": "gen-1788344442-KSZfvyDb8v8tCclI6ceu",
    "error_type": null,
    "error_message": null,
    "error_class": null
  },
  {
    "call_id": "call_2_judge_smoke",
    "timestamp": "2026-09-02T10:20:43.481371+00:00",
    "model": "anthropic/claude-sonnet-4",
    "http_status": 200,
    "success": true,
    "response": "PASS",
    "latency_ms": 2416.75,
    "prompt_tokens": 40,
    "completion_tokens": 5,
    "total_tokens": 45,
    "cost_usd": 0.000195,
    "cost_source": "response",
    "request_id": "gen-1788344444-LjUFDyrRwNTBLcttzBOl",
    "error_type": null,
    "error_message": null,
    "error_class": null
  },
  {
    "call_id": "call_3_target_compat",
    "timestamp": "2026-09-02T10:20:45.898318+00:00",
    "model": "openai/gpt-4o-mini",
    "http_status": 200,
    "success": true,
    "response": "2 + 2 equals 4.",
    "latency_ms": 1489.63,
    "prompt_tokens": 36,
    "completion_tokens": 8,
    "total_tokens": 44,
    "cost_usd": 1.02e-05,
    "cost_source": "response",
    "request_id": "gen-1788344446-yU8STbmUyu6KxuuSIfYs",
    "error_type": null,
    "error_message": null,
    "error_class": null
  }
]
```

Frozen dataset SHA-256: `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24` (unchanged=True)
