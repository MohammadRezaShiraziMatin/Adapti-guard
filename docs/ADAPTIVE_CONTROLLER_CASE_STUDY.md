# Adaptive guard controller: a case study

Scope: what an adaptive defense-level controller does for a prompt-injection guard, whether it beats
the best fixed level, and what limited it. This is a case study of one stack (regex detector, optional
LLM guard, delimiting sanitizer, levels L0-L3), not evidence that "AdaptiGuard works". Track A
(frozen, FAIL) is untouched; nothing here is part of any AUDIT.

## What was built
Controller with attack/legitimate pressure counters, decay, benign-streak de-escalation, minimum dwell
and attack-memory back-off (`docs/ADAPTIVE_CONTROLLER_SPEC.md`); hardened regex detector; delimiting
sanitizer; optional semantic guard layer (`LayeredPromptInjectionDetector`).

## Failure modes found in review, and fixed
Unreachable de-escalation, level oscillation, no attack memory, padding bypass of the detector,
a stripping sanitizer that left payloads intact, and a concurrency race. Each has a regression test
(`tests/test_adaptive_q1_fixes.py`, `tests/test_adaptive_redesign.py`, `tests/test_layered_detector.py`).

## Findings
1. **Detector is the bottleneck.** Regex recall: 0.94 on the pool it was designed on, 0.21-0.26 on 24 fresh
   attacks. An LLM guard raised the fresh-pool recall to 0.75 with 0/20 benign flagged; a linear classifier
   trained on repo data did not generalise (0.12) and was dropped.
2. **Adaptive does not beat the best fixed level.** Live F3 v2 (2 models, 5 seeds): fixed L1 dominates on
   gpt-4o-mini; on llama adaptive sits on the ASR/cost trade-off between L1 and L3. Small live check with
   the guard (gpt-4o-mini, 4 seeds): adaptive+guard ASR 0.07-0.08 vs 0.12-0.15 with regex only, but fixed
   arms did not get the guard, so that gain is mostly the detector.
3. **Why there is little headroom.** L1 and L2 both delimit; L3 only adds blocking of flagged inputs.
   On gpt-4o-mini, delimited detected attacks already succeed ~0%, so blocking adds only cost. On llama,
   blocking flagged attacks removes ~0.08 ASR but also drops ~3.5% of benign inputs and costs more.
4. **Offline dev replay** (`scripts/f3_dev_replay.py`, `scripts/f3_dev_grid.py`; llama outcome table, 20 dev
   seeds x 2 streams, 16 adaptive configs): best adaptive collapses to L1 (loss 0.239 vs 0.240); escalating
   configs fall on the L1-L3 line and are worse than time-sharing the two fixed levels; with an
   ASR-weighted loss fixed L3 wins. Loss = ASR + 0.5(1-utility) + cost.

## Confirmatory F3 (executed once)
Design frozen before the run (`docs/F3_CONFIRMATORY_CONTRACT.md`): llama-3.1-8b, fresh pool v3 written by a different
model, 20 new seeds, same guard for every arm, loss ASR + 0.5(1-utility) + cost, best fixed = L1 from dev.
Primary result: adaptive_dev - fixed L1 = -0.012, 95% CI [-0.026, +0.002], **inconclusive** under the pre-specified
rule; the escalating config (adaptive_exp) is worse than L1 (+0.066, CI [+0.055, +0.077]). Adaptive_dev beats fixed
L2/L3 but those were not the pre-specified comparator. Details and limits: `results/f3_confirmatory/RESULTS.md`.
Note: an earlier offline replay predicted a tie at best and had treated L0 like L1; it was corrected before freezing.

## Caveats
Synthetic text-only probes, keyword utility, two cheap models, 4-5 seeds, no adaptive attacker, replay
outcome model ignores per-prompt effects, guard prompt written after seeing regex misses on the v2 pool
(so v2 is no longer blind), guard cost not in the cost metric, and the guard is itself an LLM that can be
injected.

## Defensible claim
A cost-aware adaptive controller can be made reliable (de-escalates, no oscillation, bounded memory,
documented limits). With a dev-tuned configuration it is at best marginally cheaper than the best fixed level
(a -0.012 loss difference whose CI includes 0), and an untuned escalating configuration is clearly worse; on this
stack no gain over the best fixed level is demonstrated. The detector, not the controller, determines security.
