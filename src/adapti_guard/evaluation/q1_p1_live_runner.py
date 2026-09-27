"""Q1 P1_rq1_primary_j1_j2 live runner (owner-scoped; shared budget ledger)."""
from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml
from sklearn.metrics import cohen_kappa_score

from adapti_guard.attacker.adaptive_attacker import AdaptiveAttacker, AttackAttempt
from adapti_guard.evaluation.attack_success import EvalEpisode, episode_judge_failed
from adapti_guard.evaluation.b2_adaptive_contract import (
    LIVE_WIRING_MAX_TURNS,
    build_b2_judge_input,
    synthesize_b2_eval_episode,
)
from adapti_guard.evaluation.b2_matrix_contract import (
    build_pre_target_defense_bundle,
    defense_mode_for_condition_id,
)
from adapti_guard.evaluation.live_budget_gate import BudgetGatedTargetModel, BudgetLedger
from adapti_guard.core.models import DefenseAction
from adapti_guard.evaluation.live_extension_wiring import (
    authorization_allows_live_spend,
    load_authorization_yaml,
)
from adapti_guard.evaluation.live_model_resolver import (
    assert_target_ne_judge,
    model_id_for_config_key,

)
from adapti_guard.evaluation.llm_judge import LLMJudge
from adapti_guard.evaluation.q1_cost_preflight import estimate_q1_phase_preflight
from adapti_guard.evaluation.q1_evaluation_contract import (
    contract_sha256,
    load_q1_contract,
    validate_q1_evaluation_contract,
)
from adapti_guard.evaluation.q1_protocol_runner import (
    build_blind_judge_input,
    mcnemar_pair_complete,
    q1_episode_judge_failed,
)
from adapti_guard.evaluation.statistics import holm_correction, mcnemar_exact_p_value
from adapti_guard.evaluation.target_model import build_target_model

PANEL_PATH = Path("configs/models_q1_eval_panel.yaml")
MANIFEST_REL = "configs/q1/manifests/j2_preregistered_subset.jsonl"
EXPECTED_CONTRACT_SHA = "eebe84f3b13f69ca48d57f4f968e3945447766d538603ebea4b57002eb73d0c9"
EXPECTED_MANIFEST_SHA = "1ccf9fe1c632909adc131c7d776749361d13bbcb3ec8e4c0806abfbd887863b0"
PHASE_ID = "P1_rq1_primary_j1_j2"
ARMS = ("A0", "B3")
CONDITION = {"A0": "B2-ADAPTIVE-A0", "B3": "B2-ADAPTIVE-B3"}


class DatasetAnchoredAdaptiveAttacker(AdaptiveAttacker):
    def __init__(self, anchor_prompt: str) -> None:
        super().__init__()
        self._anchor = anchor_prompt
        self._anchor_used = False

    def generate(self) -> AttackAttempt:
        if not self._anchor_used:
            self._anchor_used = True
            self.state.attempts += 1
            return AttackAttempt(
                attack_id=self.state.attempts,
                family="dataset_anchor",
                payload=self._anchor,
                successful=False,
            )
        return super().generate()


@dataclass(frozen=True)
class Q1P1EpisodePlan:
    episode_index: int
    attack_id: str
    target_model_id: str
    target_config_key: str
    defense_arm: str
    condition_id: str
    j2_required: bool


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _load_manifest_pairs(repo_root: Path) -> set[tuple[str, str]]:
    path = repo_root / MANIFEST_REL
    lines = path.read_text(encoding="utf-8").splitlines()
    pairs = set()
    for line in lines[1:]:
        row = json.loads(line)
        pairs.add((row["attack_id"], row["target_model_id"]))
    return pairs


def _load_attacks(repo_root: Path) -> list[dict[str, Any]]:
    contract = load_q1_contract(repo_root / "configs/q1_evaluation_contract.yaml")
    ds_path = repo_root / contract["dataset"]["path"]
    rows = []
    for line in ds_path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("label") == "attack":
            rows.append(row)
    rows.sort(key=lambda r: r["id"])
    return rows


