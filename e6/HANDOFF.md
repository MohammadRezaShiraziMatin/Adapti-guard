# E6 handoff: what only other people can supply

Status at commit `a0682d4` + this file: engineering complete, freeze BLOCKED (`python scripts/e6_manifest.py`).

## 1. Independent author (nothing may be written, repaired or simulated by the project's AI assistants or owner)
Needs a human who: did not take part in E1-E5; is not the project owner; used no AI assistance; has not seen the detector or defense code; has not seen any E3 per-family result. Deliverable: one JSON file in the `e6-authoring-1` schema (`authoring_schema_v1.json`), 30 families x 10 instances, 15 `retrieve_document` + 15 `get_weather`, no marker, `synthetic` absent or false, and an `author` block with their real id, role, `attestation_utc` and the six flags set to true by them with a statement in their own words. Rules and the H4 `inert` instruction (the neutral twin carries `{MARKER}` and every `required_args` value once, as inert data): `AUTHORING_GUIDE.md`. They can self-check with `python scripts/e6_render.py PACK.json --h4-policy inert`.

## 2. Owner: public ref for the sanitized harness
Stage with `python scripts/e6_stage_harness.py --out DIR --git` (templates excluded, no scan findings), review the tree, then publish it yourself to a public branch or tag and give the full commit SHA and ref name. Nothing here publishes anything.

## 3. Owner: approval record
Copy `APPROVAL_FORM_TEMPLATE.json` to `APPROVAL_RECORD.json` and fill it yourself (status `APPROVED`, approver, protocol hash, harness ref, `budget_authorization.usd_soft_cap` and `http_hard_cap`). The launcher's live path reads only `APPROVAL_RECORD.json`.

## 4. Then (existing tooling only)
`e6_render.py PACK --h4-policy inert --out RENDERED` -> `e6_launcher.py selfcheck --out SC` and `replay --rendered RENDERED --out REPLAY` (in the staged tree) -> E6 tests -> `e6_manifest.py --authoring PACK --rendered RENDERED --selfcheck SC --replay REPLAY --harness-commit SHA --harness-public-ref REF`; live only on `FREEZE: ALLOWED`.
