# Attack pack v4: staged plan and coverage matrix (Stage 2)

Status: design only. No examples were generated. Machine-readable outputs are in `generated/` and are reproduced by:

```
PYTHONPATH=src python3 scripts/dataset_upgrade/coverage_matrix.py --out-dir <DIR>
```

Time estimates are **my estimates**, not measurements. They assume one researcher and no API cost. This document was revised in the remediation of the Stage 1–2 audit (`REMEDIATION_LOG_v4.md`).

## 1. Staged plan

| stage | scope | est. effort | depends on | verification criterion | status |
|---|---|---|---|---|---|
| 1 | Schema doc, validator, tests | ~1 day | owner answers D1, D6, D11 | `pytest tests/test_attack_schema_v4.py` passes; every rejection rule in SCHEMA_v4.md has a test; mutation checks catch broken rules | **remediated on branch** (see remediation log) |
| 2 | Coverage matrix and power design | ~0.5 day | Stage 1 constants | Generated matrix sums to targets; every primary cell ≥10; multi-turn families ≥50; power recomputed by exact enumeration | **remediated on branch** |
| 3 | Draft generation under `datasets/drafts/attack_v4_draft/` | 2–3 weeks (est.) | owner approval of Stage 2; author/evaluator split (D2); D5 | Every record passes `validate_record`; ≥3 writing styles per family | **not started; needs separate owner approval** |
| 4 | Validation: duplicates, offline execution, provenance, anonymised review form, shortcut audit | 1–2 weeks (est.) | Stage 3 drafts; reviewers (D2) | Duplicate method and threshold reported; execution check per record; kappa or % agreement only if real reviewers completed the review | **not started** |
| 5 | Freeze to `datasets/frozen/attack_v4_<date>/`, manifest, SHA-256, DATASET_CARD, provenance table, validation report; BASELINE_SHA256 entry in a separate commit; protocol amendment | ~2 days (est.) | explicit owner approval | `sha256sum -c` passes; no existing frozen file changed | **not started; needs owner approval** |
| 6 | Upgrade report | ~1 day (est.) | Stage 5 | Covers changes, inconsistencies, validation, limitations, human-review status, risks | **not started** |

Dependencies: Stage 3 depends on D1, D2, D5, D6 and D11. Stage 4 depends on at least one human reviewer (D2). Any model evaluation is out of scope and needs a protocol, a budget and owner approval (protocol section 6).

Main risks:
- **Shortcuts.** Attacks and counterparts may differ in a lexical way (length, imperative verbs, the word "ignore"). Stage 4 must test for a simple structural rule before freezing.
- **Templating.** The three styles per family can still share a skeleton. Stage 4 must measure similarity within and across styles.
- **Hard-negative confusion.** A hard negative that is too close to an attack makes the label arguable. D5 governs how these are labelled.
- **Measurability.** Attacks that depend on a model choosing to comply may have ambiguous success. The validator requires a tool call or canary and a span-evidenced injection; Stage 4 must confirm the execution.

## 2. Coverage matrix

Primary cell = (attack family, injection channel, turn type). Each cell is split into three writing styles: `formal`, `conversational`, `structured_or_fabricated_instruction`. Each per-cell target must divide evenly across the three styles; the generator refuses targets that do not.

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

Single-turn: 276 attacks across 23 cells (12 per cell). Multi-turn: 120 attacks across 5 cells.

Checks against the protocol targets:
- Every primary cell has at least 12 attacks (single-turn) or 15 (multi-turn), above the minimum of 10.
- Each multi-turn family has 60 attacks, above the 50 floor.
- Benign-side records equal attacks (1:1). Each attack has exactly one counterpart with the same channel, turn type and tools.

### 2.1 Hard-negative allocation: not encoded

Earlier drafts said that about one third of counterparts would be `hard_negative` and two-thirds `benign_task`, and that hard negatives would be spread proportionally across families. **That allocation is not in the generator and is not in the generated artifacts.** The generated `coverage_summary_v4.json` states that the proportion is not encoded and is pending decision D5. Until D5 is answered, the counterpart label is unassigned, and no hard-negative count is claimed.

