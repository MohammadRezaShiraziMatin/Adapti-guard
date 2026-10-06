"""Conservative USD placeholder for client-cancelled HTTP (Amendment 8 §2.5.2)."""
from __future__ import annotations

from adapti_guard.evaluation.openrouter_panel_pricing import OpenRouterPricingTable


def cancelled_timeout_placeholder_usd(
    *,
    model_id: str,
    prompt_tokens: int,
    max_tokens: int,
    pricing: OpenRouterPricingTable,
) -> float:
    """``prompt_tokens × input_price + max_tokens × output_price`` (hard-cap reserve)."""
    return pricing.cost_from_tokens(model_id, int(prompt_tokens), int(max_tokens))
