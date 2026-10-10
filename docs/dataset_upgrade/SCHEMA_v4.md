# Attack pack v4: dataset schema (Stage 1)

Status: **draft for owner review**. No examples have been generated and no frozen artifact was modified.
Code: `src/adapti_guard/data/attack_schema_v4.py` (validator). Tests: `tests/test_attack_schema_v4.py`.
The older `src/adapti_guard/data/schema.py` and `validator.py` are unused stubs with a different schema and are left untouched.
This document was revised in the remediation of the Stage 1–2 audit; see `REMEDIATION_LOG_v4.md`.

## 1. Record format

One JSON object per line (`.jsonl`). The record must be a JSON object. Every field below is required; unknown fields are rejected. Provenance fields (section 1.2) are allowed only for external sources.

### 1.1 Fields

| field | type | rule |
|---|---|---|
| `id` | string | Full match of `av4-(atk\|ben\|hn)-[0-9]{6}`. The middle segment must match the label: `atk` = attack, `ben` = benign, `hn` = hard_negative. |
| `label` | enum | `attack`, `benign`, `hard_negative`. |
| `family` | string | For attacks: a key of the family registry (section 3). For `benign` and `hard_negative`: exactly `benign`. |
| `category` | enum | One of the 14 values in protocol section 3. Attack categories are every category except `benign_task` and `hard_negative_benign`. |
| `turn_type` | enum | `single` (exactly one entry in `turns`) or `multi` (at least two). |
| `injection_channel` | enum | `user_turn`, `tool_output`, `retrieved_doc`, `email`, `web_content`, `none`. Never empty. |
| `injection_location` | string | A pointer, not free text (section 2). Attacks and hard negatives: `turns[<index>]` for `user_turn`, otherwise `untrusted_content`. Benign: `none`. |
| `injection_span` | string or null | The exact text of the injection (attack) or decoy (hard negative). It must be a substring of the location it names and at least 8 characters long. Benign: `null`. This field is a schema extension; see owner decision D11. |
| `attack_objective` | string | Plain-language objective. Compared after `strip()` and lower-casing: `none` is a placeholder and is rejected for attacks. For benign and hard negatives it must normalise to `none`. |
| `success_condition` | string | At least 10 characters. For attacks: must contain `tool_call.name` when a tool call is present, and must contain the `canary` when one is present. |
| `tools` | list | Non-empty list of `{name, arguments?}`. `name` is a non-blank string and unique within the list. `arguments`, when present, is a list of strings. |
| `tool_call` | object or null | `{name, arguments}` with exactly those two keys. `name` must be declared in `tools`; `arguments` is an object. Null is allowed for benign and hard-negative records. For attacks it is allowed only when `canary` is present. |
| `turns` | list of strings | Each entry is non-blank. Length rules follow `turn_type`. |
| `untrusted_content` | string | The content carried through `injection_channel`. Must be `""` for `none`. Must be non-blank for every channel except `user_turn` (where the untrusted text may sit in `turns`). |
| `pair_id` | string | `id` of the structural counterpart. Required for attacks, benign and hard-negative records. |
| `canary` | string or null | Measurable token for output-based success. Required (non-blank) for attacks without `tool_call`. Must be `null` for benign-side records. |
| `redistributable` | boolean | Required on every record. For external sources, `false` means the record may not carry any text. |
| `source` | string | `self_authored`, or one of `garak`, `InjecAgent`, `TrustLLM`, `AgentDojo`, `LLMail-Inject`. |
| `author_id` | string | Non-blank. Attack author and defense evaluator should be different people; this cannot be checked by the validator. |
| `created_at` | string | ISO-8601 string. Other JSON types (for example a number) are rejected, not converted. |
| `version` | string | Full match of `attack_v4(_[a-z0-9_]+)?`. |
| `license` | string | Non-blank. The project licence (MIT) for self-authored records; the source licence for external records. |
| `sha256` | string | 64 lowercase hex characters, full match. Must equal the SHA-256 of the canonical JSON of the record without `sha256` (`sort_keys`, `ensure_ascii=False`, compact separators, UTF-8). |

### 1.2 Provenance fields (external sources only)

`source_url`, `source_version`, `retrieved_at`: required and non-blank when `source` is an external source; rejected when `source` is `self_authored`. `source_url` is exempt from the content safety scan because it names the real upstream source.

## 2. Injection and decoy evidence

For every attack and hard negative, the validator checks that the stated injection or decoy is really present:

