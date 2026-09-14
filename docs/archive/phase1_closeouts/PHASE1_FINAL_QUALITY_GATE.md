# Phase 1 final quality gate

**Decision: PASS**

Architectural + evidence-quality upgrade for the core defense pipeline.  
Not a VNEXT re-score. Not an ASR claim. Official VNEXT confirmation remains **FAIL**.

LLM/API calls = **0**.

---

## Already completed (prior turn)

- `CoreDefensePipeline`, ContextBuilder, Risk/Policy/Action/ToolPermissionGate, EpisodeTrace
- Label-blind runtime; A2/A3 action-level enforcement
- 17 core causal tests; offline pack harness; audit/design/results stubs

## Changed in this continuation

1. **Detector coverage investigation** on frozen pack (diagnostic only): 53/61 attack misses were mostly `evidence_without_primary_gate` (forced markers / weak tool evidence), not threshold miscalibration.
2. **`PromptInjectionDetectorPhase1` (`evidence_phase1.0`)** — composable evidence (hierarchy, tool-invoke, unicode/HTML/hex/ROT13-labeled decode, exfil sinks) + expanded hard-negative E10. Frozen **`evidence_v4.0`** left for VNEXT-ADAPT.
3. **`RiskEngineCore` 1.1** — same 0.25/0.60 bands; privilege floors only with attack-like evidence (not E4 alone).
4. **`CorePolicyEngine`** — action sensitivity: MEDIUM+any declared tool → A2; MEDIUM text-only → A1; LOW tools → A0.
5. **Legacy `AdaptiGuard.run`** documented as historical regex-v3 compatibility; not Phase 1 core.
6. Hard-negative + scenario tests added.

## Failure matrix (diagnostic; frozen pack SHA `523c8818…`)

| Family / mode | Evidence available | Detector (Phase1) | Risk | Policy | Outcome class | Failure reason |
| --- | --- | --- | --- | --- | --- | --- |
| direct override + tool | hierarchy / tool-invoke / marker | hit → MED/HIGH | MED/HIGH | A2 | tool denied | — (fixed) |
| indirect RAG / tool-result followups | context tool-invoke / FOLLOWUP | hit | MED/HIGH | A2 | tool denied | — (mostly fixed) |
| privilege exfil | tool-invoke + exfil sink | hit | MED/HIGH | A2 | tool denied | — (mostly fixed) |
| obfuscation (unicode/hex/html/rot13) | decoded tool text | hit when decode recovers toolish text | MED/HIGH | A2 | tool denied | residual: l33t / Morse / reverse |
| multi-turn persistence | dialogue + tool | hit when control tokens present | MED/HIGH | A2 | tool denied | residual subtle turns |
| text-only MEDIUM | exclusive output | hit | MEDIUM | A1 | sanitize; tools N/A | intentional A1 |
| hard-negative analysis / quoting | attack text in context | E10 → p=0 | LOW | A0 | allow | — (fixed FPs) |
| benign tool workflow | create_record / send_email | E4 without primary | LOW | A0 | execute | — (fixed floors) |

**Offline diagnostic counts (NOT security performance / NOT VNEXT re-score):** attacks hit 56/61; attack actions A2=56 A0=5; benign A0=60 A1=1; false A2/A3=0.

## Exact tests

| Suite | Result |
| --- | --- |
| `tests/test_phase1_core_pipeline.py` | collected + passed with evidence suite |
| `tests/test_phase1_evidence_scenarios.py` | passed |
| Combined Phase1 + related regression | **95 passed** |
| Broader deterministic suite | **241 passed**; 3 pre-existing provider import failures |

Pre-existing: `test_artifact_standard.py` collection error; `test_gemini_provider` / `test_groq_provider` missing optional deps — not Phase 1 regressions.

## Integrity

| Item | Status |
| --- | --- |
| Frozen VNEXT pack `523c8818…` | YES unchanged |
| Layer A TEST `47b975f7…` | YES unchanged |
| VNEXT AUDIT / MSID 0.20 / FAIL numbers | YES unchanged |
| `PromptInjectionDetectorV4` version `evidence_v4.0` | YES unchanged identity |
| LLM/API | **0** |

## Remaining limitations (honest)

- Residual detector blind spots: l33t, Morse, string-reversal, some social-engineering privilege prompts, some subtle multi-turn / RAG captions (~5/61 diagnostic misses).
- Text-only MEDIUM still uses A1 (sanitize); that is minimum intervention, not tool denial.
- Legacy `AdaptiGuard.run` remains regex-v3 for compatibility.
- No live Target/Judge evaluation; offline pack counts are architectural diagnostics only.

## Gate checklist

| Requirement | Met? |
| --- | --- |
| Detector/Risk/Policy/Enforcement separated | YES |
| Label-blind runtime | YES |
| A2/A3 observable action semantics | YES |
| Major blind spots fixed or justified | YES |
| Explainable deterministic signals; no VNEXT threshold tune | YES |
| Risk observable-only; boundary tests | YES |
| A0–A3 explicit; action sensitivity; no maximize-block | YES |
| Attack-like + benign + hard-negatives | YES |
| Refusal ≠ defense win | YES (prior taxonomy) |
| Frozen integrity; API=0 | YES |
| Tests pass; docs updated | YES |

**PHASE 1 = PASS.** Do not start Phase 2 / Multi-Turn / live eval.
