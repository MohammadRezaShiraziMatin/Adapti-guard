"""Defense baseline factories for real LLM evaluation (B0–B3)."""

from __future__ import annotations

from typing import Callable

DefenseFn = Callable[[str, str | None], tuple[str, bool, str]]


def make_b0_no_defense() -> DefenseFn:
    def fn(prompt: str, context: str | None = None):
        return "A0", False, prompt

    return fn


def make_b1_rule_based(threshold: float = 0.25) -> DefenseFn:
    from src.adapti_guard.detector.prompt_injection_detector import PromptInjectionDetector

    detector = PromptInjectionDetector()

    def fn(prompt: str, context: str | None = None):
        text = f"{context}\n\n{prompt}" if context else prompt
        detection = detector.detect(text)
        blocked = detection.injection_probability >= threshold
        action = "A3" if blocked else "A0"
        fn.last_detector_hit = detection.injection_probability >= threshold
        return action, blocked, "" if blocked else prompt

    fn.last_detector_hit = False
    return fn


def make_b2_fixed_defense(level: int) -> DefenseFn:
    from src.adapti_guard.defense.action_layer import DefenseActionLayer
    from src.adapti_guard.detector.prompt_injection_detector import PromptInjectionDetector
    from src.adapti_guard.policy.policy_engine import DefensePolicyEngine
    from src.adapti_guard.risk.risk_engine import RiskEngine

    detector = PromptInjectionDetector()
    risk_engine = RiskEngine()
    policy_engine = DefensePolicyEngine()
    action_layer = DefenseActionLayer()

    def fn(prompt: str, context: str | None = None):
        text = f"{context}\n\n{prompt}" if context else prompt
        detection = detector.detect(text)
        risk = risk_engine.assess(detection)
        decision = policy_engine.decide(
            risk=risk, tool_sensitive=False, defense_level=level
        )
        defense = action_layer.execute(decision.action, prompt)
        blocked = not defense.allowed
        action = decision.action.value if hasattr(decision.action, "value") else str(decision.action)
        fn.last_detector_hit = bool(getattr(detection, "is_injection", False))
        return action, blocked, defense.content if not blocked else ""

    fn.last_detector_hit = False
    return fn


def make_l1_fixed_sanitize() -> DefenseFn:
    """Unconditional A1 (sanitize). Does not consult the detector."""
    from src.adapti_guard.core.models import DefenseAction
    from src.adapti_guard.defense.action_layer import DefenseActionLayer

    action_layer = DefenseActionLayer()

    def fn(prompt: str, context: str | None = None):
        del context
        defense = action_layer.execute(DefenseAction.SANITIZE, prompt)
        blocked = not defense.allowed
        return "A1", blocked, defense.content if not blocked else ""

    return fn


def make_l2_fixed_tool_restriction() -> DefenseFn:
    """Unconditional A2 (tool restriction). Does not consult the detector.

    DefenseFn still returns (action, blocked, prompt); ``evaluate_episode``
    enforces A2 by denying requested tools in ``tool_loop``. The prompt is
    unchanged and the turn is not blocked.
    """
    from src.adapti_guard.core.models import DefenseAction
    from src.adapti_guard.defense.action_layer import DefenseActionLayer

    action_layer = DefenseActionLayer()

    def fn(prompt: str, context: str | None = None):
        del context
        defense = action_layer.execute(DefenseAction.TOOL_RESTRICTION, prompt)
        blocked = not defense.allowed
        return "A2", blocked, defense.content if not blocked else ""

    return fn


def make_l3_fixed_block() -> DefenseFn:
    """Unconditional A3 (block). Does not consult the detector."""
    from src.adapti_guard.core.models import DefenseAction
    from src.adapti_guard.defense.action_layer import DefenseActionLayer

    action_layer = DefenseActionLayer()

    def fn(prompt: str, context: str | None = None):
        del context
        defense = action_layer.execute(DefenseAction.BLOCK, prompt)
        blocked = not defense.allowed
        return "A3", blocked, defense.content if not blocked else ""

    return fn


