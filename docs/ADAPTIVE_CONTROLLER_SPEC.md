# Adaptive Controller Specification

**Type:** Threshold-based adaptive defense policy (non-learning).
Supersedes the archived copy in [`archive/q1/ADAPTIVE_CONTROLLER_SPEC.md`](archive/q1/ADAPTIVE_CONTROLLER_SPEC.md), which is kept unchanged for provenance.

Implementation: `src/adapti_guard/adaptation/{feedback_engine,policy_update_engine}.py`, `src/adapti_guard/runtime.py`, `src/adapti_guard/experiments/defense_baselines.py` (`AdaptiveDefenseState`).

## State

```text
defense_level      in {0, 1, 2, 3}
attack_pressure, legitimate_pressure, benign_streak, successful_attacks   (non-negative ints)
```

`PolicyUpdateEngine.update` validates its inputs: unknown `adaptation_signal` values raise `ValueError` (valid values: `AdaptationSignal`), `defense_level` outside 0..3 raises `ValueError`, thresholds must be `int >= 1` (NaN, `bool`, floats rejected). `update` returns a new `PolicyState` and never mutates the state passed in.

## Observation

`FeedbackEngine.generate(outcome)` returns one of `INCREASE_DEFENSE`, `REDUCE_DEFENSE`, `MAINTAIN`, plus `attack_success`, `legitimate_success`, `defense_cost`.

## Defense levels

| Level | Action |
|------:|--------|
| L0 | NO_INTERVENTION |
| L1 | SANITIZE |
| L2 | TOOL_RESTRICTION |
| L3 | BLOCK (medium risk only; see [DEFENSE_LEVELS.md](DEFENSE_LEVELS.md)) |

## Transition

```text
INCREASE_DEFENSE: attack_pressure += 1; legitimate_pressure = 0; benign_streak = 0
REDUCE_DEFENSE:   legitimate_pressure += 1; attack_pressure = 0; benign_streak = 0
MAINTAIN:         if pressure_decay: both pressures = max(0, pressure - pressure_decay)
                  benign_streak = benign_streak + 1 if legitimate_success and not attack_success else 0

attack_pressure     >= attack_threshold (2):     level = min(level + 1, 3); attack_pressure = 0
legitimate_pressure >= legitimate_threshold (2): level = max(level - 1, 0); legitimate_pressure = 0
benign_streak       >= benign_streak_threshold (if set): level = max(level - 1, 0); benign_streak = 0
```

`pressure_decay` (default 0) and `benign_streak_threshold` (default `None` on `PolicyUpdateEngine`) are opt-in so frozen experiments keep their historical behaviour. `AdaptiGuard` (MVP runtime) defaults `benign_streak_threshold=20`.

### Feedback rules

De-escalation via `REDUCE_DEFENSE` requires a legitimate task under a cost >= 0.50 action (BLOCK). Branch 1 (legitimate task *succeeded* despite BLOCK) is unreachable from the in-repo pipelines, which only score a legitimate task as successful when it was allowed. It exists for callers with an independent outcome judge. Over-defense is detected in-pipeline via branch 2 (legitimate task blocked). Benign traffic that is never blocked de-escalates only through the benign-streak rule above.

### Reward (feedback only)

`reward = 0.5 * security + 0.4 * utility - 0.1 * cost`. It is reported but never read by `update()`; there is no learning.

## Behavioural limits (read before citing results)

1. **False negatives are invisible by default.** In `AdaptiveDefenseState` feedback comes from the detector's own verdict, so an attack the detector misses is booked as a legitimate task and never raises the level. Supply an independent `outcome_judge` to close the loop.
2. **Caller-supplied labels are trusted.** `AdaptiGuard.run` takes `legitimate_task`, `legitimate_succeeded` and `attack_succeeded` from the caller unless `outcome_judge` is set. Labels an attacker can influence can lower the level (and with attacks present produce a bounded L2<->L3 cycle). Do not use this path for security claims.
3. **Feedback lag.** Episode *t*'s outcome is applied at the start of *t+1*; the last episode's outcome needs `AdaptiveDefenseState.flush()`. A level change needs `attack_threshold` / `legitimate_threshold` consecutive same-direction signals.
4. **Pressure never decayed in the original code**; one attack followed by 1000 benign episodes and one more attack escalated. Use `pressure_decay` to avoid this.
5. **De-escalation was unreachable** for correctly labelled benign traffic in the original code (one-way ratchet). Use `benign_streak_threshold`. The frozen `AdaptiveDefenseState` default and `harmonized_runner` ablations keep the ratchet on purpose; their committed results must not be re-run.
6. **Level mostly matters for MEDIUM/LOW risk.** HIGH risk is always BLOCK regardless of level; L0 and L1 are identical for MEDIUM.
7. **No evidence that adaptation helps.** All committed adaptive-vs-fixed results are `LEGACY_SIMULATION_ONLY` and fixed L1 dominates the adaptive arm there. A real-LLM, non-circular comparison with variance is still open (Q1 F3).
8. **Detector limits.** `PromptInjectionDetector.detect` raises `TypeError` for non-`str` input, scans at most `MAX_INPUT_CHARS` (200,000; head and tail windows only for longer input), and is regex-based, so non-English, spaced-letter, base64 and paraphrased injections score 0.0.

## Configuration and thread safety

Thresholds are the only controller knobs; all are validated at construction. `PolicyUpdateEngine.update` is serialised by an internal lock. `AdaptiGuard` and `AdaptiveDefenseState` as a whole are **not** thread-safe: use one instance per stream. Multi-process use is unsupported.

## Scientific classification

Adaptive: yes (level changes over time). Learning-based: no. Bayesian / RL: no.
