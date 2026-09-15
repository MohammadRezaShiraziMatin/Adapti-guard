# Human Budget / Live-Evaluation Gate

**ID:** `LIVE-EVAL-GATE-0.1`  
**Status:** DESIGN ONLY — blocks execution until human sign-off  
**Protocol:** [`LIVE_EVALUATION_PROTOCOL.md`](LIVE_EVALUATION_PROTOCOL.md)  
**MASTER_PROMPT:** rule 6 — default **API=0**

---

## Purpose

This gate is the **only** authorization path for Track L1 live LLM/API evaluation of frozen pack `p1_mechanism_v1.0.0`.

Until every required item below is checked and signed, agents and humans must treat live evaluation as **forbidden**.

```text
NO CHECKLIST → NO LIVE CALLS → NO API SPEND
```

---

## Preconditions (repository)

| Check | Expected |
| --- | --- |
| Pack path exists | `datasets/frozen/p1_mechanism_v1.0.0/dataset.jsonl` |
| Pack SHA-256 | `1a0b0053c392e7b3e0727b92b4f088790abda001fd852ec1703c5ee0a67dd235` |
| Pack status | `manifest.status=FROZEN`, `live_evaluated=false` **before** the run |
| Historical `eval_v1` | `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24` |
| Historical `common_attack_stream` | `d101f94d97e0a29e8b9f9cc4dacb92472e29cd9af403114cb09b8f1d50a06c47` |
| Offline tests | `pytest -q` green on the execution commit |
| Track A / B AUDIT dirs | Untouched (read-only) |

If the freeze tree is not yet on the execution branch, **merge or checkout the freeze artifact first** — do not regenerate the pack.

---

## Human approval checklist

Copy into the run lock file / PR description. All boxes required for Stage B. Stage A may proceed with a reduced subset only if explicitly marked “Stage A only” and still signed.

```text
[ ] Benchmark SHA verified (p1_mechanism_v1.0.0 = 1a0b0053…6818)
[ ] Frozen dataset unchanged (byte identity / cmp vs provenance candidate if present)
[ ] Execution commit recorded (git rev-parse HEAD)
[ ] Canonical main ancestry / dual-track status acknowledged (Track A FAIL immutable; Track B scoped)
[ ] Evaluation matrix approved (models × policies × episodes × repetitions)
[ ] Target models approved (ids + provider; fresh availability/pricing lookup done)
[ ] Judge model approved (independent; not self-scoring target)
[ ] Budget approved (max USD)
[ ] Maximum request count approved
[ ] Retry policy approved (≤2 unless overridden here)
[ ] Timeout policy approved
[ ] Stopping / failure thresholds approved
[ ] Judge/scorer procedure approved
[ ] Logging / JSONL schema approved
[ ] Output directory approved (must not overwrite Track A/B AUDIT paths)
[ ] Data retention policy approved
[ ] No Track A/B contamination (no unlabeled pooling; no AUDIT edits)
[ ] No historical result overwrite
[ ] Detector/policy lock commit approved (no retune on this pack)
[ ] Contamination limitation acknowledged (exact-only screen; near/semantic NOT ruled out)
[ ] Stage A smoke completed and declared non-primary
[ ] Explicit human sentence: "I authorize Track L1 live API spend under LIVE-EVAL-GATE-0.1"
[ ] Approver name / date (UTC)
```

**Signature block (fill at approval time):**

```text
Approver:
Date (UTC):
Max USD:
Max requests:
Primary target model:
Judge model:
Policies: B0, STATIC-A1, PHASE1-CORE (confirm or amend)
Stage authorized: A only / A+B / A+B+C
```

---

## Staged authorization

| Stage | May run when | Produces scientific primary result? |
| --- | --- | --- |
| A Smoke | Partial checklist + explicit “Stage A only” | **No** |
| B Main | Full checklist | Yes (L1 only) |
| C Replication | Full checklist + extra budget line | Optional / exploratory |

---

## Budget worksheet (human-filled; not a spend)

| Item | Value |
| --- | --- |
| Stage A max USD | |
| Stage B max USD | |
| Stage C max USD | |
| Hard stop USD (sum) | |
| Hard stop requests | |
| Provider account(s) | |
| Pricing lookup date (UTC) | |

Theoretical Stage B planning bound (1 primary model × 3 policies × 96 episodes × ≤2 LLM calls): **≤576** LLM calls — replace with priced estimate after human lookup.

---

## Lock file (to create at approval — not in this design commit)

Suggested path (created only when human approves execution):

```text
configs/p1_mechanism_l1_live_lock.json
```

Minimum keys: `benchmark_sha256`, `code_commit`, `policies`, `target_model`, `judge_model`, `temperature`, `max_usd`, `max_requests`, `approver`, `approved_at_utc`, `protocol_id`, `gate_id`.

Do **not** invent lock contents in advance of approval.

---

## After a successful L1 run (future)

1. Write AUDIT under `experiments/real_llm_eval/P1_MECHANISM_L1/<run_id>/` only.  
2. Keep `live_evaluated=false` on the **pack manifest** unless a separate, explicit pack-metadata update is human-approved (recommended: leave pack frozen; record live status only in the run AUDIT).  
3. Do **not** start Track L2/P2 automatically.  
4. Do **not** retune detectors from L1 outcomes without a new independent holdout plan.

---

## Safety statement (design phase)

Publishing this gate:

- does not perform live LLM calls  
- does not spend API credits  
- does not modify `datasets/frozen/p1_mechanism_v1.0.0/dataset.jsonl`  
- does not modify Track A or Track B evidence  
- does not change historical metrics or manuscript claims  
