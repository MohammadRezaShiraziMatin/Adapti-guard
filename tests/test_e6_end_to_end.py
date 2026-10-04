"""Offline end-to-end test of the E6 pipeline on the REAL archived harness runner with a mock transport (no API).

Chain: SYNTHETIC authoring fixture -> renderer -> sanitized harness tree -> E6 launcher -> A0, A0/r1, B3, CORE, NOINJ episodes -> analysis,
replay, manifest. The fixture is test data, never an independent pack. Outside a staged tree the test stages one into a temp directory from
the archived commit and skips if that commit is not available.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import e6_analysis as an  # noqa: E402
import e6_manifest as mf  # noqa: E402
import e6_render as rd  # noqa: E402
import e6_stage_harness as stg  # noqa: E402
from test_e6_prefreeze import fixture  # noqa: E402


def _env():
    env = {k: v for k, v in os.environ.items() if not k.startswith(("OPENROUTER", "HTTP", "HTTPS", "ALL_PROXY", "NO_PROXY"))}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "OPENROUTER_BASE_URL": "http://127.0.0.1:9/v1"})  # nothing may leave the machine
    return env


def _sh(root: Path, *args, check=True):
    r = subprocess.run([sys.executable, *args], cwd=root, env=_env(), capture_output=True, text=True)
    if check and r.returncode:
        raise AssertionError(r.stdout[-1500:] + r.stderr[-1500:])
    return r


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("e6e2e")
    if (ROOT / "SANITIZED_MANIFEST.json").is_file():
        root = ROOT
    else:
        try:
            stg.stage(tmp / "stage", git=True)
        except Exception as exc:  # archived commit not available in this checkout
            pytest.skip(f"cannot stage the harness: {exc}")
        root = tmp / "stage"
    auth = tmp / "authoring.json"
    auth.write_text(json.dumps(fixture()))
    out = tmp / "out"
    _sh(root, "scripts/e6_launcher.py", "mock", "--authoring", str(auth), "--h4-policy", "inert", "--out", str(out), "--error-instances", "2")
    rendered = tmp / "rendered.json"
    _sh(root, "scripts/e6_render.py", str(auth), "--h4-policy", "inert", "--out", str(rendered), check=False)  # exit 1 = not freeze-eligible (synthetic)
    return {"root": root, "tmp": tmp, "out": out, "rendered": rendered, "auth": auth,
            "rows": [json.loads(x) for x in (out / "episodes.jsonl").read_text().splitlines() if x.strip()],
            "plan": json.loads((out / "e6_plan.json").read_text())}


def test_accounting_ids_and_identical_records(run):
    rows = run["rows"]
    assert len(rows) == 1300
    arms = {a: [r for r in rows if r["arm"] == a] for a in ("A0", "A0R", "B3", "CORE", "NOINJ")}
    assert {a: len(v) for a, v in arms.items()} == {"A0": 300, "A0R": 300, "B3": 300, "CORE": 300, "NOINJ": 100}
    assert len({r["episode_id"] for r in rows}) == 1300
    assert all(r["episode_id"].endswith("/r1") for r in arms["A0R"]) and not any(r["episode_id"].endswith("/r1") for r in arms["A0"])
    assert all(r["scenario_id"].endswith("__noinj") for r in arms["NOINJ"]) and not any(r["scenario_id"].endswith("__noinj") for r in arms["A0"])
    assert {r["model_id"] for r in rows} == {"deepseek/deepseek-v3.2"} and {r["family"] for r in rows} == {"deepseek"}
    a0 = {(r["scenario_id"], r["instance_index"]): r for r in arms["A0"]}
    for r in arms["A0R"]:  # identical rendered record: same scenario, same exec_spec, same first user message
        a = a0[(r["scenario_id"], r["instance_index"])]
        assert a["exec_spec"] == r["exec_spec"] and a["final_messages"][0] == r["final_messages"][0]
    assert {r["status"] for r in rows} <= {"COMPLETE", "INVALID_PROVIDER_ERROR"}


def test_runner_provenance_uses_the_protocol_not_the_private_approval_document(run):
    summ = json.loads((run["out"] / "pilot_summary.json").read_text())
    proto = run["root"] / "docs/paper/negative_result/PROTOCOL_CONFIRMATORY_E6_DRAFT.md"
    assert summ["criteria_doc_sha256"] == hashlib.sha256(proto.read_bytes()).hexdigest() and summ["templates_sha256"] == rd.rendered_sha256(json.loads(run["rendered"].read_text()))
    m = json.loads((run["out"] / "e6_manifest.json").read_text())
    for k in ("seed", "scenario_set_sha256", "scoring_schema_sha256", "analysis_sha", "authoring_sha256", "protocol_sha256", "plan_file_sha256", "runner_script_sha256",
              "launcher_script_sha256", "harness_tree_sha256", "model_id", "h4_policy"):
        assert m.get(k) not in (None, "", mf.NOT_SET), k
    assert m["synthetic_pack"] is True and m["mode"] == "mock" and m["harness_constants_check"]["matches"]
    assert (run["out"] / "progress_log.txt").is_file()
    assert json.loads((run["out"] / "run_manifest.json").read_text())["runner_worktree_dirty"] is False


def test_nothing_private_in_the_sanitized_tree(run):
    sm = json.loads((run["root"] / "SANITIZED_MANIFEST.json").read_text())
    assert sm["findings"] == [] and not any(stg.forbidden_path(f) for f in sm["files"] if f not in stg.E6_EXTRA)
    for bad in ("e6/APPROVAL_RECORD.json", "configs/datasets.yaml", "experiments/harness_v2/PILOT2_CRITERIA_LOCKED.md", "experiments/harness_v2/SCENARIO_INSTANCE_TEMPLATES.json"):
        assert not (run["root"] / bad).exists()


def test_analysis_on_mock_traces(run):
    res = an.analyze_run(run["rows"], run["plan"], seed=1, h4_policy="inert")
    assert res["join"]["total"] and res["blocks"] == {"planned": 300, "complete": 300, "partial_run": False}
    assert res["arm_counts"] == {"A0": 300, "A0R": 300, "B3": 300, "CORE": 300, "NOINJ": 100} and res["h4"]["passed"]
    assert res["endpoint_consistency"]["mismatches"] == 0 and res["primary"]["B3"]["families"] == 30
    assert res["error_and_unusable_rates"]["provider_error_rate"]["A0"] > 0  # the two injected provider errors reach the error accounting
    cli = _sh(ROOT, "scripts/e6_analysis.py", "--episodes", str(run["out"] / "episodes.jsonl"), "--plan", str(run["out"] / "e6_plan.json"), "--h4-policy", "inert")
    assert json.loads(cli.stdout)["join"]["total"]


def test_replay_is_executor_derived_deterministic_and_non_gating(run):
    p1, p2, post = (run["tmp"] / n for n in ("r1.json", "r2.json", "post.json"))
    _sh(run["root"], "scripts/e6_launcher.py", "replay", "--rendered", str(run["out"] / "e6_rendered.json"), "--out", str(p1),
        "--episodes", str(run["out"] / "episodes.jsonl"), "--post-run-out", str(post))
    _sh(run["root"], "scripts/e6_launcher.py", "replay", "--rendered", str(run["out"] / "e6_rendered.json"), "--out", str(p2))
    a, b = json.loads(p1.read_text()), json.loads(p2.read_text())
    assert a == b and a["gate"].startswith("none") and p1.read_bytes() == p2.read_bytes()
    assert a["summary"]["B3"]["carrier_byte_changed"] == 0 and a["summary"]["B3"]["non_carrier_byte_changed"] == 300 and a["summary"]["CORE"]["carrier_byte_changed"] == 0
    cons = json.loads(post.read_text())
    for d in ("B3", "CORE"):
        assert cons[d]["comparable"] > 0 and cons[d]["text_equal"] == cons[d]["block_equal"] == cons[d]["action_equal"] == cons[d]["comparable"]
    assert cons["carrier_call_consistency"]["called_with_expected_arg"] > 1100


def test_manifest_checklist_records_selfcheck_but_stays_blocked(run, tmp_path, monkeypatch):
    st = tmp_path / "status.json"
    st.write_text(json.dumps({"INDEPENDENT_AUTHOR": "NOT_AVAILABLE", "H4_NEUTRAL_TWIN": "inert"}))  # test-only: the real file leaves H4 undecided
    monkeypatch.setattr(mf, "STATUS", st)
    sc = run["tmp"] / "selfcheck.json"
    _sh(run["root"], "scripts/e6_launcher.py", "selfcheck", "--out", str(sc))
    ev = json.loads(sc.read_text())
    assert ev["passed"] and ev["harness_tree_sha256"] != mf.NOT_SET
    m = mf.build_manifest(run["auth"], run["rendered"], selfcheck_path=sc)
    assert m["runner_support_verified"] and m["rendering_reproduced"] and m["plan_accounting"] == {"episodes": 1300, "A0R": 300, "NOINJ": 100}
    status = {i: ok for i, ok, _ in mf.checklist(m)}
    assert any("self-check" in i and ok for i, ok in status.items()) and not all(status.values())


def test_live_execution_is_refused_without_freeze_and_approval(run):
    r = _sh(run["root"], "scripts/e6_launcher.py", "live", "--rendered", str(run["rendered"]), check=False)
    assert r.returncode != 0 and "LIVE REFUSED" in (r.stdout + r.stderr)
