# Pre-fix evidence @ git `23125d7`

Captures the **pre–wire-fix** failure: `main()` against a local fake OpenRouter server receives **zero** `chat/completions` POST bodies (old runner did not route HTTP to the local base URL correctly for the wire-main scenario).

## Prerequisites

- Git worktree at `23125d7` (runner code under test)
- Copy **only** the local-server test helper from this branch:

```bash
git worktree add /tmp/adapti-guard-pre23125d7 23125d7
cp tests/harness_v2_local_openrouter_server.py /tmp/adapti-guard-pre23125d7/tests/
```

## Run (single-episode schedule via env — not the full 160-episode pilot)

From the **23125d7 worktree** root:

```bash
cd /tmp/adapti-guard-pre23125d7
PYTHONPATH=src python3 -m pytest \
  /path/to/adapti-guard/tests/prefix_evidence/test_pre23125d7_zero_server_hits.py -q --tb=short
```

Or use the capture script from a checkout that contains `tests/prefix_evidence/`:

```bash
./tests/prefix_evidence/capture_pre23125d7_evidence.sh
```

Expected failure assertion:

`server received 0 chat/completions requests` (`len(server.chat_bodies) == 0`).

Regenerated log: `experiments/harness_v2/AMENDMENT9_WIRE_MAIN_PRE23125d7_PYTEST.txt`.
