# Pre-fix evidence @ git `23125d7`

Captures the **pre–wire-fix** failure mode on the **160-episode wire-main pilot schedule**: `main()` against a local fake OpenRouter server received **zero** `chat/completions` POST bodies because **`run_tools_episode_async` / the pilot passed `http_transport=None` into `WireCapturingTransport`**, which raised **`RuntimeError: WireCapturingTransport requires an inner transport for mock runs` on every billed attempt** (not a base-URL routing bug and not httpx proxy `None` mounts on the production path at that commit).

## Prerequisites

- Git worktree at `23125d7` (runner code under test)
- Copy **only** the local-server test helper from this branch:

```bash
git worktree add /tmp/adapti-guard-pre23125d7 23125d7
cp tests/harness_v2_local_openrouter_server.py /tmp/adapti-guard-pre23125d7/tests/
```

## Run (160-episode schedule via env — full wire-main pilot)

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
