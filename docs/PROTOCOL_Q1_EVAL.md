# Q1 Evaluation Protocol (canonical contract)

**Binding file:** `configs/q1_evaluation_contract.yaml`  
**Model panel (additive):** `configs/models_q1_eval_panel.yaml`  
**Offline check:** `validate_q1_evaluation_contract()` · `tests/test_q1_evaluation_contract.py`

Does **not** replace VNEXT `target_2`/`judge_fallback` binding in `configs/models.yaml` (SHA `37174858…`).  
Dataset: `vnext_confirm_v1` (61+61, SHA `523c8818…`). Primary attack episode count: **owner-locked** (`primary_episode_budget.attack_episodes`); **derived** = `n_attack × n_primary_targets × n_arms` (currently 61×4×3 if panel/arms unchanged). Budget **hard_cap_usd**: owner-locked (`NEEDS_DECISION` until sign-off); enforcement via `BudgetLedger` when set.

Items marked `NEEDS_DECISION` in YAML require owner lock before live authorization. Protocol freeze: **not** active (`execution_gate: BLOCKED`); see `scientific_design.owner_decision_intake` in contract YAML. Minimum freeze scope (P0/P1/P2): `docs/Q1_OWNER_DECISION_PACK.md` § Minimum Q1 Scientific Protocol.

Scientific design audit: `docs/Q1_SCIENTIFIC_COMPLETENESS_AUDIT.md`. Owner decisions: `docs/Q1_OWNER_DECISION_PACK.md`.
