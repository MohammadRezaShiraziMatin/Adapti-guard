# Corrections and deviations: R1 pilot cost basis

Status: correction to `R1_PILOT_NOTE.md` (commit `d66fae6`). This file records what changed and why. It does not edit the R1 run folder, which is committed unchanged.

## 1. Cause: the post-run `/auth/key` read was taken before usage settled
- The launcher read `/auth/key` once, immediately after the R1 run ended (22:55:20 UTC). That read gave usage 0.006742489 USD.
- Two later reads of the same key, with at least 10 minutes between them, both gave usage 0.007482165 USD:
  - 2026-10-11T23:04:32 UTC: 0.007482165 USD (limit 0.6 USD).
  - 2026-10-11T23:14:56 UTC: 0.007482165 USD (limit 0.6 USD).
- The settled value agrees with the runner's own recorded spend for R1 (0.007482180 USD) to within 0.000000015 USD.
- Conclusion: the value read at 22:55:20 UTC was taken before OpenRouter usage had settled. R1's settled `/auth/key` cost is 0.007482165 USD.

## 2. OLD → NEW values

| Item | OLD (registered snapshot rule, read at 22:55:20) | NEW (settled, read at 23:04:32 and 23:14:56) |
|---|---|---|
| R1 cost, `/auth/key` basis (USD) | 0.006742489 | 0.007482165 |
| c = R1 cost ÷ 60 (USD per llama episode) | 0.00011237 | 0.00012470 |
| R2 llama, 490 episodes (USD) | 0.055064 | 0.061104 |
| R2 qwen, 490 episodes, registered rate 0.0001772 (USD) | 0.086828 | 0.086828 (unchanged) |
| R2 expected total (USD) | 0.141892 | 0.147932 |
| R3 gpt, 72 episodes, registered rate 0.0014775 (USD) | 0.106380 | 0.106380 (unchanged) |
| R2 + R3 expected (USD) | 0.248272 | 0.254312 |
| Campaign total: R1 + R2 + R3 (USD), cap 0.50 | 0.255014 | 0.261795 (still below 0.50) |

- The R2 `--expected-usage-usd` value (snapshot 0 plus R1's settled cost) becomes 0.007482165, not 0.006742489.
- The registered R2 soft cap (0.2978 USD) and R3 soft cap (0.1822 USD) are unchanged. They are registered values.

## 3. Still open: R1 remains AUTH_MISMATCH
- Against the provisional estimate 0.0107 USD, the settled R1 cost 0.007482165 USD is 30.1% lower. That is still outside the 5% rule.
- R1's recorded status is `AUTH_MISMATCH`, and it stays that way. The run folder is not edited.
- The provisional estimate was designated for recalibration from the pilot (protocol §9A item 3). The recalibration above uses the settled cost.

## 4. Deviation from the registered snapshot rule (for the paper)
- The registered rule reads `/auth/key` after the run and treats the difference from the pre-run snapshot as the cost basis.
- In R1 the post-run read was taken before usage settled, and that single read was not stable. The reconciliation therefore used a value that did not match the settled cost.
- This is a deviation from the rule as implemented. It must be reported in the manuscript and in the OSF text. It is not corrected here by changing the rule, the frozen protocol or the run folder.
- Proposed launcher change for R2 and R3, to take the post-run read only after usage is stable: see the separate pull request that proposes it.

## Not changed by this file
- The frozen protocol file, `docs/protocols/CONFIRMATORY_PROTOCOL_DRAFT_v0.1.md`.
- The OSF registration text.
- The R1 run folder, `experiments/external/injecagent_R1_pilot_20261011T225134Z/`.
- Any run. R2 and R3 have not started.
