# DATASET CARD — `p1_mechanism_v1.0.0`

**Status:** `FROZEN`  
**live_evaluated:** `false`  
**Freeze date (UTC):** 2026-09-15

| Field | Value |
| --- | --- |
| Path | `datasets/frozen/p1_mechanism_v1.0.0/dataset.jsonl` |
| Created from | `datasets/candidates/p1_mechanism_v1/` (byte-identical `dataset.jsonl`) |
| SHA-256 | `1a0b0053c392e7b3e0727b92b4f088790abda001fd852ec1703c5ee0a67dd235` |
| Rows | 96 (44 attack / 44 benign twins / 8 hard negatives; benign total 52) |
| Mechanisms | 22 in-scope leaves × 2 attacks; C4 = 0 |
| Construction commit | `949672ff69bfeacce0654e5082521c95364679a9` |
| Freeze decision | `FREEZE-READY` — `docs/research/P1_FREEZE_READINESS_AUDIT.md` |

## Freeze decision

Independent audit verdict **FREEZE-READY** with **NONE** blocking issues. This freeze is **benchmark versioning + integrity**, not a live evaluation and not a claim of improved security.

## Known limitations (retained at freeze)

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

## Live evaluation

```text
NO LIVE LLM EVALUATION PERFORMED
live_evaluated = false
```

Next gate: **HUMAN BUDGET / LIVE-EVALUATION GATE** (not automatic).

## Provenance

Candidate copy retained at `datasets/candidates/p1_mechanism_v1/` for provenance. Do not edit either `dataset.jsonl` after freeze.
