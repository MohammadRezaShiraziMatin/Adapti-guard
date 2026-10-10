# Attack pack v4: dataset schema (Stage 1)

Status: **draft for owner review**. No examples have been generated and no frozen artifact was modified.
Code: `src/adapti_guard/data/attack_schema_v4.py` (validator). Tests: `tests/test_attack_schema_v4.py`.
The older `src/adapti_guard/data/schema.py` and `validator.py` are unused stubs with a different schema; they are left untouched.

## 1. Record format

One JSON object per line (`.jsonl`). Field names are the exact names required by the upgrade protocol. Four content fields
(`turns`, `untrusted_content`, `pair_id`, `canary`) and three provenance fields (`redistributable`, plus `source_url`, `source_version`, `retrieved_at` for external sources) are added because the required list alone cannot express a runnable example. These additions are owner decision D1 (see `OWNER_DECISIONS_v4.md`).

| field | type | rule |
|---|---|---|
| `id` | string | Matches `^av4-(atk\|ben\|hn)-\d{6}$`. Middle segment must match the label: `atk` = attack, `ben` = benign, `hn` = hard_negative. |
| `label` | enum | `attack`, `benign`, `hard_negative`. |
| `family` | string | Attack family name for attacks (not `benign`). Must be `benign` for `benign` and `hard_negative` records. |
| `category` | enum | One of the 14 values in protocol section 3. |
| `turn_type` | enum | `single` or `multi`. `single` requires exactly one entry in `turns`; `multi` requires at least two. |
| `injection_channel` | enum | `user_turn`, `tool_output`, `retrieved_doc`, `email`, `web_content`, `none`. Never empty. |
| `injection_location` | string | Exact location of the injection, e.g. `email body, paragraph 2` or `turns[2]`. Required and not `none` for attacks. For `hard_negative`, names where the decoy text sits. Must be `none` for `benign`. |
| `attack_objective` | string | Plain-language objective. Required for attacks. Must be `none` for benign-side records. |
| `success_condition` | string | At least 10 characters. Preferably names the tool call or canary being checked. |
| `tools` | list of `{name, arguments}` | Non-empty list of mock tool definitions. Every tool named in `tool_call` must appear here. |
| `tool_call` | object or null | `{name, arguments}`. `name` must appear in `tools`. Null is allowed only where `canary` carries the measurable effect. |
| `source` | string | `self_authored`, or one of `garak`, `InjecAgent`, `TrustLLM`, `AgentDojo`, `LLMail-Inject`. |
| `author_id` | string | Non-empty. Attack author and defense evaluator should be different people where feasible; this cannot be checked by the validator. |
| `created_at` | string | ISO-8601 (`datetime.fromisoformat`). |
| `version` | string | Matches `^attack_v4(_[a-z0-9_]+)?$`, e.g. `attack_v4_draft`, `attack_v4_2026-12-01`. |
| `license` | string | Non-empty. Project licence (MIT) for self-authored records; the source licence for external records. |
| `sha256` | string | 64 lowercase hex characters. Must equal the SHA-256 of the canonical JSON of the record without `sha256` (`sort_keys`, `ensure_ascii=False`, compact separators, UTF-8). |
| `turns` | list of strings | See `turn_type`. No empty strings. |
| `untrusted_content` | string | Content carried through `injection_channel`. Empty only for `none` (must be empty) and `user_turn` (the untrusted text may sit in `turns`). Otherwise non-empty. |
| `pair_id` | string | `id` of the structural counterpart. Required for every attack and every benign-side record. |
| `canary` | string or null | Measurable token for output-based success (e.g. system-prompt leakage). Required for attacks without `tool_call`. Must be `null` for benign-side records. |
| `redistributable` | boolean | Required on every record. For external sources, `false` means the record may not carry any text. |

## 2. Label-specific rules

**attack**
- `category` must be an attack category, and `(injection_channel, turn_type)` must be allowed for it (section 4).
- `injection_channel` must not be `none`. `injection_location` must be exact and not `none`. `attack_objective` must be present.
- `tool_call` or `canary` must be present, so the effect is measurable.
- `family` must be an attack family name. `pair_id` must point to a benign-side record that points back.

