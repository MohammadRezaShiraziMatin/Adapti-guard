"""Minimal live Fixed vs Adaptive pilot (shared ledger; canonical run_live_condition)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from adapti_guard.evaluation.b2_adaptive_contract import (
    B2_LIVE_JUDGE_CONFIG_KEY,
    B2_LIVE_TARGET_CONFIG_KEY,
)
from adapti_guard.evaluation.b2_attack_mode_contract import (
    B2_LIVE_CONDITION_ADAPTIVE,
    B2_LIVE_CONDITION_FIXED,
)
from adapti_guard.evaluation.b2_campaign_protocol import (
    b2_episode_request_budget_worst,
    campaign_worst_case_requests,
)
from adapti_guard.evaluation.live_extension_wiring import (
    DEFAULT_LIVE_RUN_ROOT,
    budget_ledger_from_authorization,
    load_authorization_yaml,
    run_live_condition,
)


@dataclass
class B2AttackModePilotEpisode:
    condition_id: str
    attack_mode: str
    seed: int
    run_id: str
    run_dir: str
    status: str
    metrics: dict[str, Any] = field(default_factory=dict)
    stop_reason: str | None = None


@dataclass
class B2AttackModePilotResult:
    pilot_id: str
    episodes: list[B2AttackModePilotEpisode]
    requests_used: int
    spent_usd: float
    preflight_ok: bool
    preflight_reason: str
    worst_case_requests: int


def preflight_attack_mode_pilot(auth_yaml: dict[str, Any], n_episodes: int = 2) -> tuple[bool, str, int]:
    max_req = int(auth_yaml.get("max_requests", 10))
    max_usd = float(auth_yaml.get("budget_ceiling", 1.0))
    worst = campaign_worst_case_requests(n_episodes)
    if worst > max_req:
        return False, f"worst_case_requests={worst} > max_requests={max_req}", worst
    per = b2_episode_request_budget_worst()
    from adapti_guard.evaluation.live_b0_report import preflight_worst_case_usd

    ok_usd, worst_usd = preflight_worst_case_usd(
        n_target_calls=n_episodes * 3,
        n_judge_calls=n_episodes,
        max_usd=max_usd,
    )
    if not ok_usd:
        return False, f"worst_case_usd={worst_usd} > max_usd={max_usd}", worst
    return True, "ok", worst


def run_live_b2_attack_mode_pilot(
    *,
    pilot_id: str = "B2-ATTACK-MODE-PILOT-20260924",
    seed: int = 42,
    output_root: Path | str | None = None,
) -> B2AttackModePilotResult:
    auth = load_authorization_yaml()
    pf_ok, pf_reason, worst = preflight_attack_mode_pilot(auth, n_episodes=2)
    if not pf_ok:
        return B2AttackModePilotResult(
            pilot_id=pilot_id,
            episodes=[],
            requests_used=0,
            spent_usd=0.0,
            preflight_ok=False,
            preflight_reason=pf_reason,
            worst_case_requests=worst,
        )

    root = Path(output_root or DEFAULT_LIVE_RUN_ROOT) / pilot_id
    root.mkdir(parents=True, exist_ok=True)
    ledger = budget_ledger_from_authorization(auth)
    episodes: list[B2AttackModePilotEpisode] = []
    sequence = (
        (B2_LIVE_CONDITION_FIXED, "fixed_sequence", f"{pilot_id}-FIXED-S{seed}", 0),
        (B2_LIVE_CONDITION_ADAPTIVE, "adaptive_defense_feedback", f"{pilot_id}-ADAPTIVE-S{seed}", 1),
    )
    for condition_id, mode, run_id, _idx in sequence:
        run_dir = root / run_id
        if run_dir.exists() and any(run_dir.iterdir()):
            episodes.append(
                B2AttackModePilotEpisode(
                    condition_id=condition_id,
                    attack_mode=mode,
                    seed=seed,
                    run_id=run_id,
                    run_dir=str(run_dir),
                    status="failed",
                    stop_reason="artifact_collision: run_dir not empty",
                )
            )
            break
        run_dir.mkdir(parents=True, exist_ok=True)
        try:
            run_live_condition(
                condition_id,
                run_id=run_id,
                run_dir=run_dir,
                seed=seed,
                execution_mode="LIVE",
                target_config_key=B2_LIVE_TARGET_CONFIG_KEY,
                judge_config_key=B2_LIVE_JUDGE_CONFIG_KEY,
                injected_ledger=ledger,
                attack_mode=mode,
            )
        except Exception as exc:  # noqa: BLE001 — pilot surface
            episodes.append(
                B2AttackModePilotEpisode(
                    condition_id=condition_id,
                    attack_mode=mode,
                    seed=seed,
                    run_id=run_id,
                    run_dir=str(run_dir),
                    status="failed",
                    stop_reason=str(exc),
                )
            )
            break
        metrics_path = run_dir / "derived" / "metrics.json"
        metrics = json.loads(metrics_path.read_text()) if metrics_path.is_file() else {}
        episodes.append(
            B2AttackModePilotEpisode(
                condition_id=condition_id,
                attack_mode=mode,
                seed=seed,
                run_id=run_id,
                run_dir=str(run_dir),
                status="ok",
                metrics=metrics,
            )
        )

    aggregate_path = root / "pilot_aggregate.json"
    aggregate_path.write_text(
        json.dumps(
            {
                "pilot_id": pilot_id,
                "seed": seed,
                "episodes": [ep.__dict__ for ep in episodes],
                "requests_used": ledger.requests_used,
                "spent_usd": ledger.spent_usd,
                "worst_case_requests": worst,
            },
            indent=2,
        )
    )
    return B2AttackModePilotResult(
        pilot_id=pilot_id,
        episodes=episodes,
        requests_used=ledger.requests_used,
        spent_usd=ledger.spent_usd,
        preflight_ok=True,
        preflight_reason="ok",
        worst_case_requests=worst,
    )
