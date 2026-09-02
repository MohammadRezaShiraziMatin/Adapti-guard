# ADAPTI-GUARD — Phase 2.7 / EXP-004 Status Report

**Date:** 2026-09-02  
**Project:** ADAPTI-GUARD  
**Research Area:** LLM Security / Prompt Injection Defense  
**Status:** `INFRA_PASS — EXP-004 NOT COMPLETE`

---

## 1. Executive Summary

The Phase 2.5 dataset remediation and freeze have been completed successfully.

The frozen evaluation dataset contains **770 samples**, evenly distributed across seven attack categories, with **110 samples per category**. The dataset integrity audit passed, and the frozen dataset SHA-256 hash was verified.

Phase 2.7 pilot execution completed successfully after an earlier partial failure (see §3 historical note). The successful rerun produced **30/30 paired episodes** with **0 judge failures** and **0 API errors**.

**EXP-004 was not launched** — publication-grade multi-model evaluation (n=500, 3 models) remains pending API budget and metric/reporting fixes applied post-audit.

Therefore, there is currently **no publication-grade experimental evidence** supporting the effectiveness of ADAPTI-GUARD.

---

## 2. Dataset Status

The frozen evaluation dataset was successfully verified.

### Dataset

```text
Location: datasets/frozen/eval_v1/
```

### Size

```text
Total: 770 samples
```

### Category distribution

| Category | Samples |
|----------|--------:|
| Prompt Injection | 110 |
| Jailbreak | 110 |
| RAG Security | 110 |
| Context Attack | 110 |
| Tool Abuse | 110 |
| System Prompt Leakage | 110 |
| Role Attack | 110 |
| **Total** | **770** |

### SHA-256

```text
27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24
```

### Integrity

| Check | Status |
|-------|--------|
| Dataset hash | PASS |
| Manifest verification | PASS |
| Dataset freeze | PASS |
| benchmark_q1 | UNCHANGED |

The frozen dataset must remain immutable during subsequent experiments.

---

## 3. Phase 2.7 Pilot

### Current status (successful rerun — authoritative)

```text
PASS — infrastructure pilot
```

| Field | Value |
|-------|-------|
| Timestamp | `2026-09-02T09:27:28Z` |
| Git commit | `612f577118a19949b4862a3b27b801db8c7eef65` |
| Predictions | 30 (B0: 15, B6: 15) |
| Judge failures | 0 |
| API errors | 0 |
| Pilot status | PASS |

The pilot executed:

```text
15 frozen samples × 2 conditions (B0/B6) = 30 paired episodes
```

**Artifacts:** `experiments/PHASE2_7_PILOT/`  
**Report:** `experiments/PHASE2_7_PILOT/REPORT.md` (PILOT ONLY — NOT FINAL SCIENTIFIC EVIDENCE)

### Historical — earlier failed attempt (superseded)

The **first** pilot run partially completed but did **not** satisfy go/no-go:

| Metric | Value |
|--------|------:|
| Total episodes | 30 |
| Valid episodes | 27 |
| Judge failures | 3 |

Cause: OpenRouter HTTP 402 (in-flight credit budget exhausted) on judge `anthropic/claude-sonnet-4`.

The failures were not converted into synthetic success/failure labels. A later rerun with sufficient API credit produced the PASS artifacts above.

---

## 4. Pilot Metrics

| Metric | B0 | B6 |
|--------|---:|---:|
| ASR | 0.133 | 0.133 |
| Defense Rate | 0.867 | 0.867 |
| Utility | N/A | N/A |

These values are **pilot-only diagnostics** and must NOT be presented as experimental evidence because:

- sample size is very small (n=15);
- only one model was tested;
- no statistical analysis was performed;
- the dataset contains attack samples only;
- no benign utility holdout was evaluated;
- EXP-004 was not completed.

```text
Pilot metrics = NOT publication-grade
```

---

## 5. Model Coverage

| Model | Pilot Status |
|-------|--------------|
| openai/gpt-4o-mini | PASS (30/30, infrastructure pilot) |
| qwen/qwen3-30b-a3b | Not tested |
| deepseek/deepseek-chat-v3-0324 | Not tested |

---

## 6. EXP-004 Status

```text
EXP-004 NOT COMPLETE
```

The experiment was correctly **not launched** — EXP-004 requires publication-grade scale (n=500, 3 models) and sufficient API budget.

Infrastructure prepared:

