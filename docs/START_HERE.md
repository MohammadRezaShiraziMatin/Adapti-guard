# Start here

Short read order for a new contributor or reviewer. Documentation only. **No merge. No venue submit. No live LLM. No retune.**

**Tip / process unlock (2026-09-23):** Docs-only quality work on `main` (baseline `e4870b9` after PR #73 merge) reduces admin bottlenecks and improves publisher readiness. That does **not** relax science locks below (frozen packs, AUDIT numbers, Track A FAIL, default **API=0**).

## Read in this order

1. **This file** — dual-track honesty, tree, and where to go next.
2. [`docs/experiments/QUALITY_ROADMAP_5PHASE.md`](experiments/QUALITY_ROADMAP_5PHASE.md) — five-phase quality plan (**P1–P5 done** on tip `e4870b9`); [`docs/experiments/STATUS.md`](experiments/STATUS.md) — tip intent and D-22 lock pointer. **Q1 findings ladder:** [`Q1_ROADMAP_4PHASE.md`](experiments/Q1_ROADMAP_4PHASE.md) · [`Q1_BLOCKER_MATRIX.md`](experiments/Q1_BLOCKER_MATRIX.md) · P2 lock [`DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md`](experiments/DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md) · **P4 packet** [`paper/q1_findings/`](paper/q1_findings/README.md) (P3 live = budget pending).
3. [`docs/paper/dual_track/DUAL_TRACK_STATUS.md`](paper/dual_track/DUAL_TRACK_STATUS.md) — Track A vs Track B in one page.
4. [`docs/paper/dual_track/CLAIMS_DUAL_TRACK.md`](paper/dual_track/CLAIMS_DUAL_TRACK.md) — allowed / forbidden wording.
5. [`docs/paper/workshop_vnext_fail/PR_STACK.md`](paper/workshop_vnext_fail/PR_STACK.md) — open PR roles; **CLOSE / SKIP**; human merge only.
6. [`docs/paper/dual_track/RELEASE_NEXT_FA.md`](paper/dual_track/RELEASE_NEXT_FA.md) — next steps for Matin (Persian).
7. [`docs/experiments/MASTER_PROMPT.md`](experiments/MASTER_PROMPT.md) — standing orders for agents.

Workshop / negative-result packet (Track A FAIL manuscript, not a venue upload): [`docs/paper/workshop_vnext_fail/`](paper/workshop_vnext_fail/README.md). Human submit readiness: [`SUBMISSION_CHECKLIST.md`](paper/workshop_vnext_fail/SUBMISSION_CHECKLIST.md) (**venue TBD**; no agent upload).

**P0 scientific audit (benchmark / attack taxonomy; no live eval):** [`docs/research/P0_ATTACK_TAXONOMY_AUDIT.md`](research/P0_ATTACK_TAXONOMY_AUDIT.md). Inventory of frozen packs, role surface-vs-mechanism audit, estimand limits, and P1 design constraints. Does not modify frozen evidence.

**P1 mechanism benchmark:** candidate provenance `datasets/candidates/p1_mechanism_v1/` · **FROZEN** `datasets/frozen/p1_mechanism_v1.0.0/` ([freeze record](research/P1_MECHANISM_V1_0_0_FREEZE.md); [freeze-readiness audit](research/P1_FREEZE_READINESS_AUDIT.md); [spec](research/P1_ATTACK_BENCHMARK_SPEC.md)). `live_evaluated=false`. No automatic live eval.

**Next scientific gate (design only; API=0):** [`docs/research/LIVE_EVALUATION_GATE.md`](research/LIVE_EVALUATION_GATE.md) · protocol [`LIVE_EVALUATION_PROTOCOL.md`](research/LIVE_EVALUATION_PROTOCOL.md). Frozen `p1_mechanism_v1.0.0` is on tip `main` (SHA `1a0b0053…dd235`; see [`docs/experiments/REPRODUCIBILITY_PACKAGE.md`](experiments/REPRODUCIBILITY_PACKAGE.md)); **`live_evaluated=false`** until human budget sign-off. No automatic live run.

**Offline verification:** [`docs/experiments/REPRODUCIBILITY_PACKAGE.md`](experiments/REPRODUCIBILITY_PACKAGE.md).

Full keep-vs-historical map: [`docs/paper/DOCS_INDEX.md`](paper/DOCS_INDEX.md).

## Dual-track (do not mix)

- **Track A VNEXT = FAIL (immutable).** Pack `vnext_confirm_v1.0`, SHA-256 `523c8818…`. Qualified win (H1) = **NO**. Do not edit the frozen pack, the AUDIT folder, or FAIL numbers.
- **Track B Phase-1 LIVE = SUPPORTED_IMPROVEMENT** on a **different** pack (`phase1_confirm_v1`, SHA-256 `c789811a…`), treatment PHASE1-CORE vs B0. Scoped. Not a VNEXT PASS.
- **Track B does NOT reverse Track A.** Mixing VNEXT ASR with Phase-1 harmful-action rates in one unlabeled sentence is a claims error.
- **Phase-2 protocol** (docs only; unevaluated): [`docs/experiments/protocols/PHASE2_PROTOCOL.md`](experiments/protocols/PHASE2_PROTOCOL.md). Not implemented. Not live.

Canonical AUDIT pointers (do not rewrite in place):

- Track A: `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md`
- Track B: `experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/AUDIT.md`

## Repository tree (mental model)

```text
/
  README.md                      # short; points here
  pyproject.toml                 # installable package from src/
  docs/experiments/MASTER_PROMPT.md  # canonical project standing orders
  src/adapti_guard/              # package (import as adapti_guard; pip install -e .)
  configs/                       # YAML/JSON configs only
  scripts/                       # CLI entrypoints
  tests/                         # pytest (flat; package-mirror deferred)
  docs/
    START_HERE.md                # you are here
    paper/
      dual_track/                # DUAL_TRACK_STATUS, CLAIMS_DUAL_TRACK
      workshop_vnext_fail/       # Track A packet (folder name frozen for citations)
      phase1/                    # Phase-1 scientific docs (not live AUDIT)
    experiments/
      QUALITY_ROADMAP_5PHASE.md    # process unlock vs science locks
      STATUS.md                   # tip status + D-22 pointer
      MASTER_PROMPT.md
      RESEARCH_LOG.md
      protocols/                 # VNEXT + Phase-2 protocol (Phase-2 unevaluated)
    archive/                     # SUPERSEDED / Q1 / old closeouts
  datasets/frozen/               # UNCHANGED location
  experiments/real_llm_eval/     # UNCHANGED location
```

Old paths keep one-line **Moved to …** stubs so frozen cards and external links still resolve.

## Human-only

Agents do not merge, close PRs via API, submit to a venue, call OpenRouter, or retune detectors. See the **CLOSE / SKIP** section in `PR_STACK.md`.

- Project standing orders live in [`docs/experiments/MASTER_PROMPT.md`](experiments/MASTER_PROMPT.md); tag that file for agent chats.