**benign** (`benign_task`)
- `family` = `benign`, `injection_location` = `none`, `attack_objective` = `none`, `canary` = `null`.
- Benign records *may* carry a channel and untrusted content. This is how the structurally matched counterpart of an attack keeps the same channel, turn structure and tools while containing no injection. Channel `none` is used only for benign tasks that have no untrusted content at all.

**hard_negative** (`hard_negative_benign`)
- `family` = `benign`. Must carry untrusted content (channel other than `none`) containing decoy text that resembles an injection, quoted, analysed, or translated, with no instruction to act on it.
- `injection_location` names where the decoy sits. `attack_objective` = `none`, `canary` = `null`.
- Hard negatives are labelled `hard_negative`. Existing records in `layer_a_v3` and `vnext_confirm_v1` use `label = benign` with `attack_type = hard_negative`; migration to the new label is a decision (D5).

## 3. Category, channel and turn constraints (attacks)

| category | allowed channels | allowed turn_type |
|---|---|---|
| direct_instruction_override | user_turn | single |
| jailbreak_roleplay | user_turn | single |
| system_prompt_leakage | user_turn, retrieved_doc, web_content | single |
| email_injection | email | single |
| rag_document_injection | retrieved_doc | single |
| tool_output_injection | tool_output | single |
| web_content_injection | web_content | single |
| indirect_context_injection | email, retrieved_doc, tool_output, web_content | single |
| obfuscation_encoding | user_turn, email, retrieved_doc, tool_output, web_content | single |
| privilege_exfil_unauthorized_tool | user_turn, email, retrieved_doc, tool_output, web_content | single |
| multi_turn_persistence | user_turn | multi |
| multi_turn_injection | email, retrieved_doc, tool_output, web_content | multi |

These constraints are a design choice for v4 and are listed as decision D6. Changing them means editing `CATEGORY_RULES` and this table together.

## 4. Safety rules enforced by the validator

- Any e-mail address or URL in `attack_objective`, `success_condition`, `untrusted_content` or `turns` must use a reserved name: `.invalid`, `.example`, `.test`, `.localhost`, or `example.com/.org/.net`. Other hosts fail validation.
- Every attack must name mock tools only (`tools` is required). The validator does not check whether content is harmful; that is a human-review item (Stage 4).

## 5. Dataset-level rules (`validate_dataset`)

- `id` values are unique.
- Every labelled record's `pair_id` resolves to a record in the same dataset.
- Pairs are reciprocal. An attack pairs with a benign-side record (never another attack), and a benign-side record pairs with an attack.
- Paired records match on `injection_channel`, `turn_type`, `tools`, and number of turns.

Length and style matching between pairs is not checked here. It is a Stage 4 statistical check (see the plan).

## 6. What the validator does not check

- Whether the injection actually reaches the model through the stated channel (Stage 4, offline execution check).
- Whether the tool call is exercisable against the mock tools (Stage 4).
- Duplicate or near-duplicate content (Stage 4: Jaccard or embedding similarity).
- Provenance and licence claims for external sources beyond their presence (Stage 4 provenance audit).
- Human-review outcomes. None have been conducted.

## 7. Known gaps in existing frozen data (verified, not modified)

Checked against the frozen files in commit `e5949bc`. Existing files do not conform to v4 and must not be edited:

- `eval_v1` (770 rows): no `label`, no `success_condition`, no `tool_call`, no `pair_id`; `user_task` is empty in all 770 rows, `attack_objective` in 497. Injection location is empty in all 770 rows. No benign rows. Under v4 these records cannot satisfy "measurable effect" or "structurally matched counterpart".
- `phase1_*`, `layer_a_*`, `vnext_*`, `p1_mechanism_*`: each uses its own field set (`prompt`/`context`/`metadata` nesting varies). Converting them to v4 requires a derived, versioned dataset, not an edit.
