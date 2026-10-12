# R2 interruption analysis (read-only)

Scope: why the R2 run reportedly stopped at 571 of 980 episodes after about 30 minutes.
Branch inspected: `origin/phase3/confirmatory-protocol` (contains merged #137, #138, #139). Container checkout was `main`; the branch was fetched, not run.
No run, model call, launcher, or existing file was changed. No API key was read or printed.

## Conclusion

**The cause cannot be determined from the material available here. No evidence supports a specific cause.**

- No R2 run folder, `progress.log`, `run_manifest.json`, `episodes.jsonl`, pid file, or status file exists in the branch, in `main`, or anywhere in the container's filesystem (searched `/home`, `/root`, `/tmp`, `/var/tmp` and the repo tree for `*R2*`, `*.pid`, `progress.log`, and `injecagent_R2*`).
- The container has no running `python` or launcher processes (`ps` shows none).
- The only InjecAgent run folder on the branch with a progress log is the R1 pilot (`experiments/external/injecagent_R1_pilot_20261011T225134Z/`). It is not R2 and ended normally (see section 3).
- The branch's R1 note states "no R2 or R3 run has started" (`experiments/external/R1_PILOT_NOTE.md`). That note predates any R2 attempt, so it does not rule out a later run on another machine.

Next step that would settle it: on the machine where R2 ran, locate `experiments/external/injecagent_R2*/` (the launcher creates a fresh timestamped run folder under `--out-root`) and read `progress.log`, `run_manifest.json`, and `episodes.jsonl`. The diagnostic in section 3 applies directly to those files.

## 1. Where the records would be

- Run folder: created by `make_run_dir(out_root, started)` in `scripts/injecagent_executed_launcher_v02.py`. Files written there: `run_manifest.json`, `auth_key_pre.json`, `progress.log`, `episodes.jsonl`, `auth_key_post.json`.
- `progress.log` is staged with git only when the run folder is inside the repo (launcher docstring, lines 17 to 22). A run from another checkout or a container would not have been staged.
- Found on the branch: R1 folder only, `experiments/external/injecagent_R1_pilot_20261011T225134Z/`.
- Found in the repo for R2: only planning text (`docs/protocols/CONFIRMATORY_PROTOCOL_DRAFT_v0.1.md` lines 196, 205, and `docs/protocols/injecagent_S-A_campaign_plan_20261001.json` line 1546). Plan: 980 episodes, HTTP cap 980.

## 2. Last 50 lines of the log

Not available. No R2 `progress.log` exists in the material inspected. The R1 log's last lines are shown in section 3 as a reference format; no key-like strings appear in them.

## 3. Signal, timeout, or error: what the launcher would leave behind

The launcher's end-of-run handling (`scripts/injecagent_executed_launcher_v02.py`, run loop at lines 595 to 625):

- Line 622: `except Exception as exc:` calls `finish(f"ERROR: {type(exc).__name__}", ...)`, writes `end status=ERROR: ...` to the log, then re-raises.
- There is no `except BaseException`, `finally`, or signal handler anywhere in the launcher (`grep` for `signal`, `SIGTERM`, `KeyboardInterrupt`, `finally` returns nothing relevant).
- So:
  - **Killed by a signal** (SIGTERM, SIGHUP, SIGKILL, or a session teardown): no `end status=` line is written, and `run_manifest.json` keeps `"status": "RUNNING"` with no `finished_utc`. The log simply stops after the last `episode` line. `except Exception` does not catch signals.
  - **Python exception during the episode loop**: the log ends with `end status=ERROR: <ExceptionType>`, and the manifest is updated to that status.
  - **Normal end or cap stop**: `end status=COMPLETE` or `STOPPED_HTTP_CAP` / `STOPPED_SOFT_CAP`, with `finished_utc` set.

Baseline from the branch (R1 `progress.log`, last two lines, abbreviated):

```
2026-10-11T22:55:20.537774+00:00 meta-llama/llama-4-maverick ds-0518 SPOT_TOOL http=200 executed=False ...
2026-10-11T22:55:20.639919+00:00 end status=AUTH_MISMATCH
```

R1 `run_manifest.json`: `"status": "AUTH_MISMATCH"`, `"started_utc": "2026-10-11T22:51:34.991316+00:00"`, `"finished_utc": "2026-10-11T22:55:20.639935+00:00"`. This is a clean exit, and it is the reference against which an R2 interruption can be judged.

Pace check (consistency only, not evidence of cause): R1 ran 60 episodes in about 3 min 46 s (about 3.8 s per episode). 571 episodes in 30 minutes is about 3.2 s per episode, in the same range. Nothing in the timing points to a slowdown or a timeout.

## 4. Timeouts in the launcher and repo

| Setting | Where | Value | Would it end a run at ~30 min? |
|---|---|---|---|
| Per-request socket timeout | `scripts/injecagent_executed_launcher_v02.py` lines 280 and 283 (`timeout: float = 120.0`), used at lines 289 and 301 | 120 s per HTTP request | No. A timeout is recorded per episode as `transport:timeout` and the run continues (docstring lines 20 to 21). |
| Post-run `/auth/key` settle | `--settle-wait-s` (default 600 s per the D1 text), `--settle-max-reads` (default 3 per D1; the code default at line 97 is 1, so the merged code and D1 disagree) | Runs only after the episode loop | No. It runs after the loop, so it cannot cut the loop short at 571. |
| Wall-clock or session timeout | none found | none | No configured value. |

- `grep` for `session`, `shell`, `ulimit`, `timeout`, `nohup`, `cron`, `systemd` across `scripts/` and `docs/protocols/` finds only the 120 s socket timeout and the 600 s settle wait.
- Shell or session limits outside the repo (the environment that launched R2) cannot be checked from here. If the launch used a tool with its own command timeout, that is the only candidate for a 30-minute stop, and it would appear as a signal-killed run (section 3, first case).

## 5. Caps that could stop a run without an interruption

- HTTP cap: `if settings.http_cap - http_calls < settings.max_turns:` sets `STOPPED_HTTP_CAP` and writes `stop: STOPPED_HTTP_CAP`. With the planned cap of 980 and `max_turns` worst case, this would not trigger at 571 unless the run was launched with a lower `--http-cap`. Unknown from here.
- Soft USD cap: `STOPPED_SOFT_CAP`. Planned R2 spend is about 0.14 USD against a 0.2978 USD soft cap (`R1_PILOT_NOTE.md`), so a cap stop at 571 is unlikely on the planned numbers, but the actual spend is not in the material.
- A cap stop would be a clean `end status=` line, so it is distinguishable from an interruption.

## 6. Items that do not match and should be reviewed (not edited)

- `docs/protocols/DEVIATIONS.md` line 41 (D2 Status) says "Proposed ... not merged at the time of writing". Git history shows `6b309d2` (PR #139, "Accept settled R1 cost only through a committed RECONCILIATION.json") is merged on this branch. The status line is stale.
- `DEVIATIONS.md` line 33 (D2) says "The launcher refused R2 because the prior-run check accepts only reconciled manifests." That refusal is described in the deviation text only; no refusal folder or log for R2 exists in the branch. If an R2 attempt was refused at launch, it would have left a `REFUSED_*` manifest or a log line, and none is in the repo.

## Recommended next step

Collect the R2 folder from the machine where it ran (`progress.log`, `run_manifest.json`, `episodes.jsonl`, and any shell or tool timeout log for that session) and check it against section 3:

1. `end status=` line present → an exception or cap; the status text names it.
2. No `end status=` line and manifest `RUNNING` → killed by a signal from outside the Python process (the launcher cannot distinguish SIGTERM from SIGHUP here; the launching shell or session log would show which).
3. Log timestamps stop at about 30 minutes after `start run` → matches a wall-clock limit of the launching environment; confirm in that environment's configuration.

No cause is asserted here.
