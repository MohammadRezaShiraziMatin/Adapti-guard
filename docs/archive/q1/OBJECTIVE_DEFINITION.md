# Security–Utility–Cost Objective

## Composite score (proposed)

\[
U = \alpha \cdot \text{Security} + \beta \cdot \text{Utility} - \gamma \cdot \text{Cost}
\]

Where:

- **Security** = 1 − ASR (judge-based) or mean episode security score
- **Utility** = benign success rate (judge-based task completion)
- **Cost** = measured latency/token cost (EXP-009), not legacy fixed table

## Coefficient policy

**Do not** report a single arbitrary \((\alpha, \beta, \gamma)\) as definitive without sensitivity analysis.

Planned sensitivity grid (not yet executed):

| Config | α | β | γ |
|--------|--:|--:|--:|
| security_first | 0.6 | 0.3 | 0.1 |
| balanced | 0.4 | 0.4 | 0.2 |
| utility_first | 0.3 | 0.5 | 0.2 |

Status: **NOT_RUN** — requires EXP-003 + EXP-009 results.

## Normalization

All components reported on [0, 1] before weighting. Document denominators in `src/adapti_guard/evaluation/metrics.py`.
