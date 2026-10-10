# Remediation log: Stage 1–2 audit findings (attack pack v4)

Audited commit: `76f1f0e`. Remediation builds on it on branch `claude/adoring-turing-4z5aol`. Nothing has been committed or pushed by this remediation.

Each finding is listed with the change made, the regression tests that cover it, and whether a mutation (a deliberate break of the rule in a scratch copy) made those tests fail.

## CRITICAL

**C1. Category exclusion.** `ATTACK_CATEGORIES = CATEGORIES[:11]` omitted `multi_turn_injection`, so the whole 60-attack family was rejected.
- Fix: `ATTACK_CATEGORIES = tuple(c for c in CATEGORIES if c not in BENIGN_CATEGORIES)` (`attack_schema_v4.py`).
- Tests: `test_attack_categories_are_exactly_the_non_benign_categories`; `test_every_attack_category_has_a_valid_positive_example` (parametrised over all 12 categories); `test_every_attack_category_allows_every_declared_channel_and_turn_type`; `test_benign_categories_are_rejected_as_attacks`.
- Mutation M1 (restore `[:11]`): 7 failed.

**C2. Safety scan coverage.** The scan covered only four text fields. Real hosts in `tool_call.arguments`, `injection_location`, tool definitions, `canary` and bare domains passed.
- Fix: scan every string leaf except metadata keys, including nested `tools`, `tool_call` and `turns`. Detect URLs with schemes (any TLD), e-mail domains, bare domains with a public TLD, and IPv4 literals outside documentation ranges. Reserved names and RFC 5737 / RFC 3849 documentation ranges are allowed. External `source_url` is exempt because it names the real upstream.
- Tests: `test_prohibited_host_in_untrusted_content_is_rejected`, `..._in_attack_objective_...`, `test_prohibited_host_in_tool_call_arguments_is_rejected`, `..._in_tool_definition_...`, `..._in_tool_name_...`, `..._in_turns_...`, `..._in_canary_...`, `..._inside_injection_span_...`; `test_legitimate_synthetic_references_are_accepted` (preserves legitimate synthetic examples, including `plate.png`, `config.json`, `2001:db8::1`, `203.0.113.7`).
- Mutation M2 (scan disabled): 25 failed.
- Limitation: bare domains whose TLD is not in `PUBLIC_TLDS` are not detected (documented in `SCHEMA_v4.md` section 4).

## HIGH

**H1. Malformed inputs raised exceptions.** Malformed URLs (`ValueError`), non-JSON values (`TypeError`), non-dictionary records, non-dictionary dataset items, and non-list `turns` in the pair path all raised.
- Fix: non-object records return an error; a JSON-type check reports non-JSON values by path; malformed URLs are reported; `validate_dataset` guards every type; `created_at` must be a string (no coercion); unknown fields are rejected; a last-resort wrapper converts any unexpected internal error into an error string. Pair checks report `pair cannot be verified` when `turns` is not a list.
- Tests: `test_non_dictionary_record_returns_error` (parametrised over `None`, string, int, list, tuple); `test_non_json_type_in_tools_is_reported_without_exception`; `test_tuple_value_is_not_json_compatible`; `test_non_finite_or_bytes_values_are_reported`; `test_non_string_dictionary_key_is_reported`; `test_deeply_nested_input_returns_error_not_exception`; `test_invalid_turns_structure_is_an_error` (6 cases); `test_created_at_is_not_coerced_from_other_types`; `test_unknown_field_is_rejected`; `test_malformed_url_in_text_is_an_error_not_an_exception`; `test_dataset_rejects_non_list_input_without_exception`; `test_dataset_reports_non_dictionary_items_without_exception`; `test_dataset_survives_malformed_pair_structure`.
- Mutation M5 (wrapper removed): 3 failed. M6 (JSON check disabled): 6 failed. M11 (unknown fields accepted): 3 failed.

