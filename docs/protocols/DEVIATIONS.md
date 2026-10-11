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
