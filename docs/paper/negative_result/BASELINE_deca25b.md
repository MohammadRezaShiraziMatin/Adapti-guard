# Research baseline at commit `deca25b` (rollback point)

Record of what exists at this commit; it adds no result, claim, experiment, model, metric or framework. Verification manifest: `BASELINE_deca25b_manifest.json` (commit, root and directory tree ids, SHA-256 of the manuscript, ledger, section sources, figures, artifacts, configs and key scripts, all read from the commit with `git show`). To check a working tree against it: `git diff --stat deca25b -- <path>` or compare `git rev-parse deca25b:<dir>` with the manifest.

## 1. Repository state
- Commit `deca25b6750469495bbbaec6033a1f8ceb4f5437` (2026-10-07 02:37 UTC), branch `claude/analysis-5vlrfi`, root tree `f202e370ad2b8638778d1c87c33de3ef34555b3d`. Pushed to `origin/claude/analysis-5vlrfi`; `main` was not changed. Working tree clean when this baseline was started.
- Offline validation run on this commit: `STRICT=1 bash scripts/reproduce_negative_result.sh` ends with "manuscript numbers regenerate from committed artifacts"; tests: 61 passed (number ledger, blind version, new offline analyses, E6 offline suite).

## 2. What the paper is
- **Title (authoritative):** "What Reached the Executor? Six Measurement Checks for Evaluating Runtime Defenses of LLM Agents, with a Negative Result" (`MANUSCRIPT_DRAFT_v1.md`, 19,935 words; assembled by `scripts/assemble_manuscript.py` from the section sources). Project and `CITATION.cff` title differs ("AdaptiGuard: An Empirical Case Study ..."); not the paper title.
- **Question (§1):** whether the undefended model actually carries out the attack, and whether the evidence of execution is valid, before a defense is scored; defenses are the case study for measurement decisions. No claim that any defense is effective.
- **Contribution (§1, six items):** six candidate measurement checks M1 to M6 (M1 executed vs proposed; M2 blocked-payload labeling; M3 attacker-controlled effect; M4 scenario authorship independence; M5 per-model reporting and noise floor; M6 defense applied to the untrusted channel, found post hoc); judge-executor disagreement in E1; a partially independent seven-family scenario set; a null on two detector-style defenses with a measured nondeterminism floor; a floor calibration on five 2026 targets; committed traces and offline scripts; a reduced external InjecAgent test.
- **Status of claims:** exploratory; M1 to M5 hypotheses, M6 preliminary; nothing confirmatory (§8.1, §9).

## 3. Experiments, models, data (as committed)
| id | what | data | models |
|---|---|---|---|
| E1 | re-score frozen judge-scored Tracks A and B | 61 + 61 attack episodes per arm (frozen packs, `datasets/frozen/`) | one target, same-family judge (names not stated in the text read) |
| E2 | four-arm run on original scenarios (A0, B3, PHASE1-CORE, TOOLDENY) | 468 episodes (72 attack, 45 benign per arm), `experiments/harness_v2/HARNESS_V2_EXPLORATORY_20260930` | `deepseek/deepseek-v3.2`, `google/gemma-4-31b-it`, `qwen/qwen3-30b-a3b` |
| E3 | 7 partially independent families x 8 instances x 3 models, undefended screen then B3 and CORE | 168 (A0, `..._INDEPENDENT_SCREEN_...`) + 336 (B3, CORE, `..._INDEPENDENT_DEFENDED_...`) episodes | same three models |
| E4 / MT1 | held-out application of the rules; channel re-run | MT1 pack: six targets x four arms; 180 live episodes in the re-run (18 indirect episodes) | six targets (names not read); three in the re-run |
| E5 | external InjecAgent test, protocol drafted locally, unregistered | frozen 186-case sample; NOINJ 40 | run: `llama-4-maverick`, `qwen3.8-flash`; planned and not run: `deepseek-v4.1-flash`, `glm-4.7`, `gpt-5.6-sol` |
| pilot / calibration | Appendix A pilot (120 cases); floor calibration (n = 40 per target) | InjecAgent, Hard set | `qwen-2.5-7b-instruct`, `llama-3.1-8b`, `llama-3.3-70b`, `mistral-small-3.2-24b`; calibration on the five 2026 targets |
- **Defenses:** B3 (adaptive stack), PHASE1-CORE (deterministic), static tool policy / TOOLDENY, delimiters / spotlighting (tool channel). Own defenses only; no published system defense (CaMeL, Progent) was run.
- **Metrics:** executed attacker call with key argument (primary, from the mock tool log); judge success; proposal-level first tool call (InjecAgent); canary emission (MT1); benign utility; κ; paired difference, exact McNemar (descriptive), bootstrap and t intervals.

