# Statistical Validation Report

**Generated:** 2026-09-01  
**Status:** Framework implemented; real-LLM statistics pending API execution

---

## Implemented Tests

| Test | Module | Use case |
|---|---|---|
| Bootstrap 95% CI | `statistics.bootstrap_ci` | ASR, utility, latency means |
| McNemar exact test | `statistics.mcnemar_test` | Paired binary outcomes (method A vs B) |
| Wilcoxon signed-rank | `statistics.wilcoxon_signed_rank` | Paired continuous (latency, cost) |

---

## EXP-005 Adaptation Ablation (Simulation)

**Mode:** HARMONIZED_SIMULATION (heuristic ASR)  
**Seeds:** 5  
**Episodes per seed:** 100

| Condition | ASR mean | ASR std | 95% CI |
|---|---:|---:|---|
| A: No adaptation (Fixed L1) | 0.000 | 0.000 | [0.000, 0.000] |
| B: Rule-based (Escalation only) | 0.027 | 0.000 | [0.027, 0.027] |
| C: De-escalation only | 0.013 | 0.000 | [0.013, 0.013] |
| D: Full ADAPTI-GUARD | 0.027 | 0.000 | [0.027, 0.027] |

**Caveat:** All seeds produce identical results because `HarmonizedRunner` is deterministic. Seed parameter is not wired. **Not valid for publication.**

**Effect size:** Negligible (ΔASR ≤ 0.027 on simulation).

---

## EXP-008 Adaptive Attack (Simulation)

**Mode:** DETECTOR_SIMULATION  
**Rounds:** 3 × 50 attacks

Block rate evolves as attacker changes family after failures. Results in `experiments/EXP008_ADAPTIVE_ATTACK/metrics.json`.

---

## Required for Publication

### Per EXP-002 (Real LLM)
```python
from src.adapti_guard.evaluation.statistics import bootstrap_ci, mcnemar_test

# ASR confidence interval
asr_ci = bootstrap_ci(attack_success_binary, seed=42)

# Paired: ADAPTI-GUARD vs no defense
mcnemar = mcnemar_test(no_def_success, adapti_success)
```

### Multi-seed protocol
- 5 seeds: `{42, 123, 456, 789, 1011}`
- Different test subsamples (stratified shuffle)
- Report mean ± std and 95% bootstrap CI
- Apply Bonferroni correction for 7 baseline comparisons (α = 0.05/7 ≈ 0.007)

### Effect size
Cohen's d for ASR difference:
```
d = (mean_asr_baseline - mean_asr_method) / pooled_std
```

---

## Power Analysis (planned)

For detecting ASR reduction from 15% → 10% at α=0.05, power=0.80:
- Required paired samples: ~400 per comparison
- Current EXP-002 target: 500 ✓

---

## Status Summary

| Claim | Statistical support | Valid? |
|---|---|---|
| Adaptation reduces ASR | EXP-005 sim only | NO |
| ADAPTI-GUARD beats no defense | Not run (real LLM) | NO |
| Adaptive robustness | EXP-008 sim only | PARTIAL |
| Judge reliability | Human eval not run | NO |