class AdaptiveDefenseState:
    """Stateful B3 adaptive defense for sequential evaluation.

    VNEXT leakage rule: gold ``is_attack`` / labels never enter this controller.
    Adaptation uses only runtime-observable detector/risk/action signals.
    """

    def __init__(self, initial_level: int = 1, detector=None, risk_engine=None):
        from src.adapti_guard.adaptation.feedback_engine import FeedbackEngine
        from src.adapti_guard.adaptation.policy_update_engine import PolicyUpdateEngine
        from src.adapti_guard.defense.action_layer import DefenseActionLayer
        from src.adapti_guard.detector.prompt_injection_detector import PromptInjectionDetector
        from src.adapti_guard.policy.policy_engine import DefensePolicyEngine
        from src.adapti_guard.risk.risk_engine import RiskEngine

        self.detector = detector or PromptInjectionDetector()
        self.risk_engine = risk_engine or RiskEngine()
        self.policy_engine = DefensePolicyEngine()
        self.action_layer = DefenseActionLayer()
        self.feedback_engine = FeedbackEngine()
        self.policy_update = PolicyUpdateEngine()
        self.policy_update.state.defense_level = initial_level
        self._last_outcome: dict | None = None
        self.last_detector_hit: bool = False

    def reset(self) -> None:
        from src.adapti_guard.adaptation.policy_update_engine import PolicyState

        self.policy_update.state = PolicyState(defense_level=1)
        self._last_outcome = None
        self.last_detector_hit = False

    def evaluate(self, prompt: str, context: str | None = None):
        from src.adapti_guard.evaluation.outcome_evaluator import OutcomeResult

        if self._last_outcome is not None:
            prev = self._last_outcome
            # Runtime stand-ins only — never gold labels.
            detector_hit = bool(prev["detector_hit"])
            contained = bool(prev["contained"])
            blocked = bool(prev["blocked"])
            outcome = OutcomeResult(
                attack_success=detector_hit and not contained,
                legitimate_success=(not detector_hit) and (not blocked),
                attack_present=detector_hit,
                legitimate_task=not detector_hit,
                defense_cost=prev["defense_cost"],
                security_score=0.0 if (detector_hit and not contained) else 1.0,
                utility_score=1.0 if ((not detector_hit) and (not blocked)) else 0.0,
            )
            feedback = self.feedback_engine.generate(outcome)
            self.policy_update.update(feedback)

        level = self.policy_update.state.defense_level
        if hasattr(self.detector, "detect_episode"):
            detection = self.detector.detect_episode(prompt or "", context or "")
        else:
            text = f"{context}\n\n{prompt}" if context else prompt
            detection = self.detector.detect(text)
        risk = self.risk_engine.assess(detection)
        decision = self.policy_engine.decide(
            risk=risk, tool_sensitive=False, defense_level=level
        )
        defense = self.action_layer.execute(decision.action, prompt)
        blocked = not defense.allowed
        action = decision.action.value if hasattr(decision.action, "value") else str(decision.action)
        detector_hit = bool(getattr(detection, "is_injection", False))
        contained = blocked or (action == "A2" and not defense.tool_access)
        cost_map = {"A0": 0.0, "A1": 0.1, "A2": 0.25, "A3": 0.5}

        self.last_detector_hit = detector_hit
        self._last_outcome = {
            "detector_hit": detector_hit,
            "blocked": blocked,
            "action": action,
            "contained": contained,
            "defense_cost": cost_map.get(action, 0.0),
        }

        return action, blocked, defense.content if not blocked else ""


_LEAKED_GOLD_KWARGS = frozenset({"is_attack", "label", "gold_label", "category"})


def make_b3_adaptive() -> tuple[DefenseFn, AdaptiveDefenseState]:
    state = AdaptiveDefenseState()

    def fn(prompt: str, context: str | None = None, **kwargs):
        for key in _LEAKED_GOLD_KWARGS:
            kwargs.pop(key, None)
        result = state.evaluate(prompt, context)
        fn.last_detector_hit = state.last_detector_hit
        return result

    fn.last_detector_hit = False
    return fn, state


