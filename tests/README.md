# Tests

Pytest suite at the repo root (`pytest.ini` `pythonpath = . src`). Test files stay flat so `Path(__file__).parents[1]` continues to mean the repository root.

Mirroring `tests/` to `src/adapti_guard/` package layout is **deferred** (would require rewriting every `parents[1]` ROOT).

Workshop FAIL facts: `tests/test_workshop_vnext_fail_facts.py`.
