"""Q1 evaluation protocol — offline contract validation (no API)."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from adapti_guard.evaluation.b2_adaptive_contract import LIVE_WIRING_MAX_TURNS
from adapti_guard.evaluation.b2_matrix_contract import (
    B2_CONDITION_ADAPTIVE_B1,
    B2_CONDITION_ADAPTIVE_A0,
    B2_CONDITION_ADAPTIVE_B3,
    Q1_PRIMARY_CAUSAL_B2_CONDITIONS,
)
DEFAULT_CONTRACT_PATH = Path("configs/q1_evaluation_contract.yaml")
DEFAULT_PANEL_PATH = Path("configs/models_q1_eval_panel.yaml")
DEFAULT_OWNER_PACK_PATH = Path("docs/Q1_OWNER_DECISION_PACK.md")
VNEXT_DATASET_SHA = "523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518"
VNEXT_MODELS_YAML_SHA = "37174858710a087b3fe58c40e65c796418d1791ff4280bca08d96486b35d7ec3"
EPISODE_BUDGET_FORMULA = "n_attack * n_primary_targets * n_arms"
PRIMARY_PAIRED_COMPARISONS = 244
PRIMARY_CAUSAL_EPISODES = 488
J2_SUBSET_PAIRS = 49
J2_SUBSET_EPISODES = 98


class Q1ContractError(Exception):
    pass


def load_q1_contract(path: str | Path = DEFAULT_CONTRACT_PATH) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def contract_sha256(path: str | Path = DEFAULT_CONTRACT_PATH) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def derived_primary_attack_episodes(contract: dict[str, Any]) -> int:
    ds = contract.get("dataset") or {}
    n_attack = int(ds.get("n_attack", 0))
    prim = contract.get("primary_targets") or {}
    n_targets = len(list(prim.get("config_keys", [])))
    n_arms = len(contract.get("arms") or {})
    return n_attack * n_targets * n_arms


def _panel_model_id(panel: dict[str, Any], config_key: str) -> str:
    spec = (panel.get("models") or {}).get(config_key) or {}
    return str(spec.get("model", ""))


def _validate_sheet_v2_propagation(
    contract: dict[str, Any],
    panel: dict[str, Any],
) -> None:
    sheet = contract.get("q1_decision_sheet_v2") or {}
    fam = sheet.get("primary_holm_family") or {}
    open_ids = list(fam.get("open_target_model_ids") or [])
    if len(open_ids) != 4:
        raise Q1ContractError("primary_holm_family must list 4 open targets")
    if int(fam.get("primary_family_paired_comparisons", 0)) != PRIMARY_PAIRED_COMPARISONS:
        raise Q1ContractError("primary_family_paired_comparisons must be 244")
    if int(fam.get("primary_family_causal_episodes", 0)) != PRIMARY_CAUSAL_EPISODES:
        raise Q1ContractError("primary_family_causal_episodes must be 488 (244×2 arms)")

    exec_block = contract.get("q1_execution") or {}
    if list(exec_block.get("open_target_model_ids") or []) != open_ids:
        raise Q1ContractError("q1_execution.open_target_model_ids must match sheet v2")

    prim_keys = list((contract.get("primary_targets") or {}).get("config_keys") or [])
    resolved = [_panel_model_id(panel, k) for k in prim_keys]
    if resolved != open_ids:
        raise Q1ContractError(
            f"primary_targets panel models {resolved} != sheet open_target_model_ids {open_ids}"
        )

    judges = contract.get("judges") or {}
    j1 = judges.get("J1_primary") or {}
    j2 = judges.get("J2_agreement") or {}
    j1_sheet = (sheet.get("judges") or {}).get("J1_primary_all_confirmatory") or {}
    j2_sheet = (sheet.get("judges") or {}).get("J2_subset_only") or {}
    if str(j1.get("openrouter_model_id")) != str(j1_sheet.get("openrouter_model_id")):
        raise Q1ContractError("J1 openrouter_model_id mismatch vs sheet v2")
    if str(j2.get("openrouter_model_id")) != str(j2_sheet.get("openrouter_model_id")):
        raise Q1ContractError("J2 openrouter_model_id mismatch vs sheet v2")

    b2_conds = (exec_block.get("b2_adaptive_conditions") or {}).get("primary_holm") or []
    if tuple(b2_conds) != tuple(Q1_PRIMARY_CAUSAL_B2_CONDITIONS):
        raise Q1ContractError("primary_holm B2 conditions must match Q1_PRIMARY_CAUSAL_B2_CONDITIONS")
    sec = (exec_block.get("b2_adaptive_conditions") or {}).get("secondary_exploratory") or []
    if B2_CONDITION_ADAPTIVE_B1 not in sec:
        raise Q1ContractError("secondary_exploratory must include B2-ADAPTIVE-B1")
    if B2_CONDITION_ADAPTIVE_A0 not in b2_conds or B2_CONDITION_ADAPTIVE_B3 not in b2_conds:
        raise Q1ContractError("primary Holm conditions must be A0 and B3")

    stats = contract.get("statistics") or {}
    if int((stats.get("holm_families") or {}).get("primary", {}).get("n_mcnemar_tests", 0)) != 4:
        raise Q1ContractError("primary Holm family must be m=4")
    if stats.get("mcnemar_sidedness") != "two_sided":
        raise Q1ContractError("primary test must be two-sided McNemar")
    if float(stats.get("alpha", 0)) != 0.05:
        raise Q1ContractError("alpha must be 0.05")

    d01 = sheet.get("d01_research_questions_hypotheses") or {}
    if d01.get("RQ1b", {}).get("outside_primary_holm") is not True:
        raise Q1ContractError("RQ1b must be outside primary Holm family")
    if "RQ2" not in d01:
        raise Q1ContractError("RQ2 must be registered in D01")

    budget = sheet.get("budget_planning") or {}
    sheet_phase_ids = list(budget.get("execution_phase_ids") or [])
    exec_phases = list((exec_block.get("phases") or []))
    exec_ids = [str(p.get("id")) for p in exec_phases]
    if sheet_phase_ids != exec_ids:
        raise Q1ContractError(
            f"execution_phase_ids mismatch sheet vs q1_execution: {sheet_phase_ids} != {exec_ids}"
        )


def _validate_owner_decision_pack_sync(
    contract: dict[str, Any],
    *,
    pack_path: Path,
    repo_root: Path,
) -> None:
    pack_text = (repo_root / pack_path).read_text(encoding="utf-8")
    d13 = (contract.get("q1_decision_sheet_v2") or {}).get("j2_subset_d13") or {}
    manifest_path = str(d13.get("manifest_path", ""))
    manifest_sha = str(d13.get("manifest_sha256", ""))
    if manifest_path not in pack_text:
        raise Q1ContractError(f"owner pack missing manifest path: {manifest_path}")
    if manifest_sha not in pack_text:
        raise Q1ContractError(f"owner pack missing manifest sha256: {manifest_sha}")

    budget = (contract.get("q1_decision_sheet_v2") or {}).get("budget_planning") or {}
    for phase_id in budget.get("execution_phase_ids") or []:
        if str(phase_id) not in pack_text:
            raise Q1ContractError(f"owner pack missing execution phase id: {phase_id}")


def validate_q1_evaluation_contract(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    panel_path: str | Path = DEFAULT_PANEL_PATH,
    owner_pack_path: str | Path = DEFAULT_OWNER_PACK_PATH,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    contract = load_q1_contract(contract_path)
    panel = yaml.safe_load(panel_path.read_text(encoding="utf-8"))
    models = panel.get("models") or {}

    ds = contract.get("dataset") or {}
    ds_path = root / str(ds.get("path", ""))
    if not ds_path.is_file():
        raise Q1ContractError(f"missing dataset: {ds_path}")
    actual_ds_sha = hashlib.sha256(ds_path.read_bytes()).hexdigest()
    expected_ds_sha = str(ds.get("sha256", ""))
    if actual_ds_sha != expected_ds_sha:
        raise Q1ContractError(f"dataset SHA mismatch: {actual_ds_sha} != {expected_ds_sha}")

    if int(ds.get("n_attack", 0)) != 61 or int(ds.get("n_benign", 0)) != 61:
        raise Q1ContractError("dataset N must be 61 attack + 61 benign")

    prim = contract.get("primary_targets") or {}
    if len(list(prim.get("config_keys", []))) != 4:
        raise Q1ContractError("primary_targets must list exactly 4 config keys")
    supp = contract.get("supplementary_targets") or {}
    if len(list(supp.get("config_keys", []))) != 2:
        raise Q1ContractError("supplementary_targets must list exactly 2 config keys")
    if supp.get("merge_with_primary_comparisons") is not False:
        raise Q1ContractError("supplementary must not merge with primary comparisons")

    arms = contract.get("arms") or {}
    if set(arms) != {"B0", "B1", "B2"}:
        raise Q1ContractError("arms must be exactly B0, B1, B2")
    b2 = arms.get("B2") or {}
    if int(b2.get("max_turns", 0)) != LIVE_WIRING_MAX_TURNS:
        raise Q1ContractError(f"B2 max_turns must match LIVE_WIRING_MAX_TURNS={LIVE_WIRING_MAX_TURNS}")
    if str(arms["B1"].get("defense_resolver_key")) != "B1":
        raise Q1ContractError("arms.B1 must resolve to B1")
    if str(arms["B2"].get("defense_resolver_key")) != "B2-ADAPTIVE":
        raise Q1ContractError("arms.B2 must resolve to B2-ADAPTIVE")

    _validate_sheet_v2_propagation(contract, panel)
    _validate_owner_decision_pack_sync(contract, pack_path=Path(owner_pack_path), repo_root=root)

    peb = contract.get("primary_episode_budget") or {}
    if str(peb.get("formula")) != EPISODE_BUDGET_FORMULA:
        raise Q1ContractError(f"primary_episode_budget.formula must be {EPISODE_BUDGET_FORMULA!r}")
    derived_attack = derived_primary_attack_episodes(contract)
    declared_attack = peb.get("attack_episodes")
    if str(declared_attack) != "NEEDS_DECISION":
        if int(declared_attack) != derived_attack:
            raise Q1ContractError(
                f"attack_episodes {declared_attack} != derived {derived_attack} from formula"
            )

    budget = contract.get("budget") or {}
    cap = budget.get("hard_cap_usd")
    if str(cap) != "NEEDS_DECISION":
        try:
            cap_f = float(cap)
        except (TypeError, ValueError):
            raise Q1ContractError("hard_cap_usd must be NEEDS_DECISION or a positive number")
        if cap_f <= 0:
            raise Q1ContractError("hard_cap_usd must be positive when set")
    if budget.get("hard_stop") is not True:
        raise Q1ContractError("budget hard_stop must be true")

    binding = contract.get("legacy_binding_untouched") or {}
    models_yaml = root / "configs/models.yaml"
    if hashlib.sha256(models_yaml.read_bytes()).hexdigest() != VNEXT_MODELS_YAML_SHA:
        raise Q1ContractError("configs/models.yaml VNEXT binding SHA changed")

    for key in list(prim.get("config_keys", [])) + list(supp.get("config_keys", [])):
        if key not in models:
            raise Q1ContractError(f"panel missing key: {key}")

    judges = contract.get("judges") or {}
    if "J1_primary" not in judges or "J2_agreement" not in judges:
        raise Q1ContractError("judges J1 and J2 required")
    for jkey in ("J1_primary", "J2_agreement"):
        ck = str((judges[jkey] or {}).get("config_key", ""))
        if ck not in models:
            raise Q1ContractError(f"judge panel missing key: {ck}")
        if str(models[ck].get("model", "")).startswith("NEEDS_DECISION"):
            raise Q1ContractError(f"judge model NEEDS_DECISION: {ck}")

    blocked = [
        k
        for k in prim.get("config_keys", [])
        if str(models[k].get("model", "")).startswith("NEEDS_DECISION")
        or str(models[k].get("verification", "")) == "NEEDS_DECISION"
    ]

    needs = []
    if str(peb.get("attack_episodes")) == "NEEDS_DECISION":
        needs.append("primary_episode_budget.attack_episodes")
    stats = contract.get("statistics") or {}
    if str(stats.get("multiple_comparison")) == "NEEDS_DECISION":
        needs.append("statistics.multiple_comparison")

    sheet = contract.get("q1_decision_sheet_v2") or {}
    d13 = sheet.get("j2_subset_d13") or {}
    manifest_rel = d13.get("manifest_path")
    manifest_sha256 = None
    if manifest_rel and str(manifest_rel) != "NEEDS_DECISION":
        manifest_path = root / str(manifest_rel)
        if not manifest_path.is_file():
            raise Q1ContractError(f"missing J2 subset manifest: {manifest_path}")
        expected_manifest_sha = str(d13.get("manifest_sha256", ""))
        actual_manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        manifest_sha256 = actual_manifest_sha
        if expected_manifest_sha and actual_manifest_sha != expected_manifest_sha:
            raise Q1ContractError(
                f"J2 subset manifest SHA mismatch: {actual_manifest_sha} != {expected_manifest_sha}"
            )
        if int(d13.get("subset_pairs", 0)) != J2_SUBSET_PAIRS or int(d13.get("j2_episodes", 0)) != J2_SUBSET_EPISODES:
            raise Q1ContractError("D13 J2 subset must be 49 pairs / 98 episodes")
    needs.extend(blocked)

    from adapti_guard.evaluation.q1_cost_preflight import estimate_q1_phase_preflight

    phase_preflight = estimate_q1_phase_preflight(
        contract, panel_path=Path(panel_path), repo_root=root
    )
    if not phase_preflight.get("all_phases_within_cap"):
        raise Q1ContractError("phase cost preflight exceeds per-phase cap")

    sci = contract.get("scientific_design") or {}
    execution_gate = str(sci.get("execution_gate", "BLOCKED"))
    p0_intake = (sci.get("owner_decision_intake") or {})
    p0_open = [
        k
        for k, v in p0_intake.items()
        if k.startswith("D") and str(v.get("tier")) == "P0" and str(v.get("status")) != "OWNER_SPECIFIED"
    ]
    p0_freeze_ready = (
        execution_gate == "BLOCKED"
        and not needs
        and not p0_open
        and phase_preflight.get("all_phases_within_cap") is True
        and phase_preflight.get("estimator") == "model_aware_panel_pricing"
    )

    return {
        "status": "valid_offline" if not needs else "valid_offline_with_blockers",
        "execution_gate": execution_gate,
        "p0_freeze_ready": p0_freeze_ready,
        "contract_sha256": contract_sha256(contract_path),
        "dataset_sha256": actual_ds_sha,
        "models_yaml_sha256": VNEXT_MODELS_YAML_SHA,
        "j2_subset_manifest_sha256": manifest_sha256,
        "panel_keys_pending_verification": blocked,
        "needs_decision": sorted(set(needs)),
        "p0_intake_open": p0_open,
        "derived_attack_episodes": derived_attack,
        "primary_causal_episodes": PRIMARY_CAUSAL_EPISODES,
        "attack_episodes_declared": declared_attack,
        "episode_budget_formula": EPISODE_BUDGET_FORMULA,
        "budget_cap_usd": cap,
        "phase_cost_preflight": phase_preflight,
    }
