#!/usr/bin/env python3
"""Verify Q1 findings manuscript numbers against frozen AUDIT + offline artifacts.

No live LLM. No pack/AUDIT mutation. Exit 0 iff PASS.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
Q1_DIR = Path(__file__).resolve().parent
MANUSCRIPT = Q1_DIR / "MANUSCRIPT.md"
CLAIMS_MAP = Q1_DIR / "CLAIMS_MAP.md"
DELTA_CI_JSON = Q1_DIR / "artifacts/vnext_delta_ci_offline.json"
POWER_JSON = Q1_DIR / "artifacts/vnext_track_a_power_sensitivity.json"

VNEXT_AUDIT = ROOT / "experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147"
PHASE1_AUDIT = (
    ROOT
    / "experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92"
)

TRACK_A = {
    "b0_asr": "0.9508",
    "vnext_asr": "0.8689",
    "p": "0.0625",
    "delta": "0.0820",
    "utility": "0.9344",
    "b10": "5",
    "b01": "0",
    "status": "FAIL",
}

TRACK_B = {
    "b0_asr": "1.0000",
    "core_asr": "0.5574",
    "delta": "0.4426",
    "ci_lo": "0.2757",
    "ci_hi": "0.6096",
    "utility": "0.9672131147540983",
    "classification": "SUPPORTED_IMPROVEMENT",
}


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    if not path.is_file():
        fail(f"missing {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def forbid_win_language(text: str, label: str) -> None:
    pats = (
        r"VNEXT-ADAPT works",
        r"qualified win \(H1\) is \*\*YES\*\*",
        r"overturns Track A FAIL",
        r"overturns FAIL",
        r"solves prompt injection",
        r"production-ready",
    )
    skip = re.compile(r"(?i)not |does not|do not|forbidden|without reversing|is not a")
    for pat in pats:
        for m in re.finditer(pat, text, flags=re.I):
            line_start = text.rfind("\n", 0, m.start()) + 1
            line_end = text.find("\n", m.end())
            line = text[line_start : line_end if line_end >= 0 else None]
            if skip.search(line):
                continue
            fail(f"{label} forbidden wording: {pat}")


def check_track_a_verdict(verdict: dict) -> None:
    if verdict.get("status") != "FAIL" or verdict.get("qualified_win") is not False:
        fail("Track A verdict must be FAIL / qualified_win false")
    if verdict.get("p_value") != 0.0625:
        fail("Track A p_value")
    if verdict.get("b10") != 5 or verdict.get("b01") != 0:
        fail("Track A McNemar cells")
    if abs(float(verdict["delta_hat"]) - 0.0820) > 5e-4:
        fail("Track A delta_hat")


def check_track_b_verdict(verdict: dict) -> None:
    if verdict.get("classification") != "SUPPORTED_IMPROVEMENT":
        fail("Track B classification")
    im = verdict["intervention_mediated"]
    if im["b10"] != 27 or im["b01"] != 0:
        fail("Track B McNemar cells")
    if abs(im["effect_delta_hat"] - 0.4426229508196721) > 1e-6:
        fail("Track B delta")
    ci = im["ci95"]
    if abs(ci[0] - 0.27566461068024595) > 1e-6:
        fail("Track B CI lo")


def check_manuscript_numbers(ms: str) -> None:
    for key, val in TRACK_A.items():
        if val not in ms and key not in ("status",):
            fail(f"MANUSCRIPT missing Track A {key}={val}")
    for key, val in TRACK_B.items():
        if key == "classification":
            continue
        if val not in ms:
            fail(f"MANUSCRIPT missing Track B {key}={val}")
    if "FAIL" not in ms:
        fail("MANUSCRIPT missing FAIL framing")


def check_offline_ci_hygiene(ms: str, delta_artifact: dict) -> None:
    ci = delta_artifact["delta_hat_ci_95"]
    lo, hi = ci["lower"], ci["upper"]
    # Rounded forms allowed in prose
    if "0.0164" not in ms and f"{lo:.4f}" not in ms:
        fail("MANUSCRIPT missing offline CI lower bound")
    if "0.1639" not in ms and f"{hi:.3f}" not in ms:
        fail("MANUSCRIPT missing offline CI upper bound")
    bad = re.search(
        r"(?i)AUDIT.{0,80}(95%|delta.?hat).{0,40}CI.{0,40}(0\.01|0\.16)",
        ms,
    )
    if bad:
        fail("MANUSCRIPT implies Track A delta CI was in AUDIT")
    markers = (
        "offline",
        "recomputed",
        "not in original AUDIT",
        "Original AUDIT has **no**",
        "post-hoc offline",
    )
    if not any(m.lower() in ms.lower() for m in markers):
        fail("MANUSCRIPT must label Track A delta CI as offline/recomputed")
    if delta_artifact.get("label") != "recomputed_offline_not_in_original_AUDIT":
        fail("delta CI artifact label wrong")


def check_offline_power_hygiene(ms: str, power: dict) -> None:
    if not POWER_JSON.is_file():
        fail("power artifact missing")
    p_at_msid = power["power_mcnemar_significance"]["theta_0.2"]
    if p_at_msid < 0.95:
        fail("power artifact sanity")
    if "99%" in ms or "0.989" in ms or "~99" in ms:
        if not re.search(r"(?i)offline|scaffold|b01\s*=\s*0|simplified", ms):
            fail("MANUSCRIPT cites high power without offline/scaffold label")
    if re.search(r"(?i)underpowered for MSID(?!\s*under)", ms):
        fail("MANUSCRIPT must not claim underpowered for MSID without negation/scaffold")
    if power.get("label") != "offline_power_sensitivity_not_in_original_AUDIT":
        fail("power artifact label wrong")
    if power["observed_track_a"]["mcnemar_p"] != 0.0625:
        fail("power artifact observed p mismatch")


def check_claims_map(cm: str) -> None:
    if "Q1-A4" not in cm or "offline artifact" not in cm:
        fail("CLAIMS_MAP missing offline CI rule Q1-A4")
    if "Q1-A6" not in cm:
        fail("CLAIMS_MAP missing Q1-A6 power rule")
    if "Q1-F7" not in cm:
        fail("CLAIMS_MAP missing Q1-F7")


def main() -> None:
    v_a = load_json(VNEXT_AUDIT / "verdict.json")
    v_b = load_json(PHASE1_AUDIT / "verdict.json")
    check_track_a_verdict(v_a)
    check_track_b_verdict(v_b)

    delta_art = load_json(DELTA_CI_JSON)
    power_art = load_json(POWER_JSON)

    ms = MANUSCRIPT.read_text(encoding="utf-8")
    cm = CLAIMS_MAP.read_text(encoding="utf-8")

    check_manuscript_numbers(ms)
    check_offline_ci_hygiene(ms, delta_art)
    check_offline_power_hygiene(ms, power_art)

    abstract = ms.split("## 1. Introduction", 1)[0]
    conclusion = ms.split("## 11. Conclusion", 1)[-1]
    forbid_win_language(abstract, "Abstract")
    forbid_win_language(conclusion, "Conclusion")

    check_claims_map(cm)

    if "CONTRIBUTION_CEILING.md" not in ms:
        fail("MANUSCRIPT should link CONTRIBUTION_CEILING.md in intro")

    print(
        "PASS q1_findings "
        f"track_a=FAIL track_b=SUPPORTED_IMPROVEMENT "
        f"offline_ci={delta_art['inputs_sha256'][:8]}… "
        f"offline_power={power_art['inputs_sha256'][:8]}…"
    )


if __name__ == "__main__":
    main()
