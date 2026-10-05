# Adaptive Controller Specification

**Type:** Threshold-based adaptive defense policy (non-learning).
Supersedes the archived copy in [`archive/q1/ADAPTIVE_CONTROLLER_SPEC.md`](archive/q1/ADAPTIVE_CONTROLLER_SPEC.md), which is kept unchanged for provenance.

Implementation: `src/adapti_guard/adaptation/{feedback_engine,policy_update_engine}.py`, `src/adapti_guard/runtime.py`, `src/adapti_guard/experiments/defense_baselines.py` (`AdaptiveDefenseState`).

## State

```text
defense_level      in {0, 1, 2, 3}
attack_pressure, legitimate_pressure, benign_streak, successful_attacks   (non-negative ints)
episode, last_change_episode, last_attack_episode                        (hysteresis clock)
streak_deescalations, backoff                                             (attack memory)
transition_history (bounded to the last 1000), total_updates, transitions_dropped
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
INCREASE_DEFENSE: attack_pressure += 1; legitimate_pressure = 0; benign_streak = 0; last_attack_episode = episode
REDUCE_DEFENSE:   legitimate_pressure += 1; attack_pressure = 0; benign_streak = 0
MAINTAIN:         if pressure_decay: both pressures = max(0, pressure - pressure_decay)
                  benign_streak = benign_streak + 1 if legitimate_success and not attack_success else 0

attack_pressure >= attack_threshold (2):
    level = min(level + 1, 3); attack_pressure = 0            # never delayed by dwell
    if streak_deescalations and backoff_cap: backoff = min(backoff + 1, backoff_cap)
    streak_deescalations = 0

legitimate_pressure >= legitimate_threshold (2) and dwell_elapsed:
    level = max(level - 1, 0); legitimate_pressure = 0

benign_streak >= benign_streak_threshold * 2**backoff:
    if level == 0:            backoff = max(0, backoff - 1); benign_streak = 0
    elif dwell_elapsed:       level -= 1; streak_deescalations += 1; benign_streak = 0

dwell_elapsed := min_dwell == 0, or episodes since the last level change AND since the last
                 INCREASE_DEFENSE signal are both >= min_dwell
```

Opt-in parameters of `PolicyUpdateEngine` (defaults reproduce the historical behaviour used by frozen experiments): `pressure_decay=0`, `benign_streak_threshold=None`, `min_dwell=0`, `backoff_cap=0`.
`AdaptiGuard` (MVP runtime) defaults: `benign_streak_threshold=20`, `min_dwell=10`, `backoff_cap=4`, `pressure_decay=0`.

* **Hysteresis (`min_dwell`)** removes the L2<->L3 limit cycle: a down-move cannot happen while attack signals keep arriving, and cannot immediately undo an escalation.
* **Attack memory (`backoff_cap`)**: every escalation that follows a streak-driven down-move doubles the benign streak needed for the next one (at most `2**backoff_cap` times the base); a full quiet streak at level 0 forgives one step. A patient attacker can still wait the streak out, and benign traffic from the attacker counts like anyone else's, so de-escalation is steerable by whoever can send traffic. Dwell and back-off bound the gain per probe; they do not remove the trade-off between utility recovery and exposure.
* **Pressure is not "consecutive"** at `pressure_decay=0`: `INCREASE, MAINTAIN, INCREASE` escalates. Use `pressure_decay>=1` for strictly consecutive behaviour. (An earlier version of this spec said "consecutive"; that was wrong.)

### Feedback rules

De-escalation via `REDUCE_DEFENSE` requires a legitimate task under a cost >= 0.50 action (BLOCK). Branch 1 (legitimate task *succeeded* despite BLOCK) is unreachable from the in-repo pipelines, which only score a legitimate task as successful when it was allowed. It exists for callers with an independent outcome judge. Over-defense is detected in-pipeline via branch 2 (legitimate task blocked). Benign traffic that is never blocked de-escalates only through the benign-streak rule above.

### Reward (feedback only)

