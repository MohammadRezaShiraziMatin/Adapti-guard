#!/usr/bin/env python3
"""PREREG_JUDGE_V3 Step 0: 32 target-only format samples (no judge)."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.core.models import DefenseAction
from adapti_guard.evaluation.adaptive_episode import AdaptiveEpisodeRunner
from adapti_guard.evaluation.b2_matrix_contract import (
    build_pre_target_defense_bundle,
    defense_mode_for_condition_id,
)
from adapti_guard.evaluation.b2_adaptive_contract import LIVE_WIRING_MAX_TURNS
from adapti_guard.evaluation.live_budget_gate import BudgetGatedTargetModel, BudgetLedger
from adapti_guard.evaluation.live_model_resolver import model_id_for_config_key
from adapti_guard.evaluation.openrouter_panel_pricing import load_openrouter_pricing_table
from adapti_guard.evaluation.provider_errors import classify_generation_result
from adapti_guard.evaluation.stateful_target_adapter import TargetModelExecutionError
from adapti_guard.evaluation.target_model import GenerationRequest, build_target_model, token_usage_from_generation_result
from adapti_guard.evaluation.q1_p1_live_runner import (  # noqa: E402
    DatasetAnchoredAdaptiveAttacker,
    PANEL_PATH,
)

STEP0_CAP_USD = 0.04
PREREG_REF = "experiments/judge_gold/PREREG_JUDGE_V3.md"

# Frozen §6.1 (32 rows)
FROZEN_EPISODES: list[dict[str, str]] = [
    {"slot": 1, "attack_id": "vnext_c1_atk_001", "defense_arm": "A0", "target_family": "qwen3", "target_model_id": "qwen/qwen3-30b-a3b", "target_config_key": "q1_primary_qwen3_30b_a3b"},
    {"slot": 2, "attack_id": "vnext_c1_atk_001", "defense_arm": "B3", "target_family": "qwen3", "target_model_id": "qwen/qwen3-30b-a3b", "target_config_key": "q1_primary_qwen3_30b_a3b"},
    {"slot": 3, "attack_id": "vnext_c1_atk_010", "defense_arm": "A0", "target_family": "qwen3", "target_model_id": "qwen/qwen3-30b-a3b", "target_config_key": "q1_primary_qwen3_30b_a3b"},
    {"slot": 4, "attack_id": "vnext_c1_atk_010", "defense_arm": "B3", "target_family": "qwen3", "target_model_id": "qwen/qwen3-30b-a3b", "target_config_key": "q1_primary_qwen3_30b_a3b"},
    {"slot": 5, "attack_id": "vnext_c1_atk_025", "defense_arm": "A0", "target_family": "qwen3", "target_model_id": "qwen/qwen3-30b-a3b", "target_config_key": "q1_primary_qwen3_30b_a3b"},
    {"slot": 6, "attack_id": "vnext_c1_atk_025", "defense_arm": "B3", "target_family": "qwen3", "target_model_id": "qwen/qwen3-30b-a3b", "target_config_key": "q1_primary_qwen3_30b_a3b"},
    {"slot": 7, "attack_id": "vnext_c1_atk_035", "defense_arm": "A0", "target_family": "qwen3", "target_model_id": "qwen/qwen3-30b-a3b", "target_config_key": "q1_primary_qwen3_30b_a3b"},
    {"slot": 8, "attack_id": "vnext_c1_atk_035", "defense_arm": "B3", "target_family": "qwen3", "target_model_id": "qwen/qwen3-30b-a3b", "target_config_key": "q1_primary_qwen3_30b_a3b"},
    {"slot": 9, "attack_id": "vnext_c1_atk_001", "defense_arm": "A0", "target_family": "gemma", "target_model_id": "google/gemma-4-31b-it", "target_config_key": "q1_primary_gemma_4_31b_it"},
    {"slot": 10, "attack_id": "vnext_c1_atk_001", "defense_arm": "B3", "target_family": "gemma", "target_model_id": "google/gemma-4-31b-it", "target_config_key": "q1_primary_gemma_4_31b_it"},
    {"slot": 11, "attack_id": "vnext_c1_atk_010", "defense_arm": "A0", "target_family": "gemma", "target_model_id": "google/gemma-4-31b-it", "target_config_key": "q1_primary_gemma_4_31b_it"},
    {"slot": 12, "attack_id": "vnext_c1_atk_010", "defense_arm": "B3", "target_family": "gemma", "target_model_id": "google/gemma-4-31b-it", "target_config_key": "q1_primary_gemma_4_31b_it"},
    {"slot": 13, "attack_id": "vnext_c1_atk_025", "defense_arm": "A0", "target_family": "gemma", "target_model_id": "google/gemma-4-31b-it", "target_config_key": "q1_primary_gemma_4_31b_it"},
    {"slot": 14, "attack_id": "vnext_c1_atk_025", "defense_arm": "B3", "target_family": "gemma", "target_model_id": "google/gemma-4-31b-it", "target_config_key": "q1_primary_gemma_4_31b_it"},
    {"slot": 15, "attack_id": "vnext_c1_atk_035", "defense_arm": "A0", "target_family": "gemma", "target_model_id": "google/gemma-4-31b-it", "target_config_key": "q1_primary_gemma_4_31b_it"},
    {"slot": 16, "attack_id": "vnext_c1_atk_035", "defense_arm": "B3", "target_family": "gemma", "target_model_id": "google/gemma-4-31b-it", "target_config_key": "q1_primary_gemma_4_31b_it"},
    {"slot": 17, "attack_id": "vnext_c1_atk_001", "defense_arm": "A0", "target_family": "llama", "target_model_id": "meta-llama/llama-3.3-70b-instruct", "target_config_key": "q1_primary_llama_3_3_70b"},
    {"slot": 18, "attack_id": "vnext_c1_atk_001", "defense_arm": "B3", "target_family": "llama", "target_model_id": "meta-llama/llama-3.3-70b-instruct", "target_config_key": "q1_primary_llama_3_3_70b"},
    {"slot": 19, "attack_id": "vnext_c1_atk_010", "defense_arm": "A0", "target_family": "llama", "target_model_id": "meta-llama/llama-3.3-70b-instruct", "target_config_key": "q1_primary_llama_3_3_70b"},
    {"slot": 20, "attack_id": "vnext_c1_atk_010", "defense_arm": "B3", "target_family": "llama", "target_model_id": "meta-llama/llama-3.3-70b-instruct", "target_config_key": "q1_primary_llama_3_3_70b"},
    {"slot": 21, "attack_id": "vnext_c1_atk_025", "defense_arm": "A0", "target_family": "llama", "target_model_id": "meta-llama/llama-3.3-70b-instruct", "target_config_key": "q1_primary_llama_3_3_70b"},
    {"slot": 22, "attack_id": "vnext_c1_atk_025", "defense_arm": "B3", "target_family": "llama", "target_model_id": "meta-llama/llama-3.3-70b-instruct", "target_config_key": "q1_primary_llama_3_3_70b"},
    {"slot": 23, "attack_id": "vnext_c1_atk_035", "defense_arm": "A0", "target_family": "llama", "target_model_id": "meta-llama/llama-3.3-70b-instruct", "target_config_key": "q1_primary_llama_3_3_70b"},
    {"slot": 24, "attack_id": "vnext_c1_atk_035", "defense_arm": "B3", "target_family": "llama", "target_model_id": "meta-llama/llama-3.3-70b-instruct", "target_config_key": "q1_primary_llama_3_3_70b"},
    {"slot": 25, "attack_id": "vnext_c1_atk_001", "defense_arm": "A0", "target_family": "deepseek", "target_model_id": "deepseek/deepseek-v3.2", "target_config_key": "q1_primary_deepseek_v3_2"},
    {"slot": 26, "attack_id": "vnext_c1_atk_001", "defense_arm": "B3", "target_family": "deepseek", "target_model_id": "deepseek/deepseek-v3.2", "target_config_key": "q1_primary_deepseek_v3_2"},
    {"slot": 27, "attack_id": "vnext_c1_atk_010", "defense_arm": "A0", "target_family": "deepseek", "target_model_id": "deepseek/deepseek-v3.2", "target_config_key": "q1_primary_deepseek_v3_2"},
    {"slot": 28, "attack_id": "vnext_c1_atk_010", "defense_arm": "B3", "target_family": "deepseek", "target_model_id": "deepseek/deepseek-v3.2", "target_config_key": "q1_primary_deepseek_v3_2"},
    {"slot": 29, "attack_id": "vnext_c1_atk_025", "defense_arm": "A0", "target_family": "deepseek", "target_model_id": "deepseek/deepseek-v3.2", "target_config_key": "q1_primary_deepseek_v3_2"},
    {"slot": 30, "attack_id": "vnext_c1_atk_025", "defense_arm": "B3", "target_family": "deepseek", "target_model_id": "deepseek/deepseek-v3.2", "target_config_key": "q1_primary_deepseek_v3_2"},
    {"slot": 31, "attack_id": "vnext_c1_atk_035", "defense_arm": "A0", "target_family": "deepseek", "target_model_id": "deepseek/deepseek-v3.2", "target_config_key": "q1_primary_deepseek_v3_2"},
    {"slot": 32, "attack_id": "vnext_c1_atk_035", "defense_arm": "B3", "target_family": "deepseek", "target_model_id": "deepseek/deepseek-v3.2", "target_config_key": "q1_primary_deepseek_v3_2"},
]

CONDITION = {"A0": "B2-ADAPTIVE-A0", "B3": "B2-ADAPTIVE-B3"}

FORMAT_PATTERNS = [
    ("bracket_TOOL_CALL", re.compile(r"\[TOOL_CALL\s+\w+\(", re.I)),
    ("plain_fn_call", re.compile(r"\b(send_email|retrieve_document|create_record|search)\s*\(", re.I)),
    ("xml_tool_call", re.compile(r"<tool_call>", re.I)),
    ("openai_tool_calls", re.compile(r'"tool_calls"\s*:', re.I)),
    ("json_name_tool", re.compile(r'\{\s*"name"\s*:\s*"(send_email|retrieve_document|create_record|search)"', re.I)),
]


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=ROOT).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _load_attacks() -> dict[str, dict[str, Any]]:
    ds = ROOT / "datasets/frozen/vnext_confirm_v1/dataset.jsonl"
    out = {}
    for line in ds.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("label") == "attack":
            out[row["id"]] = row
    return out


def _usage_from_result(result: Any) -> dict[str, int]:
    return token_usage_from_generation_result(result)


@dataclass
class CallLogState:
    entries: list[dict[str, Any]]
    call_index: int = 0

    def append(
        self,
        *,
        slot: int,
        role: str,
        model_id: str,
        result: Any,
        cost_usd: float | None,
        cumulative_usd: float,
        arm: str,
    ) -> None:
        self.call_index += 1
        u = _usage_from_result(result)
        self.entries.append(
            {
                "call_index": self.call_index,
                "slot": slot,
                "role": role,
                "model_id": model_id,
                "arm": arm,
                "prompt_tokens": u["prompt_tokens"],
                "completion_tokens": u["completion_tokens"],
                "reasoning_tokens": u["reasoning_tokens"],
                "cost_usd": cost_usd,
                "cumulative_usd": cumulative_usd,
                "cache_hit": bool(getattr(result, "cache_hit", False)),
                "error": getattr(result, "error", None),
            }
        )


def _logging_target_fn(
    model: BudgetGatedTargetModel,
    *,
    model_id: str,
    slot: int,
    arm: str,
    log: CallLogState,
    ledger: BudgetLedger,
    pricing: Any,
    turn_records: list[dict[str, Any]],
) -> Any:
    from adapti_guard.evaluation.live_budget_gate import cost_from_generation_result

    def _fn(history: list[dict[str, str]], user_message: str) -> str:
        parts = [f"{m['role']}: {m['content']}" for m in history]
        prompt = "\n".join(parts + [f"user: {user_message}"])
        system_prompt = ""
        req = GenerationRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            model_id=model_id,
            temperature=0.0,
            max_tokens=512,
        )
        result = model.generate(req)
        cost = None
        if not result.cache_hit and ledger.max_usd is not None:
            cost = cost_from_generation_result(
                result, req, provider="openrouter", pricing=pricing, model_id=model_id
            )
        log.append(
            slot=slot,
            role="target",
            model_id=model_id,
            result=result,
            cost_usd=cost,
            cumulative_usd=ledger.spent_usd,
            arm=arm,
        )
        turn_records.append(
            {
                "system_prompt": system_prompt,
                "user_prompt": prompt,
                "target_response_full": result.text or "",
                "usage": _usage_from_result(result),
            }
        )
        failure = classify_generation_result(result)
        if failure["status"] != "ok":
            raise TargetModelExecutionError(failure)
        return result.text or ""

    return _fn


def _classify_missing(
    *,
    defense_arm: str,
    turns: tuple[Any, ...],
    tech_error: str | None,
) -> tuple[str, str]:
    if tech_error:
        return "TECH_ERROR", tech_error
    if not any(t.target_called for t in turns):
        if defense_arm == "B3" and any(t.blocked for t in turns):
            actions = [t.defense_action for t in turns if t.blocked]
            return "B3_BLOCK", f"pre_target_blocked; defense_actions={actions}"
        return "TECH_ERROR", "no_target_called"
    return "TECH_ERROR", "unknown"


def _taxonomy(text: str) -> list[str]:
    if not text.strip():
        return []
    found = []
    for name, rx in FORMAT_PATTERNS:
        if rx.search(text):
            found.append(name)
    return found


def run_step0(output_root: Path) -> dict[str, Any]:
    import os

    if not os.environ.get("OPENROUTER_API_KEY", "").strip():
        raise RuntimeError("OPENROUTER_API_KEY not set")

    output_root.mkdir(parents=True, exist_ok=True)
    panel_path = ROOT / PANEL_PATH
    pricing = load_openrouter_pricing_table(panel_path)
    ledger = BudgetLedger(max_usd=STEP0_CAP_USD, hard_stop=True)
    log = CallLogState(entries=[])
    attacks = _load_attacks()
    episodes_path = output_root / "episodes.jsonl"
    cost_log_path = output_root / "cost_log.jsonl"

    stop_reason = "completed_all_32"
    rows: list[dict[str, Any]] = []

    with episodes_path.open("w", encoding="utf-8") as ep_out:
        for spec in FROZEN_EPISODES:
            if ledger.max_usd is not None and ledger.spent_usd >= ledger.max_usd:
                stop_reason = "budget_cap_exceeded"
                break
            slot = int(spec["slot"])
            attack_row = attacks[spec["attack_id"]]
            anchor = f"{attack_row.get('prompt', '')}\n{attack_row.get('context', '')}".strip()
            arm = spec["defense_arm"]
            condition_id = CONDITION[arm]
            config_key = spec["target_config_key"]
            model_id = spec["target_model_id"]

            inner = build_target_model(config_key, config_path=str(panel_path), cache_enabled=False)
            inner.max_retries = 1
            gated = BudgetGatedTargetModel(inner, ledger, provider="openrouter", pricing=pricing)
            defense_mode = defense_mode_for_condition_id(condition_id)
            bundle = build_pre_target_defense_bundle(defense_mode)  # type: ignore[arg-type]
            if defense_mode == "B3" and bundle.state is not None and hasattr(bundle.state, "reset"):
                bundle.state.reset()

            turn_api_log: list[dict[str, Any]] = []
            target_fn = _logging_target_fn(
                gated,
                model_id=model_id,
                slot=slot,
                arm=f"{arm}_{spec['attack_id']}",
                log=log,
                ledger=ledger,
                pricing=pricing,
                turn_records=turn_api_log,
            )
            attacker = DatasetAnchoredAdaptiveAttacker(anchor)
            tech_error: str | None = None
            episode_result = None
            try:

                def _legacy_defense(**_kwargs: Any) -> tuple[DefenseAction, dict[str, Any]]:
                    return DefenseAction.TOOL_RESTRICTION, {}

                episode_result = AdaptiveEpisodeRunner(max_turns=LIVE_WIRING_MAX_TURNS).run(
                    attacker=attacker,
                    defense=_legacy_defense,
                    seed=42,
                    target=target_fn,
                    baseline_defense_fn=bundle.defense_fn,
                )
            except TargetModelExecutionError as exc:
                tech_error = json.dumps(exc.detail, default=str)

            turns = episode_result.turns if episode_result else ()
            executed = [t for t in turns if t.target_called]
            full_text = executed[-1].model_response if executed else ""
            obtained = bool(full_text.strip())
            missing_kind = None
            missing_detail = None
            if not obtained:
                if executed and not full_text.strip():
                    missing_kind, missing_detail = (
                        "TECH_ERROR",
                        "empty_target_content (API returned empty message.content)",
                    )
                else:
                    missing_kind, missing_detail = _classify_missing(
                        defense_arm=arm, turns=turns, tech_error=tech_error
                    )

            record = {
                "slot": slot,
                "attack_id": spec["attack_id"],
                "defense_arm": arm,
                "condition_id": condition_id,
                "target_family": spec["target_family"],
                "target_model_id": model_id,
                "target_config_key": config_key,
                "target_called": bool(executed),
                "target_response_full": full_text,
                "format_sample_obtained": obtained,
                "missing_kind": missing_kind,
                "missing_detail": missing_detail,
                "target_turns": [
                    {
                        "turn_index": t.turn_index,
                        "blocked": t.blocked,
                        "target_called": t.target_called,
                        "defense_action": t.defense_action,
                        "outcome_source": t.outcome_source,
                        "model_response": t.model_response,
                    }
                    for t in turns
                ],
                "target_api_calls": turn_api_log,
                "ledger_spent_usd_after": ledger.spent_usd,
            }
            ep_out.write(json.dumps(record, ensure_ascii=False) + "\n")
            rows.append(record)

    for entry in log.entries:
        pass
    cost_log_path.write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in log.entries),
        encoding="utf-8",
    )

    per_target: dict[str, dict[str, int]] = {
        fam: {"obtained": 0, "slots": 8} for fam in ("qwen3", "gemma", "llama", "deepseek")
    }
    taxonomy: dict[str, Counter] = defaultdict(Counter)
    excerpts: dict[str, list[str]] = defaultdict(list)

    for r in rows:
        fam = r["target_family"]
        if r["format_sample_obtained"]:
            per_target[fam]["obtained"] += 1
            for pat in _taxonomy(r["target_response_full"]):
                taxonomy[fam][pat] += 1
            if len(excerpts[fam]) < 3:
                excerpts[fam].append(r["target_response_full"][:400])

    summary = {
        "step": "PREREG_JUDGE_V3_STEP0",
        "prereg_doc": PREREG_REF,
        "git_commit": _git_head(),
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "stop_reason": stop_reason,
        "slots_planned": 32,
        "slots_executed": len(rows),
        "api_calls": log.call_index,
        "spent_usd": ledger.spent_usd,
        "cap_usd": STEP0_CAP_USD,
        "target_texts_obtained_per_family": {k: v["obtained"] for k, v in per_target.items()},
        "format_taxonomy_counts": {k: dict(v) for k, v in taxonomy.items()},
        "format_excerpts": excerpts,
    }
    (output_root / "cost_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (output_root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# Step 0 format taxonomy",
        "",
        f"**Pack:** `{output_root.relative_to(ROOT)}`",
        f"**Spend:** ${ledger.spent_usd:.6f} / cap ${STEP0_CAP_USD}",
        "",
    ]
    for fam in ("qwen3", "gemma", "llama", "deepseek"):
        ob = summary["target_texts_obtained_per_family"].get(fam, 0)
        md_lines.append(f"## {fam} ({ob}/8 obtained)")
        tc = summary["format_taxonomy_counts"].get(fam) or {}
        if not tc:
            md_lines.append("- **Tool-call syntax found:** none in obtained texts")
        else:
            md_lines.append(f"- **Pattern counts:** {tc}")
        for ex in summary["format_excerpts"].get(fam, [])[:2]:
            md_lines.append(f"- **Verbatim excerpt:** `{ex[:300]}`")
        md_lines.append("")
    (output_root / "FORMAT_TAXONOMY.md").write_text("\n".join(md_lines), encoding="utf-8")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Default: experiments/judge_gold/STEP0_FORMAT_SAMPLE_<ts>/",
    )
    args = parser.parse_args()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    root = args.output_root or (ROOT / f"experiments/judge_gold/STEP0_FORMAT_SAMPLE_{ts}")
    summary = run_step0(root)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
