# Deviations from the registered protocol

This file lists every change made after registration that touches the executed InjecAgent S-A campaign. The frozen
protocol (`CONFIRMATORY_PROTOCOL_DRAFT_v0.1.md`, SHA-256 in `CONFIRMATORY_PROTOCOL_FROZEN.sha256`) is not edited. Each
entry states the reason, the evidence, and what it affects.

## D1. Post-run /auth/key read waits for usage to settle

- **Change.** `scripts/injecagent_executed_launcher_v02.py` reads `/auth/key` after a run until two consecutive reads,
  `--settle-wait-s` apart (default 600 s), agree within 1e-6 USD. It reads at most `--settle-max-reads` times (default 3)
  and refuses the run otherwise. `--settle-max-reads 1` restores the previous single read.
- **Reason.** In the R1 pilot the single post-run read (0.006742489 USD, 22:55:20 UTC, run folder
  `experiments/external/injecagent_R1_pilot_20261011T225134Z/`) was taken before OpenRouter usage had settled. Two later
  reads, at 23:04:32 and 23:14:56 UTC, both gave 0.007482165 USD, which matches the runner's recorded spend. The
  post-run snapshot therefore understated the cost by about 10%.
- **Effect on R2 and R3.** Accounting only. The change alters how the post-run `/auth/key` value is obtained. It does
  not change cases, arms, models, prompts, seeds, caps, or the analysis plan.
- **Effect on R1.** None. R1 ran with the launcher as registered. Its run folder is committed unmodified. The R1 record
  keeps the single-read value and its `AUTH_MISMATCH` status. `experiments/external/CORRECTIONS.md` gives the corrected
  cost basis.
- **Evidence.** Tests: `tests/test_injecagent_settled_usage.py`. The run-level test fails on the pre-change launcher
  (it records 0.05 USD early and is refused) and passes on the new code.