def make_b3_adaptive_v4() -> tuple[DefenseFn, AdaptiveDefenseState]:
    """Adaptive B3 using detector v4 + monotonic risk v4. Historical B3 is unchanged."""
    from src.adapti_guard.detector.prompt_injection_detector_v4 import (
        PromptInjectionDetectorV4,
    )
    from src.adapti_guard.risk.risk_engine_v4 import RiskEngineV4

    state = AdaptiveDefenseState(
        detector=PromptInjectionDetectorV4(),
        risk_engine=RiskEngineV4(),
    )

    def fn(prompt: str, context: str | None = None, **kwargs):
        for key in _LEAKED_GOLD_KWARGS:
            kwargs.pop(key, None)
        result = state.evaluate(prompt, context)
        fn.last_detector_hit = state.last_detector_hit
        return result

    fn.last_detector_hit = False
    return fn, state


def make_core_defense(
    *, defense_level: int = 0, ablation: str | None = None
) -> tuple[DefenseFn, object]:
    """Phase 1 core pipeline. Not VNEXT-ADAPT. Label-blind; uses declared tool names."""
    from src.adapti_guard.core.core_pipeline import CoreDefensePipeline
    from src.adapti_guard.core.episode import EpisodeInput

    pipeline = CoreDefensePipeline(defense_level=defense_level, ablation=ablation)

    def fn(prompt: str, context: str | None = None, **kwargs):
        for key in _LEAKED_GOLD_KWARGS:
            kwargs.pop(key, None)
        blob = kwargs.pop("tool_call", None)
        tool_name = kwargs.pop("tool_name", None)
        tool_arguments: dict = {}
        if isinstance(blob, dict) and blob.get("name"):
            tool_name = tool_name or blob.get("name")
            raw_args = blob.get("arguments") or blob.get("args") or {}
            if isinstance(raw_args, dict):
                tool_arguments = raw_args
        tool_output = kwargs.pop("tool_output", None)
        inp = EpisodeInput(
            prompt=prompt or "",
            context=context or "",
            tool_name=str(tool_name) if tool_name else None,
            tool_arguments=dict(tool_arguments),
            tool_output=str(tool_output) if tool_output else None,
        )
        trace = pipeline.run(inp)
        fn.last_detector_hit = trace.detector_hit
        fn.last_trace = trace
        return trace.policy_action, trace.blocked, trace.content if not trace.blocked else ""

    fn.last_detector_hit = False
    fn.last_trace = None
    return fn, pipeline


def make_b2_fixed_defense_v4(level: int) -> DefenseFn:
    """Risk-gated fixed level using v4 detector/risk. Not unconditional L3."""
    from src.adapti_guard.defense.action_layer import DefenseActionLayer
    from src.adapti_guard.detector.prompt_injection_detector_v4 import (
        PromptInjectionDetectorV4,
    )
    from src.adapti_guard.policy.policy_engine import DefensePolicyEngine
    from src.adapti_guard.risk.risk_engine_v4 import RiskEngineV4

    detector = PromptInjectionDetectorV4()
    risk_engine = RiskEngineV4()
    policy_engine = DefensePolicyEngine()
    action_layer = DefenseActionLayer()

    def fn(prompt: str, context: str | None = None):
        if hasattr(detector, "detect_episode"):
            detection = detector.detect_episode(prompt or "", context or "")
        else:
            text = f"{context}\n\n{prompt}" if context else prompt
            detection = detector.detect(text)
        risk = risk_engine.assess(detection)
        decision = policy_engine.decide(
            risk=risk, tool_sensitive=False, defense_level=level
        )
        defense = action_layer.execute(decision.action, prompt)
        blocked = not defense.allowed
        action = decision.action.value if hasattr(decision.action, "value") else str(decision.action)
        fn.last_detector_hit = bool(getattr(detection, "is_injection", False))
        return action, blocked, defense.content if not blocked else ""

    fn.last_detector_hit = False
    return fn


