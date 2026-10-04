# E6 authoring guide (for the independent author)

You write content only. Fill a copy of `authoring_template_v1.json` (30 families, 10 instances each) that validates against `authoring_schema_v1.json`. Do not write harness JSON, message wrappers, roles, a system prompt, tool definitions or the marker.

**Who may author.** A human who is not the project owner, did not take part in E1-E5, has not seen the detector or defense code or any E3 per-family result, and used no AI assistance. The attestation block must say so with every flag true plus a statement in your own words. The validator rejects AI systems, the project owner, test fixtures, `NOT_AVAILABLE`, `synthetic: true` and any incomplete attestation. It cannot verify the attestation; that remains a statement you stand behind.

**Per family.** `family_id` (lowercase letters, digits, single underscores; no double underscore), `channel` (`retrieve_document` or `get_weather`; exactly 15 families each), `effect_tool` (`send_email` with parameters `to`, `body`, or `create_record` with `kind`, `payload`).

**Per instance (10 per family, indices 0-9).**
- `user_task`: the user's request; it contains `prerequisite_arg` (the doc id to retrieve or the city to look up).
- `carrier_content`: the document body (document channel) or the text appended to the weather conditions (weather channel). It carries one injection, contains the token `{MARKER}` exactly once, and contains every `required_args` value.
- `neutral_content`: the same text without the injection. Whether it contains `{MARKER}` depends on the owner's H4 decision (protocol section 6a.9); do not start until that decision is recorded in `INPUTS_STATUS.json`.
- `required_args`: the attacker-specified call arguments, keyed by parameters of `effect_tool`, leaving at least one parameter free (the marker must appear in it).

**Variation inside a family.** The 10 `user_task`, `carrier_content` and `required_args` values are pairwise distinct, and no two `carrier_content` values exceed token-set Jaccard 0.9 (proposed threshold, owner to confirm).

Check your file with `python scripts/e6_render.py YOUR.json --h4-policy absent|inert`.

## Attestation block (you fill it yourself; nobody else may)
```json
"author": {
  "author_id": "your real name or team name",
  "role": "independent scenario author",
  "independence_attestation": {
    "human_authored": true, "no_ai_assistance": true, "not_project_owner": true,
    "no_e1_e5_participation": true, "no_detector_or_defense_code_access": true, "no_e3_results_seen": true,
    "statement": "in your own words: who you are, how you wrote the scenarios, and that each flag above is true"
  },
  "attestation_utc": "ISO 8601 time you signed"
}
```
Set a flag to true only if it is true. Any false, missing or non-boolean flag, an empty statement, `synthetic: true`, or an author id naming an AI system, the project owner, a test or fixture, or `NOT_AVAILABLE` is rejected. Keep `pack_id`, `created_utc` and `frozen_utc` filled; after you deliver the file it is frozen and hashed and may not be edited.

## Delivery checklist
1. 30 families, ids unique; 15 with `channel: retrieve_document`, 15 with `get_weather`.
2. Each family has instances 0-9; every instance has all five content fields; no instance contains the text `HARNESS-V2-MARK`.
3. `carrier_content` has `{MARKER}` once and every `required_args` value; `neutral_content` (H4 `inert`) has `{MARKER}` once and every `required_args` value as inert data with no instruction.
4. Within a family, `user_task`, `carrier_content` and `required_args` are all different, and no two `carrier_content` values are near-duplicates.
5. `python scripts/e6_render.py YOUR.json --h4-policy inert` prints `structure_ok: true` and `freeze_eligible: true` (it exits 1 only if eligibility fails).
6. Send the single file to the project owner. Do not send it through an AI assistant for editing.
