# Adaptive Controller Specification

**Type:** Threshold-Based Adaptive Defense Policy (non-learning)

## Formal definition

### State \(s_t\)

```text
defense_level_t ∈ {0, 1, 2, 3}
attack_pressure_t ∈ ℕ
legitimate_pressure_t ∈ ℕ
successful_attacks_t ∈ ℕ
```

### Observation \(o_t\)

Derived from `FeedbackEngine` after each episode:

- `adaptation_signal` ∈ {INCREASE_DEFENSE, REDUCE_DEFENSE, MAINTAIN}
- `attack_success`, `legitimate_success`, `defense_cost`

### Action \(a_t\)

Discrete defense level mapped to intervention:

| Level | Action |
|------:|--------|
| L0 | NO_INTERVENTION |
| L1 | SANITIZE |
| L2 | TOOL_RESTRICTION |
| L3 | BLOCK |

`DefensePolicyEngine` maps `(risk_level, defense_level)` → applied action per episode.

### Transition

```text
if adaptation_signal == INCREASE_DEFENSE:
    attack_pressure += 1; legitimate_pressure = 0
elif adaptation_signal == REDUCE_DEFENSE:
    legitimate_pressure += 1; attack_pressure = 0

if attack_pressure >= attack_threshold (default 2):
    defense_level = min(defense_level + 1, 3); attack_pressure = 0

if legitimate_pressure >= legitimate_threshold (default 2):
    defense_level = max(defense_level - 1, 0); legitimate_pressure = 0
```

De-escalation gated by `defense_cost >= 0.50` in `FeedbackEngine` (except `no_cost_gate` ablation).

### Reward / objective (feedback only)

```text
reward = 0.5 * security_feedback + 0.4 * utility_feedback - 0.1 * defense_cost
```

This is **not** used for gradient-based learning.

### Termination

Episodic evaluation; no terminal state within a single run.

## Scientific classification

- **Adaptive:** yes (level changes over time)
- **Learning-based:** **no**
- **Bayesian / RL:** **no**

Implementation: `src/adapti_guard/adaptation/policy_update_engine.py`
