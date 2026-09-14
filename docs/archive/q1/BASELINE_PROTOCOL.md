# Baseline Protocol

All baselines MUST share:

- Same dataset split and sample IDs
- Same attack/benign prompts
- Same target model(s)
- Same judge model
- Same temperature / max_tokens
- Same random seeds (where applicable)
- Same exclusion rules (failed API calls logged, not imputed)

## Internal baselines

| ID | Name | Status |
|----|------|--------|
| B0 | No defense (passthrough to target) | NOT_EXECUTED |
| B1 | Static regex detector only | NOT_EXECUTED |
| B2–B5 | Fixed L0–L3 | LEGACY_SIMULATION only |
| B6 | full_adaptive | LEGACY_SIMULATION only |

## External baselines

| System | Status |
|--------|--------|
| Llama Guard | NOT_EXECUTED |
| Prompt Guard | NOT_EXECUTED |
| NeMo Guardrails | NOT_EXECUTED |

## Primary metric

**Real ASR** from independent LLM judge — not `attack_outcome.py` simulation.
