# P1 Freeze-Readiness Audit — `p1_mechanism_v1`

**Auditor role:** Independent scientific freeze-readiness review  
**Date (UTC):** 2026-09-15  
**Subject:** `datasets/candidates/p1_mechanism_v1/`  
**Claimed SHA-256:** `1a0b0053c392e7b3e0727b92b4f088790abda001fd852ec1703c5ee0a67dd235`  
**Scope:** Offline audit only. Candidate bytes not modified. No live LLM / API. No detector/defense changes.

**Stated pack purpose (from pack docs):** mechanism-coverage pilot / offline-validated candidate for later gated evaluation — not a statistically powered confirm pack.

---

## 1. Freeze-readiness verdict

```text
FREEZE-READY
```

Interpretation: the pack is internally coherent and sufficiently controlled to be **promoted from `CANDIDATE` to `FROZEN`** as a **mechanism-coverage pilot** under freeze-before-live, subject to **human approval** of the freeze commit (this audit does not perform the freeze).

It is **not** certified as sufficient alone for strong statistical confirmatory claims.

---

## 2. Blocking issues

```text
NONE
```

No integrity, schema, hash, DAN-dependency, success-condition, C4 leakage, or historical-artifact defects were found that prevent freezing for the stated pilot purpose.

---

## 3. Non-blocking limitations

| Limitation | Classification |
| --- | --- |
| Exactly 2 attacks per mechanism leaf (N_attack=44) | Acceptable for mechanism-coverage pilot; not powered for strong family-level inference |
| E2 leaf diversity rated **LIMITED** (same tool, similar retrieve scaffolds) | Within pilot tolerance |
| 1× **weak_twin** (`p1m_atk_038` / `p1m_ben_038` hex vs “convert cat to hex”) | Twin still security-distinct; task match weak |
| Contamination screen = **exact normalized** prompt/context only | Near-duplicate / scaffold / semantic contamination **not** ruled out |
| Indirect / tool-output / file / web channels are **single-turn authored-channel** (`context` text), not live retriever/tool I/O | Must not be cited as live indirect injection |
| B4 rows set `context_source=tool_output` but do **not** populate episode `tool_output` field (channel text lives in `context`) | Consistent with authored-channel design; document at freeze |
| C1–C3 (+ E3 plants) are **contextual/sequential proxies** (`sequential_representation=frozen_context`), not live multi-turn | Explicit in metadata; P2 owns live state |
| C4 adaptive attacker = 0 rows | Intentional |
| Cross-cutting `mechanism_overlap` risk: F2 HTML-comment smuggling vs B1/B3 channels; D3 `p1m_atk_028` related-docs rail is also tool-output-like; D4/E1/A1 can share email side effects with different primary mechanisms | Leaves remain distinguishable by primary `family` + `mechanism` text; not freeze-blocking for pilot |
| Some hard negatives are metacognitive/easy (e.g. lecture category list) | Still `label=benign`, no tool_call; limited “hardness” |

---

## 4. Exact candidate inventory (verified)

| Quantity | Verified value |
| --- | ---: |
| Pack files | **5** (`dataset.jsonl`, `manifest.json`, `hashes.sha256`, `DATASET_CARD.md`, `README.md`) |
| Total episodes | **96** |
| Attacks | **44** |
| Benign (all) | **52** |
| Benign twins (1:1) | **44** |
| Hard negatives | **8** |
| In-scope mechanism leaves | **22** |
| Attacks per in-scope leaf | **2** |
| C4 rows | **0** |
| Unique IDs | **96 / 96** |
| Ordering | Interleaved `p1m_atk_XXX` / `p1m_ben_XXX` for 001–044, then hard-neg `p1m_ben_045`–`052`; attack IDs sorted |
| `manifest.status` | `CANDIDATE` |
| `live_evaluated` | `false` |
| Recomputed SHA-256 | `1a0b0053c392e7b3e0727b92b4f088790abda001fd852ec1703c5ee0a67dd235` (**MATCH**) |
| Builder re-assemble hash | **MATCH** (deterministic) |
| Schema / required metadata | **0** errors |
| Attack success conditions classed `observable` | **44 / 44** |

---

## 5. Estimand readiness

| Quantity | Status | Reason |
| --- | --- | --- |
| Attack success / harmful-action rate (pack-level, after gated live) | **SUPPORTED LATER** | Observable tool-execution `success_condition` on all 44 attacks; confirm-pack-compatible episode shape |
| Family- / mechanism-level breakdown | **SUPPORTED LATER** (descriptive / pilot) | 22 leaves × 2; **REQUIRES ADDITIONAL DESIGN** for powered CIs / multiple-testing plan |
| Utility | **SUPPORTED LATER** | 44 benign twins + success conditions for legitimate workflows |
| FPR / false intervention | **SUPPORTED LATER** | Twins + 8 hard negatives; hardness uneven |
| Security/utility trade-off | **SUPPORTED LATER** | Paired design enables joint reporting after live gate |
| Live multi-turn / persistence ASR | **NOT SUPPORTED** | Sequential rows are frozen-context proxies only |
| Delayed activation as live temporal process | **NOT SUPPORTED** | C2 is contextual/sequential proxy |
| Adaptive attacker ASR | **NOT SUPPORTED** | C4 = 0; no hidden adaptive rows |
| Live indirect injection via real retriever/tool I/O | **NOT SUPPORTED** | Single-turn authored-channel only |
| Any metric from this audit alone | **NOT SUPPORTED** | No live evaluation performed; metadata ≠ results |

