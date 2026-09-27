# Experiment Readiness Gate

Generated: `scripts/validate_research_readiness.py` → `EXPERIMENT_READINESS_GATE.json`.  
Phase 6 design: `scripts/validate_phase6_pre_experiment.py` → `PHASE6_COMPLETION.json`.  
Phase 7 live auth: `scripts/validate_phase7_live_authorization.py` → `PHASE7_LIVE_AUTHORIZATION.json`.

**Research Readiness:** NOT READY (live extension + Phase 7 authorization).  
**Phase 6 design gate:** see `phase6_design_gate` in `PHASE6_COMPLETION.json` (≠ live authorization).  
**Phase 7 live:** `PHASE7_LIVE_BLOCKED` until `live_execution_gate: LIVE_AUTHORIZED` (human-filled YAML).  
Phase 8: partial outline.
