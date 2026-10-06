"""Budget / request gate for live eval (fail-closed USD cap; panel-priced OpenRouter)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from adapti_guard.evaluation.target_model import GenerationRequest, GenerationResult, TargetModel

if TYPE_CHECKING:
    from adapti_guard.evaluation.openrouter_panel_pricing import OpenRouterPricingTable

# Phase 7 pilot hard ceiling (configuration may set ledger.max_usd to this value).
PILOT_HARD_CAP_USD = 1.0


def estimate_request_cost_usd(
    request: GenerationRequest,
    *,
    provider: str = "openrouter",
    default_max_tokens: int = 512,
    pricing: OpenRouterPricingTable | None = None,
    model_id: str | None = None,
) -> float | None:
    """Pre-call reservation. OpenRouter requires panel pricing (no generic rates)."""
    if provider == "openrouter":
        if pricing is None or not model_id:
            return None
        try:
            return pricing.reservation_for_request(request, model_id)
        except Exception:
            return None
    return None


def cost_from_generation_result(
    result: GenerationResult,
    request: GenerationRequest,
    *,
    provider: str,
    default_max_tokens: int = 512,
    pricing: OpenRouterPricingTable | None = None,
    model_id: str | None = None,
) -> float | None:
    if provider == "openrouter":
        if pricing is None or not model_id:
            return None
        from adapti_guard.evaluation.openrouter_panel_pricing import charge_usd_for_result

        try:
            return charge_usd_for_result(result, request, model_id=model_id, pricing=pricing)
        except Exception:
            return None
    return None


@dataclass
class BudgetLedger:
    max_requests: int | None = None
    max_usd: float | None = None
    requests_used: int = 0
    spent_usd: float = 0.0
    estimated_cost_usd: float | None = None  # legacy mirror of spent_usd when known
    hard_stop: bool = True

    def check_allowed(self, *, additional_requests: int = 1) -> tuple[bool, str]:
        if self.max_requests is not None:
            if self.requests_used + additional_requests > self.max_requests:
                return False, "budget_failure: max_requests exceeded"
        if self.max_usd is not None:
            if self.spent_usd > self.max_usd:
                return False, "budget_failure: max_usd exceeded"
        return True, "ok"

    def check_spend_allowed(self, additional_usd: float | None) -> tuple[bool, str]:
        """Cumulative USD gate. UNKNOWN additional_usd blocks when max_usd is set."""
        if self.max_usd is None:
            return True, "ok"
        if additional_usd is None:
            return False, "budget_failure: cost UNKNOWN blocked under max_usd"
        if additional_usd < 0:
            return False, "budget_failure: invalid negative cost estimate"
        if self.spent_usd + additional_usd > self.max_usd:
            return False, "budget_failure: max_usd exceeded"
        return True, "ok"

    def record_requests(self, count: int, *, retry_count: int = 0) -> None:
        total = max(0, count) + max(0, retry_count)
        self.requests_used += total

    def record_spend_usd(self, amount: float) -> None:
        if amount < 0:
            amount = 0.0
        self.spent_usd += amount
        self.estimated_cost_usd = self.spent_usd

    def record_cost_unknown(self) -> None:
        self.estimated_cost_usd = None

    def to_dict(self) -> dict:
        return {
            "max_requests": self.max_requests,
            "max_usd": self.max_usd,
            "requests_used": self.requests_used,
            "spent_usd": self.spent_usd,
            "estimated_cost": self.spent_usd if self.max_usd is not None else (
                self.estimated_cost_usd if self.estimated_cost_usd is not None else "UNKNOWN"
            ),
            "hard_stop": self.hard_stop,
        }


class BudgetGatedTargetModel(TargetModel):
    """Wrap TargetModel: request + USD accounting before provider call (fail closed)."""

    def __init__(
        self,
        inner: TargetModel,
        ledger: BudgetLedger,
        *,
        provider: str = "unknown",
        default_max_tokens: int = 512,
        pricing: OpenRouterPricingTable | None = None,
    ) -> None:
        self._inner = inner
        self._ledger = ledger
        self.provider = provider
        self._default_max_tokens = default_max_tokens
        self._pricing = pricing

    def generate(self, request: GenerationRequest) -> GenerationResult:
        model_id = request.model_id or getattr(self._inner, "model_id", "")
        max_attempts = int(getattr(self._inner, "max_retries", 0)) + 1
        allowed, reason = self._ledger.check_allowed(additional_requests=max_attempts)
        if not allowed and self._ledger.hard_stop:
            return self._budget_error(request, reason)

        per_attempt = estimate_request_cost_usd(
            request,
            provider=self.provider,
            default_max_tokens=self._default_max_tokens,
            pricing=self._pricing,
            model_id=model_id,
        )
        if self._ledger.max_usd is not None:
            worst_case = None if per_attempt is None else per_attempt * max_attempts
            ok, usd_reason = self._ledger.check_spend_allowed(worst_case)
            if not ok and self._ledger.hard_stop:
                return self._budget_error(request, usd_reason)

        result = self._inner.generate(request)
        attempts = 1
        if result.raw and isinstance(result.raw.get("http_attempts"), int):
            attempts = max(1, int(result.raw["http_attempts"]))

        if not result.cache_hit:
            self._ledger.record_requests(1, retry_count=max(0, attempts - 1))
            if self._ledger.max_usd is not None:
                actual = cost_from_generation_result(
                    result,
                    request,
                    provider=self.provider,
                    default_max_tokens=self._default_max_tokens,
                    pricing=self._pricing,
                    model_id=model_id,
                )
                if actual is None:
                    self._ledger.record_cost_unknown()
                else:
                    self._ledger.record_spend_usd(actual)

        return result

    def _budget_error(self, request: GenerationRequest, reason: str) -> GenerationResult:
        return GenerationResult(
            text="",
            model_id=request.model_id or getattr(self._inner, "model_id", ""),
            latency_ms=0.0,
            error=reason,
            raw={"failure_kind": "budget_exhausted", "http_attempts": 0},
        )
