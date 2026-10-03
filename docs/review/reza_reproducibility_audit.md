# Independent E2 reproducibility spot-check

Read-only check. No evidence, manuscript or script was modified; no experiment was rerun.

## Repository commit checked

`main` @ `e1807f040c93e183d7846d4d50fd90e0d99f9e6a`

## Files inspected

- `experiments/harness_v2/HARNESS_V2_EXPLORATORY_20260930/episodes.jsonl` (468 episodes, all `COMPLETE`; 288 attack episodes, 72 per arm) and `exploratory_analysis.json`, `run_manifest.json`
- `scripts/make_fig1_scoring_flip.py` (rule definitions only; counts below were recomputed independently from the raw episodes, not by running this script)
- `docs/paper/negative_result/figures/fig1_scoring_flip.csv`
- `docs/paper/negative_result/SECTIONS_5_6_EXPERIMENTS_RESULTS.md` §6.2, `MANUSCRIPT_DRAFT_v1.md`, `NUMBERS_LEDGER.md`

## Method

Attack episodes = `status == COMPLETE` and `scenario_id` not starting with `benign_`.
- R1 (proposed): `C2.exec_success is True`
- R2 (executed): `C2.exec_executed is True`, denominator all 72 per arm
- R3 (blocks excluded as invalid): as R2, rows with `C2.C2_state == INVALID_NOT_DELIVERED` removed from numerator and denominator

## Results

Recomputed from `episodes.jsonl`: A0, B3, CORE, TOOLDENY.
R1 = 66, 65, 36, 65 of 72. R2 = 66, 65, 36, 0 of 72. R3 = 65/71, 65/72, 36/36, 0/69.

| Group | Claimed | Recomputed | Result |
|---|---|---|---|
| R1 A0 | 66/72 | 66/72 | MATCH |
| R1 B3 | 65/72 | 65/72 | MATCH |
| R1 CORE | 36/72 | 36/72 | MATCH |
| R1 TOOLDENY | 65/72 | 65/72 | MATCH |
| R2 A0 | 66/72 | 66/72 | MATCH |
| R2 B3 | 65/72 | 65/72 | MATCH |
| R2 CORE | 36/72 | 36/72 | MATCH |
| R2 TOOLDENY | 0/72 | 0/72 | MATCH |
| R3 A0 | 66/72 | 65/71 | MISMATCH |
| R3 B3 | 65/72 | 65/72 | MATCH |
| R3 CORE | 36/36 | 36/36 | MATCH |
| R3 TOOLDENY | 0/72 | 0/69 | MISMATCH |

No group is NOT VERIFIABLE: all inputs are in the public repository.

## Discrepancies

- R3 A0: the requested list says 66/72, the data give 65/71. One A0 episode is `INVALID_NOT_DELIVERED` and is excluded by the R3 rule; it was an executed one, so numerator and denominator both drop by one.
- R3 TOOLDENY: the requested list says 0/72, the data give 0/69. Three TOOLDENY episodes are `INVALID_NOT_DELIVERED` and are excluded.

Both differences are in the task's list, not in the repository: the manuscript (§6.2 table, row "same, blocks excluded as invalid": 65/71, 65/72, 36/36, 0/69), `fig1_scoring_flip.csv` and the raw episodes all agree with each other. (R3 CORE 36/36 follows from 36 of its 72 episodes being excluded as blocked.) No manuscript number needs changing. The 0/72 and 66/72 values in the request appear to be the R2 values carried into the R3 row.

## Conclusion

10 of the 12 requested counts reproduce exactly from the raw E2 episodes. The other 2 (R3 A0, R3 TOOLDENY) do not match the requested figures but do match what the manuscript and CSV already report (65/71 and 0/69), so E2 as published is internally consistent and reproducible; only the checklist values were wrong. Scope limit: this verifies counts from the stored episode log, not that the log itself was produced as described (no live runs were repeated).