- `user_turn`: `injection_location` must be `turns[<i>]` with a canonical index (`0` or a non-zero-leading integer), `i` must be a valid index, and `injection_span` must be a substring of `turns[i]`.
- Any other channel: `injection_location` must be exactly `untrusted_content`, and `injection_span` must be a substring of `untrusted_content`.
- `injection_span` must be a string with at least 8 characters after `strip()`.

This rule closes the earlier gap in which a `user_turn` hard negative with no decoy anywhere passed. Limitation: the validator confirms that the span is present in the stated location, not that it is an effective injection; that is a Stage 4 execution check.

## 3. Family registry and category constraints

Each attack family maps to exactly one category (`FAMILY_CATEGORY` in the validator):

| family | category |
|---|---|
| DIRECT_OVERRIDE | direct_instruction_override |
| EMAIL_INJECTION | email_injection |
| RAG_DOC_INJECTION | rag_document_injection |
| TOOL_OUTPUT_INJECTION | tool_output_injection |
| WEB_CONTENT_INJECTION | web_content_injection |
| INDIRECT_CONTEXT | indirect_context_injection |
| OBFUSCATION | obfuscation_encoding |
| UNAUTHORIZED_TOOL | privilege_exfil_unauthorized_tool |
| SYSTEM_PROMPT_LEAKAGE | system_prompt_leakage |
| JAILBREAK_ROLEPLAY | jailbreak_roleplay |
| MULTI_TURN_PERSISTENCE | multi_turn_persistence |
| MULTI_TURN_INJECTION | multi_turn_injection |

An unknown family, or a family paired with another category, is rejected. The coverage generator checks its family table against this registry.

Allowed channels and turn types for attack categories:

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

These are v4 design choices (decision D6). Changing them means editing `CATEGORY_RULES`, `FAMILY_CATEGORY` and this document together.

## 4. Safety scan

Every string in the record except the metadata keys (`id`, `sha256`, `pair_id`, `version`, `created_at`, `license`, `author_id`, `source`, `source_url`, `source_version`, `retrieved_at`) is scanned, including nested values inside `tools`, `tool_call` and `turns`. The scan rejects:

- a URL with a scheme whose host is not a reserved name or documentation address (any TLD, including `localhost`);
- a scheme-relative URL (`//host/...`, with any number of leading slashes) whose host is not reserved (any TLD, including `localhost`);
- a URL, or scheme-relative URL, that cannot be parsed (for example `http://[::1`), reported as `malformed URL`;
- an e-mail address whose domain is not reserved;
- a bare domain (no scheme) whose final label is in `PUBLIC_TLDS` and which is not reserved. A host is recognised when it follows any character other than a hostname character, so `...vendor.com`, `_vendor.com`, `/vendor.com` and `(vendor.com` are all checked;
- an IPv4 literal outside the documentation ranges 192.0.2.0/24, 198.51.100.0/24 and 203.0.113.0/24, including when preceded by punctuation;
- an IPv6 literal, bare or in brackets, outside `2001:db8::/32`. A candidate is any run of hex digits, colons and dots that contains at least two colons and parses as an IPv6 address. This rule fails closed: a token such as `a::b` in code-like text is reported.

Reserved names: `.invalid`, `.example`, `.test`, `.localhost` (as suffixes), and `example.com`, `example.org`, `example.net` (and their subdomains). Documentation addresses: the RFC 5737 IPv4 ranges above and `2001:db8::/32`.

The scan runs in two passes, and the results are merged:

1. The original-text pass is unchanged. Its findings are always kept.
2. A normalised pass runs on a copy of the text. Normalisation applies NFKC, then removes Unicode format characters (category `Cf`), then maps U+3002, U+FF61 and U+FF0E to `.`. This pass reports hosts (with Unicode letters in host tokens), bare IPv4 addresses and bare IPv6 addresses, and applies the same reserved-name and documentation-range checks. A host already reported by the original pass is not reported again. A normalised IPv6 candidate may drop one leading or trailing colon that is not part of `::`; address digits are never changed.