**H2. Missing injection or decoy evidence, including `user_turn`.** A `user_turn` hard negative with no decoy anywhere passed. Locations were free text, so they could not be checked against content.
- Fix: schema extension `injection_span` (required; benign: `null`), and `injection_location` as a pointer. `user_turn` locations must be `turns[<i>]` with a canonical index that is in range, and the span must be a substring of that turn. Other channels must point at `untrusted_content`, and the span must be a substring of it. Span length ≥ 8.
- Tests: `test_user_turn_attack_with_span_in_turn_is_valid`; `test_user_turn_attack_span_must_be_in_the_stated_turn`; `test_user_turn_attack_without_any_injection_is_rejected`; `test_user_turn_attack_location_must_be_a_turn_pointer`; `test_user_turn_index_out_of_range_is_rejected`; `test_user_turn_location_grammar_rejects_non_canonical_indices` (5 cases); `test_non_user_attack_must_point_at_untrusted_content`; `test_non_user_attack_span_must_be_in_untrusted_content`; `test_attack_injection_span_must_be_a_meaningful_string` (5 cases); span boundary tests (8 accepted, 7 rejected); `test_user_turn_hard_negative_without_decoy_is_rejected` (the regression); `test_user_turn_hard_negative_with_decoy_in_turn_is_valid`; `test_hard_negative_span_must_be_in_untrusted_content`; `test_benign_span_must_be_null`.
- Mutation M3 (evidence check skipped for attacks): 21 failed. M12 (hard-negative decoy check disabled): 3 failed.
- Owner ratification required: D11.

**H3. Family/category consistency.** Families were not validated against categories, and any string was accepted as a family.
- Fix: explicit `FAMILY_CATEGORY` registry (12 families, one per attack category). Unknown families and incompatible pairs are rejected. The generator checks its family table against the registry.
- Tests: `test_registry_is_one_to_one_with_attack_categories`; `test_unknown_family_is_rejected`; `test_family_with_incompatible_category_is_rejected`; `test_attack_with_benign_family_is_rejected`; `test_attack_with_arbitrary_family_string_is_rejected`; `test_benign_with_attack_family_is_rejected`; `test_hard_negative_with_attack_family_is_rejected`; `test_every_registered_family_has_a_valid_positive_example` (12 cases); `test_generator_families_agree_with_schema_registry`; `test_generator_rejects_family_category_disagreement`.
- Mutation M4 (registry check disabled): 5 failed.

**H4. Power calculation.** The sample size of 58 per arm does not reach 80% power for the documented test. The test also hard-coded that value.
- Fix: power by exact enumeration of the pooled two-proportion z-test; minimum n = **59** for 0.50 vs 0.25 (power 0.8087; 0.7992 at 58). Normal approximation kept as a labelled reference only (57.67). Design target stays 60 (power 0.818). Floor 50 gives 0.745. Assumptions and multiplicity are recorded in the artifact and in `PLAN_AND_COVERAGE_v4.md` section 3.
- Tests: `test_exact_power_at_58_is_below_threshold_for_primary_effect`; `test_exact_minimum_sample_size_for_primary_effect_is_59` (independent implementation); `test_generator_and_independent_implementation_agree_on_power` (agreement to 1e-9); `test_power_values_match_documented_figures`; `test_floor_of_fifty_does_not_reach_threshold_for_primary_effect`; `test_design_target_of_sixty_reaches_threshold_for_primary_effect`; `test_normal_approximation_is_reference_only_and_not_the_design_basis`; `test_committed_power_artifact_matches_exact_computation`; `test_committed_power_artifact_documents_assumptions_and_multiplicity`; `test_secondary_effect_minimum_n_matches_independent_scan` (3 cases).
- Mutation M9 (variance formula wrong): 8 failed.
- Assertion replaced: the old `test_power_floor_is_below_design_target_and_documented` asserted `n_per_arm(0.5, 0.25) == 58`. It is removed because that value fails the threshold; the constants it checked are now asserted directly.

**H5 (tests). Regression coverage.** The original suite could not catch the defects above, because no test exercised `multi_turn_injection` and the safety scan covered only four fields.
- Fix: the tests listed under each finding above. Existing assertions were kept; the fixture changes below are required by the new rules and do not weaken any assertion.

## MEDIUM (fixed where the correction is clear)

**M-objective. `attack_objective` whitespace and case.** `"   "`, `"None"` and `" NONE "` were accepted.
- Fix: compare after `strip()` and lower-casing; reject placeholders for attacks.
- Tests: `test_attack_objective_placeholders_are_rejected_for_attacks` (6 cases); `test_benign_objective_placeholder_is_normalised`; `test_hard_negative_objective_placeholder_is_normalised`.