`reward = 0.5 * security + 0.4 * utility - 0.1 * cost`. It is reported but never read by `update()`; there is no learning.

## Behavioural limits (read before citing results)

1. **False negatives are invisible by default.** In `AdaptiveDefenseState` feedback comes from the detector's own verdict, so an attack the detector misses is booked as a legitimate task and never raises the level. Supply an independent `outcome_judge` to close the loop. In `AdaptiGuard` the same holds for unflagged input.
2. **Labels.** `AdaptiGuard.run` derives labels: input the detector flags is treated as an attack and a caller claim of "legitimate" for it is ignored unless an `outcome_judge` says otherwise (a blocked attack is never booked as an over-blocked legitimate task). Labels must be `bool` or `None`. Judge output is validated (dict, known keys, `bool`/`None`; `AdaptiveDefenseState` additionally requires all four keys).
3. **Feedback lag.** Episode *t*'s outcome is applied at the start of *t+1*; the last episode's outcome needs `AdaptiveDefenseState.flush()`.
4. **Frozen defaults are one-way.** `PolicyUpdateEngine()`, `AdaptiveDefenseState()` and `make_b3_adaptive` still never de-escalate and never decay pressure, because frozen experiments depend on that. Opt in with the parameters above (the `AdaptiGuard` runtime does).
5. **Level matters for MEDIUM and LOW risk; HIGH is unreachable in the pipelines.** `RiskEngine.assess(detection)` without metadata caps a pure-detector score at 0.56 (MEDIUM), so HIGH risk (always BLOCK) only occurs when callers pass attack-type metadata. L0 and L1 are identical for MEDIUM except for the sanitizer mode.
6. **Evidence.** See `results/q1_f3_real_llm/` (v1, legacy stack) and `results/q1_f3_real_llm_v2/` (redesigned stack) and their `FINDINGS.md`. Both are exploratory, synthetic, text-only, two cheap models, with an oracle-feedback arm that is an upper bound.
7. **Detector limits.** Base `PromptInjectionDetector.detect` raises `TypeError` for non-`str`, scans all input up to `MAX_INPUT_CHARS` (500,000) in overlapping 100k-char chunks, and **fails closed** (probability 1.0, indicator `oversized_input`) above that, so large documents must be split by the caller. The hardened subclass adds Unicode/spacing normalisation, base64 decoding and extra paraphrase / French / Spanish / German / Chinese patterns. It is still regex matching: `tests/test_adaptive_redesign.py::HARDENED_STILL_MISSES` pins evasions it does not catch (e.g. "Pretend the earlier rules never existed...", leetspeak, requests phrased without trigger words), and a determined attacker will find more.
8. **Sanitizer.** The historical `strip` mode deletes trigger phrases and leaves the payload (it can raise attack success, Q1 H-4). `DefenseActionLayer(sanitize_mode="delimit")` wraps content in an `<untrusted_input>` block with a data-only preface (tag look-alikes inside the content are removed so it cannot close the block) and applies to both SANITIZE and TOOL_RESTRICTION, so content protection is monotone in the level: A0 raw < A1 = A2 delimited < A3 blocked. Delimiting is a prompt-level mitigation, not a guarantee; its measured effect is in the v2 results. `AdaptiGuard` uses `delimit`; the bare `DefenseActionLayer()` default stays `strip` for frozen experiments.

## Configuration and thread safety

Controller knobs (all validated at construction; invalid values raise `ValueError`): `attack_threshold`, `legitimate_threshold`, `pressure_decay`, `benign_streak_threshold`, `min_dwell`, `backoff_cap` (<= 10), `initial_level` (0 to 3; `reset()` restores it). There is no logging or metrics hook beyond `PolicyState` (`transition_history`, `total_updates`, `transitions_dropped`). `PolicyUpdateEngine.update` is serialised by an internal lock. `AdaptiGuard` and `AdaptiveDefenseState` as a whole are **not** thread-safe: use one instance per stream. Multi-process use is unsupported.

## Scientific classification

Adaptive: yes (level changes over time). Learning-based: no. Bayesian / RL: no.
