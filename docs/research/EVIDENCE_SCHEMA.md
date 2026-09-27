# Evidence schema (Phase 3)

**Machine-readable:** [`EVIDENCE_SCHEMA.yaml`](EVIDENCE_SCHEMA.yaml).

**Rule:** No empirical claim without local raw evidence (`evidence_type: live_raw` or `historical_audit`).

**Distinctions (mandatory):** design vs empirical · offline vs live · raw vs derived · target vs judge · historical vs current · frozen vs mutable.

**Traceability:** Claim → Finding → `evidence_path` → `condition_id` → configuration → dataset/model/judge.

Immutable historical paths (do not regenerate): Track A/B `experiments/real_llm_eval/**/AUDIT.md`, `datasets/frozen/**`.
