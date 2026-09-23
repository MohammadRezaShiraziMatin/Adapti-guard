# Decision lock D-22 — Confirmatory V2 taxonomy (names only)

**Decision ID:** D-22  
**Status:** **LOCKED** (Researcher Option A)  
**Date (UTC):** 2026-09-23  
**Scope:** `family_id` strings and family count only. **No** dataset bytes, **no** SAP, **no** allocation table in this document.

Supersedes any informal taxonomy choice pending for “Confirmatory V2.” No `DECISION_REQUEST` file existed in-repo at lock time; treat this file as the authoritative close.

---

## LOCKED

| Item | Value |
| --- | --- |
| `attack_families` count | **6** |
| `family_id` set (exact strings) | `DIRECT_OVERRIDE`, `INDIRECT_RAG_DOC`, `TOOL_OUTPUT_INJECTION`, `MULTI_TURN_PERSISTENCE`, `OBFUSCATION`, `PRIVILEGE_EXFIL` |

These six keys match the only frozen confirmatory pack on Track A with exactly six attack families:

- **Path:** `datasets/frozen/vnext_confirm_v1/`
- **Pack id:** `vnext_confirm_v1.0`
- **Evidence field:** `manifest.json` → `family_counts` (also summarized in `DATASET_CARD.md`)

Confirmatory V2 **must use these names** for stratified reporting and future pack metadata. Renaming or merging families for V2 requires a **new** decision ID and must not rewrite Track A frozen labels.

---

## NOT locked (explicit)

- **151 attack allocation** across the six families (planned Confirmatory V2 sizing; not registered in this lock).
- **Episode text**, prompts, tools, trajectories, or IDs for V2.
- **Statistical analysis plan** (SAP) for Confirmatory V2.
- **New dataset bytes** under `datasets/frozen/**` or any hash lock.
- Benign / hard-negative counts, MSID, or live eval approval.

---

## Evidence (read-only; do not modify)

| Fact | Source |
| --- | --- |
| Exactly **6** attack families in the frozen Track A pack | `datasets/frozen/vnext_confirm_v1/manifest.json` (`family_counts` keys) |
| Historical confirmatory **n_attack = 61** (Track A, evaluated) | Same manifest; live result **FAIL** in `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md` |
| V2 attack episodes must be **new** | No reuse of historical confirmation episode **bytes** (same rule as VNEXT pack build: disjoint IDs and no Layer A / VNEXT text recycle for a new confirm pack) |

Family-level counts in the frozen pack (61 total) are **descriptive** for Track A only; they do **not** prescribe Confirmatory V2 allocation.

---

## Allocation remainder (151 ÷ 6)

For a **planned** Confirmatory V2 attack total **N = 151**:

\[
151 = 6 \times 25 + 1 \quad\Rightarrow\quad 151 \bmod 6 = 1
\]

One extra episode cannot be split evenly across six families. **Researcher rule for that +1 cell is deferred** — not decided in D-22. Do not invent a rounding scheme in docs or builders until locked separately.

---

## Relationship to other taxonomies

- **Track B** `phase1_confirm_v1` uses nine `metadata.attack_family` values — different pack, different scope; do not merge with V2 naming without explicit mapping doc.
- **Phase-2 protocol** (`PHASE2-PROTOCOL-0.1`) remains unevaluated; D-22 does not implement Phase 2 harness or multi-turn episodes.

---

## Process

- **API=0** for this decision record.
- **Track A FAIL** and **Track B SUPPORTED_IMPROVEMENT** unchanged.
- Implementation follow-ups (builders, SAP, freeze PR) are **later PRs** after human review.

**Navigation:** [`STATUS.md`](STATUS.md) · [`QUALITY_ROADMAP_5PHASE.md`](QUALITY_ROADMAP_5PHASE.md) · [`docs/START_HERE.md`](../START_HERE.md)
