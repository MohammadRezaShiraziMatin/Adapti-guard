# EXP005-20260903-081824

**Status:** `PARTIAL` (aborted)

This run was stopped after Gemini free-tier HTTP 429. Short retries then
attempted a same-model judge fallback, producing mixed `ok` and
`judge_error`/`target_error` rows.

Do **not** use these numbers as publication results. A later run with
Retry-After honoring and request pacing supersedes this directory.
