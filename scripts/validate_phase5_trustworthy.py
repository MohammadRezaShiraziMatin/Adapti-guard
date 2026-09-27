#!/usr/bin/env python3
"""Phase 5 gate: trustworthy / human-centered layer (design + packet helper)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

DOC = "docs/research/PHASE5_TRUSTWORTHY_APPLICATION.md"
MARKERS = [
    "Human-Centered Security Decision Layer",
    "Trustworthy AI Dimensions",
    "machine decision",
    "human decision",
    "EVIDENCE-BLOCKED",
    "CPS",
    "human_review_packet",
]
MODULE = "src/adapti_guard/evaluation/human_review_packet.py"


def main() -> int:
    errors = []
    if not (ROOT / DOC).is_file():
        errors.append(f"missing {DOC}")
    else:
        text = (ROOT / DOC).read_text()
        for m in MARKERS:
            if m not in text:
                errors.append(f"{DOC}: missing '{m}'")
    if not (ROOT / MODULE).is_file():
        errors.append(f"missing {MODULE}")
    try:
        from adapti_guard.core.episode import EpisodeTrace
        from adapti_guard.evaluation.human_review_packet import packet_from_episode_trace

        t = EpisodeTrace(
            prompt="p",
            context_present=False,
            tool_name=None,
            privileged_tool=False,
            detector_probability=0.0,
            detector_indicators=[],
            detector_hit=False,
            risk_score=0.1,
            risk_level="LOW",
            risk_reasons=[],
            risk_features={},
            policy_action="A0",
            policy_reason="",
            defense_level=0,
            blocked=False,
            allowed=True,
            content="ok",
            tool_access=True,
            tool_requested=None,
            tool_permission_allowed=None,
            tool_executed=False,
            tool_observation="",
            tool_reason=None,
        )
        pkt = packet_from_episode_trace(t)
        if pkt.get("empirical_human_outcome") is not None:
            errors.append("packet must not fabricate empirical_human_outcome")
    except Exception as exc:
        errors.append(f"smoke: {exc}")
    p4 = ROOT / "docs/research/PHASE4_COMPLETION.json"
    if p4.is_file() and json.loads(p4.read_text()).get("phase4_infrastructure") != "DONE":
        errors.append("phase4 not DONE")
    status = "DONE" if not errors else "PARTIAL"
    out = {"phase5_trustworthy": status, "errors": errors}
    (ROOT / "docs/research/PHASE5_COMPLETION.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return 0 if status == "DONE" else 1


if __name__ == "__main__":
    sys.exit(main())
