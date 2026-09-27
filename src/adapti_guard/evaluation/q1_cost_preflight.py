"""Model-aware Q1 phase cost preflight (dry-run; no provider I/O)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from adapti_guard.evaluation.b2_adaptive_contract import LIVE_WIRING_MAX_TURNS
from adapti_guard.evaluation.openrouter_panel_pricing import (
    ModelPrice,
    OpenRouterPricingError,
    prices_from_panel_dict,
)

DEFAULT_PANEL_PATH = Path("configs/models_q1_eval_panel.yaml")
DEFAULT_DATASET_PATH = Path("datasets/frozen/vnext_confirm_v1/dataset.jsonl")
SYSTEM_PROMPT_TOKENS = 50
JUDGE_EXTRA_INPUT_TOKENS = 64
RETRY_BUFFER_MULTIPLIER = 1.05


class Q1CostPreflightError(Exception):
    pass


def _load_panel(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def panel_model_prices(panel: dict[str, Any]) -> dict[str, ModelPrice]:
    try:
        return prices_from_panel_dict(panel)
    except OpenRouterPricingError as exc:
        raise Q1CostPreflightError(str(exc)) from exc


def _token_estimate_chars(text: str) -> int:
    return max(1, len(text) // 4)


def _load_dataset_rows(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    attacks: list[dict[str, Any]] = []
    benign: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("label") == "attack":
            attacks.append(row)
        elif row.get("label") == "benign":
            benign.append(row)
    return attacks, benign


def _attack_prompt_tokens(row: dict[str, Any]) -> int:
    return _token_estimate_chars(f"{row.get('prompt', '')}\n{row.get('context', '')}".strip())


def _multiturn_target_worst_usd(
    price: ModelPrice,
    *,
    base_prompt_tokens: int,
    max_turns: int,
    max_completion_tokens: int,
) -> float:
    total = 0.0
    context_tokens = SYSTEM_PROMPT_TOKENS + base_prompt_tokens
    for _ in range(max_turns):
        total += context_tokens * price.prompt_usd_per_token
        total += max_completion_tokens * price.completion_usd_per_token
        context_tokens += max_completion_tokens
    return total


def _single_turn_target_worst_usd(
    price: ModelPrice,
    *,
    base_prompt_tokens: int,
    max_completion_tokens: int,
) -> float:
    context_tokens = SYSTEM_PROMPT_TOKENS + base_prompt_tokens
    return (
        context_tokens * price.prompt_usd_per_token
        + max_completion_tokens * price.completion_usd_per_token
    )


def _judge_call_worst_usd(
    price: ModelPrice,
    *,
    episode_prompt_tokens: int,
    max_completion_tokens: int,
) -> float:
    prompt_tokens = SYSTEM_PROMPT_TOKENS + episode_prompt_tokens + JUDGE_EXTRA_INPUT_TOKENS + max_completion_tokens
    return prompt_tokens * price.prompt_usd_per_token + max_completion_tokens * price.completion_usd_per_token


def estimate_q1_phase_preflight(
    contract: dict[str, Any],
    *,
    panel_path: Path = DEFAULT_PANEL_PATH,
    dataset_path: Path = DEFAULT_DATASET_PATH,
    repo_root: Path = Path("."),
) -> dict[str, Any]:
    panel = _load_panel(repo_root / panel_path)
    prices = panel_model_prices(panel)
    attacks, benign = _load_dataset_rows(repo_root / dataset_path)
    if len(attacks) != 61 or len(benign) != 61:
        raise Q1CostPreflightError("dataset must have 61 attack + 61 benign rows")

    sheet = contract.get("q1_decision_sheet_v2") or {}
    cap = float(sheet.get("budget_planning", {}).get("hard_cap_usd_per_phase", 2.0))
    j1_id = str((sheet.get("judges") or {}).get("J1_primary_all_confirmatory", {}).get("openrouter_model_id", ""))
    j2_id = str((sheet.get("judges") or {}).get("J2_subset_only", {}).get("openrouter_model_id", ""))
    if j1_id not in prices or j2_id not in prices:
        raise Q1CostPreflightError("J1/J2 judge models missing pinned openrouter_pricing")

    open_targets = list((sheet.get("primary_holm_family") or {}).get("open_target_model_ids") or [])
    for tid in open_targets:
        if tid not in prices:
            raise Q1CostPreflightError(f"open target missing pricing: {tid}")

    attack_toks = [_attack_prompt_tokens(r) for r in attacks]
    benign_toks = [_attack_prompt_tokens(r) for r in benign]
    mean_attack_tok = sum(attack_toks) / len(attack_toks)
    mean_benign_tok = sum(benign_toks) / len(benign_toks)
    max_out = 512
    max_turns = LIVE_WIRING_MAX_TURNS

    exec_block = contract.get("q1_execution") or {}
    attacker_llm = exec_block.get("adaptive_attacker_llm_calls", 0)
    if attacker_llm not in (0, False, None):
        raise Q1CostPreflightError("adaptive attacker LLM pricing not implemented")

    rows: list[dict[str, Any]] = []
    all_required_ok = True

    for ph in exec_block.get("phases") or []:
        if ph.get("optional_for_p0_freeze") is True:
            continue
        pid = str(ph.get("id", ""))
        mode = str(ph.get("mode", ""))
        target_usd = 0.0
        j1_usd = 0.0
        j2_usd = 0.0
        attacker_usd = 0.0

        if mode == "b2_adaptive":
            eps_per_target = int(ph.get("episodes_per_open_target", 122))
            for tid in open_targets:
                p = prices[tid]
                per_ep = _multiturn_target_worst_usd(
                    p, base_prompt_tokens=int(mean_attack_tok), max_turns=max_turns, max_completion_tokens=max_out
                )
                target_usd += per_ep * eps_per_target
            j1_n = int(ph.get("j1_judge_episodes", 0))
            j2_n = int(ph.get("j2_judge_episodes", 0))
            j1_usd = j1_n * _judge_call_worst_usd(
                prices[j1_id], episode_prompt_tokens=int(mean_attack_tok), max_completion_tokens=max_out
            )
            j2_usd = j2_n * _judge_call_worst_usd(
                prices[j2_id], episode_prompt_tokens=int(mean_attack_tok), max_completion_tokens=max_out
            )
        elif mode == "single_turn_rq2":
            eps_per_target_arm = int(ph.get("attack_episodes_per_open_target_arm", 61))
            for tid in open_targets:
                p = prices[tid]
                per_ep = _single_turn_target_worst_usd(
                    p, base_prompt_tokens=int(mean_attack_tok), max_completion_tokens=max_out
                )
                target_usd += per_ep * eps_per_target_arm * 3  # B0,B1,B3
            benign_per_target = int(ph.get("benign_episodes_per_open_target", 61))
            for tid in open_targets:
                p = prices[tid]
                per_ep = _single_turn_target_worst_usd(
                    p, base_prompt_tokens=int(mean_benign_tok), max_completion_tokens=max_out
                )
                target_usd += per_ep * benign_per_target
            j1_n = int(ph.get("j1_judge_episodes", 0))
            j1_usd = j1_n * _judge_call_worst_usd(
                prices[j1_id],
                episode_prompt_tokens=int((mean_attack_tok + mean_benign_tok) / 2),
                max_completion_tokens=max_out,
            )
        else:
            raise Q1CostPreflightError(f"unknown phase mode: {mode}")

        subtotal = target_usd + j1_usd + j2_usd + attacker_usd
        total = subtotal * RETRY_BUFFER_MULTIPLIER
        within = total <= cap
        all_required_ok = all_required_ok and within
        rows.append(
            {
                "phase_id": pid,
                "target_usd": round(target_usd, 6),
                "j1_usd": round(j1_usd, 6),
                "j2_usd": round(j2_usd, 6),
                "attacker_usd": round(attacker_usd, 6),
                "retry_buffer_multiplier": RETRY_BUFFER_MULTIPLIER,
                "worst_case_usd_estimate": round(total, 6),
                "within_cap": within,
                "cap_usd": cap,
                "adaptive_attacker_llm_calls": 0,
            }
        )

    return {
        "estimator": "model_aware_panel_pricing",
        "all_phases_within_cap": all_required_ok,
        "cap_usd_per_phase": cap,
        "phases": rows,
    }
