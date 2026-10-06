"""Shared pytest fixtures (offline)."""
from __future__ import annotations

import pytest

_LIVE_AUTH_YAML = {
    "schema_version": 2,
    "approval_status": "LIVE_AUTHORIZED",
    "status": "LIVE_AUTHORIZED",
    "api_spend_permitted": True,
    "explicit_authorization_for_live_execution": True,
    "live_ready": True,
    "budget_ceiling": 1.0,
    "max_requests": 10,
    "allowed_condition_ids": [
        "LIVE-PRO-PI-B2-ADAPTIVE",
        "B2-FIXED",
        "B2-ADAPTIVE",
        "B2-FIXED-A0",
        "B2-FIXED-B1",
        "B2-ADAPTIVE-A0",
        "B2-ADAPTIVE-B1",
    ],
}

_LIVE_PHASE7 = {
    "phase7_live_authorization": "LIVE_AUTHORIZED",
    "live_execution_gate": "LIVE_AUTHORIZED",
    "authorization_state": "AUTHORIZED",
    "api_spend_permitted": True,
}


@pytest.fixture(autouse=True)
def _inject_live_auth_for_b2_batch_tests(request, monkeypatch):
    """Batch-runner tests need campaign auth; committed repo YAML stays BLOCKED."""
    mod_file = str(getattr(request.module, "__file__", ""))
    if not mod_file.endswith("test_b2_batch_runner.py"):
        return

    import adapti_guard.evaluation.b2_batch_runner as batch_runner
    import adapti_guard.evaluation.live_extension_wiring as wiring

    _load = lambda _path=None: dict(_LIVE_AUTH_YAML)
    monkeypatch.setattr(wiring, "load_authorization_yaml", _load)
    monkeypatch.setattr(batch_runner, "load_authorization_yaml", _load)
    monkeypatch.setattr(
        wiring,
        "load_phase7_gate_json",
        lambda _path=None: dict(_LIVE_PHASE7),
    )
    monkeypatch.setattr(
        wiring,
        "authorization_allows_live_spend",
        lambda *_a, **_k: (True, "ok"),
    )