## 4. Key results (quoted from the manuscript and committed artifacts)
- **E1:** Track B judge-scored paired effect 0.4426 vs 0.9016 by executed calls; benign utility 0.967 judge-scored vs 0.80 executed; κ 0.18, 0.36, 0.16 (bootstrap intervals 0.00 to 0.38, 0.16 to 0.56, 0.05 to 0.30); every disagreement is judge = success with no executed call.
- **E2 (72 attack episodes per arm):** proposed 66/65/36/65 (A0/B3/CORE/TOOLDENY); executed, blocks as non-success 66/65/36/0; valid scenario only 30/29/0/0 of 36; CORE reads "halves", "no effect" or "complete stop" by labeling. Utility TOOLDENY 15/45.
- **E3:** undefended 57/168 (deepseek 41/56, qwen3 8/56, gemma 8/56; families 23/24 down to 0/24). B3 56 vs 57 of 167 (b10/b01 3/4); CORE 57 vs 57 of 168 (4/4); no block in 336 episodes; replay changed 0 of 191 attacker-controlled messages; B3 rewrote the user message in 168 of 218 non-carrier messages. Family-level (7 clusters) intervals -4.7 to +3.5 and -3.1 to +3.1 points. Ceiling-aware power: 80% only at relative reduction 0.751 (about 25.5 points) with no between-family spread; complete removal gives power 0.754 and 0.593 at spreads 0.25 and 0.50.
- **E4/MT1:** κ 0.81 to 0.91 canary vs judge; delimiter effect 0.29 judge vs 0.19 canary; M6 re-run indirect injections 8 to 1 of 18 (preliminary).
- **E5:** A0 23/186 for each of two targets (replicates 24 and 22), NOINJ 0/40, SPOT_TOOL 5/186 and 4/186 (differences -0.097 and -0.102).
- **Calibration:** three of five 2026 targets at or near the floor on public sets.

## 5. Stated limitations (§8)
Partial independence (same assistant wrote scenarios, predicates, scoring and manuscript; detector patterns seen first); small clustered samples (7 families, 3 models); E3 defenses left the payload in place; post-hoc rules (E2 inclusion rule, M6); provider nondeterminism (8/168); judge is a construct difference, no human labels; mock tools, English, non-adaptive attacker, no frontier model; E5 on 2 of 5 targets at proposal level; live harness, run scripts, templates, trajectories and run approvals not in any public ref (only fetchable, unreachable commits); E6 is prepared protocol and tooling only, not frozen, approved, registered or run, and is not evidence.

## 6. Artifacts at this commit
Manuscript and sources `docs/paper/negative_result/`; blind version `tmlr_blind/`; number ledger (70 entries, test `tests/test_manuscript_number_ledger.py`); figures `figures/` (3 PNG/SVG/CSV sets); derived artifacts `docs/research/artifacts/`; traces `experiments/harness_v2/` (4 run directories); packs `datasets/frozen/`; E6 tooling `e6/`, `scripts/e6_*.py` (unrun); arXiv and TMLR build scripts; references: 28 entries (5 checked against abstracts only).

## 7. Discrepancies and unclear points found (reported, not fixed)
1. `SUBMISSION_PACKAGE_TMLR.md` says "References: 23 entries"; the manuscript has 28 (the five later additions). Stale count in that file only.
2. Table 4 says E2 targets "one to three"; the committed E2 episodes contain three models.
3. §1 "Framing" says the six checks are proposed and each "changes or qualifies a conclusion", while the abstract and §9 call them candidates, and M3, M4 and M6 rest on one scenario, a partly independent author and 18 episodes. Wording tension, not a numerical conflict.
4. The artifact `e6_replay_validation_e3_20261004.json` is cited in §6.3 for E3 evidence; its file name refers to the unused confirmatory protocol.
5. Names of the E1 target/judge and of the six MT1 targets were not found in the text read; not guessed.
6. `CITATION.cff`/README title differs from the paper title (intentional, project vs paper).
7. The `EXPLORATORY_SMOKE` run directory exists and is mentioned only in the provenance section (§8.5); its role in the results is unclear.
