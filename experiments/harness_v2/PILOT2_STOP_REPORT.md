# Pilot 2 STOP — final report (owner order)

**Status:** All live pilot 2 work **STOPPED**. No re-run until owner approval.

## 1) Process kill verification

```text
$ ps -eo pid,cmd | grep run_harness_v2_pilot | grep -v grep
(no run_harness_v2_pilot processes)
```

Prior PIDs terminated: **47822**, **48642** (and duplicate tmux launches). Polling bash loops on `pgrep -f run_harness_v2_pilot` also cleared.

## 2) OpenRouter `/auth/key` (now)

| Field | Value |
|-------|------:|
| `usage` | **1.624137948** |
| `limit` | 2.5 |
| `limit_remaining` | **0.875862052** |
| `usage_daily` | 1.610788592 |

## 3) Spend attribution

| Reference | USD |
|-----------|-----:|
| Post–pilot-1 usage (baseline) | **1.580534038** |
| Current usage | **1.624137948** |
| **Delta (attributed to aborted pilot-2 attempts)** | **0.043603910** |

Pilot 1 pack ledger (`1af54c1`): **$0.02815054** / 341 HTTP. The OpenRouter account delta (~**$0.044**) is **≥ pilot-1 pack spend**, consistent with **~15–16 minutes** of concurrent pilot-2 HTTP (two overlapping `run_harness_v2_pilot.py --live` processes) before kill, with **no on-disk run pack** (legacy runner wrote only at end).

## 4) Partial data preserved (append-only)

| Path | Notes |
|------|--------|
| `experiments/harness_v2/ABORTED_PILOT2_ATTEMPTS_20260927/manifest.json` | All attempts, PIDs, times |
| `.../pilot2_run.log` | Empty (buffered `tail` pipeline) |
| `.../terminal_947558_foreground_pilot2.txt` | Foreground shell metadata (~947s) |

**No** `HARNESS_V2_PILOT_*` run directory was created.

## 5) RUN_REGISTRY

Append-only rows added for manifest + three **ABORTED** attempt ids (see `experiments/judge_gold/RUN_REGISTRY.md`).

## 6) Amendment 6 (code — no live run)

- Incremental: `http_stream.jsonl`, `running_ledger.json`, `progress.log`, per-episode trajectory on complete (`fsync`).
- Single-flight: `experiments/harness_v2/.pilot_live.lock` (PID; stale if dead).
- USD cap enforced from **persisted ledger** after each HTTP.
- `--resume` skips episodes in `episodes.jsonl`.
- Tests: `tests/test_harness_v2_pilot_amendment6.py`.

**Commit SHA:** see git log (`feat(harness_v2): Amendment 6 incremental pilot persistence`).

---

**STOP.** Awaiting owner approval before any new `--live` pilot 2.
