# Research History

Append-only project history. Do not delete prior entries.

---

## 2026-09-01 — Q1 upgrade initiated

### Previous architecture (baseline commit `612f577`)

- Regex detector (~1,387 lines, V3–V18 patches)
- Simulated ASR via `attack_outcome.py` substring matching
- Harmonized runner comparing fixed L0–L3 vs threshold adaptive controller
- No target LLM, no independent judge
- Datasets and results gitignored; clone not self-contained

### Known weaknesses (audit)

- ASR circular / not scientifically valid for LLM claims
- NotInject held-out F1 ≈ 0.41
- No SOTA baselines executed
- No statistical inference (CIs, paired tests)
- Garak/Inspect integrations broken (`DefensePipeline` missing)

### Q1 upgrade actions (this session)

1. Baseline inventory documented
2. Real LLM pipeline modules added (target + judge)
3. Experiment logging standard implemented
4. benchmark_v2 builder created; external data unavailable in clone
5. EXP-000 BLOCKED pending API key in automation environment

### Failed / blocked

- EXP-000 live API validation: BLOCKED in agent environment (user reports OK locally)

### Successful

- Unit tests for logging, statistics, mock target model
- `DefensePipeline` alias restored
