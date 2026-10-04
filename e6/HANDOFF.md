# E6 handoff: the three inputs only people can supply

State: engineering complete, `python scripts/e6_manifest.py` prints `FREEZE: BLOCKED` until all three below exist. Nothing in this repository creates, fills or infers any of them.

## 1. Independent pack (human author)
- **Who:** a human who did not take part in E1-E5, is not the project owner, used no AI assistance, has not seen the detector or defense code, and has not seen any E3 per-family result.
- **What:** one JSON file, schema `e6-authoring-1` (`authoring_schema_v1.json`): 30 families x 10 instances = 300 attack instances, 15 `retrieve_document` + 15 `get_weather`, H4 = `inert`, six-flag attestation filled by the author.
- **How:** give them `e6/AUTHORING_GUIDE.md`, `e6/authoring_schema_v1.json`, `e6/authoring_template_v1.json` and this repository's `scripts/e6_render.py` (for self-checking only). They must not be given any E3 result, detector or defense code.
- **Accept only if:** `python scripts/e6_render.py PACK.json --h4-policy inert` reports `structure_ok` and `freeze_eligible` true. The project's AI assistants and the owner must not edit the file; a rejected pack goes back to the author.
- **Then record:** edit `e6/INPUTS_STATUS.json` yourself: `INDEPENDENT_AUTHOR` = the author's id and `FRESH_PACK` = the pack's SHA-256 (`e6_render.py` prints `authoring_sha256`). Commit the pack file as `e6/authoring_pack_v1.json`.

## 2. Public ref for the sanitized harness (owner publishes; nothing here pushes)
```bash
# in a clean checkout of this repository
python scripts/e6_stage_harness.py --out ../adapti-guard-e6-harness --git --strict   # must print "findings": []
cd ../adapti-guard-e6-harness
python -m pytest tests -q                       # expected at staging time: 113 passed, 1 skipped (templates and their 21 tests are excluded by decision)
git commit --amend --reset-author -m "E6 sanitized harness"   # replace the placeholder 'e6-stage' identity with yours (the tree hash is unchanged)
git remote add origin <YOUR_PUBLIC_REPOSITORY_URL>
git tag -a e6-harness-v1 -m "E6 sanitized harness"
git push origin HEAD:main e6-harness-v1         # or the branch you choose
git rev-parse HEAD                               # = harness commit SHA (40 hex)
python scripts/e6_launcher.py selfcheck --out SELFCHECK.json   # run INSIDE the published tree
```
You then know: the commit SHA (`git rev-parse HEAD`), the public ref (`e6-harness-v1` or the branch), and `harness_tree_sha256` (in `SANITIZED_MANIFEST.json` and in the selfcheck file). Check the template files and `APPROVAL_RECORD.json` are absent from the tree, and that the repository you publish to is the one you intend (this cannot be undone).

## 3. Approval record (owner)
Copy `e6/APPROVAL_FORM_TEMPLATE.json` to `e6/APPROVAL_RECORD.json` and replace every `NOT_SET` yourself: `status: "APPROVED"`, approver, timestamp, the three frozen hashes, the harness commit, public ref and tree hash, `usd_soft_cap` (number), `http_hard_cap` (integer), who authorized the budget and when. Take the hashes from the manifest output below, not from memory. `scripts/e6_manifest.py` rejects the record if any field is unset or does not match the frozen inputs.

## 4. Freeze and run (existing tooling only)
```bash
python scripts/e6_render.py e6/authoring_pack_v1.json --h4-policy inert --out e6/rendered_scenarios_v1.json
# inside the published harness tree:
python scripts/e6_launcher.py selfcheck --out SELFCHECK.json
python scripts/e6_launcher.py replay --rendered RENDERED.json --out REPLAY.json
python -m pytest tests/test_e6_analysis.py tests/test_e6_prefreeze.py tests/test_e6_end_to_end.py -q
python scripts/e6_manifest.py --authoring e6/authoring_pack_v1.json --rendered e6/rendered_scenarios_v1.json \
   --selfcheck SELFCHECK.json --replay REPLAY.json --harness-commit <SHA> --harness-public-ref <REF> --json
```
Write the approval record from that output, rerun the manifest, and run live only if it prints `FREEZE: ALLOWED`. No rerun for an unfavorable result.
