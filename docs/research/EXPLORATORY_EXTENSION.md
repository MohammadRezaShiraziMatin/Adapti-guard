# EXPLORATORY model extension of the InjecAgent case study (PROPOSED)

Status: **PROPOSED / EXPLORATORY**. Outside the frozen confirmatory protocol
(`docs/protocols/CONFIRMATORY_PROTOCOL_DRAFT_v0.1.md`, unchanged). Nothing here changes the confirmatory analysis,
its hypotheses or its results. Results from these runs must be reported as exploratory. No deviation D7, D8 or D9 is
approved by this note.

## What
- Three additional targets with the R2 design (arms A0, A0_REP, SPOT_TOOL on the 150 retained cases, NOINJ on the
  first 40 sorted ids; temperature 0, max_tokens 512, max_turns 1, R-0 no retries; transport errors are logged, the
  run continues and they are excluded from outcome denominators):
  `anthropic/claude-haiku-5.5`, `google/gemini-3.1-flash-lite`, `deepseek/deepseek-v4-flash`, each with reasoning disabled.
  490 episodes each.
- SPOT_TOOL for the R3 target `openai/gpt-5.6-sol` on the 72 R3 cases (R3 ran A0 only). 72 episodes.
- Plans: `scripts/build_exploratory_plan.py` derives `build/expl_{haiku,gemini,deepseek,gpt_spot_tool}.json` from the
  launcher plans of R2 and R3 and refuses unless those match the plan SHA-256 in the R2/R3 manifests.

## Launcher
- `--run EXPL-<name>` is accepted only when the plan has `exploratory: true`, the same `run` name and an EXPLORATORY
  label; an exploratory plan cannot be run as R1/R2/R3. The R1/R2/R3 checks are unchanged.
- An EXPL- run needs `--campaign-ledger docs/research/CAMPAIGN_LEDGER.json`. All other gates are unchanged: soft cap,
  HTTP cap, campaign cap, pre/post `/auth/key` checks, detached launch, checkpoint push. Manifests carry
  `exploratory: true` and the EXPLORATORY label.

## Budget (decided by Matin, 2026-10-15)
- Campaign cap for EXPLORATORY runs raised from 0.50 to **1.50 USD**. The confirmatory cap stays 0.50 USD.
- Prior spend 0.313657207 USD (old key 0.089485879, including R1; R2 0.110979328; R3 0.113192), recorded in
  `docs/research/CAMPAIGN_LEDGER.json`, with each entry re-checked against committed run evidence.
- Proposed soft caps (USD): haiku 0.05, deepseek 0.04, gemini 0.12, gpt SPOT_TOOL 0.20.
  Estimates (`scripts/estimate_exploratory_cost.py`): 0.0426, 0.0319, 0.1126, 0.12 to 0.19.
- The current OpenRouter key limit (0.41 USD, D6) with usage 0.224171328 leaves about 0.186 USD on the key. The
  soft caps sum to 0.41 USD, so the key limit (owner action) bounds these runs unless it is raised.

## Open
- Each live run needs explicit owner approval.

## EXPL-deepseek closeout (PROPOSED note, not approved)
- Run `experiments/external/20261015T005504Z` (code 0a19f33, plan sha256 a0db0645...bd296), EXPLORATORY.
  Manifest status **AUTH_MISMATCH**, stop reason **STOPPED_SOFT_CAP** (soft cap 0.04 USD). Not relabelled.
- 463/490 episodes sent; 27 unsent (cases ds-0480, ds-0481, ds-0492, ds-0498, ds-0501, ds-0505, ds-0530, ds-0537,
  ds-0541; arms A0, A0_REP, SPOT_TOOL each). Completed without error: A0 139, A0_REP 141, SPOT_TOOL 140, NOINJ 40.
- 3 errors, all `transport:timeout`, unpriced: dh-0445 A0, ds-0039 SPOT_TOOL, ds-0326 A0. Not retried (R-0).
- Cause of AUTH_MISMATCH: the launch estimate (0.0319 USD) was too low; the actual cost was about 0.0000870 USD
  per completed episode, so 490 episodes needed about 0.0426 USD and the 0.04 soft cap stopped the run.
