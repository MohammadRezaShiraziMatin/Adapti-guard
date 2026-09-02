"""Unified baseline comparison runner with real LLM evaluation."""

from __future__ import annotations

import csv
import json
import logging
import os
from pathlib import Path
from typing import Any, Sequence

from src.adapti_guard.evaluation.attack_success import (
    EvalEpisode,
    compute_real_metrics,
    evaluate_episode,
    load_benchmark_records,
)
from src.adapti_guard.evaluation.llm_judge import LLMJudge, build_judge
from src.adapti_guard.evaluation.target_model import build_target_model

from baselines.adapti_guard_baseline import AdaptiGuardBaseline
from baselines.base import BaselineMethod
from baselines.llama_guard import LlamaGuardBaseline
from baselines.nemo_guardrails import NeMoGuardrailsBaseline
from baselines.no_defense import NoDefenseBaseline
from baselines.prompt_guard import PromptGuardBaseline
from baselines.regex_baseline import RegexBaseline
from baselines.tfidf_baseline import TfidfMLBaseline

logger = logging.getLogger(__name__)

DEFAULT_METHODS: dict[str, type] = {
    "no_defense": NoDefenseBaseline,
    "regex_detector": RegexBaseline,
    "tfidf_ml": TfidfMLBaseline,
    "llama_guard": LlamaGuardBaseline,
    "prompt_guard": PromptGuardBaseline,
    "nemo_guard": NeMoGuardrailsBaseline,
    "adapti_guard": lambda: AdaptiGuardBaseline(defense_level=1),
}


class BaselineComparisonRunner:
    def __init__(
        self,
        methods: dict[str, BaselineMethod] | None = None,
        target_config_key: str = "target_3",
        models_config: str = "configs/models.yaml",
    ):
        if methods is None:
            self.methods = {}
            for k, fn in DEFAULT_METHODS.items():
                self.methods[k] = fn() if callable(fn) else fn()
        else:
            self.methods = methods
        self.target_config_key = target_config_key
        self.models_config = models_config
        self._target = None
        self._judge = None

    def _init_llm(self) -> str | None:
        from src.adapti_guard.experiments.env_loader import validate_openrouter_key

        valid, reason = validate_openrouter_key()
        if not valid:
            return reason
        try:
            self._target = build_target_model(self.target_config_key, config_path=self.models_config)
            self._judge = build_judge(config_path=self.models_config)
            return None
        except Exception as exc:
            return str(exc)

    def run_method(
        self,
        method_name: str,
        records: Sequence[dict[str, Any]],
    ) -> tuple[list[EvalEpisode], dict[str, Any]]:
        baseline = self.methods[method_name]

        def defense_fn(prompt: str, context: str | None):
            decision = baseline.evaluate(prompt, context)
            return decision.action, decision.blocked, decision.sanitized_prompt

        episodes: list[EvalEpisode] = []
        for record in records:
            ep = evaluate_episode(
                record,
                defense_fn=defense_fn,
                target_model=self._target,
                judge=self._judge,
            )
            ep.metadata["method"] = method_name
            ep.metadata["score"] = baseline.evaluate(
                record.get("prompt", ""), record.get("context") or None
            ).score
            episodes.append(ep)

        metrics = compute_real_metrics(episodes)
        result = metrics.to_dict()
        result["method"] = method_name
        result["n_samples"] = len(episodes)
        return episodes, result

    def compare_all(
        self,
        records: Sequence[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        err = self._init_llm()
        if err:
            return [{"status": "BLOCKED", "reason": err}]

        rows: list[dict[str, Any]] = []
        no_def_asr: float | None = None
        for name in self.methods:
            logger.info("Running baseline: %s", name)
            _eps, result = self.run_method(name, records)
            if name == "no_defense":
                no_def_asr = result.get("asr")
            rows.append(result)
        if no_def_asr is not None:
            for row in rows:
                if "asr" in row:
                    row["asr_reduction_vs_no_defense"] = round(no_def_asr - row["asr"], 4)
        return rows

    @staticmethod
    def save_csv(rows: list[dict[str, Any]], path: Path) -> None:
        if not rows or rows[0].get("status") == "BLOCKED":
            path.write_text("status,reason\nBLOCKED," + str(rows[0].get("reason", "")) + "\n")
            return
        fieldnames = sorted({k for row in rows for k in row})
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def save_figure(rows: list[dict[str, Any]], path: Path) -> None:
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            path.with_suffix(".txt").write_text("matplotlib not installed\n")
            return
        if not rows or rows[0].get("status") == "BLOCKED":
            return
        methods = [r["method"] for r in rows]
        asrs = [r.get("asr", 0) for r in rows]
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(methods, asrs, color="steelblue")
        ax.set_ylabel("Attack Success Rate (ASR)")
        ax.set_title("Baseline Comparison — Real LLM Evaluation")
        ax.set_ylim(0, max(asrs) * 1.2 + 0.05 if asrs else 1.0)
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=150)
        plt.close(fig)