def _target_config_map(contract: dict[str, Any], panel: dict[str, Any]) -> dict[str, str]:
    keys = contract["primary_targets"]["config_keys"]
    out = {}
    for key in keys:
        mid = panel["models"][key]["model"]
        out[str(mid)] = key
    return out


def build_episode_plans(repo_root: Path = Path(".")) -> list[Q1P1EpisodePlan]:
    from adapti_guard.evaluation.q1_p1_episode_schedule import build_round_robin_attack_target_order

    contract = load_q1_contract(repo_root / "configs/q1_evaluation_contract.yaml")
    panel = yaml.safe_load((repo_root / PANEL_PATH).read_text(encoding="utf-8"))
    tmap = _target_config_map(contract, panel)
    targets = list(contract["q1_execution"]["open_target_model_ids"])
    attacks = _load_attacks(repo_root)
    attack_ids = [a["id"] for a in attacks]
    j2_pairs = _load_manifest_pairs(repo_root)
    order = build_round_robin_attack_target_order(targets, attack_ids)
    plans: list[Q1P1EpisodePlan] = []
    idx = 0
    for aid, target in order:
        for arm in ARMS:
            plans.append(
                Q1P1EpisodePlan(
                    episode_index=idx,
                    attack_id=aid,
                    target_model_id=target,
                    target_config_key=tmap[target],
                    defense_arm=arm,
                    condition_id=CONDITION[arm],
                    j2_required=(aid, target) in j2_pairs,
                )
            )
            idx += 1
    return plans


def _episode_pairs(plans: list[Q1P1EpisodePlan]) -> list[tuple[Q1P1EpisodePlan, Q1P1EpisodePlan]]:
    pairs: list[tuple[Q1P1EpisodePlan, Q1P1EpisodePlan]] = []
    for i in range(0, len(plans), 2):
        if i + 1 >= len(plans):
            break
        a, b = plans[i], plans[i + 1]
        if a.defense_arm != "A0" or b.defense_arm != "B3":
            raise ValueError("schedule must alternate A0 then B3 within each attack×target pair")
        if a.attack_id != b.attack_id or a.target_model_id != b.target_model_id:
            raise ValueError("A0/B3 pair mismatch in schedule")
        pairs.append((a, b))
    return pairs


def _pair_reservation_usd(
    pair: tuple[Q1P1EpisodePlan, Q1P1EpisodePlan],
    *,
    pricing: Any,
    attacks_by_id: dict[str, dict[str, Any]],
    panel_path: Path,
    j1_key: str,
    j2_key: str,
) -> float:
    """Conservative dry reservation for one complete A0+B3 pair (3-turn + judges)."""
    from adapti_guard.evaluation.b2_adaptive_contract import LIVE_WIRING_MAX_TURNS
    from adapti_guard.evaluation.openrouter_panel_pricing import ModelPrice
    from adapti_guard.evaluation.q1_cost_preflight import (
        JUDGE_EXTRA_INPUT_TOKENS,
        SYSTEM_PROMPT_TOKENS,
        _attack_prompt_tokens,
        _multiturn_target_worst_usd,
    )

    prices = pricing._prices  # noqa: SLF001 — runner-internal worst-case
    attack_row = attacks_by_id[pair[0].attack_id]
    base_tok = _attack_prompt_tokens(attack_row)
    total = 0.0
    for plan in pair:
        t_price: ModelPrice = prices[plan.target_model_id]
        total += _multiturn_target_worst_usd(
            t_price,
            base_prompt_tokens=base_tok,
            max_turns=LIVE_WIRING_MAX_TURNS,
            max_completion_tokens=512,
        )
        j_price: ModelPrice = prices[model_id_for_config_key(j1_key, panel_path)]
        judge_in = SYSTEM_PROMPT_TOKENS + base_tok + JUDGE_EXTRA_INPUT_TOKENS + 512
        total += judge_in * j_price.prompt_usd_per_token + 128 * j_price.completion_usd_per_token
        if plan.j2_required:
            j2_price: ModelPrice = prices[model_id_for_config_key(j2_key, panel_path)]
            total += judge_in * j2_price.prompt_usd_per_token + 128 * j2_price.completion_usd_per_token
    return total * 1.05


