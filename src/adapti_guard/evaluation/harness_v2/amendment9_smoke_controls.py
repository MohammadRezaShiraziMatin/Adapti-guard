"""Amendment 9 llama smoke caps and /auth/key preflight band (PROPOSED-FINAL)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

SMOKE_USD_CAP = 0.01
SMOKE_HTTP_CAP = 80
AUTH_LIMIT_REMAINING_BASELINE = 0.8123
AUTH_USAGE_BASELINE = 1.6877
AUTH_BAND_FRACTION = 0.05


def _in_band(value: float, baseline: float) -> bool:
    lo = baseline * (1.0 - AUTH_BAND_FRACTION)
    hi = baseline * (1.0 + AUTH_BAND_FRACTION)
    return lo <= value <= hi


def auth_key_metrics(payload: dict[str, Any]) -> tuple[float | None, float | None]:
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    if not isinstance(data, dict):
        return None, None
    lr = data.get("limit_remaining")
    usage = data.get("usage")
    return (float(lr) if lr is not None else None, float(usage) if usage is not None else None)


def auth_key_within_smoke_preflight_band(payload: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    lr, usage = auth_key_metrics(payload)
    detail: dict[str, Any] = {
        "limit_remaining": lr,
        "usage": usage,
        "limit_remaining_baseline": AUTH_LIMIT_REMAINING_BASELINE,
        "usage_baseline": AUTH_USAGE_BASELINE,
        "band_fraction": AUTH_BAND_FRACTION,
    }
    if lr is None or usage is None:
        detail["abort_reason"] = "missing_limit_remaining_or_usage"
        return False, detail
    lr_ok = _in_band(lr, AUTH_LIMIT_REMAINING_BASELINE)
    usage_ok = _in_band(usage, AUTH_USAGE_BASELINE)
    detail["limit_remaining_in_band"] = lr_ok
    detail["usage_in_band"] = usage_ok
    if not lr_ok or not usage_ok:
        detail["abort_reason"] = "outside_preflight_band"
        return False, detail
    return True, detail


async def fetch_auth_key_json(*, base_url: str, api_key: str) -> dict[str, Any]:
    root = base_url.rstrip("/")
    if root.endswith("/v1"):
        url = f"{root}/auth/key"
    else:
        url = f"{root}/v1/auth/key"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, headers={"Authorization": f"Bearer {api_key}"})
        resp.raise_for_status()
        return resp.json()


async def run_amendment9_smoke_auth_preflight(
    out_dir: Path,
    *,
    base_url: str,
    api_key: str,
) -> tuple[bool, dict[str, Any]]:
    """Fetch /auth/key, persist raw JSON, return (proceed, record)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    try:
        payload = await fetch_auth_key_json(base_url=base_url, api_key=api_key)
        http_status = 200
    except httpx.HTTPError as exc:
        payload = {"error": str(exc)}
        http_status = 0
    ok, band_detail = auth_key_within_smoke_preflight_band(payload if http_status == 200 else {})
    record: dict[str, Any] = {
        "preflight_at_utc": ts,
        "http_status": http_status,
        "response": payload,
        **band_detail,
        "proceed": ok and http_status == 200,
    }
    if http_status != 200:
        record["abort_reason"] = "auth_key_http_error"
    path = out_dir / "preflight_auth_key_launch.json"
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    if http_status != 200:
        return False, record
    return ok, record


def preflight_smoke_plan(*, http_cap: int, usd_cap: float) -> dict[str, Any]:
    if http_cap != SMOKE_HTTP_CAP:
        raise RuntimeError(f"smoke preflight: http_cap must be {SMOKE_HTTP_CAP}, got {http_cap}")
    if abs(usd_cap - SMOKE_USD_CAP) > 1e-12:
        raise RuntimeError(f"smoke preflight: usd_cap must be {SMOKE_USD_CAP}, got {usd_cap}")
    return {
        "amendment9_llama_smoke": True,
        "episodes_total": 20,
        "http_cap": http_cap,
        "usd_cap": usd_cap,
    }
