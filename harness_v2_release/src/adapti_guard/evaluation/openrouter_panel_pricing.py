"""Pinned OpenRouter per-model pricing from Q1 eval panel (fail closed if missing)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from adapti_guard.evaluation.target_model import GenerationRequest, GenerationResult

DEFAULT_PANEL_PATH = Path("configs/models_q1_eval_panel.yaml")


@dataclass(frozen=True)
class ModelPrice:
    prompt_usd_per_token: float
    completion_usd_per_token: float


class OpenRouterPricingError(Exception):
    pass


class OpenRouterPricingTable:
    """model_id (OpenRouter slug) → pinned rates."""

    def __init__(self, prices: dict[str, ModelPrice]) -> None:
        self._prices = dict(prices)

    def price_for_model(self, model_id: str) -> ModelPrice | None:
        return self._prices.get(model_id)

    def require_price(self, model_id: str) -> ModelPrice:
        p = self.price_for_model(model_id)
        if p is None:
            raise OpenRouterPricingError(f"missing openrouter_pricing for model_id={model_id}")
        return p

    def cost_from_tokens(self, model_id: str, prompt_tokens: int, completion_tokens: int) -> float:
        price = self.require_price(model_id)
        return (
            max(0, int(prompt_tokens)) * price.prompt_usd_per_token
            + max(0, int(completion_tokens)) * price.completion_usd_per_token
        )

    def reservation_for_request(self, request: GenerationRequest, model_id: str) -> float:
        """Worst-case pre-call reserve: estimated prompt + max completion at model rates."""
        price = self.require_price(model_id)
        prompt_text = (request.system_prompt or "") + (request.prompt or "")
        if not prompt_text.strip():
            raise OpenRouterPricingError(f"empty prompt for reservation model_id={model_id}")
        prompt_tokens = max(1, len(prompt_text) // 4)
        max_tokens = request.max_tokens or 512
        if max_tokens <= 0:
            raise OpenRouterPricingError(f"invalid max_tokens for model_id={model_id}")
        return prompt_tokens * price.prompt_usd_per_token + int(max_tokens) * price.completion_usd_per_token


def prices_from_panel_dict(panel: dict[str, Any]) -> dict[str, ModelPrice]:
    prices: dict[str, ModelPrice] = {}
    for _key, spec in (panel.get("models") or {}).items():
        model_id = str(spec.get("model", ""))
        if not model_id or model_id.startswith("NEEDS_DECISION"):
            continue
        pricing = spec.get("openrouter_pricing") or {}
        try:
            pin = float(pricing["prompt_usd_per_token"])
            cout = float(pricing["completion_usd_per_token"])
        except (KeyError, TypeError, ValueError):
            raise OpenRouterPricingError(f"missing openrouter_pricing for panel model {model_id}")
        prices[model_id] = ModelPrice(prompt_usd_per_token=pin, completion_usd_per_token=cout)
    return prices


def load_openrouter_pricing_table(path: Path | str = DEFAULT_PANEL_PATH) -> OpenRouterPricingTable:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    prices = prices_from_panel_dict(data)
    if not prices:
        raise OpenRouterPricingError("empty pricing table")
    return OpenRouterPricingTable(prices)


def openrouter_reported_cost_usd(result: GenerationResult) -> float | None:
    """Prefer provider-reported USD when present on the generation result."""
    usage = result.usage or {}
    for key in ("cost", "total_cost", "generation_cost_usd"):
        val = usage.get(key)
        if val is not None:
            try:
                return float(val)
            except (TypeError, ValueError):
                pass
    raw = result.raw or {}
    for key in ("cost", "total_cost", "generation_cost_usd"):
        val = raw.get(key)
        if val is not None:
            try:
                return float(val)
            except (TypeError, ValueError):
                pass
    return None


def charge_usd_for_result(
    result: GenerationResult,
    request: GenerationRequest,
    *,
    model_id: str,
    pricing: OpenRouterPricingTable,
) -> float:
    reported = openrouter_reported_cost_usd(result)
    if reported is not None:
        return max(0.0, float(reported))
    usage = result.usage or {}
    pt = usage.get("prompt_tokens")
    ct = usage.get("completion_tokens")
    if pt is not None and ct is not None:
        return pricing.cost_from_tokens(model_id, int(pt), int(ct))
    return pricing.reservation_for_request(request, model_id)