def assert_p1_preconditions(repo_root: Path = Path(".")) -> dict[str, Any]:
    report = validate_q1_evaluation_contract(repo_root=str(repo_root))
    ok_auth, auth_reason = authorization_allows_live_spend()
    if not ok_auth:
        raise RuntimeError(f"authorization blocked: {auth_reason}")
    auth = load_authorization_yaml()
    if auth.get("q1_phase_id") != PHASE_ID:
        raise RuntimeError("authorization q1_phase_id mismatch")
    c_sha = contract_sha256(repo_root / "configs/q1_evaluation_contract.yaml")
    if c_sha != auth.get("contract_sha256"):
        raise RuntimeError("contract_sha256 mismatch vs authorization")
    m_sha = hashlib.sha256((repo_root / MANIFEST_REL).read_bytes()).hexdigest()
    if m_sha != auth.get("manifest_sha256"):
        raise RuntimeError("manifest_sha256 mismatch vs authorization")
    authorized = str(auth.get("code_git_commit", ""))
    head = _git_head()
    if head != authorized:
        try:
            subprocess.check_call(
                ["git", "merge-base", "--is-ancestor", authorized, head],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (OSError, subprocess.CalledProcessError):
            raise RuntimeError("code_git_commit mismatch vs authorization")
    panel = yaml.safe_load((repo_root / PANEL_PATH).read_text(encoding="utf-8"))
    if panel.get("cache", {}).get("enabled") is not False:
        raise RuntimeError("panel cache must be disabled")
    contract = load_q1_contract()
    targets = contract["q1_execution"]["open_target_model_ids"]
    j1 = contract["judges"]["J1_primary"]["config_key"]
    j2 = contract["judges"]["J2_agreement"]["config_key"]
    for tkey in contract["primary_targets"]["config_keys"]:
        tid = panel["models"][tkey]["model"]
        j1_id = panel["models"][j1]["model"]
        j2_id = panel["models"][j2]["model"]
        assert_target_ne_judge(tid, j1_id, pending_ok=False)
        assert_target_ne_judge(tid, j2_id, pending_ok=False)
    j2_pairs = _load_manifest_pairs(repo_root)
    if len(j2_pairs) != 49:
        raise RuntimeError("manifest must contain 49 pairs")
    preflight = estimate_q1_phase_preflight(contract, panel_path=PANEL_PATH, repo_root=repo_root)
    return {
        "validator": report,
        "preflight": preflight,
        "manifest_pair_count": len(j2_pairs),
        "planned_episodes": len(build_episode_plans(repo_root)),
    }


def _build_judge(
    config_key: str,
    ledger: BudgetLedger,
    *,
    panel_path: Path,
    pricing: Any,
) -> LLMJudge:
    inner = build_target_model(config_key, config_path=str(panel_path), cache_enabled=False)
    inner.max_retries = 1
    gated = BudgetGatedTargetModel(inner, ledger, provider="openrouter", pricing=pricing)
    judge = LLMJudge(
        config_key=config_key,
        fallback_config_key=config_key,
        config_path=str(panel_path),
        use_fallback=False,
        cache_enabled=False,
    )
    judge._primary = gated
    judge._fallback = gated
    return judge


def _text_excerpt(text: str, *, limit: int = 512) -> str:
    cleaned = (text or "").replace("\r\n", "\n")
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3] + "..."


def _defense_outcome_snapshot(bundle: Any) -> dict[str, Any] | None:
    state = getattr(bundle, "state", None)
    if state is None:
        return None
    inner = getattr(state, "adaptive_state", state)
    outcome = getattr(inner, "_last_outcome", None)
    return dict(outcome) if isinstance(outcome, dict) else None


