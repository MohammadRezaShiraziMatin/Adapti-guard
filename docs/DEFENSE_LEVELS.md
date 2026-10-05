# Defense Levels (L0 to L3)

Updated from [`archive/q1/DEFENSE_LEVELS.md`](archive/q1/DEFENSE_LEVELS.md). Applied action per `(risk, level)` as implemented in `src/adapti_guard/policy/policy_engine.py` (pinned by `tests/test_adaptive_q1_fixes.py::test_risk_level_matrix_pinned`):

| Risk | L0 | L1 | L2 | L3 |
|------|----|----|----|----|
| HIGH | BLOCK (A3) | BLOCK | BLOCK | BLOCK |
| MEDIUM | SANITIZE (A1) | SANITIZE | TOOL_RESTRICTION (A2) | BLOCK |
| LOW | NO_INTERVENTION (A0) | SANITIZE | SANITIZE | SANITIZE |

Tool-sensitive requests are restricted (A2) for LOW and HIGH risk, and for MEDIUM risk below L3. Low-risk traffic is never blocked, so "L3 = block" holds only for MEDIUM risk. HIGH risk ignores the level; L0 and L1 are identical for MEDIUM.

| Action | Cost (legacy table) |
|--------|--------------------:|
| A0 | 0.00 |
| A1 | 0.10 |
| A2 | 0.25 |
| A3 | 0.50 |

Cost and latency for Q1 experiments must be measured, not taken from this legacy table.
