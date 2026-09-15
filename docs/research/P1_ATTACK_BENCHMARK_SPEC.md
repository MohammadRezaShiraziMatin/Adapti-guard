# P1 Attack Benchmark Specification — Mechanism Candidate Pack

**ID:** `P1-BENCH-SPEC-0.1`  
**Pack:** `p1_mechanism_v1.0-candidate`  
**Path:** `datasets/candidates/p1_mechanism_v1/`  
**Status:** Candidate constructed + offline-validated. **Not live-evaluated. Not in `datasets/frozen/`.**

---

## 1. Purpose

Address P0 gaps by shipping a **mechanism-labelled**, **paired**, **confirm-pack-compatible** candidate benchmark for future gated evaluation of runtime LLM-agent defenses.

Optimize for: mechanism diversity, threat-model coverage, realism (mock-tool agent), semantic diversity, reproducibility, benign/attack comparability, estimand validity — **not** raw attack count.

---

## 2. Inputs

| Input | Role |
| --- | --- |
| `docs/research/P0_ATTACK_TAXONOMY_AUDIT.md` | Gaps, taxonomy proposal, freeze protocol |
| `docs/research/P1_THREAT_MODEL.md` | Attacker/defender scope |
| `docs/research/P1_MECHANISM_TAXONOMY.md` | Locked leaf codes |
| Phase-1 / VNEXT JSONL shape | Episode schema compatibility |
| `src/adapti_guard/core/episode.py` | Runtime observables |

---

## 3. Design decisions (evidence-backed)

| Decision | Rationale |
| --- | --- |
| Mechanism codes A1–F4; `surface_form` separate | P0 role audit: surface ≠ mechanism |
| No DAN/`you are now DAN` primary surfaces | P0 overloaded `role_attack` |
| C4 adaptive = 0 rows | No live adaptive harness; would falsify estimands |
| C1–C3 use `sequential_representation=frozen_context` | Honest single-turn runtime |
| 2 attacks × 22 in-scope leaves + 1:1 twins + 8 hard-negatives | Diversity without scaffold cloning |
| Write under `datasets/candidates/` | Freeze-before-live; do not mutate historical frozen packs |
| Authored templates, seed `20260915`, no LLM generation | Reproducibility; no API budget |

---

## 4. Schema

Top-level keys align with confirm packs: `id`, `label`, `split`, `category`, `attack_type`, `prompt`, `context`, `success_condition`, optional `tool_call`/`tools`, `metadata`.

`metadata` implements P0 §16 fields: `family`, `mechanism`, `surface_form`, `security_objective`, `context_source`, `turn_count`, `tool_dependency`, `external_content_dependency`, `expected_harm`, `difficulty`, `benign_twin` / `attack_twin`, `provenance`, `version`, `content_sha256`, `estimand_tags`, plus `sequential_representation` and `pack_id`.

---

## 5. Build / validate

```bash
python scripts/build_p1_mechanism_v1_pack.py
python scripts/validate_p1_mechanism_pack.py
pytest -q tests/test_p1_mechanism_candidate_pack.py
```

Builder contamination-screens exact normalized `prompt`/`context` against frozen Phase-1 / VNEXT / Layer A packs.

---

## 6. Freeze-before-live (unchanged from P0 §17)

```text
design → generate → validate → dedup → taxonomy check → benign-twin check
 → freeze → SHA-256 → offline tests → only then gated live evaluation
```

Promotion into `datasets/frozen/` requires a **separate** explicit freeze commit after human review. This candidate must not be live-evaluated while `manifest.status=CANDIDATE`.

---

## 7. Estimands

| After gated live (future) | Now |
| --- | --- |
| Harmful-action by family | NOT EVALUATED |
| Utility / FPR via twins | NOT EVALUATED |
| Live multi-turn / adaptive ASR | NOT AVAILABLE (by design) |

---

## 8. Explicit non-claims

- No improved security / ASR / utility / detection claimed.
- Does not reverse Track A FAIL or extend Track B confirm claims.
- Does not modify any frozen artifact hashes.
- Simulation stream remains a separate evidence track.