| Path | Purpose |
|------|---------|
| `experiments/EXP-004/run.py` | Main runner (500 samples, 3 models, B0/B6) |
| `experiments/EXP-004/analyze.py` | Statistical analysis + reports |
| `experiments/EXP-004/README.md` | API budget estimate |
| `experiments/EXP-004/BLOCKED_REPORT.md` | Blocker documentation |
| `src/adapti_guard/evaluation/attack_success.py` | `load_frozen_eval_records()` |

---

## 7. Current Blocker

**Primary blocker for EXP-004:** OpenRouter API budget for ~6,000-call multi-model run.

Estimated EXP-004 workload:

```text
500 paired samples × 3 models × 2 conditions × (target + judge) ≈ 6,000 API calls
```

Sufficient API credit/quota must be available before launching the full experiment.

---

Sufficient API credit/quota must be available before launching the full experiment.

**Post-audit metric fixes (2026-09-02):** Latency aggregation, attack-only N/A semantics, and judge provenance fields were corrected in code. Existing `metrics.json` / `predictions.jsonl` on disk were **not** recomputed — a fresh pilot rerun is optional for provenance fields only.

---

## 8. Required Go/No-Go Criteria

Infrastructure pilot PASS (successful rerun):

- [x] 30/30 episodes complete
- [x] 0 judge failures
- [x] 0 unexplained target failures
- [x] B0 complete
- [x] B6 complete
- [x] Raw target responses preserved
- [ ] Judge raw JSON preserved in predictions (code fixed; existing artifacts pre-fix)
- [x] Sample IDs correctly paired
- [x] Metrics generated
- [x] Experiment logs complete

EXP-004 remains blocked until multi-model n=500 run completes.

---

## 9. Next Experimental Sequence

```text
1. Confirm OpenRouter credit/quota for EXP-004 (~6,000 calls)
        ↓
2. (Optional) Re-run Phase 2.7 to populate judge_raw in predictions
        ↓
3. Audit pilot artifacts
        ↓
4. Approve EXP-004
        ↓
5. Run B0/B6 paired evaluation (n=500, 3 models)
        ↓
6. Perform statistical analysis
        ↓
7. Failure analysis
        ↓
8. Generate publication-grade report
        ↓
9. Update manuscript claims
```

```bash
cd ~/01_BASE_Q1/adapti_guard
# Optional: python experiments/PHASE2_7_PILOT/run.py   # judge_raw provenance
python experiments/EXP-004/run.py --skip-existing
python experiments/EXP-004/analyze.py
```

---

## 10. Statistical Analysis Required for EXP-004

### Security

- Attack Success Rate (ASR)
- Defense Rate
- Category-level ASR
- Model-level ASR

### Utility

- Utility score (N/A on attack-only frozen eval unless benign holdout added)
- Utility degradation
- Benign utility evaluation where applicable

### Operational

- Latency
- Token usage
- API failure rate
- Judge failure rate

### Statistical tests

- McNemar's test (paired B0 vs B6)
- Wilcoxon signed-rank (latency, continuous metrics)
- Bootstrap 95% confidence intervals
- Effect sizes
- Holm correction for multiple comparisons

No statistical significance claim should be made before EXP-004 is completed.

---

## 11. Research Integrity Assessment

| Component | Status |
|-----------|--------|
| Dataset construction | PASS |
| Dataset remediation | PASS |
| Dataset freeze | PASS |
| Dataset hash | PASS |
| benchmark_q1 immutability | PASS |
| B0 infrastructure | READY |
| B6 infrastructure | READY |
| Frozen eval loader | READY |
| Real-LLM API connection | PASS (pilot rerun) |
| Phase 2.7 pilot (infra) | PASS |
| EXP-004 execution | NOT COMPLETE |
| Multi-model evaluation | NOT STARTED |
| Statistical analysis (EXP-004) | NOT STARTED |
| Publication-grade evidence | **NONE** |

---

## 12. Paper-Safe Claims (Current)

| Claim | Status |
|-------|--------|
| Frozen 770-sample eval dataset exists | SUPPORTED |
| 7×110 balanced attack categories | SUPPORTED |
| B6 reduces ASR vs B0 | NOT SUPPORTED |
| Multi-model robustness | NOT SUPPORTED |
| Statistical significance of defense | NOT SUPPORTED |
| Production readiness | NOT SUPPORTED |
| SOTA defense | NOT SUPPORTED |

---

## 13. Conclusion

**Dataset phase:** Complete and frozen.  
**Infrastructure pilot:** PASS (30/30 episodes).  
**Experimental phase (EXP-004):** Not started — blocked on API budget for full run.  
**Publication readiness:** Infrastructure ready; no publication-grade defense evaluation results.

Do not cite pilot ASR (0.133) in the manuscript. Proceed to EXP-004 after API budget confirmation.