def make_oracle_risk_policy(*, defense_level: int = 3) -> DefenseFn:
    """Diagnostic oracle: ground-truth label drives risk, then fixed-level policy.

    Not a deployable baseline. Attack labels are treated as HIGH risk; benign as LOW.
    Requires ``is_attack`` kwarg from the evaluation loop (diagnostic only).
    """
    from src.adapti_guard.core.models import (
        DefenseAction,
        DetectionResult,
        RiskAssessment,
        RiskLevel,
    )
    from src.adapti_guard.defense.action_layer import DefenseActionLayer
    from src.adapti_guard.policy.policy_engine import DefensePolicyEngine

    policy_engine = DefensePolicyEngine()
    action_layer = DefenseActionLayer()

    def fn(prompt: str, context: str | None = None, **kwargs):
        is_attack = bool(kwargs.get("is_attack", False))
        if is_attack:
            detection = DetectionResult(injection_probability=1.0, indicators=["oracle_attack"])
            risk = RiskAssessment(
                score=1.0,
                level=RiskLevel.HIGH,
                features={"oracle": 1.0},
                reasons=["oracle_ground_truth_attack"],
            )
        else:
            detection = DetectionResult(injection_probability=0.0, indicators=[])
            risk = RiskAssessment(
                score=0.0,
                level=RiskLevel.LOW,
                features={"oracle": 0.0},
                reasons=["oracle_ground_truth_benign"],
            )
        del detection  # risk already encodes the oracle signal
        decision = policy_engine.decide(
            risk=risk, tool_sensitive=False, defense_level=defense_level
        )
        # Utility-aware policy never A3s LOW risk solely from high defense_level.
        # For the oracle diagnostic we still want attack→block via HIGH risk above.
        defense = action_layer.execute(decision.action, prompt)
        blocked = not defense.allowed
        action = (
            decision.action.value
            if isinstance(decision.action, DefenseAction)
            else getattr(decision.action, "value", str(decision.action))
        )
        return action, blocked, defense.content if not blocked else ""

    return fn


def make_oracle_block_attacks() -> DefenseFn:
    """Stronger oracle diagnostic: block iff ground-truth attack, else A0.

    Isolates intervention semantics from policy-level LOW-risk utility guards.
    """

    def fn(prompt: str, context: str | None = None, **kwargs):
        del context
        if bool(kwargs.get("is_attack", False)):
            return "A3", True, ""
        return "A0", False, prompt

    return fn


BASELINE_FACTORIES: dict[str, Callable[[], DefenseFn]] = {
    "B0": make_b0_no_defense,
    "B1": make_b1_rule_based,
    "B2_L1": lambda: make_b2_fixed_defense(1),
    "B2_L2": lambda: make_b2_fixed_defense(2),
    "B2_L3": lambda: make_b2_fixed_defense(3),
    "B2_L3_V4": lambda: make_b2_fixed_defense_v4(3),
    # Unconditional interventions (not risk-gated).
    "L1": make_l1_fixed_sanitize,
    "STATIC-A1": make_l1_fixed_sanitize,
    "L2": make_l2_fixed_tool_restriction,
    "B2": make_l2_fixed_tool_restriction,
    "STATIC-A2": make_l2_fixed_tool_restriction,
    "L3": make_l3_fixed_block,
    "STATIC-A3": make_l3_fixed_block,
    # Diagnostics only — not deployable.
    "ORACLE_RISK": lambda: make_oracle_risk_policy(defense_level=3),
    "ORACLE_BLOCK": make_oracle_block_attacks,
}


_ABLATION_KEYS = {
    "ABL-NO-EVIDENCE": "ABL-NO-EVIDENCE",
    "ABL-NO-RISK": "ABL-NO-RISK",
    "ABL-NO-ADAPTATION": "ABL-NO-ADAPTATION",
    "ABL-NO-COST-GATE": "ABL-NO-COST-GATE",
    "ABL-NO-TOOL-SENSITIVITY": "ABL-NO-TOOL-SENSITIVITY",
}


def get_defense_fn(baseline_key: str) -> tuple[DefenseFn, object | None]:
    """Return defense function and optional state object (B3/B6 adaptive only)."""
    if baseline_key in ("B3", "B6"):
        return make_b3_adaptive()
    if baseline_key in ("B3_V4", "VNEXT-ADAPT"):
        # VNEXT-ADAPT is the confirmatory scientific name; factory is label-blind v4.
        return make_b3_adaptive_v4()
    if baseline_key in ("PHASE1-CORE", "CORE"):
        return make_core_defense()
    if baseline_key in _ABLATION_KEYS:
        return make_core_defense(ablation=_ABLATION_KEYS[baseline_key])
    if baseline_key not in BASELINE_FACTORIES:
        raise KeyError(f"Unknown baseline: {baseline_key}")
    return BASELINE_FACTORIES[baseline_key](), None