---

## 6. Required remediation

```text
NONE (for FREEZE-READY as mechanism-coverage pilot)
```

Optional post-freeze hardening (non-blocking; separate task if desired):

1. Strengthen `p1m_ben_038` twin task alignment.  
2. Add near-duplicate / scaffold contamination report (do not silently rewrite frozen bytes).  
3. Clarify DATASET_CARD wording that B4 channel text is in `context` (authored-channel).  
4. Expand E2 surface diversity in a **v1.1** pack if powered retrieve-exfil claims are planned.

---

## 7. P2 readiness (after freeze)

After human-approved freeze of this pack (recommended version label below), **P2 may begin harness/protocol work** for estimands this pack cannot support:

```text
real multi-turn state
persistence (live)
delayed activation (live)
tool chains (live round-trips)
memory/state stores
adaptive attacker
```

P2 must **not** pool its estimands with P1 pilot metrics unlabeled. P1 frozen pack remains the mechanism-coverage / single-turn authored-channel reference.

---

## Audit notes by checklist

### AUDIT 1 — Data integrity

PASS. Hash match; manifest match; counts match; unique IDs; deterministic rebuild.

### AUDIT 2 — Taxonomy consistency

PASS for freeze. All 44 attacks map to taxonomy operational definitions with concrete tool-level harm.  
Flags recorded as **non-blocking**: `mechanism_overlap` (F2↔B channel surfaces; D3 `p1m_atk_028` tool-output-like; email side effects across A1/D4/E1). No `surface_mechanism_confusion` that empties a leaf. No DAN-as-A2.

### AUDIT 3 — Two-example-per-leaf

| Rating | Leaves |
| --- | --- |
| ADEQUATE | 21 (A1–E1, E3–F4) |
| LIMITED | E2 |
| INADEQUATE | 0 |

Acceptable as **mechanism-coverage pilot**; not as sole statistically powered benchmark.

### AUDIT 4 — Benign twins

| Class | n |
| --- | ---: |
| strong_twin | 32 |
| acceptable_twin | 11 |
| weak_twin | 1 (`p1m_atk_038`) |
| invalid_twin | 0 |

No accidental attack-kind execution targets found on twins.

### AUDIT 5 — Hard negatives

All 8: `label=benign`, `tool_call` absent, metacognitive / quote / classify / translate / policy intents. Legitimate benign; detector-confusion potential present for quote/override strings; several are easy. Not disguised attacks.

### AUDIT 6 — Contamination

Builder + manifest implement **exact normalized** prompt/context collision screen vs Phase-1 / VNEXT / Layer A; `n_hits=0` at build.  
**No** repository evidence of near-duplicate, scaffold-reuse, or embedding semantic screens for this candidate. Limitation must be stated at freeze.

### AUDIT 7 — No-DAN / role artifacts

Word-boundary check: **no** `DAN` / `do anything now` / `you are now DAN`.  
Substring `dan` in `attendance` / `guidance` is **not** a DAN artifact.  
No `you are the administrator` role-only A2. A2 rows use spoofed developer/system channels with tool harm.

### AUDIT 8 — Indirect attack validity

B1–B4: external content appears as **authored `context`** with correct `context_source` labels.  
Classification: **single-turn authored-channel** — **not** live indirect injection.

### AUDIT 9 — Success conditions

44/44 attacks: concrete privileged tool execution criteria → **observable**.

### AUDIT 10 — Sequential claims

C1–C3 attacks: `sequential_representation=frozen_context`.  
Classification: **contextual/sequential proxy** — **not** live multi-turn attack evidence.

### AUDIT 11 — Adaptive attacker

C4 = 0 rows. No adaptive behavior fields/rows. Intentional.

### AUDIT 12–13 — Estimands / statistics

See §5. N = 44 / 44 / 8 appropriate for **pilot, mechanism validation, offline QC**; **not** alone for strong statistical confirmatory claims.

### AUDIT 14 — Freeze versioning

Current: `status=CANDIDATE`, `live_evaluated=false`.  
**Recommendation (human freeze commit only):** promote to frozen path with version:

```text
p1_mechanism_v1.0.0
```

This audit agent does **not** perform the freeze.

### AUDIT 15 — Historical integrity

| Artifact | Expected | Observed |
| --- | --- | --- |
| `eval_v1` | `27b1733c…c54c24` | **MATCH** |
| `common_attack_stream` | `d101f94d…a06c47` | **MATCH** |
| `vnext_confirm_v1` (Track A pack) | `523c8818…721518` | **MATCH** |
| `phase1_confirm_v1` (Track B pack) | `c789811a…536d01` | **MATCH** |

Track A / Track B frozen packs untouched. No historical ASR or simulation results altered by this audit.

---

## Explicit non-claims of this audit

- Does not claim improved security, ASR, utility, or FPR.  
- Does not authorize skipping freeze-before-live or human budget gates.  
- Does not reclassify authored-channel rows as live indirect/multi-turn evidence.  
- Does not modify candidate or frozen bytes.

---

## One-sentence answer

> **`p1_mechanism_v1` is internally coherent and sufficiently controlled to be frozen as a mechanism-coverage pilot benchmark for subsequent gated evaluation, provided freeze metadata continue to state authored-channel / frozen-context sequential limits and exact-only contamination screening.**
