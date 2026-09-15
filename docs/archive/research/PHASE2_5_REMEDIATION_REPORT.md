# Phase 2.5 Dataset Remediation Report

**Date:** 2026-09-02  
**Verdict:** **`FREEZE`**  
**Policy:** `benchmark_q1` **IMMUTABLE** — verified byte-for-byte unchanged

---

## Executive Summary

Phase 2.5 remediation is **complete**. The evaluation dataset was frozen at:

`datasets/frozen/eval_v1/dataset.jsonl` (**770 samples**, SHA-256: `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24`)

The final **role_attack deficit** was resolved by importing the official **TrustLLM jailbreak** benchmark (`scenario` subclass + conservative persona-mechanism filter). No samples were fabricated or relabeled from other categories.

---

## Role Attack Remediation

| Metric | Value |
|--------|------:|
| Previous role_attack (benchmark only) | 55 |
| TrustLLM raw records | 1,400 |
| Accepted external candidates (post-filter) | 100 |
| Selected in frozen eval (TrustLLM) | 55 |
| Selected in frozen eval (benchmark_q1 test) | 55 |
| **Final role_attack** | **110** |

**Classification policy:** TrustLLM official jailbreak label `scenario` (role-play/scenario attack subclass) **plus** explicit persona-mechanism evidence in prompt text. Generic jailbreak transforms (leetspeak, CoT, etc.) excluded.

**Raw import:** `datasets/raw/role_attack/trustllm_jailbreak.json`  
**Provenance manifest:** `datasets/raw/role_attack/source_manifest.json`

---

## Final Category Counts

| Category | Count |
|----------|------:|
| prompt_injection | 110 |
| jailbreak | 110 |
| rag_security | 110 |
| context_attack | 110 |
| role_attack | 110 |
| tool_abuse | 110 |
| system_prompt_leakage | 110 |
| **Total** | **770** |

---

## Source Distribution

| Source | Count |
|--------|------:|
| benchmark_q1/test | 497 |
| trustllm (role_attack) | 55 |
| garak | 110 |
| injecagent | 62 |
| agentdojo | 46 |

---

## Integrity Checks (all passed)

| Check | Result |
|-------|--------|
| All categories ≥ 110 | ✓ |
| Total ≥ 770 | ✓ |
| Unique IDs / SHA-256 | ✓ |
| No train/val leakage | ✓ |
| No INFRA-SMOKE overlap | ✓ |
| Full provenance | ✓ |
| benchmark_q1 unchanged | ✓ |

Audit: `datasets/audit/phase2_5_remediation/eval_v1_audit_report.json`

---

## Frozen Artifacts

| Path | Description |
|------|-------------|
| `datasets/frozen/eval_v1/dataset.jsonl` | Frozen evaluation set |
| `datasets/frozen/eval_v1/manifest.json` | Build + freeze metadata |
| `datasets/frozen/eval_v1/hashes.json` | Dataset + per-sample SHA-256 |
| `datasets/frozen/eval_v1/provenance.jsonl` | Per-sample provenance |
| `datasets/frozen/eval_v1/dataset_card.md` | Dataset card |

---

## Role Attack Audit Artifacts

- `datasets/audit/phase2_5_remediation/role_attack_inventory.json`
- `datasets/audit/phase2_5_remediation/role_attack_exclusions.jsonl`
- `datasets/audit/phase2_5_remediation/role_attack_provenance.jsonl`
- `datasets/audit/phase2_5_remediation/role_attack_report.json`

---

## Re-run (deterministic)

```bash
python scripts/build_frozen_eval_v1.py
python scripts/audit_frozen_eval_v1.py
```

---

*benchmark_q1 and datasets/raw/* remain immutable and recoverable.*
