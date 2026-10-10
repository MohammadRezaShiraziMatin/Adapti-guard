# Attack pack v4: staged plan and coverage matrix (Stage 2)

Status: design only. No examples were generated. Machine-readable outputs are in `generated/` and are reproduced by:

```
PYTHONPATH=src python3 scripts/dataset_upgrade/coverage_matrix.py
```

Time estimates below are **my estimates**, not measurements. They assume one researcher and no API cost.

## 1. Staged plan

| stage | scope | est. effort | depends on | verification criterion | status |
|---|---|---|---|---|---|
| 1 | Schema doc, validator, tests | ~1 day | owner answers D1, D6 | `pytest tests/test_attack_schema_v4.py` passes; every rejection rule in SCHEMA_v4.md has a test | **done on branch**: 74 tests pass |
| 2 | Coverage matrix and power design | ~0.5 day | Stage 1 constants | Generated matrix sums to targets; every primary cell ≥10; multi-turn families ≥50 | **done on branch** |
| 3 | Draft generation under `datasets/drafts/attack_v4_draft/` | 2–3 weeks (est.) | owner approval of Stage 2; author/evaluator split (D2) | Every record passes `validate_record`; ≥3 writing styles per family | **not started; needs owner approval** |
| 4 | Validation: duplicates, offline execution, provenance, anonymised review form, shortcut audit | 1–2 weeks (est.) | Stage 3 drafts; reviewers (D2) | Duplicate method and threshold reported; execution check per record; kappa or % agreement only if real reviewers completed the review | **not started** |
| 5 | Freeze to `datasets/frozen/attack_v4_<date>/`, manifest, SHA-256, DATASET_CARD, provenance table, validation report; BASELINE_SHA256 entry in a separate commit; protocol amendment | ~2 days (est.) | explicit owner approval | `sha256sum -c` passes; no existing frozen file changed | **not started; needs owner approval** |
| 6 | Upgrade report | ~1 day (est.) | Stage 5 | Covers changes, inconsistencies, validation, limitations, human-review status, risks | **not started** |

Dependencies: Stage 3 depends on the owner's answers to decisions D1–D3 and D6. Stage 4 depends on at least one human reviewer (D2). Any model evaluation is out of scope and needs a protocol, a budget and owner approval (protocol section 6).

Main risks:
- **Shortcuts.** Attacks and counterparts may differ in a lexical way (length, imperative verbs, the word "ignore"). Stage 4 must test for a simple structural rule before freezing.
- **Templating.** The three styles per family can still share a skeleton. Stage 4 must measure similarity within and across styles.
- **Hard-negative confusion.** A hard negative that is too close to an attack makes the label arguable. D5 governs how these are labelled.
- **Measurability.** Attacks that depend on a model choosing to comply may have ambiguous success. Each attack needs a tool call or canary (validator-enforced) plus a Stage 4 execution check.

## 2. Coverage matrix

Primary cell = (attack family, injection channel, turn type). Each cell is split into three writing styles: `formal`, `conversational`, `structured_or_fabricated_instruction`.

Totals (generated, `generated/coverage_summary_v4.json`):

| family | category | primary cells | attacks | counterparts |
|---|---|---|---|---|
| DIRECT_OVERRIDE | direct_instruction_override | user_turn/single (1) | 12 | 12 |
| EMAIL_INJECTION | email_injection | email/single (1) | 12 | 12 |
| RAG_DOC_INJECTION | rag_document_injection | retrieved_doc/single (1) | 12 | 12 |
| TOOL_OUTPUT_INJECTION | tool_output_injection | tool_output/single (1) | 12 | 12 |
| WEB_CONTENT_INJECTION | web_content_injection | web_content/single (1) | 12 | 12 |
| INDIRECT_CONTEXT | indirect_context_injection | email, retrieved_doc, tool_output, web_content / single (4) | 48 | 48 |
| OBFUSCATION | obfuscation_encoding | user_turn, email, retrieved_doc, tool_output, web_content / single (5) | 60 | 60 |
| UNAUTHORIZED_TOOL | privilege_exfil_unauthorized_tool | user_turn, email, retrieved_doc, tool_output, web_content / single (5) | 60 | 60 |
| SYSTEM_PROMPT_LEAKAGE | system_prompt_leakage | user_turn, retrieved_doc, web_content / single (3) | 36 | 36 |
| JAILBREAK_ROLEPLAY | jailbreak_roleplay | user_turn/single (1) | 12 | 12 |
| MULTI_TURN_PERSISTENCE | multi_turn_persistence | user_turn/multi (1) | **60** | 60 |
| MULTI_TURN_INJECTION | multi_turn_injection | email, retrieved_doc, tool_output, web_content / multi (4) | **60** | 60 |
| **total** | | **28** | **396** | **396** |

