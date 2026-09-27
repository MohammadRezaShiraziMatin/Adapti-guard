#!/usr/bin/env python3
"""B2 campaign preflight (offline; no API)."""
import json
import sys
from pathlib import Path

PILOT_RUN_ID = "LIVE-PRO-PI-B2-EVAL-20260924-182806-8aac6be3"


def _ser(obj):
    if hasattr(obj, "__dict__") and not isinstance(obj, type):
        d = dict(obj.__dict__)
        for key, val in list(d.items()):
            if isinstance(val, tuple) and val and hasattr(val[0], "__dict__"):
                d[key] = [_ser(x) for x in val]
        return d
    return obj


def main() -> int:
    from adapti_guard.evaluation.b2_campaign_protocol import (
        assess_b2_batch_campaign_preflight,
        assess_b2_campaign_preflight,
        authorization_consistency_state,
        build_b2_campaign_batch_plan,
        campaign_scenario_fact_table,
        inspect_authorization_budget_semantics,
    )
    from adapti_guard.evaluation.live_extension_wiring import load_authorization_yaml

    auth = load_authorization_yaml()
    semantics = inspect_authorization_budget_semantics(auth)

    reports = {
        "budget_authorization_semantics": semantics,
        "consistency_state": authorization_consistency_state(auth),
        "scenario_fact_table": campaign_scenario_fact_table(auth),
        "pilot_reference_run_id": PILOT_RUN_ID,
        "pilot_n": 1,
        "campaign_size_tbd": assess_b2_campaign_preflight(
            campaign_id="PREFLIGHT-TBD", campaign_size=None
        ),
        "hypothetical_n2": assess_b2_campaign_preflight(
            campaign_id="PREFLIGHT-N2", campaign_size=2
        ),
        "hypothetical_n3_blocked": assess_b2_campaign_preflight(
            campaign_id="PREFLIGHT-N3", campaign_size=3
        ),
        "batch_campaign_n5": assess_b2_batch_campaign_preflight("PREFLIGHT-BATCH5", total_episodes=5),
        "batch_campaign_plan": build_b2_campaign_batch_plan("PREFLIGHT-BATCH5", total_episodes=5),
    }
    out = {
        "status": "PREFLIGHT_ONLY_NO_API",
        "api_calls": 0,
        "reports": {k: _ser(v) for k, v in reports.items()},
    }
    print(json.dumps(out, indent=2))
    pf = reports["hypothetical_n2"]
    return 0 if pf.max_episodes_under_request_cap >= 2 else 1


if __name__ == "__main__":
    sys.exit(main())
