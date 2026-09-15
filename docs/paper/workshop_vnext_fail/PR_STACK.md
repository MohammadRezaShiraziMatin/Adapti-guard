# PR stack (open PRs 23–44)

**Do not merge from this file.** Merge order and venue choice are **human-only**. This index is documentation. Agents must **not** close or merge PRs via the GitHub API.

Two scientific tracks sit on this unmerged stack. They are **not** one outcome:

- **Track A (VNEXT):** confirmation **FAIL** (PR #31) + negative-result manuscript (#32–#34). Adaptive cost-aware intervention is **not confirmed**.
- **Track B (Phase-1):** confirmatory LIVE **SUPPORTED_IMPROVEMENT** on a different pack (PR #39, draft). Scoped PHASE1-CORE vs B0. **Does not reverse** Track A.
- **Hygiene:** PR #40 dual-track docs/claims; PR #41 reading map + CLOSE / SKIP + untrack `.venv`; PR #42 Cursor Project Rules; PR #43 tree standardization (docs layout + package hygiene); PR #44 Phase-2 protocol path-fix under `docs/experiments/protocols/` (#36 content ported; docs only). Docs / gitignore / layout only.

Status and allowed wording: [`docs/paper/dual_track/DUAL_TRACK_STATUS.md`](../dual_track/DUAL_TRACK_STATUS.md), [`docs/paper/dual_track/CLAIMS_DUAL_TRACK.md`](../dual_track/CLAIMS_DUAL_TRACK.md). Read order: [`docs/START_HERE.md`](../../START_HERE.md).

GitHub: https://github.com/Mohammadreza583/adapti-guard/pulls

---

## CLOSE / SKIP (recommendations only; do not execute via API)

Documented for a human. **Do not close PRs via GitHub API from an agent.** **Agents never merge.**

| Action | PR | Why |
| --- | ---: | --- |
| **CLOSE or SKIP** | #29 | Unused parallel VNEXT runner (`run_vnext_confirm_eval.py`). **Not** the official FAIL. No `20260914-133147` AUDIT folder. Sibling of #30 on #28. |
| **CLOSE as superseded** after this path-fix merges (do **not** close via API) | #36 | Phase 2 protocol content is now on tip under `docs/experiments/protocols/PHASE2_*.md` via this path-fix (PR #44). #36 itself (`cursor/phase2-protocol-lock-1411`) can be closed as superseded once this merges. Original #36 was a sibling of #37 on #35 — not Track B live, not Phase 2 implementation. |
| **KEEP** merge path | … → #35 → #37 → #38 → #39 → #40 → #41 → **#42** → **#43** → **#44** | Official Track B then dual-track hygiene then Project Rules then layout reorg then Phase-2 protocol path-fix. |

**Simplified human merge:** after review, prefer landing the **tip of the stack once** (this branch, with parents), or **squash-merge the tip to `main`**. Do not merge #29 as FAIL. Do not merge #36 onto Track B; its protocol content is on tip via #44. After #44 merges, a human may close #36 as superseded. Agents never merge and never close PRs via the GitHub API. History rewrite to drop old `.venv` blobs is **out of scope**.

---

## Roles

| Role | Meaning |
| --- | --- |
| `docs` | Protocol, checklist, power/MSID, pre-live, hardening, or diagnostic manuscript. No live eval. |
| `harness` | Deterministic code repair (leakage, tool loop, scoring). No live eval. |
| `pack` | Frozen confirmation corpus + hash lock. LLM = 0 to build. |
| `live` | OpenRouter confirmation run or the runner that scored it. |
| `manuscript` | Workshop/preprint negative-result text after FAIL. |
| `packet` | Human cover letter / camera-ready map. No venue upload. |
| `core` | Phase-1 core pipeline (offline). VNEXT-ADAPT unchanged. |
| `unused` | Parallel branch; not official scoring. Do not merge as the record. |

---

## Open PRs 23–44

| PR | Head branch | Base | Role | Title (short) | Official scoring? |
| ---: | --- | --- | --- | --- | --- |
| [23](https://github.com/Mohammadreza583/adapti-guard/pull/23) | `cursor/layer-a-diagnostic-manuscript-692c` | `cursor/layer-a-v4-project-completion-f6c7` (#22) | `docs` | Layer A v4 diagnostic manuscript + claims checklist | No |
| [24](https://github.com/Mohammadreza583/adapti-guard/pull/24) | `cursor/vnext-protocol-phase1-d8c0` | #23 | `docs` | `VNEXT-PROTOCOL-0.1` Phase 1 scientific reset | No |
| [25](https://github.com/Mohammadreza583/adapti-guard/pull/25) | `cursor/vnext-harness-repair-phase2-9b3f` | #24 | `harness` | Phase 2: leakage, `tool_loop`, L2 deny, taxonomy | No |
| [26](https://github.com/Mohammadreza583/adapti-guard/pull/26) | `cursor/vnext-phase3-power-memo-9b3f` | #25 | `docs` | Phase 3 prep: power memo + hash-gate addendum | No |
| [27](https://github.com/Mohammadreza583/adapti-guard/pull/27) | `cursor/vnext-msid-lock-phase3a-e51b` | #26 | `docs` | Phase 3a: lock `VNEXT-MSID-0.1` δ = 0.20 | No |
| [28](https://github.com/Mohammadreza583/adapti-guard/pull/28) | `cursor/vnext-confirm-pack-4d85` | #27 | `pack` | Freeze `vnext_confirm_v1.0` (61+61), SHA-256 `523c8818…` | No |
| [29](https://github.com/Mohammadreza583/adapti-guard/pull/29) | `cursor/vnext-confirm-live-eval-8dd8` | #28 | `unused` | Parallel live-eval **request/runner** (`run_vnext_confirm_eval.py`) | **No — unused; not the FAIL AUDIT** |
| [30](https://github.com/Mohammadreza583/adapti-guard/pull/30) | `cursor/vnext-prelive-checklist-7aef` | #28 | `docs` | Pre-live infrastructure checklist (`PRELIVE_PASS`, LLM=0) | No |
| [31](https://github.com/Mohammadreza583/adapti-guard/pull/31) | `cursor/vnext-confirm-live-81ad` | #30 | `live` | Official Track A confirmation **FAIL** (`run_vnext_confirm.py` + AUDIT `20260914-133147`) | **Yes (Track A)** |
| [32](https://github.com/Mohammadreza583/adapti-guard/pull/32) | `cursor/vnext-fail-workshop-manuscript-de91` | #31 | `manuscript` | Workshop/preprint negative-result package | No (cites #31) |
| [33](https://github.com/Mohammadreza583/adapti-guard/pull/33) | `cursor/vnext-fail-workshop-closeout-ef12` | #32 | `docs` | Remaining workshop DONE items (facts, claims map, PR index) | No (cites #31) |
| [34](https://github.com/Mohammadreza583/adapti-guard/pull/34) | `cursor/vnext-fail-submission-packet-1411` | #33 | `packet` | Human workshop/evaluation cover packet (no venue submit) | No |
| [35](https://github.com/Mohammadreza583/adapti-guard/pull/35) | `cursor/phase1-core-defense-upgrade-1411` | #34 | `core` | Phase 1 core defense pipeline (offline; no VNEXT re-run) | No |
| [36](https://github.com/Mohammadreza583/adapti-guard/pull/36) | `cursor/phase2-protocol-lock-1411` | #35 | `docs` | Phase 2 scientific protocol lock (docs only) | No — sibling; **superseded** by #44 path-fix (human may close after #44 merges; do not close via API) |
| [37](https://github.com/Mohammadreza583/adapti-guard/pull/37) | `cursor/phase1-final-hardening-1411` | #35 | `docs` | Phase 1 final hardening: independent holdout + detector lock | No |
| [38](https://github.com/Mohammadreza583/adapti-guard/pull/38) | `cursor/phase1-scientific-hardening-1411` | #37 | `docs` | Phase 1 scientific hardening (SH1–SH8) | No |
| [39](https://github.com/Mohammadreza583/adapti-guard/pull/39) | `cursor/phase1-confirm-live-run-1411` | #38 | `live` | Track B confirmatory LIVE (`SUPPORTED_IMPROVEMENT`; **draft**) | **Yes (Track B only)** |
| [40](https://github.com/Mohammadreza583/adapti-guard/pull/40) | `cursor/dual-track-docs-hygiene-60df` | #39 | `docs` | Dual-track docs/claims hygiene (no live; no merge) | No |
| [41](https://github.com/Mohammadreza583/adapti-guard/pull/41) | `cursor/repo-hygiene-start-here-7699` | #40 | `docs` | Repo hygiene: START_HERE + PR close map + untrack `.venv` | No |
| [42](https://github.com/Mohammadreza583/adapti-guard/pull/42) | `cursor/project-rules-master-prompt-e00d` | #41 | `docs` | Always-on Cursor Project Rules from MASTER_PROMPT | No |
| [43](https://github.com/Mohammadreza583/adapti-guard/pull/43) | `cursor/tree-standardization-docs-package-954c` | #42 | `docs` | Tree standardization: docs layout + package hygiene | No |
| [44](https://github.com/Mohammadreza583/adapti-guard/pull/44) | `cursor/phase2-protocol-path-fix-26c9` | #43 | `docs` | Path-fix: Phase-2 protocol docs under `protocols/` (#36 align) | No — docs only; unevaluated |

#29 and #30 are **siblings** on #28. Official Track A scoring walked #30 → #31, not #29. #29 uses a different runner filename and has **no** `20260914-133147` AUDIT folder. **Mark #29 unused.** Do not treat #29 as a second confirmation.

#36 and #37 are **siblings** on #35. Official Track B walked #35 → #37 → #38 → #39, not #36. #36 is Phase 2 protocol docs, not Phase 2 implementation and not Track B live results. Phase-2 protocol **content** is now on tip via #44 (`docs/experiments/protocols/PHASE2_*.md`); #36 itself can be closed as superseded after #44 merges (human only; do not close via API).

#39 is a **draft** of live Track B results. It does not rewrite Track A FAIL.

---

## Human-only merge order (not executed)

Suggested stack merge, **if** a human chooses to land this work on `main`. Agents must not merge.

**Track A (VNEXT FAIL)**

1. #22 (Layer A v4 CASE B) if not already in the target default branch.
2. #23 `docs` (Layer A diagnostic manuscript).
3. #24 `docs` (protocol).
4. #25 `harness`.
5. #26 `docs` (power memo).
6. #27 `docs` (MSID lock).
7. #28 `pack` (hash-locked JSONL; do not rewrite).
8. #30 `docs` (pre-live). Prefer this over merging #29 first.
9. **CLOSE or skip #29** unless a human explicitly wants the unused `run_vnext_confirm_eval.py` path. Do not merge #29 as the official FAIL. See **CLOSE / SKIP** above.
10. #31 `live` (FAIL artifacts). Binding Track A numbers live here.
11. #32 `manuscript`.
12. #33 closeout (reproducibility / research log / this index).
13. #34 `packet`. Still not a venue submit.

**Track B (Phase-1 scoped LIVE)**

14. #35 `core` (offline pipeline; VNEXT-ADAPT unchanged).
15. **Do not merge #36** onto Track B. Phase-2 protocol content is on tip via **#44**. After #44 merges, a human may close #36 as superseded. Agents must not close PRs via the GitHub API. Not Track B live. Not Phase 2 implementation.
16. #37 holdout + detector lock.
17. #38 scientific hardening (SH1–SH8).
18. #39 `live` **draft** Track B results (`SUPPORTED_IMPROVEMENT`). Does not reverse #31.
19. #40 `docs` dual-track hygiene. Human merge only.
20. #41 `docs` repo hygiene (START_HERE, DOCS_INDEX, CLOSE / SKIP, untrack `.venv`). Human merge only.
21. #42 `docs` Cursor Project Rules (always-on MASTER_PROMPT mirror). Human merge only.
22. #43 `docs` tree standardization (docs layout + stubs + `pyproject.toml`). Human merge only.
23. #44 `docs` Phase-2 protocol path-fix under `docs/experiments/protocols/` (#36 content ported). Human merge only. After this merges, a human may close #36 as superseded.

**KEEP path (Track B onward):** … → #35 → #37 → #38 → #39 → #40 → #41 → #42 → #43 → #44.

Simplified option: review then land **tip once**, or squash-merge tip → `main`. Agents never merge.

Conflicts: #29 vs #31 both touch VNEXT runners. #36 vs #37 both stack on #35. Merging siblings without a human plan duplicates paths.

---

## Human-only venue choice (not executed)

This index does **not** submit anywhere.

| Option | Fit | Must not claim |
| --- | --- | --- |
| Security / ML workshop (negative-result track) | Honest Track A FAIL + protocol | Defense win, SOTA, production-ready, VNEXT-reversed |
| Scoped Phase-1 methods note | Track B only, with Track A FAIL still stated | That VNEXT is now PASS; solve-PI |
| arXiv preprint | Optional archival; human approval | Camera-ready “AdaptiGuard works” |
| Conference main track as a defense paper | Poor fit while Track A H1 = NO and Track B is one pack | Qualified VNEXT win; SOTA |
| Product / blog “we built a guard” | Forbidden | Any win paraphrase of p = 0.0625, or unscoped Track B |

Do not change MSID, N, or frozen packs to chase a venue.

---

## Integrity

Track A pack SHA-256 `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518`.  
FAIL reasons: `s5_mcnemar_not_significant`, `msid_not_met`, `s4_utility_ineligible`.  
Track A qualified win: **NO**.

Track B pack SHA-256 `c789811a07d3ed06e1c77d8a45eda6172f480226e006d84fa28386a982536d01`.  
Classification: **SUPPORTED_IMPROVEMENT** (scoped). Not a VNEXT PASS.
