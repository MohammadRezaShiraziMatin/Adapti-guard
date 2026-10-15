"""Offline checks for the EXPLORATORY run mode and the campaign ledger of the v0.2 launcher. No network."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("launcher_expl", ROOT / "scripts" / "injecagent_executed_launcher_v02.py")
L = importlib.util.module_from_spec(_spec)
sys.modules["launcher_expl"] = L
_spec.loader.exec_module(L)

LEDGER = ROOT / "docs/research/CAMPAIGN_LEDGER.json"


def git(repo, *a):
    subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)


def mkrepo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@t")
    git(repo, "config", "user.name", "t")
    return repo


def commit_all(repo):
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "x")


def ledger_repo(tmp_path, r3_post=0.3, doc_amount="0.100000000", claimed_total=0.3):
    repo = mkrepo(tmp_path)
    (repo / "DOC.md").write_text(f"old key {doc_amount} USD\n")
    d = repo / "r3"
    d.mkdir()
    (d / "run_manifest.json").write_text(json.dumps({"status": "AUTH_MISMATCH", "pre_usage_usd": 0.1,
                                                     "post_usage_usd": 0.3, "spend_recorded_usd": 0.2}))
    led = {"total_prior_spend_usd": claimed_total, "entries": [
        {"id": "old", "spend_usd": 0.1, "verify": "document", "document": "DOC.md"},
        {"id": "R3", "spend_usd": 0.2, "verify": "manifest_settle", "run_dir": "r3", "pre_usage_usd": 0.1,
         "settle_reads": [{"usage_usd": r3_post}, {"usage_usd": r3_post}]}],
        "cap_decisions": [{"applies_to": "all", "cap_usd": 0.5}, {"applies_to": "exploratory", "cap_usd": 1.5}]}
    (repo / "ledger.json").write_text(json.dumps(led))
    commit_all(repo)
    return repo


def test_ledger_total_is_verified_and_used(tmp_path):
    repo = ledger_repo(tmp_path)
    assert L.campaign_budget_check(0.2, 1.5, (), repo, repo / "ledger.json", exploratory=True) == pytest.approx(0.3)


@pytest.mark.parametrize("kw,msg", [({"r3_post": 0.31}, "settled usage differs"),
                                    ({"doc_amount": "0.200000000"}, "does not appear"),
                                    ({"claimed_total": 0.25}, "ledger total says")])
def test_ledger_disagreeing_with_evidence_is_refused(tmp_path, kw, msg):
    repo = ledger_repo(tmp_path, **kw)
    with pytest.raises(L.LaunchError, match=msg):
        L.campaign_budget_check(0.01, 1.5, (), repo, repo / "ledger.json", exploratory=True)


def test_raised_cap_applies_to_exploratory_runs_only(tmp_path):
    repo = ledger_repo(tmp_path)
    with pytest.raises(L.LaunchError, match="exceeds the ledger cap 0.5"):
        L.campaign_budget_check(0.01, 1.5, (), repo, repo / "ledger.json", exploratory=False)


def test_ledger_plus_soft_cap_over_cap_is_refused(tmp_path):
    repo = ledger_repo(tmp_path)
    with pytest.raises(L.LaunchError, match="campaign cap exceeded"):
        L.campaign_budget_check(1.3, 1.5, (), repo, repo / "ledger.json", exploratory=True)


def test_ledger_and_prior_run_dirs_together_are_refused(tmp_path):
    repo = ledger_repo(tmp_path)
    with pytest.raises(L.LaunchError, match="not both"):
        L.campaign_budget_check(0.01, 1.5, (repo / "r3",), repo, repo / "ledger.json", exploratory=True)


def test_uncommitted_ledger_is_refused(tmp_path):
    repo = ledger_repo(tmp_path)
    (repo / "new.json").write_text((repo / "ledger.json").read_text())
    with pytest.raises(L.LaunchError, match="not committed"):
        L.campaign_budget_check(0.01, 1.5, (), repo, repo / "new.json", exploratory=True)


def test_committed_campaign_ledger_matches_run_evidence():
    assert L.ledger_prior_spend(LEDGER, ROOT, 1.5, exploratory=True) == pytest.approx(0.353967597, abs=1e-9)
    with pytest.raises(L.LaunchError):
        L.ledger_prior_spend(LEDGER, ROOT, 1.5, exploratory=False)


def test_run_name_argument():
    assert L.run_name_arg("R2") == "R2" and L.run_name_arg("EXPL-haiku") == "EXPL-haiku"
    for bad in ("R9", "EXPL-", "expl-x", "EXPL-a b"):
        with pytest.raises(Exception):
            L.run_name_arg(bad)


def _plan(tmp_path, **extra):
    plan = {"run": "EXPL-x", "exploratory": True, "label": "EXPLORATORY - test",
            "models": [{"model_id": "m/x", "route": "openrouter", "reasoning": {"enabled": False}}],
            "cases": [{"case_id": "c1", "kind": "dh", "messages": [], "tools": [], "attacker_tools": [],
                       "arms": {"A0": {"messages": [], "denied_tools": []}}}]}
    plan.update(extra)
    p = tmp_path / "plan.json"
    p.write_text(json.dumps(plan))
    return p


FLAGS = ["--soft-cap-usd", "0.05", "--http-cap", "1", "--estimate-usd", "0.01", "--run-label", "EXPL-x",
         "--expected-usage-usd", "0", "--usage-tolerance-usd", "0.01"]


def test_dry_run_exploratory_with_ledger(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(ROOT)
    rc = L.main(["--dry-run", "--plan", str(_plan(tmp_path)), "--out-root", str(tmp_path / "o"), "--run", "EXPL-x",
                 "--campaign-ledger", str(LEDGER), "--campaign-cap-usd", "1.5", *FLAGS])
    out = capsys.readouterr().out
    assert rc == 0 and "0.353967597" in out and "EXPLORATORY" in out


@pytest.mark.parametrize("argv_extra,plan_extra,msg", [
    (["--run", "EXPL-x"], {"exploratory": False}, "exploratory: true"),
    (["--run", "EXPL-y", "--campaign-ledger", "x"], {}, "differs from the plan"),
    (["--run", "EXPL-x"], {}, "needs --campaign-ledger"),
    (["--run", "R2"], {}, "only be run as --run EXPL-"),
    ([], {}, "only be run as --run EXPL-"),
])
def test_exploratory_mode_refusals(tmp_path, capsys, argv_extra, plan_extra, msg):
    rc = L.main(["--dry-run", "--plan", str(_plan(tmp_path, **plan_extra)), "--out-root", str(tmp_path / "o"),
                 *argv_extra, *FLAGS])
    assert rc == 2 and msg in capsys.readouterr().err


class _Client:
    def __init__(self):
        self.usage = iter([0.0, 0.01, 0.01])

    def key_usage(self):
        return next(self.usage)

    def chat(self, body):
        return 200, {"choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}], "usage": {"cost": 0.01}}


def test_exploratory_manifest_is_labelled(tmp_path, monkeypatch):
    repo = ledger_repo(tmp_path)
    monkeypatch.setattr(L, "checkpoint_progress", lambda *a, **k: "skipped")
    doc = repo / "DOC.md"
    s = L.RunSettings(models=(L.ModelSpec("m/x", "openrouter", {"enabled": False}),), run_label="EXPL-x",
                      soft_cap_usd=0.05, http_cap=1, estimate_usd=0.01, expected_usage_usd=0.0,
                      pre_usage_tolerance_usd=0.01, campaign_cap_usd=1.5, run_name="EXPL-x", exploratory=True,
                      campaign_ledger=repo / "ledger.json")
    case = L.Case("c1", "dh", [{"role": "user", "content": "hi"}], [], (), {"A0": {"messages": [{"role": "user", "content": "hi"}], "denied_tools": []}})
    res = L.run_study(_Client(), [case], s, repo / "out", repo, doc)
    m = json.loads((res.run_dir / "run_manifest.json").read_text())
    assert m["exploratory"] is True and "EXPLORATORY" in m["label"] and m["prior_spend_usd"] == pytest.approx(0.3)
