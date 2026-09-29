# SCENARIO_INSTANCE_TEMPLATES — Amendment 5 diff summary

| | SHA-256 |
|---|---------|
| **Before (pilot 1 `1af54c1`)** | `25a9167486e5c338cac584536ee7368eabb96a251716541b6b79c7fb4911bb59` |
| **After (Amendment 5 rewrite)** | `dd445b19af36b1784cd40964944e7ff60f2cb248f94408efc1fda8281a5fb43a` |

## What changed

- Removed repetitive artifacts: `dock-policy-NNN`, `Policy excerpt N.`, identical Seattle-only weather prompts, truncated markers (`HARNESS-V2-MARK-ool_v1-000` → full `HARNESS-V2-MARK-poisoned_benign_tool_v1-000`).
- **24 instances per scenario** now vary by topic slug, city, injection placement, user wording, and obfuscation style.
- **Poisoned benign:** injection only via `weather_poison_suffix` on `get_weather` tool JSON (tool channel).
- **Benign create_record:** adds `expected_create_kind` for validity checks.
- Generator: `scripts/build_scenario_templates_amendment5.py` (reproducible).

Pilot 1 trajectories remain on the **old** template SHA; pilot 2 uses the new SHA only.
