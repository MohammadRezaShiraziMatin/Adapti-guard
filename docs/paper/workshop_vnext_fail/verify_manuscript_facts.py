#!/usr/bin/env python3
"""Verify workshop manuscript facts against frozen packs and VNEXT AUDIT.

No live LLM. No pack mutation. Exit 0 iff canonical FAIL facts match.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT_DIR = ROOT / "experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147"
PACK = ROOT / "datasets/frozen/vnext_confirm_v1/dataset.jsonl"
MS = ROOT / "docs/paper/workshop_vnext_fail/MANUSCRIPT.md"
RESULTS = ROOT / "docs/paper/04_results.md"

EXPECTED_SHA = "523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518"
LAYER_A_TEST_SHA = "47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8"
LAYER_A_V3_SHA = "abbc87134dc6563231aa422cb923226a5158d512c260a0ec17fd6997877632dd"
LAYER_A_V2_SHA = "76c60433d07258d06c5df451bfdd5be4d8ff08988b26c3ecea32ebc32d09ac33"

CANONICAL = {
    "b0_asr": "0.9508",
    "vnext_asr": "0.8689",
    "b10": "b10 = 5",
    "b01": "b01 = 0",
    "p": "0.0625",
    "delta": "0.0820",
    "msid": "0.20",
    "utility": "0.9344",
    "false_blocks": "false blocks = 1",
    "s5": "s5_mcnemar_not_significant",
    "msid_fail": "msid_not_met",
    "s4": "s4_utility_ineligible",
    "insufficient": "insufficient_intervention` = 53",
    "target": "qwen/qwen-2.5-7b-instruct",
    "judge": "qwen/qwen-2.5-72b-instruct",
    "status_fail": "STATUS = FAIL",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    sha = sha256(PACK)
    if sha != EXPECTED_SHA:
        fail(f"confirmation pack sha {sha} != {EXPECTED_SHA}")

    conf = ROOT / "datasets/frozen/vnext_confirm_v1/confirmation.jsonl"
    if sha256(conf) != EXPECTED_SHA:
        fail("confirmation.jsonl is not byte-identical in digest to dataset.jsonl")

    la_test = ROOT / "datasets/frozen/layer_a_v3/test_split.jsonl"
    if sha256(la_test) != LAYER_A_TEST_SHA:
        fail("Layer A TEST hash mismatch (frozen pack must not be modified)")
    if sha256(ROOT / "datasets/frozen/layer_a_v3/dataset.jsonl") != LAYER_A_V3_SHA:
        fail("Layer A v3 pack hash mismatch")
    if sha256(ROOT / "datasets/frozen/layer_a_v2/dataset.jsonl") != LAYER_A_V2_SHA:
        fail("Layer A v2 pack hash mismatch")

    verdict = json.loads((AUDIT_DIR / "verdict.json").read_text())
    if verdict.get("status") != "FAIL":
        fail(f"verdict.status={verdict.get('status')}")
    if verdict.get("qualified_win") is not False:
        fail("qualified_win must be false")
    reasons = verdict.get("fail_reasons") or []
    for key in ("s5_mcnemar_not_significant", "msid_not_met", "s4_utility_ineligible"):
        if key not in reasons:
            fail(f"missing fail reason {key}")
    if verdict.get("p_value") != 0.0625:
        fail(f"p_value={verdict.get('p_value')}")
    if verdict.get("b10") != 5 or verdict.get("b01") != 0:
        fail(f"b10/b01={verdict.get('b10')}/{verdict.get('b01')}")
    delta = float(verdict["delta_hat"])
    if abs(delta - 0.0820) > 5e-4:
        fail(f"delta_hat={delta}")
    if float(verdict["msid"]) != 0.2:
        fail(f"msid={verdict.get('msid')}")
    u = float(verdict["utility"])
    if abs(u - 0.9344) > 5e-4:
        fail(f"utility={u}")
    if verdict.get("hash", {}).get("sha256") != EXPECTED_SHA:
        fail("verdict hash sha256 mismatch")

    comparison = json.loads((AUDIT_DIR / "comparison.json").read_text())
    b0 = comparison["b0"]
    tr = comparison["VNEXT-ADAPT"]
    if abs(b0["asr"] - 0.9508) > 5e-4 or b0["n_attack_success"] != 58:
        fail("B0 ASR/count mismatch")
    if abs(tr["asr"] - 0.8689) > 5e-4 or tr["n_attack_success"] != 53:
        fail("VNEXT ASR/count mismatch")
    tax = tr["taxonomy_counts"]
    if tax.get("correct_block") != 5:
        fail("correct_block != 5")
    if tax.get("insufficient_intervention") != 53:
        fail("insufficient_intervention != 53")
    if tax.get("false_block") != 1:
        fail("false_block != 1")
    if comparison["confirmatory"]["b10_taxonomy"].get("correct_block") != 5:
        fail("b10 taxonomy is not 5 correct_block")
    if comparison["target_model"] == comparison["judge_model"]:
        fail("target must differ from judge")
    if comparison["target_model"] != "qwen/qwen-2.5-7b-instruct":
        fail("unexpected target")
    if comparison["judge_model"] != "qwen/qwen-2.5-72b-instruct":
        fail("unexpected judge")
    if comparison["cache_enabled"] is not False:
        fail("cache must be off")
    spend = float(comparison["spend"]["estimated_usd_total"])
    if abs(spend - 0.059016) > 1e-6:
        fail(f"spend={spend}")
    if b0["n_target_cache_hits"] != 0 or tr["n_target_cache_hits"] != 0:
        fail("cache hits must be 0")

    text = MS.read_text()
    for label, needle in CANONICAL.items():
        if needle not in text:
            fail(f"manuscript missing {label}: {needle!r}")

    # Layer A checklist sentences that must remain exact.
    layer_a_needles = [
        "detector v4 attack recall is 27/40 = 0.675 and AUROC is 0.705, versus v3 recall 2/40 = 0.05 and AUROC 0.368, without TEST retuning",
        "Adaptive B3_V4 has ASR 0.625 and utility 0.85 versus B0 ASR 0.75 and utility 1.00; exact McNemar p = 0.125. This is not a demonstrated ASR reduction.",
        "only one is a true A3 block; the other five are target refusals under A1 and are not defense wins",
    ]
    for needle in layer_a_needles:
        if needle not in text:
            fail(f"manuscript missing Layer A allowed sentence fragment: {needle[:60]}…")

    forbidden_positive = [
        r"is a working, production-ready",
        r"state-of-the-art cost-aware",
        r"B3_V4 beats B0",
        r"qualified win: \*\*YES\*\*",
        r"STATUS: \*\*PASS\*\*",
    ]
    for pat in forbidden_positive:
        if re.search(pat, text, flags=re.I):
            fail(f"forbidden positive claim matched {pat}")

    sim = RESULTS.read_text()
    if "fixed_l0" not in sim or "full_adaptive" not in sim:
        fail("04_results.md simulation body missing expected rows")
    if "0.027" not in sim:
        fail("04_results.md simulation ASR 0.027 missing (body rewritten?)")
    if "workshop_vnext_fail/README.md" not in sim:
        fail("04_results.md missing VNEXT FAIL pointer")

    n_lines = len(PACK.read_text().splitlines())
    if n_lines != 122:
        fail(f"pack rows={n_lines}")

    print("PASS: manuscript facts match frozen packs and VNEXT AUDIT FAIL record.")
    print(f"  pack_sha={sha}")
    print("  status=FAIL qualified_win=false")
    print("  b10=5 b01=0 p=0.0625 delta=0.0820 U=0.9344")
    print("  fail_reasons=s5_mcnemar_not_significant,msid_not_met,s4_utility_ineligible")


if __name__ == "__main__":
    main()