- Settle reads 2026-10-15T07:41:26Z and 07:52:00Z: usage 0.264481718 (limit 1.5), equal to the manifest post-run
  value. Settled spend 0.040310390 USD vs runner 0.040010062 USD: difference 0.000300328 USD, unattributed (the 3
  timeouts may have been billed; no record shows it). The ledger counts the settled value; new total 0.353967597 USD.
- Top-up (PROPOSED, needs explicit approval before any live run): `EXPL-deepseek-topup`, exactly the 27 unsent
  episodes, built by `python scripts/build_exploratory_plan.py --topup deepseek --write`. The 3 errored episodes are
  excluded. Proposed soft cap 0.005 USD (estimate 0.00235 USD).

## EXPL-deepseek-topup closeout (PROPOSED note, not approved)
- Run `experiments/external/20261015T084221Z` (code 5150299, plan sha256 d624255e...0a39), EXPLORATORY, authorized
  by Matin ("RUN EXPL-deepseek-topup", 2026-10-15 08:31Z). Manifest status **AUTH_MISMATCH** (not relabelled).
- 27/27 sent (the unsent episodes of EXPL-deepseek), 0 errors, 0 unpriced. The 3 errored parent episodes
  (dh-0445 A0, ds-0039 SPOT_TOOL, ds-0326 A0) were not retried and stay missing.
- Settle reads 2026-10-15T09:49:01Z and 09:59:38Z: 0.267042028 (limit 1.5), equal to the manifest post-run usage.
  Settled spend 0.002560310 USD, runner 0.002560318 USD. Ledger total 0.356527907 USD.

## Re-estimates for the remaining runs (PROPOSED, not approved)
DeepSeek actual: 0.0425704 USD over 487 priced episodes. Scaled to the 490-episode plan that is 0.042849 USD, versus the
token method's 0.031921 USD, so the token method under-estimated by a factor of 1.342. Two methods are shown below.
(1) Token method x 1.342. (2) DeepSeek actual mean cost per arm x (model price / DeepSeek price) on the R2 token basis.
The proposed soft cap is about 1.5x the larger of the two.

| run | episodes | token method | token x 1.342 | DeepSeek x price ratio | proposed soft cap |
|---|---|---|---|---|---|
| EXPL-haiku | 490 | 0.042558 | 0.057128 | 0.056564 | 0.086 |
| EXPL-gemini | 490 | 0.112629 | 0.151188 | 0.149306 | 0.23 |
| EXPL-gpt-SPOT_TOOL | 72 | 0.188874 | 0.253534 | 0.267861 | 0.40 |

Ledger 0.356527907 USD + these caps (0.716 USD) = 1.072 USD, which is within the 1.50 USD exploratory cap. Caveat: the
completion length of another model may differ from DeepSeek's, so these are estimates, not bounds.

## EXPL-haiku closeout (PROPOSED note, not approved)
- Run `experiments/external/20261015T103612Z` (code b4bfdf6, plan sha256 016a84e9...c511), EXPLORATORY, authorized by
  Matin ("RUN EXPL-haiku"). Manifest status **AUTH_MISMATCH** (not relabelled). The run stopped with
  **STOPPED_SOFT_CAP** at 2026-10-15T10:54:06Z (soft cap 0.086).
- 392/490 sent, 98 unsent, 0 errors, 0 unpriced. Completed per arm: A0 118, A0_REP 117, SPOT_TOOL 117, NOINJ 40.
- Cause: the 0.0572 estimate (DeepSeek-calibrated) was too low. Haiku cost about 0.000220 USD per episode, about 2.5x
  DeepSeek. The launcher refused: /auth/key spend 0.086209 vs the scaled estimate 0.045760 (more than 5% apart).
