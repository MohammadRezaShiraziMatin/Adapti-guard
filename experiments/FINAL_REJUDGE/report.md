# FINAL REJUDGE REPORT

**Status:** BLOCKED_CEREBRAS_402

- Source Target observations: 300 (not re-run)
- Cerebras validation attempts: 10
- Valid structured judgments: 0
- Mass rejudge calls: 0 (stopped after validation failure per protocol STEP 5)

Cause: HTTP 402 `payment_required` on Cerebras chat completions for `qwen-3.8-27b`.
Models list succeeded; chat did not. Failures are stored as JUDGE_FAILED / not converted to ASR.

Mean ICS (actions): B0=0.00, B6=0.10.
