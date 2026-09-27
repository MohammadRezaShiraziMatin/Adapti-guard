#!/usr/bin/env python3
"""Phase 7 live authorization gate — validates contract only; does not execute APIs."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTH_PATH = ROOT / "docs/research/live_budget_authorization.yaml"
WIRING_PATH = ROOT / "docs/research/PHASE7_LIVE_EXTENSION_WIRING.yaml"
GATE_DOC = ROOT / "docs/research/LIVE_EVALUATION_GATE.md"

PENDING_RE = re.compile(r"^PENDING", re.I)
VALID_APPROVAL = frozenset(
    {"DESIGN_ONLY", "AUTHORIZATION_PENDING", "LIVE_AUTHORIZED", "LIVE_EXECUTION"}
)


def _load_auth() -> dict:
    import yaml

    if not AUTH_PATH.is_file():
        return {}
    return yaml.safe_load(AUTH_PATH.read_text()) or {}


def _has_pending(val) -> bool:
    if val is None:
        return True
    if isinstance(val, str):
        s = val.strip()
        if s.startswith("DEPRECATED"):
            return True
        return bool(PENDING_RE.match(s)) or s == ""
    if isinstance(val, (list, tuple)):
        return len(val) == 0 or any(_has_pending(x) for x in val)
    if isinstance(val, dict):
        return any(_has_pending(v) for v in val.values())
    return False


def _contract_schema_complete(auth: dict) -> tuple[bool, list[str]]:
    """Fields exist for Phase 7 (values may still be PENDING)."""
    missing = []
    for key in (
        "status",
        "api_spend_permitted",
        "allowed_condition_ids",
        "budget_ceiling",
        "max_requests",
        "provider",
        "target_models",
        "judge_model",
        "n_episodes",
        "seeds",
        "repetitions",
        "timeout_seconds",
        "retry_policy",
        "stopping_policy",
        "execution_window",
        "explicit_authorization_for_live_execution",
        "api_live_execution_confirmed",
        "live_ready",
        "output_directory",
    ):
        if key not in auth:
            missing.append(f"missing schema field: {key}")
    targets = auth.get("target_models") or []
    if len(targets) < 4:
        missing.append("target_models must list 4 EAAI targets")
    judge = auth.get("judge_model") or {}
    if "api_model_identifier" not in judge:
        missing.append("judge_model.api_model_identifier missing")
    for t in targets:
        if t.get("lifecycle") == "LIVE_EVALUATED":
            missing.append(f"forbidden LIVE_EVALUATED on {t.get('contract_id')}")
    if WIRING_PATH.is_file():
        import yaml

        w = yaml.safe_load(WIRING_PATH.read_text())
        for cid in (
            "COND-E1-STATEFUL-OFFLINE",
            "COND-E2-ADAPTIVE-OFFLINE",
            "COND-E3-AGENT-OFFLINE",
            "COND-EXT6-BASELINE",
            "COND-PHASE7-CAMPAIGN",
        ):
            if cid not in (w.get("conditions") or {}):
                missing.append(f"wiring missing {cid}")
    return (not missing, missing)


def evaluate() -> dict:
    errors = []
    auth_errors = []
    if not GATE_DOC.is_file():
        errors.append("missing LIVE_EVALUATION_GATE.md")

    auth = _load_auth()
    schema_ok, schema_issues = _contract_schema_complete(auth)
    if not schema_ok:
        errors.extend(schema_issues)

    if not auth:
        return {
            "phase7_live_authorization": "DESIGN_ONLY",
            "live_execution_gate": "PHASE7_LIVE_BLOCKED",
            "authorization_state": "DESIGN_ONLY",
            "contract_schema_complete": False,
            "authorization_complete": False,
            "errors": errors or ["missing live_budget_authorization.yaml"],
            "api_spend_permitted": False,
        }

    status = str(auth.get("approval_status", auth.get("status", "DESIGN_ONLY")))
    if status not in VALID_APPROVAL:
        errors.append(f"invalid approval_status: {status}")

    if auth.get("api_spend_permitted") is True and status != "LIVE_AUTHORIZED":
        errors.append("api_spend_permitted true without LIVE_AUTHORIZED")

    if _has_pending(auth.get("authorization_id")):
        auth_errors.append("authorization_id pending")
    if _has_pending(auth.get("provider")):
        auth_errors.append("provider pending")
    for field in (
        "budget_ceiling",
        "currency",
        "max_requests",
        "n_episodes",
        "seeds",
        "repetitions",
        "timeout_seconds",
        "retry_policy",
        "stopping_policy",
    ):
        if field in auth and _has_pending(auth.get(field)):
            auth_errors.append(f"{field} pending")

    window = auth.get("execution_window") or {}
    if _has_pending(window.get("start_utc")) or _has_pending(window.get("end_utc")):
        auth_errors.append("execution_window pending")

    if not auth.get("allowed_condition_ids"):
        auth_errors.append("allowed_condition_ids empty")

    if not auth.get("explicit_authorization_for_live_execution"):
        auth_errors.append("explicit_authorization_for_live_execution not true")
    if not auth.get("api_live_execution_confirmed"):
        auth_errors.append("api_live_execution_confirmed not true (API=0 default)")

    approver = auth.get("approver") or {}
    if _has_pending(approver.get("name")) or _has_pending(approver.get("approval_timestamp_utc")):
        auth_errors.append("approver sign-off pending")

    judge_id = (auth.get("judge_model") or {}).get("api_model_identifier")
    for t in auth.get("target_models") or []:
        tid = t.get("api_model_identifier")
        if not _has_pending(tid) and not _has_pending(judge_id) and tid == judge_id:
            auth_errors.append("target api_model_identifier equals judge")

    auth_state = "AUTHORIZATION_PENDING"
    if status == "DESIGN_ONLY":
        auth_state = "DESIGN_ONLY"
    elif status == "LIVE_AUTHORIZED" and not auth_errors:
        auth_state = "AUTHORIZED"
    elif status == "LIVE_EXECUTION":
        auth_errors.append("LIVE_EXECUTION is runtime-only")

    live_gate = "PHASE7_LIVE_BLOCKED"
    api_ok = False
    if auth_state == "AUTHORIZED" and not errors:
        live_gate = "LIVE_AUTHORIZED"
        api_ok = True

    all_errors = errors + auth_errors
    return {
        "phase7_live_authorization": status,
        "live_execution_gate": live_gate,
        "authorization_state": auth_state,
        "contract_schema_complete": schema_ok,
        "authorization_complete": auth_state == "AUTHORIZED",
        "errors": all_errors,
        "api_spend_permitted": api_ok,
    }


def main() -> int:
    out = evaluate()
    (ROOT / "docs/research/PHASE7_LIVE_AUTHORIZATION.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return 0 if out["live_execution_gate"] == "LIVE_AUTHORIZED" else 1


if __name__ == "__main__":
    sys.exit(main())