- Settle reads 2026-10-15T11:07:44Z and 11:18:19Z: 0.353251428 (limit 1.5), equal to the manifest post-run usage.
  Settled spend 0.086209400 USD, equal to the runner's spend. Ledger total 0.442737307 USD.

## Haiku top-up and re-estimates (PROPOSED; caps need Matin's approval)
- `EXPL-haiku-topup`: the 98 unsent episodes (A0 32, A0_REP 33, SPOT_TOOL 33). Build it with
  `python scripts/build_exploratory_plan.py --topup haiku --write` (plan sha256 ce17ae16...b412).
  Estimate from Haiku's actual cost per arm: 0.022054 USD. Proposed soft cap 0.033.
- Gemini and gpt SPOT_TOOL: actual cost per arm x price ratio, from Haiku and from DeepSeek; the higher is used.

| run | from DeepSeek | from Haiku | proposed soft cap (about 1.5x the higher) |
|---|---|---|---|
| EXPL-gemini | 0.149306 | 0.284143 | 0.43 |
| EXPL-gpt-SPOT_TOOL | 0.267861 | 0.546052 | 0.82 |

- Projection: ledger 0.442737 plus the expected costs of the remaining runs (0.022 + 0.284 + 0.546) = 1.295 USD, within
  1.50. But the ledger plus all three soft caps (0.033 + 0.43 + 0.82) = 1.726 USD, which is over 1.50. The gate checks
  prior spend plus one run's cap, so run in this order: top-up, then gemini, then gpt (ledger about 0.75 after
  gemini). Then a gpt soft cap of 0.82 would be refused (0.75 + 0.82 > 1.50), and the largest gpt cap that passes is
  about 0.75. Options for Matin: (a) a gpt cap of about 0.70 (1.28x its estimate; it may stop early, then a top-up),
  (b) raise the exploratory campaign cap, or (c) drop or shrink a run. No cap is changed here.

## Exploratory campaign cap change (PROPOSED; Matin's choice, 2026-10-15)
- OLD: 1.50 USD. NEW: **2.00 USD**. Applies to EXPLORATORY EXPL- runs only; the confirmatory cap stays 0.50 USD.
- Evidence: Matin chose this after EXPL-haiku, because the soft caps did not fit under 1.50 (see above). He reports
  raising the OpenRouter key limit to 2.0. /auth/key read 2026-10-15T11:41:33Z: limit 2, usage 0.353251428 (unchanged).
- Recorded in `docs/research/CAMPAIGN_LEDGER.json` cap_decisions (exploratory cap_usd 2.00). Takes effect for the launcher
  gate when this PR is merged.
- Soft caps unchanged: EXPL-haiku-topup 0.033, EXPL-gemini 0.43, EXPL-gpt-SPOT_TOOL 0.82. Worst case, all three in
  sequence: 0.442737307 + 0.033 + 0.43 + 0.82 = 1.725737307 USD, within 2.00 (margin 0.274).
- Supersedes the sentence "Campaign cap for EXPLORATORY runs raised from 0.50 to 1.50 USD" above, once approved.

## EXPL-haiku-topup closeout (PROPOSED note, not approved)
- Run `experiments/external/20261015T122507Z` (code 552472b, plan sha256 ce17ae16...b412), EXPLORATORY, authorized by
  Matin ("RUN EXPL-haiku-topup"). Manifest status **AUTH_MISMATCH** (not relabelled). The launcher refused because
  /auth/key spend 0.024156 was 9.5% above the 0.022054 estimate (more than the 5% tolerance).
- 98/98 sent, 0 errors, 0 unpriced, 0 unsent.
- Settle reads 2026-10-15T12:46:41Z and 12:57:01Z: 0.377407028 (limit 2.0), equal to the manifest post-run usage.
  Settled spend 0.024155600 USD, equal to the runner's spend. Ledger total 0.466892907 USD.
- Haiku completeness (EXPL-haiku + top-up): 490/490 planned (case, arm) pairs have one error-free record, with no
  duplicates. A0 150, A0_REP 150, SPOT_TOOL 150, NOINJ 40; 150/150 cases complete.
