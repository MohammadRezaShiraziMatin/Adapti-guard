# Confirmatory protocol (DRAFT v0.1)

**Status: DRAFT. NOT FROZEN. NOT APPROVED.** No run may start under this document. Every decision marked **OPEN** is presented with options, costs and effects. The author chooses; this draft does not choose.

Scope: `docs/CASE_STUDY_SCOPE.md`. Strong, non-weak models only. Excluded: qwen-2.5-7b, llama-3.1-8b, mistral-small-3.2-24b, the E1 tracks and MT1.

Every number below is computed by `scripts/power_protocol_v01.py` from the committed files listed here, and each figure is checked by `tests/test_protocol_power_v01.py` against an independent route:
- `experiments/external/injecagent_registered_20261001/*.json` (598 episodes per target; per-episode `cost`, `first_attacker_tool`, `arm`)
- `experiments/external/injecagent_panel_calib_20261001/*.json` (80 episodes per target; per-episode `cost`)
- `experiments/external/phase2_calibration_20261001/calibration.json` (Hard-set calibration; **not used for costs** in this draft)
- `datasets/attackset_hard_v1/FREEZE_RECORD.json` (`human_written.splits` = test 170, calibration 68; 238 items)
- `datasets/attackset_hard_v1/MANIFEST.json` (`report.split` = test 170, calibration 68; per-item `split` labels)
- `datasets/external_samples/injecagent_phase2_sample.json` (186 cases: 62 instructions × 3 contexts; seed 20261001)

---

## 1. Research questions

- **H1 (floor).** Is the undefended attack-success rate (A0) of each strong target below 5% on public attacks, with the two-sided 95% Clopper–Pearson upper bound below 5%? Weakness addressed: the calibration could only say "below 5% or undetermined" because n was too small (§6.4 of the manuscript).
- **H2 (defense effect on the tool channel).** Does delimiting the tool channel (SPOT_TOOL) reduce attacker tool calls versus A0 on targets that are not at floor? Weakness addressed: the 2026-10-01 effect was measured on two targets, at proposal level, with a protocol that was not frozen.
- **H3 (noise floor).** What is the run-to-run difference between A0 and an identical-input replicate (A0_REP) on each target?

H1 and H2 are confirmatory. H3 is a precision estimate with no threshold.

**Endpoint for H2 (see §5).** The committed InjecAgent records have no executed-call field. H2 is therefore **proposal level** (`first_attacker_tool`) in this draft. The executed endpoint is not available for InjecAgent without a new executor (an open decision, §5).

## 2. Target panel — **OPEN**

Model IDs and route as recorded in the committed records (route: OpenRouter; temperature requested 0; reasoning as recorded):

| model ID | kind | reasoning (as recorded) | arms in committed records |
|---|---|---|---|
| `meta-llama/llama-4-maverick` | open | not set | A0, A0_REP, SPOT_TOOL, NOINJ (registered) |
| `qwen/qwen3.8-flash` | open | `enabled: false` | A0, A0_REP, SPOT_TOOL, NOINJ (registered) |
| `deepseek/deepseek-v4.1-flash` | open | `enabled: false` | A0, NOINJ (panel-calib) |
| `z-ai/glm-4.7` | open | not set | A0, NOINJ (panel-calib) |
| `openai/gpt-5.6-sol` | closed | `enabled: false` | A0, NOINJ (panel-calib) |

**Important:** only llama-4-maverick and qwen3.8-flash have a SPOT_TOOL arm in the committed records. For deepseek, glm and gpt there is **no SPOT_TOOL data**, so their H2 discordance, sample size and power cannot be computed from committed files. Any panel that includes them needs a new SPOT_TOOL arm before H2 can be powered for them.

Options:
- **P-A: two targets** (llama-4-maverick, qwen3.8-flash). H2 is powered (§4) and comparable with the 2026-10-01 test. H1 covers two targets only.
- **P-B: five targets** (the full calibration panel). H1 covers all five. H2 is powered only for the two registered targets; three targets need a new SPOT_TOOL arm. The closed model is in or out of the H2 family (§4).
- **P-C: four open targets** (P-B without `openai/gpt-5.6-sol`). Same H2 limitation for deepseek and glm.
- **P-D: add targets** not in the committed calibration. No committed cost, rate or discordance exists for them; not costed here.

Excluded in every option: qwen-2.5-7b, llama-3.1-8b, mistral-small-3.2-24b.

