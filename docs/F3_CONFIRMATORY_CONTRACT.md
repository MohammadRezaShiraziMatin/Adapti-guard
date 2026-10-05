# F3 confirmatory contract (draft, status: NOT EXECUTED)

Separate from Track A (frozen, FAIL). F3 is a new experiment, not part of any AUDIT.

## Question
Does the adaptive controller beat the best fixed level when detector (regex + the same semantic
guard), corpus, model, seeds, protocol and analysis are identical across arms?

## Pre-specified design
- Model: llama-3.1-8b-instruct (chosen from dev evidence: the only tested model where levels differ;
  gpt-4o-mini reported as "no headroom": delimited detected attacks already succeed ~0%, see below).
- Arms: fixed L1, L2, L3, adaptive_proxy; all use `LayeredPromptInjectionDetector` with the same guard.
- Loss (primary): ASR + 0.5 * (1 - utility) + mean cost (cost table A0 0 / A1 0.1 / A2 0.25 / A3 0.5).
  Weights are a value judgement fixed before any confirmatory data; a security-weighted variant
  (ASR x 3) is a pre-declared sensitivity analysis, not a decision rule.
- Best fixed: arm with lowest dev loss, chosen on dev data only.
- Test: paired bootstrap over seeds, 95% CI of (adaptive - best fixed) loss.
  Superiority: CI upper < 0. Equivalence: CI inside +-0.02. Inferiority: CI lower > 0.
- Held-out pool: fresh attacks/benign written by a different model, frozen before the run.
  Seeds: frozen list disjoint from dev seeds (dev used 0-19 in replay, 0-7 in live v2).

## Dev-phase result (offline replay, llama outcome table from existing episodes, guard cache on v1/v2 pools)
Loss / ASR / utility / cost, 20 dev seeds x 2 streams:

| arm | loss | ASR | utility | cost |
|---|---|---|---|---|
| fixed L1 | 0.240 | 0.065 | 0.850 | 0.100 |
| fixed L2 | 0.251 | 0.059 | 0.869 | 0.127 |
| fixed L3 | 0.272 | 0.003 | 0.805 | 0.172 |
| adaptive (best of 16-config grid: attack_thr 3, decay 1, dwell 3) | 0.239 | 0.067 | 0.848 | 0.097 |
| adaptive (experiment-scale default) | 0.279 | 0.008 | 0.823 | 0.182 |

The best adaptive configuration just stays at L1 (ties best fixed). Configurations that do escalate
(attack_thr 2) fall on the ASR/cost line between L1 and L3 and are worse than time-sharing the two
fixed levels (adaptive ASR 0.035 at cost 0.148; interpolating fixed L1/L3 gives about 0.024). With
the security-weighted variant (ASR x 3) fixed L3 is best (0.278) and adaptive is worse (0.337).
For gpt-4o-mini, delimiting already neutralises detected attacks, so L3 adds only cost.

## Consequence
On this stack and loss, offline dev evidence predicts Adaptive <= best fixed (tie at best). The
confirmatory live run was therefore not executed; this file records the contract and the dev
evidence so any later run is pre-specified. Caveat: the replay outcome model ignores that delimit
success depends on the prompt, and uses guard verdicts only on the v1/v2 prompts.
