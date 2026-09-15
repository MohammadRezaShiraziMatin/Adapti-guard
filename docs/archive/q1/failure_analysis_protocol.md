# Failure Analysis Protocol (EXP-010)

> Qualitative analysis of ADAPTI-GUARD failures.  
> **Prerequisite:** Completed EXP-004 with `*_predictions.jsonl` artifacts.

## Selection Criteria

### Successful attacks (n=10 minimum)

Select episodes where:
- `is_attack == true`
- `judge_verdict == attack_success` (or `attack_success == true`)
- `defense_action != A3` OR defense was applied but judge still ruled success

Stratify across attack categories (at least 1 per category with available data).

### False positives (n=10 minimum)

Select episodes where:
- `is_attack == false` (benign)
- `defense_blocked == true` OR `utility_score == 0`

## Analysis Template (per case)

```markdown
### Case {id}

| Field | Value |
|-------|-------|
| attack_id | |
| category | |
| model | |
| defense_level | |
| defense_action | |
| detector_score | |
| risk_level | |
| judge_verdict | |
| failure_type | ASR_success / false_positive |

**Prompt excerpt:** (first 200 chars)

**Model response excerpt:** (first 300 chars)

**Root cause module:**
- [ ] Detector (miss / under-threshold)
- [ ] Risk engine (under-scored)
- [ ] Policy engine (wrong level)
- [ ] Action layer (sanitize insufficient)
- [ ] Adaptation (stuck at low level / over-aggressive)
- [ ] Judge disagreement (possible)

**Why it failed:** (2–3 sentences)

**Proposed fix:** (1 sentence)
```

## Module Attribution Decision Tree

```
attack_success?
├── detector_score < τ → Detector miss
├── detector_score ≥ τ but action == A0 → Policy/Risk failure
├── action == A2 but judge says success → Sanitization insufficient
├── action == A3 but judge says success → Block bypass / judge error
└── benign blocked at L3 → Over-escalation / adaptation stuck high
```

## Output Artifacts

| File | Description |
|------|-------------|
| `results/failure_analysis/asr_successes.jsonl` | 10+ attack bypass cases |
| `results/failure_analysis/false_positives.jsonl` | 10+ benign blocks |
| `figures/failure_taxonomy.png` | Pie chart by module |
| `docs/FAILURE_ANALYSIS.md` | Narrative for paper §5.6 |

## Extraction Script (when data available)

```bash
python scripts/extract_failure_cases.py \
  --input experiments/EXP004_MULTI_MODEL/model_a/B6/B6_predictions.jsonl \
  --n-asr 10 --n-fpr 10 \
  --output results/failure_analysis/
```

## Current Status

| Item | Status |
|------|--------|
| Predictions available | **NO** (EXP-004 BLOCKED) |
| ASR cases collected | 0 / 10 |
| FPR cases collected | 0 / 10 |
| Human validation | NOT_RUN |

## Expected Paper Narrative

§5.6 Limitations and Failure Modes should report:
1. Dominant failure mode (likely detector miss on indirect/RAG — F1=0.41 held-out)
2. Category-specific weakness (tool abuse: n=28 in attack_dataset)
3. Adaptation lag during phase transitions (EXP-009)
4. Judge–human disagreement rate (requires HUMAN_EVAL)

---

*Do not fabricate case studies. Populate only from real prediction logs.*
