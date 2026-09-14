# Manuscript Evidence Map

| Claim | Experiment | Dataset | Metric | Artifact | Status |
|-------|------------|---------|--------|----------|--------|
| Adaptive policy reduces ASR vs fixed | EXP-003, EXP-005 | benchmark_v2 + external | ASR (judge) | TBD | **NOT_RUN** |
| Adaptive preserves utility | EXP-003 | benchmark_v2 | benign_success_rate | TBD | **NOT_RUN** |
| Cross-model robustness | EXP-004 | benchmark_v2 | ASR per model | TBD | **NOT_RUN** |
| Ablations explain adaptation | EXP-006 | benchmark_v2 | ΔASR, transitions | TBD | **NOT_RUN** |
| Detector generalizes | EXP-002 | NotInject | F1, AUROC | historical only | **PARTIAL** |
| RAG indirect injection defense | EXP-007 | TBD | ASR | TBD | **NOT_RUN** |
| Agent tool injection defense | EXP-008 | TBD | unsafe tool rate | TBD | **NOT_RUN** |
| Cost/latency trade-off | EXP-009 | benchmark_v2 | p50/p95, $/1K | TBD | **NOT_RUN** |