def fetch_openrouter_key_snapshot() -> dict[str, Any]:
    """OpenRouter auth/key (usage/limit); no secrets in returned dict."""
    import os
    import urllib.error
    import urllib.request

    from adapti_guard.experiments.env_loader import load_project_env

    load_project_env()
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        return {"error": "OPENROUTER_API_KEY not set"}
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/auth/key",
        headers={"Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        return {"error": f"HTTP {exc.code}", "body": exc.read().decode()[:500]}
    data = body.get("data") if isinstance(body.get("data"), dict) else body
    return {
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "limit": data.get("limit"),
        "usage": data.get("usage"),
        "label": data.get("label"),
        "is_free_tier": data.get("is_free_tier"),
    }


def run_q1_p1_live(
    output_root: Path,
    *,
    repo_root: Path = Path("."),
    openrouter_before: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root)
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    pre = assert_p1_preconditions(repo_root)
    auth = load_authorization_yaml()
    ledger = BudgetLedger(hard_stop=True, max_usd=float(auth.get("budget_ceiling", 2.0)))
    panel_path = repo_root / PANEL_PATH
    from adapti_guard.evaluation.openrouter_panel_pricing import load_openrouter_pricing_table
    from adapti_guard.evaluation.q1_p1_episode_schedule import pair_boundary_stop_ok

    pricing = load_openrouter_pricing_table(panel_path)

    j1_key = load_q1_contract()["judges"]["J1_primary"]["config_key"]
    j2_key = load_q1_contract()["judges"]["J2_agreement"]["config_key"]
    j1_judge = _build_judge(j1_key, ledger, panel_path=panel_path, pricing=pricing)
    j2_judge = _build_judge(j2_key, ledger, panel_path=panel_path, pricing=pricing)

    episodes_path = output_root / "episodes.jsonl"
    ledger_path = output_root / "budget_ledger.json"
    plans = build_episode_plans(repo_root)
    pairs = _episode_pairs(plans)
    attacks_by_id = {r["id"]: r for r in _load_attacks(repo_root)}
    (output_root / "episode_order.json").write_text(
        json.dumps(
            [
                {
                    "episode_index": p.episode_index,
                    "attack_id": p.attack_id,
                    "target_model_id": p.target_model_id,
                    "defense_arm": p.defense_arm,
                }
                for p in plans
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    stop_reason = "completed_all_planned"
    rows_written = 0
    judge_fail = 0
    timeout_fail = 0

    def _run_one_plan(plan: Q1P1EpisodePlan, ep_out: Any) -> None:
        nonlocal rows_written, judge_fail, timeout_fail
        attack_row = attacks_by_id[plan.attack_id]
        anchor = f"{attack_row.get('prompt', '')}\n{attack_row.get('context', '')}".strip()
        inner_target = build_target_model(
            plan.target_config_key,
            config_path=str(panel_path),
            cache_enabled=False,
        )
        inner_target.max_retries = 1
        target_model = BudgetGatedTargetModel(
            inner_target, ledger, provider="openrouter", pricing=pricing
        )
        target_id = model_id_for_config_key(plan.target_config_key, panel_path)

        defense_mode = defense_mode_for_condition_id(plan.condition_id)
        bundle = build_pre_target_defense_bundle(defense_mode)  # type: ignore[arg-type]
        if defense_mode == "B3" and bundle.state is not None and hasattr(bundle.state, "reset"):
            bundle.state.reset()

        from adapti_guard.evaluation.stateful_target_adapter import target_fn_from_model

        attacker = DatasetAnchoredAdaptiveAttacker(anchor)
        from adapti_guard.evaluation.adaptive_episode import AdaptiveEpisodeRunner

        def _legacy_defense(**_kwargs: Any) -> tuple[DefenseAction, dict[str, Any]]:
            return DefenseAction.TOOL_RESTRICTION, {}

        episode_result = AdaptiveEpisodeRunner(max_turns=LIVE_WIRING_MAX_TURNS).run(
            attacker=attacker,
            defense=_legacy_defense,
            seed=42,
            target=target_fn_from_model(target_model, model_id=target_id),
            baseline_defense_fn=bundle.defense_fn,
        )

        judge_input = build_b2_judge_input(
            turns=episode_result.turns,
            success_condition=str(attack_row.get("success_condition", "")),
            is_benign=False,
            primary_user_prompt=anchor,
        )
        blind = build_blind_judge_input(
            user_prompt=judge_input.user_prompt,
            model_response=judge_input.model_response,
            task_context=judge_input.task_context,
            success_condition=judge_input.success_condition,
            is_benign=False,
        )

        j1_verdict = None
        if any(t.target_called for t in episode_result.turns):
            j1_verdict = j1_judge.judge(blind)
        eval_ep = synthesize_b2_eval_episode(
            episode_result,
            episode_id=plan.attack_id,
            category=str(attack_row.get("category", "")),
            label="attack",
            success_condition=str(attack_row.get("success_condition", "")),
            judge_verdict=j1_verdict,
        )
        j1_success = bool(j1_verdict.attack_success) if j1_verdict else False

        j2_record = None
        j2_verdict = None
        if plan.j2_required and any(t.target_called for t in episode_result.turns):
            j2_verdict = j2_judge.judge(blind)
            j2_record = j2_verdict.to_dict()

        target_excerpt = ""
        if episode_result.turns:
            executed = [t for t in episode_result.turns if t.target_called]
            if executed:
                target_excerpt = _text_excerpt(executed[-1].model_response)

        record = {
            "phase_id": PHASE_ID,
            "episode_index": plan.episode_index,
            "attack_id": plan.attack_id,
            "target_model_id": plan.target_model_id,
            "target_config_key": plan.target_config_key,
            "defense_arm": plan.defense_arm,
            "condition_id": plan.condition_id,
            "j2_required": plan.j2_required,
            "attack_succeeded_j1": j1_success,
            "blocked": eval_ep.blocked,
            "judge_reason": eval_ep.judge_reason,
            "j1_model": model_id_for_config_key(j1_key, panel_path),
            "j2_model": model_id_for_config_key(j2_key, panel_path) if plan.j2_required else None,
            "j2_attack_success": j2_record.get("attack_success") if j2_record else None,
            "j2_judge_reason": j2_record.get("reason") if j2_record else None,
            "target_response_excerpt": target_excerpt,
            "j1_judge_raw_excerpt": _text_excerpt(j1_verdict.raw_text if j1_verdict else ""),
            "j2_judge_raw_excerpt": _text_excerpt(j2_verdict.raw_text if j2_verdict else ""),
            "pre_target_defense_last": _defense_outcome_snapshot(bundle),
            "ledger_spent_usd_after": ledger.spent_usd,
            "ledger_requests_after": ledger.requests_used,
        }
        if q1_episode_judge_failed(eval_ep):
            judge_fail += 1
        if eval_ep.judge_reason in ("timeout", "judge_timeout", "target_timeout"):
            timeout_fail += 1
        ep_out.write(json.dumps(record, ensure_ascii=False) + "\n")
        ep_out.flush()
        rows_written += 1

    with episodes_path.open("w", encoding="utf-8") as ep_out:
        for pair in pairs:
            reserve = _pair_reservation_usd(
                pair,
                pricing=pricing,
                attacks_by_id=attacks_by_id,
                panel_path=panel_path,
                j1_key=j1_key,
                j2_key=j2_key,
            )
            ok, usd_reason = ledger.check_spend_allowed(reserve)
            if not ok and ledger.hard_stop:
                stop_reason = (
                    f"budget_hard_stop_before_pair_{pair[0].attack_id}_{pair[0].target_model_id}: "
                    f"{usd_reason}; reserve_usd={reserve:.6f}"
                )
                break
            _run_one_plan(pair[0], ep_out)
            _run_one_plan(pair[1], ep_out)
            if not pair_boundary_stop_ok(rows_written):
                stop_reason = f"pair_boundary_violation_after_episode_{rows_written - 1}"
                break

    ledger_path.write_text(json.dumps(ledger.to_dict(), indent=2), encoding="utf-8")
    p1_pref = next(
        (p for p in pre["preflight"].get("phases", []) if p.get("phase_id") == PHASE_ID),
        {},
    )
    post = _post_run_analysis(
        episodes_path,
        repo_root=repo_root,
        stop_reason=stop_reason,
        planned_episodes=len(plans),
        ledger_spent_usd=ledger.spent_usd,
        preflight_worst_usd=float(p1_pref.get("worst_case_usd_estimate", 0)),
    )
    openrouter_after = fetch_openrouter_key_snapshot()
    usage_before = float((openrouter_before or {}).get("usage") or 0)
    usage_after = float(openrouter_after.get("usage") or 0)
    openrouter_delta = {
        "before": openrouter_before,
        "after": openrouter_after,
        "usage_delta_usd": usage_after - usage_before,
        "ledger_spent_usd": ledger.spent_usd,
    }
    (output_root / "openrouter_usage_delta.json").write_text(
        json.dumps(openrouter_delta, indent=2),
        encoding="utf-8",
    )
    (output_root / "AUDIT.json").write_text(
        json.dumps(
            {
                "verdict": post.get("audit_verdict"),
                "reasons": post.get("audit_reasons"),
                "phase_id": PHASE_ID,
                "episodes_completed": rows_written,
                "episodes_planned": len(plans),
                "stop_reason": stop_reason,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    pack = {
        "phase_id": PHASE_ID,
        "stop_reason": stop_reason,
        "episodes_planned": len(plans),
        "episodes_completed": rows_written,
        "judge_fail_count": judge_fail,
        "timeout_fail_count": timeout_fail,
        "ledger": ledger.to_dict(),
        "preconditions": pre,
        "preflight_estimate": pre["preflight"],
        "post_analysis": post,
        "openrouter_usage_delta": openrouter_delta,
        "authorization": {
            "contract_sha256": auth.get("contract_sha256"),
            "manifest_sha256": auth.get("manifest_sha256"),
            "code_git_commit": auth.get("code_git_commit"),
        },
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (output_root / "run_summary.json").write_text(json.dumps(pack, indent=2), encoding="utf-8")
    (output_root / "preflight_vs_actual.json").write_text(
        json.dumps(
            {
                "preflight": pre["preflight"],
                "actual_spent_usd": ledger.spent_usd,
                "actual_episodes": rows_written,
                "stop_reason": stop_reason,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return pack


def _post_run_analysis(
    episodes_path: Path,
    *,
    repo_root: Path,
    stop_reason: str = "",
    planned_episodes: int = 488,
    ledger_spent_usd: float = 0.0,
    preflight_worst_usd: float = 0.0,
) -> dict[str, Any]:
    rows = [json.loads(line) for line in episodes_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    contract = load_q1_contract()
    targets = list(contract["q1_execution"]["open_target_model_ids"])

    per_target_arm: dict[str, dict[str, dict[str, int]]] = {}
    judge_fail_by_target_arm: dict[str, dict[str, dict[str, int]]] = {}
    incomplete_pairs = 0
    j1_labels = []
    j2_labels = []

    for target in targets:
        per_target_arm[target] = {}
        judge_fail_by_target_arm[target] = {}
        for arm in ARMS:
            arm_rows = [r for r in rows if r["target_model_id"] == target and r["defense_arm"] == arm]
            n = len(arm_rows)
            judgeable = [r for r in arm_rows if not q1_episode_judge_failed(_row_as_eval(r))]
            n_j = len(judgeable)
            succ = sum(1 for r in judgeable if r.get("attack_succeeded_j1"))
            raw_succ = sum(1 for r in arm_rows if r.get("attack_succeeded_j1"))
            per_target_arm[target][arm] = {
                "n": n,
                "n_judgeable": n_j,
                "asr_j1_raw_denominator_n": n,
                "asr_j1": (succ / n_j if n_j else float("nan")),
                "asr_j1_raw_including_judge_fail": (raw_succ / n if n else float("nan")),
            }
            jf = sum(1 for r in arm_rows if q1_episode_judge_failed(_row_as_eval(r)))
            to = sum(
                1
                for r in arm_rows
                if (r.get("judge_reason") or "") in ("timeout", "judge_timeout", "target_timeout")
            )
            judge_fail_by_target_arm[target][arm] = {"judge_fail": jf, "timeout": to, "n": n}

    mcnemar_by_target = {}
    for target in targets:
        a0 = {r["attack_id"]: r for r in rows if r["target_model_id"] == target and r["defense_arm"] == "A0"}
        b3 = {r["attack_id"]: r for r in rows if r["target_model_id"] == target and r["defense_arm"] == "B3"}
        b10 = b01 = 0
        for aid in sorted(set(a0) & set(b3)):
            ra, rb = a0[aid], b3[aid]
            if not mcnemar_pair_complete(
                _row_as_eval(ra),
                _row_as_eval(rb),
            ):
                incomplete_pairs += 1
                continue
            sa = bool(ra.get("attack_succeeded_j1"))
            sb = bool(rb.get("attack_succeeded_j1"))
            if sa and not sb:
                b10 += 1
            elif sb and not sa:
                b01 += 1
        p_val = mcnemar_exact_p_value(b10, b01)
        mcnemar_by_target[target] = {
            "b10": b10,
            "b01": b01,
            "p_value": p_val,
            "method": "mcnemar_exact_two_sided",
        }

    holm_input = [mcnemar_by_target[t]["p_value"] for t in targets]
    holm = holm_correction(holm_input)
    holm_by_target = {t: holm[i] for i, t in enumerate(targets)}

    for r in rows:
        if not r.get("j2_required"):
            continue
        if q1_episode_judge_failed(_row_as_eval(r)):
            continue
        j2_reason = r.get("j2_judge_reason")
        if j2_reason in ("judge_parse_error", "judge_api_error"):
            continue
        j1_labels.append(int(bool(r.get("attack_succeeded_j1"))))
        j2_labels.append(int(bool(r.get("j2_attack_success"))))

    kappa = (
        float(cohen_kappa_score(j1_labels, j2_labels))
        if len(j1_labels) >= 2
        else float("nan")
    )
    agree = sum(x == y for x, y in zip(j1_labels, j2_labels)) / len(j1_labels) if j1_labels else float("nan")

    audit_reasons: list[str] = []
    if not rows:
        audit_reasons.append("no_episodes_recorded")
    if len(rows) < planned_episodes:
        audit_reasons.append(f"episodes_completed={len(rows)}<{planned_episodes}")
    if stop_reason != "completed_all_planned":
        audit_reasons.append(f"stop_reason={stop_reason}")
    if incomplete_pairs:
        audit_reasons.append(f"incomplete_pairs={incomplete_pairs}")
    if ledger_spent_usd > 2.0 + 1e-6:
        audit_reasons.append(f"ledger_spent_usd={ledger_spent_usd}>2.0")
    if preflight_worst_usd > 2.0 + 1e-6:
        audit_reasons.append(f"preflight_worst_usd={preflight_worst_usd}>2.0")
    audit_verdict = "VALID" if not audit_reasons else "INVALID"

    return {
        "per_target_asr_j1": per_target_arm,
        "judge_fail_timeout_by_target_arm": judge_fail_by_target_arm,
        "mcnemar_exact_two_sided_by_target": mcnemar_by_target,
        "holm_adjusted_p_primary_m4": holm,
        "holm_adjusted_p_by_target": holm_by_target,
        "j1_j2_cohen_kappa_on_j2_subset": kappa,
        "j1_j2_agreement_rate_on_j2_subset": agree,
        "j2_subset_episodes_analyzed": len(j1_labels),
        "j2_subset_episodes_j2_required_total": sum(1 for r in rows if r.get("j2_required")),
        "incomplete_pairs_excluded_from_mcnemar": incomplete_pairs,
        "audit_verdict": audit_verdict,
        "audit_reasons": audit_reasons,
    }


def _row_as_eval(row: dict[str, Any]) -> EvalEpisode:
    reason = row.get("judge_reason") or "ok"
    failed = reason in ("judge_api_error", "judge_parse_error", "timeout", "judge_timeout")
    return EvalEpisode(
        id=row["attack_id"],
        prompt="",
        context="",
        category="attack",
        label="attack",
        defense_action=row["defense_arm"],
        blocked=bool(row.get("blocked")),
        model_response="",
        attack_succeeded=bool(row.get("attack_succeeded_j1")),
        utility_success=False,
        judge_reason=reason if not failed else "judge_api_error",
        metadata={"timeout": reason == "timeout"},
    )
