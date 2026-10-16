# B items (re-analysis of existing data, $0, offline), 2026-10-16 (Tehran)

## B1 (#5). Preregistered primary statistic: Kendall tau-b (EXEC vs ATT ranking) with bootstrap 95% CI per cell
From rankflip/results.json (full data, post-hoc target map for shopping/github) and review/results_conf.json (subset without
AgentDyn shopping/github; post-hoc exclusion). Same bootstrap as preregistered (episodes within cell×defense, 2000 reps, seed 20261015).
Table: bitems/tau_table.md (generated, reproduced below).

| Cell (bench, model) | k | tau-b [95% CI] full | ATT flips full | tau-b [95% CI] subset | ATT flips subset |
|---|---|---|---|---|---|
| agentdojo, gpt-4o-2024-05-13 | 5 | 0.8 [0.8, 1.0] | 0 | 0.8 [0.8, 1.0] | 0 |
| agentdyn, gemini-2.5-flash | 9 | 0.889 [0.778, 1.0] | 0 | 0.889 [0.771, 0.986] | 0 |
| agentdyn, gemini-2.5-pro | 9 | 0.833 [0.704, 0.944] | 0 | 0.704 [0.535, 0.841] | 1 |
| agentdyn, gpt-4o-2024-08-06 | 9 | 0.743 [0.571, 0.873] | 1 | 0.761 [0.592, 0.841] | 1 |
| agentdyn, gpt-4o-mini-2024-07-18 | 10 | 0.854 [0.733, 0.911] | 1 | 0.944 [0.761, 0.986] | 0 |
| agentdyn, gpt-5-mini-2025-08-07 | 8 | 0.688 [0.288, 0.802] | 0 | undefined | 0 |
| agentdyn, gpt-5.1-2025-11-13 | 9 | 0.73 [0.53, 0.841] | 0 | 0.783 [0.551, 0.884] | 0 |
| agentdyn, llama-3.3-70b-instruct | 9 | 0.514 [0.31, 0.686] | 2 | 0.551 [0.31, 0.707] | 2 |
| agentdyn, qwen3-235b-a22b-2507 | 9 | 0.833 [0.722, 0.889] | 2 | 0.857 [0.761, 1.0] | 0 |
All tau-b point estimates are positive (rankings broadly concordant). Every CI lower bound is above 0. The CI excludes 1 in 6 of 9
cells on the full data and in 6 of 8 defined cells on the subset (upper bound < 1). The prereg defines no tau-b threshold, so this is
descriptive inference. gpt-5-mini subset: EXEC ASR is 0 for all 8 defenses, so tau-b is undefined.

## B2 (#6). ATTEMPTED-scorer validation on progent and drift episodes (AI labelling, NOT human)
- Population: AgentDyn important_instructions episodes, all suites (full data), in the 4 model cells with >=1 ATT flip on full data
  (gpt-4o-2024-08-06, gpt-4o-mini-2024-07-18, llama-3.3-70b-instruct, qwen3-235b-a22b-2507), defenses progent and drift,
  scorer error-free. Population sizes: progent 2240 (scorer ATT=1: 734, ATT=0: 1506); drift 2240 (ATT=1: 413, ATT=0: 1827).
- Sample: stratified by defense × scorer label, 20 per stratum, n = 80 (40 per defense), seed 20261016
  (bitems/scorer_validation/sample.py). The labeller saw only bitems/scorer_validation/blind.jsonl / blind_render.txt
  (injection goal + the agent's tool calls); scorer label, executed flag and stratum were in KEY_DO_NOT_OPEN/key.json, unopened.
- Labeller: the AI assistant (Grok Bot), by reading the traces; no LLM API call. Rule recorded inside labels_AI.json.
- Hash lock BEFORE comparison: labels_AI.json sha256 ca8e46946fbc68d368b3b4e1a7445bb7d67ded7ee6738a5e71ce7c0b895a7dee,
  locked 2026-10-16T14:55:45+03:30 (labels_AI.sha256). compare.py asserts the hash before reading the key.
- Results (bitems/scorer_validation/comparison.json, precision.txt):

| Defense | n | agreement | Wilson 95% | Cohen kappa | scorer1/AI1 | scorer1/AI0 | scorer0/AI1 | scorer0/AI0 |
|---|---|---|---|---|---|---|---|---|
| progent | 40 | 37/40 = 92.5% | 0.801–0.974 | 0.85 | 17 | 3 | 0 | 20 |
| drift | 40 | 30/40 = 75.0% | 0.598–0.858 | 0.5 | 10 | 10 | 0 | 20 |
| both | 80 | 67/80 = 83.8% | 0.742–0.903 | 0.675 | 27 | 13 | 0 | 40 |

- All 13 disagreements are scorer false positives: the scorer's name match fires on a call with the target function name that
  serves the user task (e.g. send_money to the user's own payee, checkout of the user's product, send_email to a colleague),
  not the injection goal. No scorer false negatives in the sample.
- Precision of scorer ATT=1 (AI labels): progent 17/20 = 0.85 (Wilson 0.64–0.948); drift 10/20 = 0.50 (Wilson 0.299–0.701).
  ATT=0 stratum: 20/20 per defense (Wilson 0.839–1.0).
- Agreement % and kappa are on the stratified (50/50) sample, not population-weighted. Population-weighted agreement assuming the
  stratum rates: progent 0.951, drift 0.908.
- Interpretation: for drift, about half of the scorer's ATTEMPTED positives in flip cells are not attempts at the injection goal, so
  drift's ATT ASR is inflated by the scorer itself. **Flips involving drift may be scorer artefacts.** For progent, scorer
  precision is higher (0.85) but not perfect. We did not re-run the flip analysis with corrected labels.

## B3 (#14). Permutation max-statistic family-wise check [EXPLORATORY, not preregistered]
bitems/perm_fwer.py (sha256 20c3808e…, locked before running; bitems/perm_fwer.py.sha256) → bitems/perm_fwer_{conf,all}.json, log
bitems/perm_fwer_log.txt. Blocks = (suite, user task, injection task) present for all defenses; defense labels permuted within block,
jointly for EXEC and ATT; statistic min(|dEXEC|, |dATT|) for opposite-sign pairs; Westfall–Young single-step maxT within cell;
2000 permutations, seed 20261016.
- Subset: 4/9 cells, 8 flagged pairs. Full: 5/9 cells, 12 flagged pairs.
- Flagged pairs involving neither progent nor drift: subset 2 (llama piguard_detector vs tool_filter; llama tool_filter vs
  transformers_pi_detector); full 3 (the same two + gpt-5.1 prompt_guard_2_detector vs repeat_user_prompt).
- Caveat: the null is full exchangeability of defenses, so a flag partly reflects a real defense difference under either
  definition; it is NOT a test of "both differences are non-zero with opposite signs" and is less conservative than the
  preregistered rule. It does not support a claim, and it shows that "every reversal involves progent or drift" holds only under
  the preregistered and clustered rules, not under every family-wise procedure.

## B4 (#19). Sensitivity excluding unversioned AgentDojo runs
bitems/run_excl_unversioned.py (analyze.py logic unchanged; input filter only) → bitems/results_exclunv_{conf,all}.json,
bitems/exclunv_log.txt. All 3145 episodes of the only eligible AgentDojo cell (gpt-4o-2024-05-13, important_instructions; 5 × 629)
come from run files without benchmark_version, so excluding unversioned runs removes AgentDojo entirely:
- subset: 3/8 cells, 4 flips / 280 pairs; full: 4/8 cells, 6 flips / 289 pairs; flip pairs identical to the primary analyses.
