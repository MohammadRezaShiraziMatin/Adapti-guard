# Reproducibility — Q1 findings (offline checklist)

**API default:** **0** — no OpenRouter unless Matin approves Phase 3 budget ([`DECISION_LOCK_Q1_P3_ARMS.md`](../../experiments/DECISION_LOCK_Q1_P3_ARMS.md)).

---

## Frozen packs (SHA-256)

| Track | Pack | SHA-256 |
| --- | --- | --- |
| A — VNEXT | `vnext_confirm_v1.0` | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` |
| B — Phase-1 | `phase1_confirm_v1` | `c789811a07d3ed06e1c77d8a45eda6172f480226e006d84fa28386a982536d01` |

Verify: `sha256sum datasets/frozen/vnext_confirm_v1/dataset.jsonl` (and Phase-1 pack path on tip).

---

## Canonical AUDIT paths (do not edit)

| Track | Path |
| --- | --- |
| A | `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md` |
| A verdict | `…/verdict.json` |
| B | `experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/AUDIT.md` |
| B verdict | `…/verdict.json` |

---

## Live eval contract (historical runs only)

| Field | Value |
| --- | --- |
| Target | `qwen/qwen-2.5-7b-instruct` |
| Judge | `qwen/qwen-2.5-72b-instruct` (**Target ≠ Judge**) |
| Cache | **off** on confirmatory AUDIT |
| Track A FAIL | **Do not rerun** to amend verdict |

---

## Offline scripts + artifacts (no LLM)

| Script | Output | Seeds / inputs |
| --- | --- | --- |
| [`scripts/recompute_vnext_delta_ci.py`](../../scripts/recompute_vnext_delta_ci.py) | [`artifacts/vnext_delta_ci_offline.json`](artifacts/vnext_delta_ci_offline.json) | b10/b01/n from verdict; bootstrap **5000**, **seed=42** |
| [`scripts/recompute_vnext_mcnemar_power.py`](../../scripts/recompute_vnext_mcnemar_power.py) | [`artifacts/vnext_track_a_power_sensitivity.json`](artifacts/vnext_track_a_power_sensitivity.json) | Same contingency; binomial scaffold documented in JSON |
| [`verify_q1_findings_facts.py`](verify_q1_findings_facts.py) | exit 0 = manuscript hygiene PASS | — |
| [`../workshop_vnext_fail/verify_manuscript_facts.py`](../workshop_vnext_fail/verify_manuscript_facts.py) | workshop + dual-track hygiene | — |

```bash
python3 docs/paper/q1_findings/verify_q1_findings_facts.py
python3 docs/paper/workshop_vnext_fail/verify_manuscript_facts.py
python3 scripts/run_q1_p3_1_confirm.py --defense-smoke
python3 -m pytest tests/test_q1_findings_facts.py tests/test_vnext_delta_ci_offline.py tests/test_vnext_mcnemar_power_offline.py tests/test_q1_p3_1_baseline_smoke.py -q
```

---

## Requires human API budget (not done on this branch)

- Phase 3 arms per [`DECISION_LOCK_Q1_P3_ARMS.md`](../../experiments/DECISION_LOCK_Q1_P3_ARMS.md) · P3-1 runner ready-when-budget [`DECISION_LOCK_Q1_P3_1_BASELINE.md`](../../experiments/DECISION_LOCK_Q1_P3_1_BASELINE.md)
- Any new live eval → **new** AUDIT folder; never rewrite Track A FAIL numbers

**Hub:** [`docs/experiments/REPRODUCIBILITY_PACKAGE.md`](../../experiments/REPRODUCIBILITY_PACKAGE.md) · hashes [`../workshop_vnext_fail/APPENDIX_HASHES.md`](../workshop_vnext_fail/APPENDIX_HASHES.md)
