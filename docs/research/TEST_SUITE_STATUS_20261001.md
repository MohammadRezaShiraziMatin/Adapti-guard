# Full test suite status (2026-10-01) — documentation only, nothing was repaired

Command: `python3 -m pytest tests -q` in the session container after `pip install httpx scikit-learn numpy pandas`.
Result: **661 passed, 32 failed, 6 skipped.** The paper-related tests pass (`tests/test_manuscript_number_ledger.py`, `tests/test_panel_registry.py`, and the external-adapter and attack-set tests).

These 32 failures are outside the scope of the manuscript and were deliberately left unrepaired; they explain why the whole suite is not green.

| test file | failures |
|---|---|
| `FAILED` | 9 |
| `FAILED` | 6 |
| `FAILED` | 3 |
| `FAILED` | 2 |
| `FAILED` | 2 |
| `FAILED` | 2 |
| `FAILED` | 1 |
| `FAILED` | 1 |
| `FAILED` | 1 |
| `FAILED` | 1 |
| `FAILED` | 1 |
| `FAILED` | 1 |
| `FAILED` | 1 |
| `FAILED` | 1 |

Causes seen in the pytest output (not every failure was diagnosed individually):
- 16 tracebacks: configuration placeholders that cannot be parsed as integers (`PENDING_BUDGET_APPROVAL`, `PENDING_N`) in the older Q1 / B2 campaign preflight and batch tests.
- several failures (counted per traceback line, so possibly overlapping): optional provider packages not installed in this container (`google`, `openai`).
- a few failures: a script run in a subprocess cannot import `adapti_guard` (no editable install / `PYTHONPATH` in the test environment).
- the rest: assertion failures in older harness and ledger-order tests (for example `assert 1 == 0`, `'stopped' == 'ok'`), not examined.

Side effect to know about: running the full suite rewrites `docs/research/PHASE7_LIVE_AUTHORIZATION.json`. That file was restored with `git checkout` after each run and was never committed in modified form.

No file of the frozen evidence, the pre-registration draft or `PHASE7_LIVE_AUTHORIZATION.json` was changed in this work.
