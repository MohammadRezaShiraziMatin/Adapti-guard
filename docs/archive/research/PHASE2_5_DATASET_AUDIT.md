# Phase 2.5 — Dataset Audit Report (Read-Only)

**Date:** 2026-09-02  
**Policy:** DATA MUTATION POLICY — **no source datasets modified**  
**Verdict:** **`FREEZE_BLOCKED`**

---

## Executive Summary

A read-only audit of `benchmark_q1` and `attack_dataset.json` was performed. **No samples were deleted, relabeled, moved, or overwritten.** No frozen evaluation artifact was created because the current data **does not meet scientific freeze criteria**.

**Priority followed:** audit → identify problems → document problems → freeze only if defensible.

---

## Mutation Log

| Operation | Datasets modified |
|-----------|-------------------|
| READ_ONLY_AUDIT | **None** |

Full audit trail: `datasets/audit/phase2_5_readonly/mutation_audit_log.jsonl`

Machine-readable report: `datasets/audit/phase2_5_readonly/phase2_5_audit_report.json`

---

## What Passed (Integrity)

| Check | Result |
|-------|--------|
| SHA-256 train/val/test vs `hashes.json` | **All match** |
| Duplicate sample IDs across splits | **0** |
| Cross-split exact prompt-hash overlap | **0** (train∩test, train∩val, val∩test) |
| Total benchmark_q1 samples | **15,053** (matches `statistics.json`) |
| attack_dataset upstream IDs in benchmark_q1 | **528/528** (provenance OK) |
| attack_dataset duplicate upstream IDs | **0** |

`benchmark_q1` split hygiene is **good**. The blockers are **coverage, taxonomy gaps, and eval-set design** — not hash corruption.

---

## What Failed (Freeze Blockers)

### 1. `attack_dataset.json` — incomplete (528 / 700 target)

| Category | Have | Need | Shortfall |
|----------|-----:|-----:|----------:|
| system_prompt_leakage | **0** | 100 | **100** |
| tool_abuse_attacks | **28** | 100 | **72** |
| (total samples) | **528** | **700** | **172** |

Documented in file's own `coverage_gaps` field — not patched by relabeling.

### 2. Test-split taxonomy gaps (mapped to Phase 2 categories)

Counts from **read-only** keyword/category mapping on `benchmark_q1/test.jsonl` (n=2,259):

| Taxonomy | Test count | Min required |
|----------|----------:|-------------:|
| prompt_injection | 368 | 100 ✓ |
| jailbreak | 921 | 100 ✓ |
| context_attack (indirect) | 157 | 100 ✓ |
| rag_security | 282 | 100 ✓ |
| role_attack (keyword-derived) | 51 | 100 ✗ |
| tool_abuse | **2** | 100 ✗ |
| system_prompt_leakage | **0** | 100 ✗ |

### 3. Agent/tool category scientifically unsupported

- `agent_tool_injection` in test: **2 samples** (mean prompt length ~74 chars)
- Source pool (AgentDojo): **28 total** in full benchmark — cannot reach 100 without **new external data**

### 4. Eval leakage risk — `attack_dataset` vs test split

- Built with `--split all` (train + val + test)
- **70/528** upstream IDs also appear in `benchmark_q1/test.jsonl`
- Using `attack_dataset` as-is for main eval **confounds** held-out test claims

### 5. Adaptive sample derivation (documentation concern)

- **379/2,259** test samples are `adaptive_attacks`
- Derived by template mutation from same upstream corpora present in train
- Not cross-split prompt duplicates, but **source-level derivation** — must be disclosed as limitation

### 6. System prompt leakage — zero coverage

- Keyword scan across test split: **0 matches**
- Cannot freeze a 7-category eval set including leakage

---

## INFRA-SMOKE-001 Overlap (informational)

All 5 smoke samples are from `benchmark_q1/test.jsonl` — acceptable for infrastructure validation, **not** grounds to tune defense on test.

---

## Directory Structure (current)

```text
datasets/
├── benchmark_q1/          # UNTOUCHED — authoritative corpus
├── attack_dataset/        # UNTOUCHED — incomplete derived subset
├── audit/
│   └── phase2_5_readonly/ # NEW — audit outputs only
│       ├── phase2_5_audit_report.json
│       ├── test_taxonomy_counts.json
│       ├── hash_verification.json
│       └── mutation_audit_log.jsonl
├── raw/                   # NOT CREATED — awaiting external imports
├── processed/             # NOT CREATED
└── frozen/                # NOT CREATED — FREEZE_BLOCKED
```

**No files written to `frozen/`** — forcing a freeze would produce a scientifically indefensible artifact.

---

## Required Fixes Before Freeze (in order)

### A. External data import (new files in `datasets/raw/` only)

| Need | Source (examples) | Target |
|------|-------------------|--------|
| +100 system prompt leakage | Garak probe set, curated leakage prompts | `raw/system_prompt_leakage/` |
| +72+ tool abuse | AgentDojo, InjecAgent (when available) | `raw/tool_abuse/` |
| Optional role_attack balance | Tag existing jailbreak/adaptive or import | document in audit |

**Rule:** Import into `raw/` → validate → build **new** processed artifact → never overwrite `benchmark_q1/`.

### B. Eval split design (new artifact, not mutation)

1. Define **frozen eval ID list** drawn from `benchmark_q1/test.jsonl` only
2. Exclude IDs used in any detector tuning or threshold selection
3. Exclude INFRA-SMOKE-001 IDs from main eval (or document as consumed)
4. Build `datasets/frozen/eval_v1/manifest.json` with:
   - ID list + SHA-256
   - category counts per taxonomy
   - explicit exclusion rules
5. Record every ID's provenance — no relabeling to fill gaps

### C. Pass/fail gate for freeze attempt

Freeze allowed only when:

- [ ] All 7 taxonomy categories ≥100 in **frozen eval manifest**
- [ ] Total attack samples ≥700 (or revised pre-registered minimum)
- [ ] Zero IDs from train/val in frozen eval
- [ ] Zero overlap with tuning/dev sets
- [ ] Each gap filled from **documented external raw imports**, not relabeling
- [ ] Mutation audit log entry per build step

---

## What NOT To Do

- Relabel jailbreak → system_prompt_leakage to hit counts
- Move train samples into test
- Duplicate samples across categories
- Freeze `attack_dataset.json` as-is (528, leaky, gapped)
- Declare PASS by lowering category minimums without pre-registration

---

## Recommendation

```text
FREEZE_BLOCKED

Proceed with:
  1. External raw data import (leakage + tool abuse)
  2. New frozen manifest from test split only
  3. Re-audit (read-only) before any freeze attempt

Do NOT proceed to pilot n=20 main eval on an unfrozen, gapped dataset
for publication-grade claims (infrastructure pilot on benchmark_q1 test
subsampling is OK if documented as non-frozen).
```

---

*Original datasets remain fully recoverable and unmodified.*
