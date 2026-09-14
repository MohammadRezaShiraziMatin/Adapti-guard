# Defense Levels (L0–L3)

| Level | Action code | Behavior | Security effect | Utility effect | Cost (legacy table) | Latency |
|------:|-------------|----------|-----------------|----------------|--------------------:|---------|
| L0 | A0 | No intervention | Minimal | Full | 0.00 | detector + policy only |
| L1 | A1 | Regex sanitization | Moderate | High (allowed) | 0.10 | + sanitization |
| L2 | A2 | Tool access disabled | Higher for tool attacks | Medium | 0.25 | + restriction |
| L3 | A3 | Block interaction | Maximum (no model call if blocked) | Low (legitimate blocked) | 0.50 | minimal if blocked early |

**Note:** Cost and latency for Q1 experiments must be **measured** (EXP-009), not taken from the legacy fixed table.

Source: `src/adapti_guard/defense/action_layer.py`, `src/adapti_guard/policy/policy_engine.py`
