# Amendment 6 — practical proof (mock HTTP only; no live OpenRouter)

**Canonical demo pack:** `experiments/harness_v2/AMENDMENT6_DEMO_20260927-155900/`  
**Supervisor:** `experiments/harness_v2/amendment6_run_kill_demo.py`  
**Mock server:** `experiments/harness_v2/amendment6_mock_openai_server.py`  
**Runner:** `scripts/run_harness_v2_pilot.py` with `OPENROUTER_BASE_URL` → local mock (see `openrouter_tools_session.py`).

---

## 1) Process check (now)

Raw output (`process_check_owner_commands.txt`):

```text
$ pgrep -af run_harness_v2_pilot; pgrep -af python; tmux ls
53819 /bin/bash -O extglob -c snap=$(command cat <&3) && ... pgrep -af run_harness_v2_pilot; pgrep -af python; tmux ...
1216 python3 -m websockify --web /usr/local/novnc/noVNC-1.2.0/utils/../ 26058 localhost:5901
53819 /bin/bash -O extglob -c snap=$(command cat <&3) && ... (same wrapper)
harness-v2-pilot: 1 windows (created Sun Sep 27 13:50:05 2026)
harness-v2-pilot2-run: 1 windows (created Sun Sep 27 15:01:51 2026)
... (other idle tmux sessions)
```

**Interpretation:** No `python3 scripts/run_harness_v2_pilot.py` process. The only `pgrep -af run_harness_v2_pilot` hit is the shell running `pgrep` itself (pattern appears in the wrapper command line). Only unrelated Python is `websockify` (noVNC).

---

## 2) Usage drift (stop vs addendum vs now)

| Snapshot | `usage` | Notes |
|----------|--------:|-------|
| `PILOT2_STOP_REPORT.md` @ kill | **1.624137948** | `limit_remaining` 0.875862052 |
| Addendum write (~15:52 UTC) | **1.624804008** | Δ **+0.000666060** |
| Auth/key T+0 (~15:52) | **1.624804008** | saved `/tmp/auth_key_t1.json` |
| Auth/key T+~2min | **1.624804008** | saved `/tmp/auth_key_t2.json` — **no further drift** |
| This proof (~15:56 UTC) | **1.624804008** | unchanged |

**`/auth/key` is not billable** — repeated reads in this proof did not move `usage`.

**Likely source of +$0.000666 (not proven per-request):**

- Concurrent **aborted pilot 2** OpenRouter HTTP may have still been **settling** after process kill when the stop snapshot was taken; account `usage` updated before the addendum read.
- This agent turn after stop: only **`/auth/key`** and **`/activity`** (403) to OpenRouter — **no** `chat/completions` on the real API. Mock demo uses `127.0.0.1` only.
- **Unexplained residual:** cannot attribute the $0.000666 to a specific post-kill script in-repo (no request logs for pilot 2). Treat as **aggregate lag / in-flight billing** from aborted live pilot 2, not Amendment 6 mock work.

**`/api/v1/activity`:** `403` — `"Only management keys can fetch activity for an account"` (non-management key).

---

## 3) Incremental persistence demo (SIGKILL at N=7)

**Command:**

```bash
python3 experiments/harness_v2/amendment6_run_kill_demo.py
```

**At SIGKILL (frozen artifacts in demo dir, before `--resume` mutates live files):**

```text
$ wc -l experiments/harness_v2/AMENDMENT6_DEMO_20260927-155900/http_stream_at_sigkill.jsonl \
       experiments/harness_v2/AMENDMENT6_DEMO_20260927-155900/mock_server_requests_at_sigkill.jsonl
7 .../http_stream_at_sigkill.jsonl
7 .../mock_server_requests_at_sigkill.jsonl
```

`running_ledger_at_sigkill.json`:

```json
{
  "http_used": 7,
  "spent_usd": 0.00028,
  "episodes_complete": 2,
  ...
}
```

`post_sigkill_report.json`:

```json
{
  "N": 7,
  "http_stream_lines": 7,
  "server_requests": 7,
  "ledger_http_used": 7,
  "sum_stream_cost_usd": 0.00028000000000000003,
  "ledger_spent_usd": 0.00028
}
```

**Checks:** `http_stream` line count = mock server request log lines = `running_ledger.json` `http_used` = **7**; `spent_usd` equals sum of per-line `cost_usd` in the 7-line stream (**0.00028**).

**`--resume`:** same `out-dir`; `resume_skip_check.json`:

```json
{
  "episodes_complete": 33,
  "first_in_completed": true,
  "episode_begin_first_count": 1
}
```

First schedule episode appears **once** in `episode_begin` (not re-run from scratch); resume continued until mock **USD cap** (`stopped_reason=budget_cap` in final `pilot_summary.json`). Live `http_stream.jsonl` after resume is **101** lines — expected; use **`*_at_sigkill`** files for kill proof.

---

## 4) Lock demo (mock runner)

From `run_amendment6_lock_demo.sh`:

**Lock while first pilot holds it:**

```json
{
  "pid": 53601,
  "out_dir": "/workspace/experiments/harness_v2/AMENDMENT6_LOCK_HOLD_20260927-155434",
  "pilot_label": "harness_v2_pilot_2",
  "started_at_utc": "2026-09-27T15:54:35.196261+00:00"
}
```

**Second concurrent `--live` pilot:**

```text
exit_code=2
pilot_run_lock_held: pid=53601 out_dir=/workspace/experiments/harness_v2/AMENDMENT6_LOCK_HOLD_20260927-155434
```

**Stale lock (dead PID 999999999):** manual `.pilot_live.lock` replaced; `PilotRunLock.try_acquire` succeeded with new pid; lock file removed on release (`lock_after_release_exists False`).

Path: `experiments/harness_v2/.pilot_live.lock`

---

## 5) Registry — ABORTED pilot 2 per-attempt spend

| Attempt id | Per-attempt `spent_usd` | Evidence |
|------------|-------------------------|----------|
| `pilot2_tmux_harness-v2-pilot` | **UNKNOWN** | No pack, no HTTP log |
| `pilot2_foreground_947558` | **UNKNOWN** | No request bodies; `/tmp/pilot2_run.log` **0 bytes** |
| `pilot2_tmux_harness-v2-pilot2-run` | **UNKNOWN** | Concurrent; no per-attempt ledger |

**Aggregate only (OpenRouter):** **$0.043604** vs post–pilot-1 baseline (`manifest.json`, `PILOT2_STOP_REPORT.md`).  
**Not reconstructable per attempt** without request-level logs.

Append-only manifest note: `ABORTED_PILOT2_ATTEMPTS_20260927/manifest_spend_attribution.json`.

---

## 6) STOP

No live OpenRouter pilot proposed or started. Owner may re-run proof via `amendment6_run_kill_demo.py` (mock only).

**Git commit SHA:** `10d4280fe636` (`10d4280fe6365be6b33b8d43fe7bd0ef8911db4a`).
