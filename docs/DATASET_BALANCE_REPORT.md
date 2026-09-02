# Dataset Balance Report — benchmark_v2

**Status:** PARTIAL — smoke subset only; external benchmarks unavailable.

## Distribution table

| category | subcategory | source | attack/benign | count | percentage |
|----------|-------------|--------|---------------|------:|-----------:|
| direct_injection | template | internal_attack_stream | attack | 2 | 18.2% |
| indirect_injection | template | internal_attack_stream | attack | 2 | 18.2% |
| context_manipulation | template | internal_attack_stream | attack | 2 | 18.2% |
| tool_output_injection | template | internal_attack_stream | attack | 2 | 18.2% |
| benign | qa | internal_benign_tasks | benign | 3 | 27.3% |

**Total:** 11 samples (test split only)

## Class imbalance

- Attack: 72.7% (8/11)
- Benign: 27.3% (3/11)

## Imbalance assessment

The current benchmark is **not suitable for publication**. It is dominated by four near-duplicate template families from the internal attack stream. External datasets must be integrated before EXP-003+.

## Methodology note

Test set was **not** artificially balanced. Stratified evaluation will be applied once full benchmarks are loaded.
