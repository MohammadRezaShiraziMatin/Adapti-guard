# Phase 2.7 Pilot — Historical Blocker Notes

## Superseded (successful rerun)

**Status:** PASS (infrastructure pilot)

| Field | Value |
|-------|-------|
| Timestamp | `2026-09-02T09:27:28Z` |
| Git commit | `612f577118a19949b4862a3b27b801db8c7eef65` |
| Predictions | 30 (B0: 15, B6: 15) |
| Judge failures | 0 |
| API errors | 0 |
| Frozen dataset SHA-256 | `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24` |

See `REPORT.md`, `metrics.json`, and `predictions.jsonl` for current artifacts.

---

## Earlier failed attempt (historical — superseded)

The first pilot run partially completed but **failed go/no-go** due to judge API errors:

- **Cause:** OpenRouter HTTP 402 (in-flight credit budget exhausted)
- **Judge model:** `anthropic/claude-sonnet-4`
- **Outcome:** 27/30 valid episodes, 3 judge failures
- **Integrity:** Failures were **not** converted to synthetic labels

A later rerun with sufficient API credit produced the PASS artifacts above.

---

## Stale local blocker (historical — superseded)

An intermediate state reported:

```text
API: OPENROUTER_API_KEY not set
```

This reflected a missing-key preflight failure, not the final successful run.
