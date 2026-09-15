# Novelty Matrix (conceptual — no fabricated citations)

Comparison of ADAPTI-GUARD target contribution vs related areas. Details must be verified against primary sources before manuscript.

| System / area | Threat focus | Detection | Adaptation | Agent | RAG | Evaluation | ADAPTI-GUARD difference (target) |
|---------------|-------------|-----------|------------|-------|-----|------------|----------------------------------|
| Llama Guard | broad safety | ML classifier | static | partial | partial | model-based | threshold adaptive **levels** + cost gate (if demonstrated) |
| Prompt Guard | injection | small classifier | static | no | no | benchmark | multi-level runtime actions L0–L3 |
| NeMo Guardrails | dialog/rails | rules + models | configurable | yes | yes | app-specific | harmonized security–utility–cost **protocol** |
| GuardBench | benchmarks | various | varies | varies | varies | standardized | contributes protocol + adaptive policy eval |
| AgentDojo / InjecAgent | agent attacks | varies | varies | yes | partial | environment | **not yet evaluated** in ADAPTI-GUARD |
| BIPIA / TensorTrust | injection | varies | static | no | partial | public data | **not yet integrated** |
| Adaptive attack literature | adaptive offense | N/A | N/A | varies | varies | adaptive attacks | defense-aware eval **NOT_RUN** |

**Current novelty claim (valid only if EXP-003+ succeed):**

> Harmonized evaluation of a **threshold-based adaptive discrete intervention policy** under judge-measured security–utility–cost trade-offs.

**Invalid claim:** novel regex detector or ML-based adaptation (not implemented).
