# Phase-1 Completeness Statement

**Role:** Honest boundary document — what Phase-1 dual-track work has **closed with evidence**, what **requires a future gated live evaluation**, and what is **out of scope by design**.  
**Not a claim that every scientific limitation has disappeared.**  
**API / live LLM calls for this statement’s supporting offline work:** **0**  
**Authority:** Frozen AUDIT/verdict artifacts and the dual-track audits linked below win over narrative polish.

Standing gates: [`docs/experiments/MASTER_PROMPT.md`](../../experiments/MASTER_PROMPT.md) (especially rule 6 for live eval).

---

## 1. Closed (with evidence)

| Item | Evidence (one-line pointer) |
|------|-----------------------------|
| Label blindness of core path | `tests/test_phase1_core_pipeline.py` (`test_label_blind_core_factory_ignores_gold_kwargs`, ablation label-blind tests); `tests/test_vnext_phase2_harness.py` (adaptive ignores gold `is_attack`); architecture: gold labels stay off detector→risk→policy→action path |
| VNEXT-pack textual independence of Track B pack | [`PHASE1_INDEPENDENCE_AUDIT.md`](PHASE1_INDEPENDENCE_AUDIT.md) — exact/near prompt overlap vs `vnext_confirm_v1` = 0; distinct seeds/builders/markers |
| No detector tuning on holdout pack | [`PHASE1_HOLDOUT_OVERLAP_AUDIT.md`](PHASE1_HOLDOUT_OVERLAP_AUDIT.md) Q1 — `evidence_phase1.0` authored in `c462945` before holdout path exists; lock hashes that blob; no post-holdout detector/threshold edits |
| Full 59/59 confirm↔holdout near-pair classification | [`artifacts/phase1_holdout_pairs_full59.md`](artifacts/phase1_holdout_pairs_full59.md) via `scripts/classify_phase1_holdout_pairs_full59.py` — **0 `GENUINE_DUPLICATE`**; 35 entity-swap / 24 wording scaffolds |
| Scoring taxonomy integrity (`target_refusal` ≠ win) | `src/adapti_guard/experiments/vnext_confirm.py` (`INTERVENTION_WIN_CLASSES`, refusal recorded as ties); AUDIT notes on both tracks; claims guardrails in [`CLAIMS_DUAL_TRACK.md`](CLAIMS_DUAL_TRACK.md) |
| Track A gate-checked from frozen artifacts | `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/verdict.json` + `AUDIT.md` — δ̂=0.0820, p=0.0625, U=0.9344 → **FAIL** (MSID/signif/utility not all met) |
| Track B gate-checked from frozen artifacts | `experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/verdict.json` + `AUDIT.md` — δ̂=0.4426, CI [0.2757, 0.6096], p=1.49012e-08, U=0.9672131147540983, b10/b01=27/0 → **SUPPORTED_IMPROVEMENT** |
| Dual-track non-merge of claims | [`CLAIMS_DUAL_TRACK.md`](CLAIMS_DUAL_TRACK.md) + [`PHASE1_SCIENTIFIC_REPORT.md`](PHASE1_SCIENTIFIC_REPORT.md) §4.3 — Track B does not reverse Track A |

**Also closed as offline documentation gaps (not new science):** Q1 raise of the scientific report; holdout overlap forensics; standing MASTER prompt; reconstructed Q1-raise prompt.

---

## 2. Structurally open — requires a future **gated** live evaluation

These are **not** unfinished paperwork. Closing them means new packs and/or new live runs under `MASTER_PROMPT.md` **rule 6** (independent holdout frozen+hashed → detector/policy frozen → written eval plan → explicit human budget sign-off). **This task does not authorize or run them.**

| Open item | What closing would require | Why correctly deferred |
|-----------|----------------------------|------------------------|
| Small N (61 attack + 61 benign per track) | Pre-register a larger frozen pack (hashed), lock detector/policy, approved eval plan, human sign-off, then confirmatory live run | Rushing a larger N without rule 6 reintroduces pack-fit / post-hoc N shopping — the failure mode the freeze+audit chain exists to prevent |
| No external / published baseline arm | Implement or reproduce a published defense as an additional treatment under the **same** protocol, then gated live eval | A casual side comparison without shared locks would not be commensurate and could be spun as SOTA; rule 6 + claims forbid unlabeled merges |
| Single-turn-only scope | Multi-turn / persistence evaluation is Phase-2 work by design (`docs/experiments/protocols/PHASE2_PROTOCOL.md`, `docs/experiments/protocols/VNEXT_PROTOCOL.md` Phase-2 harness; `docs/paper/phase1/PHASE1_THREAT_MODEL.md` / stub `docs/experiments/PHASE1_THREAT_MODEL.md` excludes live multi-turn adaptive attacker in Phase 1) | Retrofitting multi-turn into Phase-1 “closeout” under time pressure would blur estimands and invite protocol drift |

**Boundary sentence:** Items in this section remain **open**. They are not resolved by this Completeness Statement.

---

## 3. Out of scope by design (not a gap — do not reopen)

| Item | Why not a Phase-1 gap |
|------|----------------------|
| Adaptive attacker aware of the defense | Explicitly excluded from Phase-1 threat model (`docs/paper/phase1/PHASE1_THREAT_MODEL.md`: no live multi-turn adaptive attacker in Phase 1) |
| Cross-model generalization beyond tested targets | Phase-1 confirmatory claims are scoped to the locked target/judge pairs per track; no broader model-family claim was registered |
| Production deployment readiness | `CITATION.cff` already disclaims citing this as a confirmed / SOTA / production prompt-injection defense |

---

## Integrity note for this close-out

- Frozen packs and `experiments/real_llm_eval/**` were **not** edited to produce this statement.
- Track A/B numeric results were **not** re-derived or altered.
- “Complete” here means: **offline dual-track scientific documentation and contamination audits are finished and boundary-honest** — not that Phase-1 has answered every possible follow-on empirical question.
