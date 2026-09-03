# FINAL JUDGE VALIDATION — Cerebras qwen-3.8-27b

**Status:** FAIL  
**Blocker:** HTTP 402 `payment_required` on Cerebras **chat completions**

- Attempted: 10
- OK: 0
- Invalid: 0
- Failed: 10 (all 402)

Authentication: API key present (whitespace stripped at load).  
Model listing: `qwen-3.8-27b` is in the Cerebras model catalog.  
Chat: 402 for `qwen-3.8-27b`, and diagnostic probes of `gpt-oss-120b` and `gemma-4-31b` also returned 402.

Failed judgments were stored as `JUDGE_FAILED`, not as ASR labels.

Mass rejudge was **not** started (protocol STEP 5).
