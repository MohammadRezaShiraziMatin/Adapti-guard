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
