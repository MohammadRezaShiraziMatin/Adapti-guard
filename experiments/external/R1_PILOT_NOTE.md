# R1 pilot: post-pilot note

Status: post-pilot parameters recorded. Not a confirmatory result. No run was repeated and no R2 or R3 run has started.

## What R1 did
- Run folder: `experiments/external/injecagent_R1_pilot_20261011T225134Z/` (committed unmodified).
- R1 completed 60 of 60 episodes with 0 provider errors (all HTTP 200).
- The launcher ended with status `AUTH_MISMATCH` because the `/auth/key` spend (0.006742489 USD) differs from the provisional estimate scaled to 60 episodes (0.0107 USD) by more than 5%.

## Why this is not a run failure
- The estimate 0.0107 USD is provisional. The frozen protocol (§9A item 3, line 195) designates it for recalibration from the pilot, using the pilot's `/auth/key` cost.
- The 5% rule is a check on the `/auth/key` snapshot difference, as registered. The runner's own cost is reported only for comparison.

## Post-pilot parameters (registered formula)
- Pilot cost basis: `/auth/key` spend = 0.006742489 USD (pre usage 0, post usage 0.006742489).
- Per-episode llama cost: c = 0.006742489 / 60 = 0.00011237 USD per episode.
- R2 llama (490 episodes, A0, A0_REP, SPOT_TOOL, NOINJ): 490 × c = 0.055064 USD.
- R2 qwen (490 episodes, committed rate 0.0001772 USD per episode): 0.086828 USD.
- R2 expected total: 0.141892 USD.
- R3 gpt (72 episodes, committed rate 0.0014775 USD per episode): 0.106380 USD.
- R2 + R3 expected: 0.248272 USD.
- Pilot + R2 + R3 expected: 0.255014 USD, below the 0.50 USD campaign cap.

## Runner cost, for comparison only
- Runner-recorded spend: 0.007482180 USD, about 11.0% above `/auth/key`. It is not the cost basis.
