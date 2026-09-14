# PR stack (open PRs 23–32)

**Do not merge from this file.** Merge order and venue choice are **human-only**. This index is documentation.

Scientific outcome on the tip of this stack: VNEXT confirmation **FAIL** (PR #31) + negative-result manuscript (PR #32). Adaptive cost-aware intervention is **not confirmed**.

GitHub: https://github.com/Mohammadreza583/adapti-guard/pulls

---

## Roles

| Role | Meaning |
| --- | --- |
| `docs` | Protocol, checklist, power/MSID, pre-live, or diagnostic manuscript. No live eval. |
| `harness` | Deterministic code repair (leakage, tool loop, scoring). No live eval. |
| `pack` | Frozen confirmation corpus + hash lock. LLM = 0 to build. |
| `live` | OpenRouter confirmation run or the runner that scored it. |
| `manuscript` | Workshop/preprint negative-result text after FAIL. |

---

## Open PRs 23–32

| PR | Head branch | Base | Role | Title (short) | Official scoring? |
| ---: | --- | --- | --- | --- | --- |
| [23](https://github.com/Mohammadreza583/adapti-guard/pull/23) | `cursor/layer-a-diagnostic-manuscript-692c` | `cursor/layer-a-v4-project-completion-f6c7` (#22) | `docs` | Layer A v4 diagnostic manuscript + claims checklist | No |
| [24](https://github.com/Mohammadreza583/adapti-guard/pull/24) | `cursor/vnext-protocol-phase1-d8c0` | #23 | `docs` | `VNEXT-PROTOCOL-0.1` Phase 1 scientific reset | No |
| [25](https://github.com/Mohammadreza583/adapti-guard/pull/25) | `cursor/vnext-harness-repair-phase2-9b3f` | #24 | `harness` | Phase 2: leakage, `tool_loop`, L2 deny, taxonomy | No |
| [26](https://github.com/Mohammadreza583/adapti-guard/pull/26) | `cursor/vnext-phase3-power-memo-9b3f` | #25 | `docs` | Phase 3 prep: power memo + hash-gate addendum | No |
| [27](https://github.com/Mohammadreza583/adapti-guard/pull/27) | `cursor/vnext-msid-lock-phase3a-e51b` | #26 | `docs` | Phase 3a: lock `VNEXT-MSID-0.1` δ = 0.20 | No |
| [28](https://github.com/Mohammadreza583/adapti-guard/pull/28) | `cursor/vnext-confirm-pack-4d85` | #27 | `pack` | Freeze `vnext_confirm_v1.0` (61+61), SHA-256 `523c8818…` | No |
| [29](https://github.com/Mohammadreza583/adapti-guard/pull/29) | `cursor/vnext-confirm-live-eval-8dd8` | #28 | `live` | Parallel live-eval **request/runner** (`run_vnext_confirm_eval.py`) | **No — not the FAIL AUDIT** |
| [30](https://github.com/Mohammadreza583/adapti-guard/pull/30) | `cursor/vnext-prelive-checklist-7aef` | #28 | `docs` | Pre-live infrastructure checklist (`PRELIVE_PASS`, LLM=0) | No |
| [31](https://github.com/Mohammadreza583/adapti-guard/pull/31) | `cursor/vnext-confirm-live-81ad` | #30 | `live` | Official confirmation **FAIL** (`run_vnext_confirm.py` + AUDIT `20260914-133147`) | **Yes** |
| [32](https://github.com/Mohammadreza583/adapti-guard/pull/32) | `cursor/vnext-fail-workshop-manuscript-de91` | #31 | `manuscript` | Workshop/preprint negative-result package | No (cites #31) |

#29 and #30 are **siblings** on #28. Official scoring walked #30 → #31, not #29. #29 uses a different runner filename and has **no** `20260914-133147` AUDIT folder. Do not treat #29 as a second confirmation.

---

## Human-only merge order (not executed)

Suggested stack merge, **if** a human chooses to land this work on `main`. Agents must not merge.

1. #22 (Layer A v4 CASE B) if not already in the target default branch.
2. #23 `docs` (Layer A diagnostic manuscript).
3. #24 `docs` (protocol).
4. #25 `harness`.
5. #26 `docs` (power memo).
6. #27 `docs` (MSID lock).
7. #28 `pack` (hash-locked JSONL; do not rewrite).
8. #30 `docs` (pre-live). Prefer this over merging #29 first.
9. **Close or skip #29** unless a human explicitly wants the unused `run_vnext_confirm_eval.py` path. Do not merge #29 as the official FAIL.
10. #31 `live` (FAIL artifacts). Binding numbers live here.
11. #32 `manuscript`.
12. Later closeout PRs that base on #32 (reproducibility / research log / this index).

Conflicts: #29 vs #31 both touch `src/adapti_guard/experiments/vnext_confirm.py` and related scoring. Merging both without a human plan can duplicate runners.

---

## Human-only venue choice (not executed)

This package does **not** submit anywhere.

| Option | Fit after FAIL | Must not claim |
| --- | --- | --- |
| Security / ML workshop (negative-result or evaluation track) | Honest FAIL + protocol contribution | Defense win, SOTA, production-ready |
| arXiv preprint | Optional archival of the negative result | Camera-ready “AdaptiGuard works” |
| Conference main track as a defense paper | Poor fit while H1 = NO | Qualified win, MSID met, utility gate passed |
| Product / blog “we built a guard” | Forbidden by claims map | Any win paraphrase of p = 0.0625 |

Do not change MSID, N, or frozen packs to chase a venue.

---

## Integrity

Pack SHA-256 `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518`.  
FAIL reasons: `s5_mcnemar_not_significant`, `msid_not_met`, `s4_utility_ineligible`.  
Qualified win: **NO**.