### 2.2 Infeasible or invalid combinations (excluded)

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
- **Tool-output attacks** need a mock tool that returns the untrusted text. The schema checks that the tool is declared; it does not check that the mock returns the text (Stage 4).
- **System-prompt leakage** needs a canary placed in the mock system prompt. The schema checks that the success condition names the canary; it does not check the mock prompt (Stage 4).
- **Multi-turn injection** needs a turn in which a tool or document returns untrusted content, followed by a turn in which the model could act on it. The number of turns per family must be fixed before drafting.

## 3. Statistical design and sample size

### 3.1 Hypothesis test and assumptions

- **Test:** two-sided pooled two-proportion z-test, comparing an attack-success proportion between two arms.
- **Significance level:** α = 0.05 (two-sided).
- **Power target:** 0.80.
- **Allocation:** equal n per arm.
- **Power computation:** exact enumeration of every pair of outcomes (x1, x2) under the binomial model, applying the pooled z statistic. When the pooled variance is zero the test is counted as not rejecting. This is the calculation used for the design, and the generator and an independent implementation in the test suite agree to 1e-9.
- **Normal approximation:** shown in the power artifact for reference only. It uses an unpooled variance under H1 and gives 57.67 for the primary effect; it is not the design basis.

Assumptions (also recorded in `generated/power_multiturn_v4.json`):
1. The two arms are independent and each attack is scored once per arm. If the same attacks are run in both arms, the design is paired and the calculation above is conservative or wrong; a paired calculation is not done here.
2. Outcomes are independent Bernoulli trials within each arm: no clustering by family, writing style or template. Attacks sharing a template are not independent, so the effective sample size may be smaller.
3. Power is computed for one primary comparison. **No multiplicity adjustment is applied.** Across 12 families and 28 primary cells the family-wise error rate is not controlled, and no correction is proposed here (decision D12).
4. Statistical power describes the design's sensitivity. It does not establish that any defense works or fails.

### 3.2 Results

Exact power by enumeration (`generated/power_multiturn_v4.json`):

| baseline | treated | exact min n for power ≥ 0.80 | power at min n | power at n−1 | power at n = 50 | power at n = 60 |
|---|---|---|---|---|---|---|
| 0.50 | 0.25 | **59** | 0.8087 | 0.7992 | 0.7452 | 0.8180 |
| 0.50 | 0.30 | 94 | 0.8002 | 0.7991 | 0.5455 | 0.6177 |
| 0.40 | 0.20 | 80 | 0.8009 | 0.7950 | 0.5953 | 0.6835 |
| 0.30 | 0.15 | 119 | 0.8016 | 0.7977 | 0.4425 | 0.5142 |

Corrections to earlier figures:
- The earlier sample size of **58** per arm for the primary effect is wrong. Power at 58 is 0.7992, below the threshold. The correct minimum is **59**.
- The earlier power at n = 50 (0.74) and n = 60 (0.82) are rounded differently now: 0.745 and 0.818.
- The earlier power at n = 60 for 0.40 vs 0.20 (0.67) is 0.684 under exact enumeration.

Note on the sawtooth: exact power is not monotone in n. For 0.40 vs 0.20 the first n reaching 0.80 is 80, while the normal approximation gives 81.2. The table reports the first n reaching the target and the power at n−1 so that the non-monotonicity is visible.

### 3.3 Design targets

- **Primary effect (0.50 vs 0.25):** the exact minimum is 59 per arm. The design keeps a target of **60** per multi-turn family, which gives power 0.818 for that effect.
- **Floor:** 50 per multi-turn family gives power 0.745 for the primary effect. This is below 0.80 and is acceptable only if the owner accepts that power (decision D4).

## 4. Verification criteria for Stage 2

- The matrix is generated from code. `coverage_matrix.py` checks that each family's category agrees with the schema registry, that each cell is allowed by `CATEGORY_RULES`, and that each per-cell target divides across the three styles.
- The power figures are computed by exact enumeration and independently re-computed in `tests/test_dataset_upgrade_coverage.py` with log-space binomial terms.
- The committed artifacts are regenerated outside the repository, compared, and then copied in. The CSV is deterministic across runs.
- No dataset example was generated; `datasets/drafts/` does not exist.
