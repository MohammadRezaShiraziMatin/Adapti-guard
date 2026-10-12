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
