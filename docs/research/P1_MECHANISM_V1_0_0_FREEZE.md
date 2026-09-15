# P1 Mechanism Benchmark — Freeze Record `v1.0.0`

**Status:** `FROZEN`  
**Date (UTC):** 2026-09-15  
**Pack path:** `datasets/frozen/p1_mechanism_v1.0.0/`  
**dataset SHA-256:** `1a0b0053c392e7b3e0727b92b4f088790abda001fd852ec1703c5ee0a67dd235`

---

## Decision chain

```text
P0 COMPLETE
 ↓
P1 CANDIDATE COMPLETE
 ↓
P1 FREEZE AUDIT = FREEZE-READY (blocking issues: NONE)
 ↓
P1 v1.0.0 FROZEN
 ↓
HUMAN BUDGET / LIVE-EVALUATION GATE
 ↓
P2 / LIVE AGENTIC EVALUATION (not started by this freeze)
```

Audit: `docs/research/P1_FREEZE_READINESS_AUDIT.md`

---

## Inventory (verified at freeze)

| Item | Count |
| --- | ---: |
| Attacks | 44 |
| Benign twins | 44 |
| Hard negatives | 8 |
| Total episodes | 96 |
| In-scope mechanisms | 22 |
| Attacks per leaf | 2 |
| C4 adaptive | 0 |

---

## Provenance

| Field | Value |
| --- | --- |
| Created from | `datasets/candidates/p1_mechanism_v1/` |
| Construction commit | `949672ff69bfeacce0654e5082521c95364679a9` |
| Freeze base commit | `b87c76761b381d91096651e2e309a66bd85982a6` |
| Candidate retained | yes (byte-identical `dataset.jsonl`) |

`dataset.jsonl` bytes were **copied without modification**. Manifest/card/README for the frozen path are freeze metadata only.

---

## Explicit status

```text
status = FROZEN
live_evaluated = false
NO LIVE LLM EVALUATION PERFORMED
```

---

## Known limitations (immutable documentation)

- 2 examples per leaf
- pilot-scale, not statistically powered
- E2 diversity limited
- 1 weak benign twin
- contamination screen is exact-normalized only
- near/scaffold/semantic contamination not ruled out
- indirect channels are single-turn authored-channel
- B4 tool-output injection is represented in context rather than live tool_output
- C1–C3 are frozen-context sequential proxies
- C4 adaptive attacker is absent

Freeze means **immutable artifact**, not **perfect benchmark**.

---

## Scientific integrity at freeze

```text
Track A unchanged
Track B unchanged
historical results unchanged
detector unchanged
defense policy unchanged
thresholds unchanged
```

Historical hashes verified at freeze prep:

- `eval_v1` → `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24`
- `common_attack_stream` → `d101f94d97e0a29e8b9f9cc4dacb92472e29cd9af403114cb09b8f1d50a06c47`

---

## Next gate

```text
HUMAN BUDGET / LIVE-EVALUATION GATE
```

Do not start P2 or live evaluation automatically from this freeze.