- **Status.** Merged into `phase3/confirmatory-protocol` (PR #138, merge commit 085c554).

## D2. Settled cost accepted for an AUTH_MISMATCH prior run

- **Change.** `campaign_budget_check` in `scripts/injecagent_executed_launcher_v02.py` accepts a prior run whose
  `run_manifest.json` status is `AUTH_MISMATCH` only if a committed `RECONCILIATION.json` exists in that run folder. The
  file must be bound to the manifest by SHA-256, carry two stable post-run reads, agree with the runner's recorded
  spend to 1e-6 USD, and cite `experiments/external/CORRECTIONS.md`, which must be committed. The settled value is then
  that run's spend. Any other non-reconciled status is still refused. `--dry-run` performs the same prior-run check.
- **Reason.** R1 ended with status `AUTH_MISMATCH` because its single post-run `/auth/key` read preceded settlement
  (D1, CORRECTIONS.md). The launcher refused R2 because the prior-run check accepts only reconciled manifests. The
  manifest was left unedited, so the settled value needs its own committed record.
- **Effect on R2 and R3.** Accounting only: the prior-run total for the campaign cap uses the settled R1 cost,
  0.007482165 USD. No change to cases, arms, models, prompts, seeds, caps or analysis.
- **Effect on R1.** None on its record. `run_manifest.json` is unchanged. `RECONCILIATION.json` in the R1 folder records
  the settled reads (23:04:32.642693 UTC and 23:14:56.468760 UTC, both 0.007482165 USD) and the manifest SHA-256.
- **Evidence.** `tests/test_injecagent_reconciliation.py`: missing file, mismatched value, manifest-hash binding,
  unstable reads, uncommitted files, other statuses, and the dry-run check.
- **Status.** Proposed on its own branch from `phase3/confirmatory-protocol`, not merged at the time of writing.

## D3. R2 interrupted at 571/980; raw run folder lost

- **Change.** None to the protocol. The R2 run stopped at about 571 of 980 episodes after a process kill at roughly 30
  minutes. Its raw run folder is lost: it is not on the owner's computer, not in the run environment, and not on any git
  ref. No episode from the interrupted run is analyzed. The R2 rerun is a full run in a fresh folder.
- **Reason.** The launcher staged `progress.log` and `episodes.jsonl` only when a run finished, so the kill lost the
  record. The launcher now runs detached (`--detach`, `setsid -f nohup`), commits `progress.log` and `episodes.jsonl`
  every 10 episodes, and pushes each checkpoint to `runs/<run folder>` on the remote. The validation of arguments runs
  before the launch, so an invalid launch fails at once.
- **Spend.** `/auth/key` pre-R2: 0.007482 USD. Post-kill: 0.068159 USD. Exact difference: 0.060677 USD. Runner-reported
  spend: 0.061056 USD. Later read: 0.068611519 USD, so +0.000453 USD after the kill, **unattributed**. No cause is
  assigned; the provider's usage breakdown is needed before this entry closes. The spend counts against the campaign cap.
- **Campaign total.** Cap 0.50 USD. Projected: 0.007482165 (R1 settled) + 0.060677 (R2 interrupted) + 0.147932 (R2
  rerun, expected) + 0.106380 (R3, expected) = **0.322471 USD**. R3 has not run.
- **Evidence.** `tests/test_injecagent_detached_launch.py`, 12 tests. Failing counts by reference launcher: 12 of 12 on
  the base `6b309d2`; 6 of 12 on `5aa352e`; 1 of 12 on `b188675` (the stalled-push test, which waits about 20 s there
  and passes in about 2 s with the timeout). Reconciliation: the earlier figures of 11/11 on `6b309d2` and 5/11 on
  `5aa352e` were measured on the 11-test version of the file, before the stalled-push test was added. The 12-test file
  gives the counts above. Every git call made while checkpointing has a 60 s timeout and runs with
  `GIT_TERMINAL_PROMPT=0`; a stalled or failed push is logged as FAILED and the run continues.
- **Status.** Open. The R2 rerun has not started. Owner decision required before it starts.

## D4: second R2 attempt stopped at 109/980 by a transport error the launcher did not handle

- **What happened.** The R2 run `experiments/external/20261012T100745Z/` was launched detached at 10:07:45Z (the
  `/auth/key` pre-run read is in `auth_key_pre.json`). Its authorizing explicit "RUN R2" was the owner message at
  **09:56:32Z**; the earlier "RUN R2" at 09:47:44Z was before the gates were met and did not launch anything. The
  launch at 10:07:45Z followed the 09:56:32Z message. A later "RUN R2" at 10:49:11Z came after the run had already
  stopped and launched nothing.
- **Cause.** `urllib` response reads raise `http.client.IncompleteRead`, which is an `http.client.HTTPException`, not an
  `OSError`. `run_episode` caught only `OSError`, so the exception escaped `run_study`, which recorded
  `ERROR: IncompleteRead` and re-raised. The run ended at 109 of 980 episodes, 10:13:20Z (`finished_utc` in
  `run_manifest.json`). This is a launcher bug, not a provider failure.
- **Evidence kept.** The full run folder is archived unchanged, commit `8d48586` on `runs/20261012T100745Z` (PR #141,
  not merged), including `launcher_stdout.log` with the traceback. Remote checkpoints reached 100 episodes; commit `8d48586`
  adds the remaining 9 episodes and the logs.
- **Spend.** `/auth/key` pre-run 10:07:45Z: 0.068611519 USD. Reads at 10:49:33Z and 10:58:05Z: 0.079647838 USD each.
  Run delta: 0.011036319 USD. The local episode-cost sum is 0.010903 USD; the 0.000133 USD gap is not attributed. The
  likely cause is the request in flight when the read failed, but this is unconfirmed. The earlier D3 drift of
  +0.000453 USD also remains unattributed.
- **Fix.** `run_episode` now catches `(OSError, http.client.HTTPException)` and records the episode as
  `transport:<ExceptionName>`. The run continues. The truncated episode is billed by the provider, so the reconciliation
  expects its cost in `/auth/key`. Test: `test_a_truncated_response_is_a_transport_error_for_that_episode_and_the_run_continues`
  in `tests/test_injecagent_detached_launch.py`; it fails on `9260ed6` and passes with the fix.
- **Campaign total (recomputed).** Cap 0.50 USD. Account spend so far: 0.079647838 USD (read at 10:58:05Z; not yet
  settled under the D1 rule, which needs two reads at least 10 minutes apart that agree within 1e-6). Projected:
  0.079647838 (spent) + 0.147932 (R2 full rerun, expected) + 0.106380 (R3, expected) = **0.333960 USD**, leaving
  0.166040 USD of headroom. The D3 projection of 0.322471 USD omitted the D4 partial run.
- **Status.** Open. R2 has not been restarted. The R2 rerun needs a fresh explicit "RUN R2" and is held until the
  launcher fix is merged.

## D5: third R2 attempt stopped at 90/980; the cloud environment was lost

- **What happened.** The R2 run `experiments/external/20261012T115338Z/` (label `R2_rerun_20261012`, soft cap 0.2978, HTTP cap 980) started at 11:53:38Z and stopped after 90 of 980 episodes. The last `progress.log` line is 11:57:11Z. The cloud container that ran it was lost, and no process (PID 793) or local copy of the run folder survived.
- **Cause.** Not a launcher exception: no traceback was recovered. The stop is unexplained. The launcher's checkpoint did not commit `run_manifest.json` or `launcher_stdout.log`, so neither was recovered. The checkpoint fix is in `claude/r2-checkpoint-manifest-stdout` (PR pending review).
- **Evidence kept.** Commit `a2a1f92` on `runs/20261012T115338Z` holds `episodes.jsonl` (90 lines) and `progress.log`, unchanged. `run_manifest.json` and `launcher_stdout.log` are not on the branch. This PR records the run as interrupted and does not change its files.
- **Spend.** `/auth/key` read after 20:02Z: 0.089485879 USD. Baseline read at 10:58:05Z: 0.079647838 USD. Difference: 0.009838041 USD. Runner-reported spend at the last progress line: 0.008602 USD. The gap of 0.001236 USD is **unattributed**. The reading is not yet settled under the D1 rule (two reads at least 10 minutes apart that agree within 1e-6).
- **Campaign total (recomputed).** Cap 0.50 USD. Spent: 0.089485879 USD. Projected: 0.089485879 (spent) + 0.147932 (R2 full rerun, expected) + 0.106380 (R3, expected) = **0.343798 USD**, leaving 0.156202 USD of headroom. The R2 rerun estimate does not subtract the 90 episodes already paid, so the total is conservative.
- **Protocol.** Retries stay R-0 (`docs/protocols/CONFIRMATORY_PROTOCOL_DRAFT_v0.1.md`, "Retries: R-0"). No change to the frozen protocol is made here.
- **Status.** Open. R2 has not been restarted. The next launch needs an explicit "RUN R2" from the owner and is planned to run on the owner's own machine, not in a cloud session.

## D6: OpenRouter key rotated after HTTP 401; R2 pre-launch on owner's WSL

- **What happened.** After D5, the original campaign OpenRouter key returned HTTP 401 on `/auth/key`. It was replaced by a new key. The key value is never recorded.
- **Old-key spend.** Last documented in D5: 0.089485879 USD (unsettled read after 2026-10-12 20:02Z; old key no longer readable). This amount is carried into campaign cap accounting.
- **New key baseline.** Settled baseline per the D1 rule on the owner's WSL machine: read 1 2026-10-14T07:52:31.208Z usage 0 limit 0.41; read 2 2026-10-14T08:03:39.560Z usage 0 limit 0.41 (668 s apart, agree). The key limit was set to 0.41 USD by the owner so that old-key spend + new-key limit = 0.499485879 USD < 0.50 USD campaign cap; the key limit is the hard backstop.
- **Non-baseline reads.** Earlier reads on 2026-10-13 22:08:50Z and 22:19:14Z were taken in a Cursor cloud environment on a key showing limit 0.8 USD; that key is not the one used for R2 and those reads are not the R2 baseline.
- **Launcher gap.** `campaign_budget_check` sums only reconciled `--prior-run-dir` folders (R1 via `RECONCILIATION.json`); it cannot represent the old-key spend or the unreconciled D3/D4/D5 partial runs. Therefore cap compliance for R2 is ensured by (a) the 0.41 key limit and (b) a manual ledger: 0.089485879 + R2 soft cap 0.2978 = 0.387285879 < 0.50; R2 expected 0.147932.
- **R2 pre-launch.** On the owner's WSL: HEAD `94a5ede`, InjecAgent `f19c9f2` verifier MATCH, R2 plan SHA-256 `d522b21bfb35c3c80d763742aee449dda1ce35442cca73bb2bd9d0bc99d6c5df` (150 cases), dry run with `--expected-usage-usd 0 --estimate-usd 0.147932 --soft-cap-usd 0.2978 --campaign-cap-usd 0.50` passed. R2 not launched; requires the owner's explicit text `RUN R2`.
- **R3.** R3 is decided only after R2's settled cost.
- **Status.** PROPOSED / pending owner review.

## D7: R2 actual cost below estimate (launcher cost check failed); four transport failures

- **What happened.** R2 (run folder `experiments/external/20261014T142921Z`, code `862ee09`, plan SHA-256 `d522b21b?c6d5df`, seed 20261001) sent 980/980 episodes between 2026-10-14T14:29:21Z and 16:22:55Z. The launcher's post-run check refused: `/auth/key spend 0.110979 differs from the estimate scaled to 980 of 980 episodes (0.147932) by more than 5%`. Manifest status is `AUTH_MISMATCH`. The check was not bypassed and the run folder is committed as written by the launcher.
- **Cost.** Pre-run usage 0 (settled baseline, D6). Post-run usage 0.110979328 USD. Settle reads: 2026-10-14T17:10:38Z usage 0.110979328, 2026-10-14T17:22:00Z usage 0.110979328 (682 s apart, agree; key limit 0.41). Sum of per-episode recorded costs: 0.110979457 USD (difference from /auth/key 1.29e-7 USD). Final R2 cost: **0.110979328 USD**.
- **Estimate gap.** Actual is 0.036953 USD (?25.0%) below the pre-registered estimate 0.147932. The spend is within the soft cap (0.2978) and campaign cap. The mismatch reflects an over-estimate of per-request cost, not missing or extra requests: http_calls = episodes_sent = 980, matching the HTTP cap.
- **Transport failures.** Four episodes, case `dh-0218` for qwen/qwen3.8-flash, arms A0, A0_REP, NOINJ, SPOT_TOOL (2026-10-14T15:33:32Z?15:34:05Z), recorded `error=transport:gaierror` (DNS resolution failure on the owner's network), no HTTP response, no cost (`unpriced_episodes: 4`). Per the transport-error rule and R-0 (no retries) they were logged and the run continued. They are **not** model or defense outcomes and must be excluded from outcome denominators and reported as missing (4/980 = 0.41%, below the 5% error limit).
- **Campaign ledger.** Old key 0.089485879 + R1 (in old-key total) + R2 0.110979328 = 0.200465207 USD of 0.50 USD.
- **Status.** PROPOSED / pending owner review.
