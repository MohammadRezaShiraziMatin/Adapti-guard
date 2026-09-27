"""Structured provider failure taxonomy (live eval). No secrets."""
from __future__ import annotations

from enum import Enum
from typing import Any

from adapti_guard.evaluation.target_model import GenerationResult, infer_http_status


class ProviderFailureKind(str, Enum):
    AUTHENTICATION = "authentication"
    INSUFFICIENT_CREDIT = "insufficient_credit"
    ACCESS_PERMISSION = "access_permission"
    MODEL_OR_ENDPOINT = "model_or_endpoint"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    PROVIDER_SERVER_ERROR = "provider_server_error"
    UNKNOWN_ERROR = "unknown_error"


def classify_http_status(status: int | None) -> ProviderFailureKind:
    if status == 401:
        return ProviderFailureKind.AUTHENTICATION
    if status == 402:
        return ProviderFailureKind.INSUFFICIENT_CREDIT
    if status == 403:
        return ProviderFailureKind.ACCESS_PERMISSION
    if status == 404:
        return ProviderFailureKind.MODEL_OR_ENDPOINT
    if status == 408:
        return ProviderFailureKind.TIMEOUT
    if status == 429:
        return ProviderFailureKind.RATE_LIMIT
    if status is not None and status >= 500:
        return ProviderFailureKind.PROVIDER_SERVER_ERROR
    return ProviderFailureKind.UNKNOWN_ERROR


def classify_generation_result(result: GenerationResult) -> dict[str, Any]:
    """Map TargetModel GenerationResult to structured failure (not attack outcome)."""
    if not result.error:
        return {"status": "ok", "failure_kind": None}
    msg = result.error or ""
    status = None
    if result.raw:
        status = result.raw.get("http_status") or result.raw.get("status_code")
    kind = classify_http_status(status if isinstance(status, int) else None)
    if kind == ProviderFailureKind.UNKNOWN_ERROR:
        low = msg.lower()
        if "timeout" in low:
            kind = ProviderFailureKind.TIMEOUT
        elif "rate" in low and "limit" in low:
            kind = ProviderFailureKind.RATE_LIMIT
        elif "auth" in low:
            kind = ProviderFailureKind.AUTHENTICATION
    return {
        "status": "provider_failure",
        "failure_kind": kind.value,
        "error_message": msg[:500],
        "latency_ms": result.latency_ms,
        "model_id": result.model_id,
    }


def classify_exception(exc: BaseException) -> ProviderFailureKind:
    return classify_http_status(infer_http_status(exc))