This normalised pass is candidate detection. It does not claim to reproduce browser IDNA (UTS #46) processing, and it does not handle confusable characters.

Limitations, stated explicitly:
- A bare domain whose TLD is not in `PUBLIC_TLDS` is not detected. Schemes, scheme-relative URLs and e-mail addresses are checked for any TLD. `PUBLIC_TLDS` is a curated list, chosen so that file names such as `plate.png` or `config.json` are not treated as hosts.
- A bare IPv4 address with a leading zero (for example `08.8.8.8`) is not reported, because Python's `ipaddress` rejects it. It is still reported when it appears in a URL, where the host is not a parsed address.
- The normalised pass does not apply the URL, e-mail, scheme-relative or `file:` rules. A fullwidth URL scheme (for example `ｈｔｔｐｓ://…`) is therefore not recognised as a URL by those rules.
- For a Cyrillic label such as `vеndor.com`, the original pass still reports the fragment `ndor.com`, because original findings are kept. The normalised pass adds the whole name `vеndor.com`. Both are reported.
- Confusable characters (for example Cyrillic letters that look like Latin ones) are not mapped. A host whose top-level domain is written with them is not in `PUBLIC_TLDS` and is not reported.
- The scan is a lexical check. It does not establish that content is harmless; that is a human-review item (Stage 4).

## 5. Malformed input

- A record that is not a JSON object returns `record must be a JSON object`.
- Values that are not JSON-compatible (sets, tuples, bytes, non-finite numbers, non-string keys, dates) are reported with their path. Tuples are rejected even though `json` would serialise them, so that in-memory records match what is stored.
- Missing fields and unknown fields are reported.
- Wrong types are reported and never coerced: for example `created_at` must be a string, and `turns` must be a list of strings.
- An unexpected internal error is converted into an error string (`internal validation failure`), not raised. Tests check that the specific rules catch the common malformed inputs, so this path is a last resort.

`validate_dataset` accepts any value: a non-list gives a dataset-level error, and each non-object item gives a per-item error.

## 6. Label-specific rules

**attack**
- `category` is an attack category, and `(injection_channel, turn_type)` is allowed for it (section 3).
- `family` is a registry key compatible with `category`.
- `injection_location` and `injection_span` satisfy section 2.
- `attack_objective` is present and not a placeholder after normalisation.
- `tool_call` or `canary` is present, so the effect is measurable. A tool call's name must appear in `success_condition`; a canary must appear in `success_condition`.

**benign** (`benign_task`)
- `family` = `benign`, `injection_location` = `none`, `injection_span` = `null`, `attack_objective` normalises to `none`, `canary` = `null`.
- Benign records may carry a channel and untrusted content. This is how the structurally matched counterpart of an attack keeps the same channel, turn structure and tools while containing no injection.

**hard_negative** (`hard_negative_benign`)
- `family` = `benign`. Must carry untrusted content (channel other than `none`) containing a decoy that is evidenced by section 2.
- `attack_objective` normalises to `none`, `canary` = `null`.
- Existing records in `layer_a_v3` and `vnext_confirm_v1` use `label = benign` with `attack_type = hard_negative`. Whether v4 uses the `hard_negative` label for counterparts is decision D5.

## 7. Dataset-level rules (`validate_dataset`)

- `id` values are unique. A duplicate is reported under its id.
- Every labelled record's `pair_id` resolves to a record in the same dataset.
- Pairs are reciprocal: an attack pairs only with a benign-side record and vice versa, and each points back.
- Paired records match on `injection_channel`, `turn_type`, tool definitions (compared order-insensitively) and number of turns. If either record's `turns` is not a list, the pair is reported as unverifiable. If either record's `tools` is not a JSON-compatible list, the pair is reported as `pair cannot be verified` and the tool lists are not compared. An integer beyond Python's string-conversion digit limit is not serialisable and is treated the same way. An unexpected error during a pair check is reported as a pair error, not raised.

Length and style matching between pairs is not checked here; it is a Stage 4 statistical check.

## 8. What the validator does not check

- Whether the injection reaches the model through the stated channel, or whether a tool call executes against mock tools (Stage 4).
- That tools are mock tools. The validator checks only that tools are declared with unique names and that `tool_call` refers to a declared tool. This is the actual guarantee; the stronger claim in earlier drafts is withdrawn (see `REMEDIATION_LOG_v4.md`, finding M-tools).
- Duplicate or near-duplicate content (Stage 4).
- Provenance and licence claims for external sources beyond their presence (Stage 4).
- That a canary token is present in the mock system prompt for leakage attacks (Stage 4).
- Human-review outcomes. None have been conducted.

## 9. Known gaps in existing frozen data (verified, not modified)

- `eval_v1` (770 rows): no `label`, no `success_condition`, no `tool_call`, no `pair_id`, no `injection_span`; `user_task` is empty in all 770 rows, `attack_objective` in 497. Injection location is empty in all 770 rows. No benign rows. Under v4 none of the 770 rows is accepted (verified: 0 of 770). Migration would need a documented, versioned process (decision D7).
- `phase1_*`, `layer_a_*`, `vnext_*`, `p1_mechanism_*` use their own field sets. Converting them to v4 requires a derived, versioned dataset, not an edit.