Checks against the protocol targets:
- Every primary cell has at least 12 attacks (single-turn) or 15 (multi-turn), above the minimum of 10.
- Each multi-turn family has 60 attacks, above the 50 floor.
- Benign-side records = attacks (1:1). Each attack has exactly one counterpart with the same channel, turn type and tools. About one third of counterparts are intended as `hard_negative` and two thirds as `benign_task`; this split is a proposal (D5), not yet applied.
- Hard negatives are spread across families in the same proportion as attacks, so no family is over- or under-represented in them.

### Infeasible or invalid combinations (excluded)

| family | channel | turn | reason |
|---|---|---|---|
| DIRECT_OVERRIDE | email, tool_output | single | a direct override is by definition a user-turn instruction; the other channels belong to the indirect families |
| JAILBREAK_ROLEPLAY | retrieved_doc, web_content | single | excluded by the v4 schema; roleplay framing is user-turn only (D6) |
| SYSTEM_PROMPT_LEAKAGE | email | single | excluded by the v4 schema (D6) |
| MULTI_TURN_PERSISTENCE | email, retrieved_doc, tool_output, web_content | multi | excluded by the v4 schema; persistence is user-turn only (D6) |
| MULTI_TURN_INJECTION | user_turn | multi | user-turn content is covered by MULTI_TURN_PERSISTENCE |
| any | none | any | channel `none` is never an attack channel |
| any non-multi family | any | multi | v4 has no multi-turn variant of single-turn families (D6) |

Feasibility concerns, not exclusions:
- **Tool-output attacks** need a mock tool that returns the untrusted text. Feasible, but each tool must be declared in `tools`.
- **System-prompt leakage** needs a canary placed in the mock system prompt. Feasible; the canary is what the success condition checks.
- **Multi-turn injection** needs a turn in which a tool or document returns untrusted content, followed by a turn in which the model could act on it. Feasible, but the fixed number of turns must be decided per family before drafting.

## 3. Multi-turn sample size

Per-arm sample sizes, normal approximation, two-sided α = 0.05 (`generated/power_multiturn_v4.json`):

| baseline ASR | treated ASR | n per arm for 80% power | power at n = 50 | power at n = 60 |
|---|---|---|---|---|
| 0.50 | 0.25 | 58 | 0.74 | 0.82 |
| 0.50 | 0.30 | 93 | — | — |
| 0.40 | 0.20 | 82 | 0.59 | 0.67 |
| 0.30 | 0.15 | 121 | — | — |

Proposal: **60 attacks per multi-turn family** (design target). The 50 floor is the smallest value I would accept. It gives 74% power for the 0.50 vs 0.25 effect, which must be disclosed. Smaller effects need more than 60. This is a statistical power argument only; it does not establish that a family is representative, and the family-level counts are a design constraint, not a result.

## 4. Verification criteria for Stage 2 (protocol section 7)

- Matrix generated from code, not typed: `scripts/dataset_upgrade/coverage_matrix.py` asserts that each cell is allowed by `CATEGORY_RULES`, so the matrix cannot silently contradict the validator.
- The rules in section 2 of this document match the validator. Changes to either must update both.
- No dataset example was generated; `datasets/drafts/` does not exist yet.