**M-tools. Mock-tool restriction.** Enforcement would need a tool registry, which is an owner decision (D13).
- Fix (documentation narrowed): the validator checks that tools are declared with unique names, that argument lists are strings, and that `tool_call` refers to a declared tool. The claim that tools are mock tools is withdrawn in `SCHEMA_v4.md` section 8.

**M-independence. Independence and multiplicity.** Assumptions were not stated.
- Fix: stated in `PLAN_AND_COVERAGE_v4.md` section 3.1, in `power_multiturn_v4.json`, and as decision D12.

**M-hardneg. Hard-negative allocation claims.** The "one third" claim was not in the generator.
- Fix: the claim is withdrawn; the generated summary states the allocation is not encoded and is pending D5. No hard-negative count is claimed anywhere.

## LOW (fixed as part of the same changes)

- Regexes used `$`, which accepts a trailing newline, and `\d`, which accepts non-ASCII digits. Fixed with full matches and `[0-9]`. Tests: `test_id_with_trailing_newline_is_rejected`, `test_version_with_trailing_newline_is_rejected`, `test_id_with_non_ascii_digits_is_rejected`, `test_sha256_with_trailing_newline_is_rejected`.
- Pair tool comparison was order-sensitive. Fixed; `test_dataset_pair_match_is_order_insensitive_for_tools`.
- Cross-reference in the code pointed at SCHEMA section 3 for content fields. Removed; section references were rewritten.
- `tool_call` null rule in the schema document contradicted the code. Corrected.
- Generator per-cell targets that do not divide across styles were silently truncated. Now rejected; `test_generator_rejects_per_cell_target_that_does_not_divide_across_styles`.

## Test assertions changed (for transparency)

| location | change | reason |
|---|---|---|
| `tests/test_dataset_upgrade_coverage.py` | removed `test_power_floor_is_below_design_target_and_documented` (asserted `n_per_arm == 58`) | the value fails the stated threshold; replaced by H4 tests |
| `tests/test_attack_schema_v4.py` | `_base()` fixture gained `injection_span`, and its location became `untrusted_content` | required by H2 |
| `tests/test_attack_schema_v4.py` | `test_reserved_host_is_accepted` passes `injection_span` | required by H2; assertion `== []` unchanged |
| `tests/test_attack_schema_v4.py` | `test_canary_attack_without_tool_call_is_valid` now builds its record with `_attack(...)` | required by H2; assertion unchanged |
| `tests/test_attack_schema_v4.py` | `test_missing_required_field_is_reported`: intermediate variable removed | refactor only; same assertion |

## Mutation results

Each mutation was applied in a scratch copy (outside the repository) and the two focused test files were run against it.

| id | mutation | result |
|---|---|---|
| M1 | positional category slice restored | 7 failed, 240 passed |
| M2 | safety scan disabled | 25 failed, 222 passed |
| M3 | user_turn/attack evidence check skipped | 21 failed, 226 passed |
| M4 | family registry check disabled | 5 failed, 242 passed |
| M5 | try/except wrapper removed | 3 failed, 244 passed |
| M6 | JSON-type check disabled | 6 failed, 241 passed |
| M7 | objective normalisation removed | 5 failed, 242 passed |
| M8 | pointer grammar weakened | 3 failed, 244 passed |
| M9 | power variance formula wrong | 8 failed, 239 passed |
| M10 | pair tool comparison order-sensitive | 3 failed, 244 passed |
| M11 | unknown fields accepted | 3 failed, 244 passed |
| M12 | hard-negative decoy check disabled | 3 failed, 244 passed |

All twelve mutations are detected.

## Not fixed (open)

- Stage 4 checks: offline execution of tool calls, whether mock tools return the injection, duplicate and near-duplicate content, provenance and licence verification, and the shortcut audit.
- Bare domains whose TLD is not in `PUBLIC_TLDS` are not detected.
- Injection effectiveness and content harm are not assessed by the validator.
- Owner decisions D2, D3, D4 (sample-size choice), D5, D6, D7, D8, D9, D10, D11, D12, D13 remain open.
