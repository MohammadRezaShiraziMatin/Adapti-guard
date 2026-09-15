# AdaptiGuard — Final Results Summary
_Generated: 2026-09-03T20:50:47.024642+00:00_
## Abstract
AdaptiGuard is a runtime LLM defense evaluation framework with discrete intervention levels (L0–L3), risk-aware policy control, and a harmonized security–utility–cost protocol. This completion pass re-executed simulation experiments, regenerated missing Phase 7 artifacts, validated providers, and confirmed that publication-grade real-LLM ASR remains blocked by judge API failures (Cerebras HTTP 402; Gemini free-tier 429). No fabricated ASR is reported.
## Experimental Setup
- Simulation: frozen attack stream (100), W1 schedule 75/25, seed 42
- Real LLM Target: Groq `openai/gpt-oss-120b`
- Intended Judge: Cerebras `qwen-3.8-27b` (blocked)
- Phase 5 matrix reused: 3×2×50 = 300 Target observations (not re-run)
## Dataset
- Frozen eval: `datasets/frozen/eval_v1/dataset.jsonl` (n=770), SHA-256 `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24` (match=True)
- Attack stream: `results/common_attack_stream.json`, SHA-256 `d101f94d97e0a29e8b9f9cc4dacb92472e29cd9af403114cb09b8f1d50a06c47` (match=True)
- Primary frozen eval is **attack-only** → utility/FPR not available for Phase 5
## Attack Methods
- Template families in `AdaptiveAttacker`: direct/indirect injection, context manipulation, tool-output injection
- Frozen eval categories include jailbreak, RAG, role, system-prompt leakage, tool abuse
- Harmonized primary protocol **replays** frozen stream (defense-unaware during eval)
## Defense Methods
- Actions A0–A3 / levels L0–L3 with costs 0.00/0.10/0.25/0.50
- Adaptive policy via `PolicyUpdateEngine` (B3/B6 alias)
- Harmonized ablations: escalation_only, de_escalation_only, no_cost_gate
## Models
- Target (executed): Groq gpt-oss-120b — provider smoke PASS; Phase 5 300/300 ok; minimal smoke 3/3 ok
- Judge Cerebras qwen-3.8-27b: FAIL 402 payment_required
- Gemini: provider smoke PASS; judging at scale historically 429 (skipped in smoke)
- OpenRouter: key invalid in this environment
## Results
### Provider smoke
- groq: **PASS** latency_ms=1864.86
- cerebras: **FAIL** (402_payment_required)
- gemini: **PASS** latency_ms=3585.33

### Harmonized simulation (LEGACY_SIMULATION_ONLY)
| Method | ASR | Defense Rate | Utility | Cost |
|---|---:|---:|---:|---:|
| fixed_l0 | 1.000 | 0.000 | 1.0 | 0.000 |
| fixed_l1 | 0.000 | 1.000 | 1.0 | 0.100 |
| fixed_l2 | 1.000 | 0.000 | 1.0 | 0.250 |
| fixed_l3 | 0.000 | 1.000 | 0.0 | 0.500 |
| full_adaptive | 0.027 | 0.973 | 1.0 | 0.379 |
| escalation_only | 0.027 | 0.973 | 1.0 | 0.379 |
| de_escalation_only | 0.013 | 0.987 | 1.0 | 0.082 |
| no_cost_gate | 0.333 | 0.667 | 1.0 | 0.318 |

> These ASR values are **simulation outcomes** (regex/detector-coupled) and are **not** independent LLM-judge ASR.

### Phase 5 real LLM (Targets)
- n_target=300, all api_status=ok
- B0 mean ICS=0.00 (A0); B6 mean ICS=0.10 (A1 on all episodes)
- Judge ASR: **NOT COMPUTABLE** (Gemini 298/300 failed historically; Cerebras rejudge blocked 402)

### Minimal real-LLM smoke (this pass)
- Targets OK: None/3
- Valid judgments: 2
- ASR: 0.0
## Ablation Study
- Simulation ablations executed in harmonized bundle (escalation_only, de_escalation_only, no_cost_gate) — see table above.
- Real-LLM EXP-006: **NOT_EXECUTED** (budget + prior artifacts LEGACY_SIMULATION_ONLY).
## Limitations
1. No publication-valid real-LLM ASR.
2. Simulation ASR is not interchangeable with judge ASR.
3. Phase 5 Target text truncation (500 chars) remains.
4. model_a/b/c in Phase 5 are the same Groq model.
5. Cerebras billing and Gemini rate limits block independent judging.
6. OpenRouter multi-model track unavailable (invalid key).
## Reproducibility
```bash
source .venv/bin/activate
pip install -r requirements-core.txt
python experiments/FINAL_COMPLETION/regen_phase7.py
python scripts/run_q1_harmonized_v1.py
python experiments/FINAL_COMPLETION/run_all.py
python experiments/FINAL_COMPLETION/finalize_artifacts.py
```
Git commit: `35833a64b35a98d596d729c3fa7687e3228381ca`
Manifest: `experiments/FINAL_RESEARCH_MANIFEST.json`
