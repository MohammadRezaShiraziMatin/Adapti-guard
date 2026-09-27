# Metrics and statistics

**Canonical definitions (pre-registration):** [`docs/archive/research/METRICS_AND_STATISTICS.md`](../archive/research/METRICS_AND_STATISTICS.md).

**Q1 extensions:** Tool-HASR (operational), Judge-ASR (diagnostic), per-turn/cumulative metrics for E1–E3 — see `UNIFIED_RESEARCH_FRAMEWORK.md`.

**Pipeline implementation:** `src/adapti_guard/evaluation/statistics.py` — validated by `tests/test_statistics.py` (fixture; not empirical results).

**Phase 3 mapping:** condition → metrics → stats in [`EXPERIMENT_MATRIX.yaml`](EXPERIMENT_MATRIX.yaml) and [`EXPERIMENT_PROTOCOL.md`](EXPERIMENT_PROTOCOL.md) §4.

**Phase 5 (trustworthy / human-centered — no new empirical metrics):**

| Dimension | Existing metrics / observables | Empirical status |
| --- | --- | --- |
| Security | Judge-ASR, Tool-HASR, McNemar cells | Track A/B where locked |
| Utility | Utility U, gates | Partial per track |
| Reliability | Failure semantics, offline harness | Design + offline |
| Transparency | `policy_reason`, risk reasons, evidence trace | Design-only explainability |
| Auditability | Schema provenance chain | Phase 3–4 |
| Human oversight | Override rate (undefined) | **EVIDENCE-BLOCKED** |
| Uncertainty | Detector probability, risk score | Not calibrated trust |
| Cost | AUDIT cost fields | Partial |

See [`PHASE5_TRUSTWORTHY_APPLICATION.md`](PHASE5_TRUSTWORTHY_APPLICATION.md).