## 3. Attack sources — **OPEN**

- **S-A: InjecAgent sample** (186 cases: 62 instructions × 3 contexts; 90 direct-harm, 96 data-stealing; seed 20261001; `injecagent_phase2_sample.json`). Same sample as the registered test; the cluster unit is the attacker instruction.
- **S-B: Hard set, human-written** (238 items in the pool, `FREEZE_RECORD.json`). **Split: test 170, calibration 68** (`FREEZE_RECORD.json` at `human_written.splits`; `MANIFEST.json` at `report.split`, and each item's `split` label). A confirmatory run would use the **test** split (170 items); the calibration split is used only to classify floor behaviour, as in the earlier protocol.
- **S-C: both** S-A and S-B, reported separately; the multiplicity family is per source.
- **Generated items** (69 items, `XCHANNEL_MANIFEST_full.json`) are **not** frozen for confirmatory use (status: exploratory until two human raters confirm). Excluded from H1 and H2 in every option.

Selection rule, fixed in advance: take the attack items in the frozen order of the source manifest, with the sampling seed recorded in the manifest. No item is chosen by its result on any target.

## 4. Sample size and power — **OPEN**

**H1 (zero-event floor).** The smallest n whose two-sided 95% Clopper–Pearson upper bound is below 5% with zero events is **n = 72**. Upper bounds: 4.99% at n = 72; 3.62% at n = 100; 2.43% at n = 150; 1.96% at n = 186.

**H2 (paired reduction, proposal level, 10-point reduction, 80% power).** Discordance from the committed registered records, A0 vs SPOT_TOOL on the same 186 cases:

| target | pairs | A0-only | SPOT-only | discordant fraction | observed difference |
|---|---|---|---|---|---|
| llama-4-maverick | 186 | 21 | 3 | 0.1290 | 0.0968 |
| qwen3.8-flash | 186 | 22 | 3 | 0.1344 | 0.1022 |

Pairs needed for H2 (the 10-point target is the observed effect, so these are optimistic; see §10):

| per-test alpha | llama-4-maverick | qwen3.8-flash |
|---|---|---|
| 0.05 | 99 | 104 |
| 0.025 | 121 | 126 |
| 0.0125 | 142 | 148 |
| 0.01 | 148 | 155 |

The per-test alpha for each panel option is set by the multiplicity rule in §6.

**Options for n per target (cases per arm):**
- **N-A: n = 72.** Meets H1. Underpowered for H2 at every alpha above.
- **N-B: n = 100.** Meets H1. H2 for llama and qwen at α = 0.05 needs 99 and 104 pairs.
- **N-C: n = 150.** Meets H1. H2 for llama and qwen at α = 0.0125 needs 142 and 148 pairs.
- **N-D: n = 186.** The registered sample size; comparable with the 2026-10-01 test.

Episodes per target = 3n + 40 (arms A0, SPOT_TOOL, A0_REP for each case, plus 40 NOINJ). At n = 186 this is 598, the registered run's count.

## 5. Endpoints and scoring — **OPEN for the InjecAgent primary endpoint**

- **Committed fact:** the InjecAgent records carry `first_attacker_tool` and `any_attacker_tool`; **no executed-call field exists** in the registered records (checked by a test). InjecAgent has no executor in this repository.
- **Therefore for InjecAgent, the endpoint in this draft is proposal level** (`first_attacker_tool`). This replaces the earlier statement that the executed call is primary, which cannot be measured on these records.
- **Options for the primary endpoint:**
  - **E-P: proposal level** (the only endpoint the committed records support). Cost: none. Consistency: the same endpoint as §6.3 of the manuscript; no executed claim is made.
  - **E-X: executed call** on a new executor-backed benchmark (a tool layer that records executed calls). Cost: not estimated; needs a new harness and a new pilot. Consistency: no committed record for it exists yet.
- **Observed-consequence rule:** an episode without a recorded endpoint is excluded and counted in the error table.
- **Provider errors, 429s and non-delivery:** each is recorded as a failure, never as "safe". A target is **invalid** if its provider-error rate exceeds the threshold chosen below. Options: **error threshold 5%** or **10%**. Retries: **R-0** (one request per episode) or **R-3** (up to three attempts, all recorded). Observed: the registered run has no provider errors; the calibration has 0 to 28 per target (`calibration.json`, `injecagent_panel_calib_20261001`).
- **Non-delivery:** InjecAgent has no delivery check (the injected text is in the tool output by construction). The Hard set's non-delivery rule is to be fixed before launch if S-B is chosen.

## 6. Analysis plan and multiplicity — **OPEN**

- **H1:** per target, zero or nonzero events in n; report the two-sided 95% Clopper–Pearson upper bound. A target is "floor confirmed" if the bound is below 5%; otherwise "not confirmed", never "effective".
- **H2:** per target, paired exact McNemar test (A0 vs SPOT_TOOL), cluster unit = attacker instruction; cluster-bootstrap interval with resample count and seed fixed in advance.
- **H3:** the paired difference A0 − A0_REP per target with a cluster-bootstrap interval; no threshold.
- **Stopping:** none. No interim analysis; n is fixed in advance.

**Multiplicity: the correction depends on the panel option.** The family for H2 is the set of targets with a SPOT_TOOL arm in the run. Per-test alpha under Bonferroni (k = family size) and the Holm sequence (step-down thresholds α/k, α/(k−1), …, α), for each option:

| panel option | H2 family (k) | closed model in family? | Bonferroni per-test alpha | Holm thresholds (step 1 → step k) |
|---|---|---|---|---|
| P-A two targets | 2 | — (no closed model) | 0.025 | 0.025, 0.05 |
| P-B five targets, closed model in | 5 | yes | 0.01 | 0.01, 0.0125, 0.0167, 0.025, 0.05 |
| P-B five targets, closed model out | 4 | no | 0.0125 | 0.0125, 0.0167, 0.025, 0.05 |
| P-C four open targets | 4 | no | 0.0125 | 0.0125, 0.0167, 0.025, 0.05 |

Note for P-B and P-C: only the two registered targets have SPOT_TOOL data (§2). The H2 family in those options therefore contains only the targets for which a SPOT_TOOL arm is run; the table gives the k the option would have if all its targets were run with a SPOT_TOOL arm. The choice of correction (Holm or Bonferroni) is open; the table lists both.

Pairs at the per-test alpha of each option, for the two registered targets: P-A (α = 0.025): 121 and 126; P-B closed-in (α = 0.01): 148 and 155; P-B closed-out and P-C (α = 0.0125): 142 and 148. These come from §4, not by hand.

## 7. Run discipline

- Fresh, timestamped output folder per run; no reuse or overwrite.
- Provider usage snapshot (`/auth/key`) saved before and immediately after the run. **Stop** if measured usage differs from the pre-run estimate by more than about 5%.
- `progress.log` committed and not git-ignored.
- `run_manifest.json` records: code SHA, `docs_sha_at_launch`, exact model IDs, provider route, temperature, reasoning setting, sample seed, sample hash, cap values.
- Working tree clean at launch.

## 8. Budget and cost source — **OPEN**

**Cost source rule (one rule for every target):** per-episode cost = total of the `cost` field over priced episodes, divided by the number of priced episodes, in **one file per target**: the registered run for llama-4-maverick and qwen3.8-flash, and the InjecAgent panel calibration file for deepseek-v4.1-flash, glm-4.7 and gpt-5.6-sol. Hard-set costs in `calibration.json` are not used in this draft.

Per-episode cost (USD), from those files:

| target | source file | episodes | priced | total (USD) | per priced episode (USD) |
|---|---|---|---|---|---|
| llama-4-maverick | `injecagent_registered_20261001/meta-llama__llama-4-maverick.json` | 598 | 598 | 0.10626 | 0.0001777 |
| qwen3.8-flash | `injecagent_registered_20261001/qwen__qwen3.8-flash.json` | 598 | 598 | 0.10594 | 0.0001772 |
| deepseek-v4.1-flash | `injecagent_panel_calib_20261001/deepseek__deepseek-v4.1-flash.json` | 80 | 80 | 0.00835 | 0.0001044 |
| glm-4.7 | `injecagent_panel_calib_20261001/z-ai__glm-4.7.json` | 80 | 80 | 0.06366 | 0.0007958 |
| gpt-5.6-sol | `injecagent_panel_calib_20261001/openai__gpt-5.6-sol.json` | 80 | 80 | 0.11820 | 0.0014775 |

**Unpriced episodes (disclosed):** `injecagent_panel_calib_20261001/qwen__qwen3.8-flash.json` has 7 of 80 episodes without a `cost` field (73 priced). Not used for the rate, because the registered qwen file is fully priced. Separately, `calibration.json` has 72 of 180 qwen3.8-flash episodes without `cost`; its `spent` value counts priced episodes only. That file is not used for costs here.

Cost per target (USD; episodes = 3n + 40):

| option | episodes per target | llama-4-maverick | qwen3.8-flash | deepseek-v4.1-flash | glm-4.7 | gpt-5.6-sol |
|---|---|---|---|---|---|---|
| N-A n = 72 | 256 | 0.0455 | 0.0454 | 0.0267 | 0.2037 | 0.3782 |
| N-B n = 100 | 340 | 0.0604 | 0.0602 | 0.0355 | 0.2706 | 0.5023 |
| N-C n = 150 | 490 | 0.0871 | 0.0868 | 0.0512 | 0.3899 | 0.7240 |
| N-D n = 186 | 598 | 0.1063 | 0.1059 | 0.0624 | 0.4759 | 0.8835 |

Panel totals (USD; unrounded sums of the same rates):

| option | N-A (72) | N-B (100) | N-C (150) | N-D (186) |
|---|---|---|---|---|
| P-A two targets | 0.0908 | 0.1206 | 0.1739 | 0.2122 |
| P-C four open targets | 0.3213 | 0.4267 | 0.6150 | 0.7505 |
| P-B five targets | 0.6995 | 0.9291 | 1.3389 | 1.6340 |

Corrections against the earlier draft: the earlier P-B and P-C totals used a different source for glm and gpt. At n = 100 the corrected values are P-B 0.9291 and P-C 0.4267 (earlier: 1.1128 and 0.4335).

**Caps (options, to be set by the author):** soft cap = 125% of the option's estimate (the convention of `PROTOCOL_EXTERNAL_TEST_DRAFT_v1.md` §8). Hard HTTP cap = episodes × (1 + retry allowance): 0 under R-0, up to 3 under R-3. The committed caps (0.36 USD registered; 0.45 USD calibration) are references, not decisions.

## 9. Freeze checklist (all must hold before the author approves)

1. Attack authorship: an independent author for the attack set, **or** an explicit written statement of partial authorship. Not decided here.
2. The launcher is tested offline with mocks; it cannot make a live call without the explicit run command.
3. Tests exist for every rule in §§4–8: CP bound, paired test, cluster bootstrap, error threshold, endpoint rule, multiplicity per option, manifest fields.
4. Registration (OSF or AsPredicted): **option**, not decided. The earlier protocol was not registered.
5. The Hard-set split (test 170, calibration 68) is verified against `FREEZE_RECORD.json` and `MANIFEST.json`. **Verified in this draft**; the confirmatory run must still use the test split only.
6. The panel option, the endpoint (E-P or E-X), the multiplicity method (Holm or Bonferroni per option), and the error threshold are chosen and written into the frozen text.

## 10. Deviations, endpoint status, and what each result would change

- **Endpoint wording (corrected).** §5 of the earlier draft made the executed call primary and §10 described H2 power on the same endpoint. Neither matched the records: the power numbers in §4 are proposal-level, and the executed endpoint is not available for InjecAgent. This draft states proposal level as the InjecAgent endpoint everywhere, and lists the executed endpoint as an open option (E-X).
- **Deviation policy:** any change after freezing is logged with date, reason and effect, and needs author approval. A change of panel, sample, endpoint or multiplicity method creates a new version.
- **Optimism:** H2 sample sizes use the effect observed on 186 cases; a smaller true effect needs more pairs. For that reason N-C (α = 0.0125) is listed beside N-B.
- **What each result would change in the paper:**
  - H1 confirmed on a target (upper bound < 5%): defense comparisons on that target would become informative; its "undetermined" label would change.
  - H1 not confirmed on a target: it stays unmeasurable at this n; the paper reports it as such.
  - H2 reduction confirmed on two or more targets: the proposal-level tool-channel effect is supported in a frozen run for those targets. The paper makes no executed-call claim unless E-X is run.
  - H2 not confirmed, with an interval that excludes a 5-point effect: the tool-channel effect in §6.3 of the manuscript is not supported by a frozen run.
  - H3 wider than the H2 effect: the H2 result cannot be separated from run-to-run noise; the paper says so.

None of these outcomes supports a claim that any defense is effective or ineffective in general.
