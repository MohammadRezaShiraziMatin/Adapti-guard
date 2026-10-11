"""Tests for the settled post-run /auth/key read in scripts/injecagent_executed_launcher_v02.py.

Offline: the clients are in-process fakes and sleep is injected or set to zero, so nothing waits and nothing touches the
network. The run_study test builds the same temporary git repository as tests/test_injecagent_executed_launcher_v02.py.
The run_study test passes the settle fields only when the launcher defines them, so it also runs against the launcher as
it was before the settled read. There it fails on the value it recorded, not on a TypeError."""
import dataclasses
import datetime as dt
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("launcher", ROOT / "scripts" / "injecagent_executed_launcher_v02.py")
L = importlib.util.module_from_spec(_spec)
sys.modules["launcher"] = L  # dataclasses look the module up by name while it is being executed
_spec.loader.exec_module(L)

FIXED = dt.datetime(2026, 10, 11, 12, 0, 0, tzinfo=dt.timezone.utc)
TOOLS = [
    {"type": "function", "function": {"name": "read_doc"}},
    {"type": "function", "function": {"name": "send_email"}},
]
MODEL = L.ModelSpec("provider/model-x", "route-a", {"enabled": False})


class Reads:
    """Scripted /auth/key readings. Each call returns the next value and counts the call."""

    def __init__(self, values):
        self.values = list(values)
        self.calls = 0

    def key_usage(self):
        self.calls += 1
        return self.values.pop(0)


def no_sleep(seconds):
    raise AssertionError(f"sleep({seconds}) must not be called here")


def recording_sleep(log):
    return lambda seconds: log.append(seconds)


# ---------- settled_key_usage on its own (injected sleep, no network) ----------

def test_lagging_usage_settles_on_the_third_read():
    reads, sleeps = Reads([0.5, 0.6, 0.6]), []
    got = L.settled_key_usage(reads, 600.0, 3, sleep=recording_sleep(sleeps))
    assert got == 0.6
    assert reads.calls == 3
    assert sleeps == [600.0, 600.0]


def test_stable_usage_settles_on_the_second_read():
    reads, sleeps = Reads([0.5, 0.5]), []
    got = L.settled_key_usage(reads, 600.0, 3, sleep=recording_sleep(sleeps))
    assert got == 0.5
    assert reads.calls == 2
    assert sleeps == [600.0]


def test_differences_within_one_micro_usd_count_as_stable():
    reads = Reads([0.5, 0.5 + 5e-7])
    assert L.settled_key_usage(reads, 600.0, 3, sleep=recording_sleep([])) == 0.5 + 5e-7
    assert reads.calls == 2


def test_never_stable_raises_after_max_reads():
    reads, sleeps = Reads([0.1, 0.2, 0.3]), []
    with pytest.raises(L.LaunchError, match="not stable after 3 reads"):
        L.settled_key_usage(reads, 600.0, 3, sleep=recording_sleep(sleeps))
    assert reads.calls == 3
    assert sleeps == [600.0, 600.0]


def test_single_read_keeps_previous_behaviour():
    reads = Reads([0.1, 0.9])  # would never be stable, but one read means no stability check
    assert L.settled_key_usage(reads, 600.0, 1, sleep=no_sleep) == 0.1
    assert reads.calls == 1


# ---------- run_study: the value recorded after a run ----------

def make_case(cid):
    return L.Case(cid, "dh", [{"role": "user", "content": "hi"}], TOOLS, ("send_email",),
                  {"A0": {"messages": [{"role": "user", "content": "hi"}], "denied_tools": []}})


def make_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    shutil.copy(ROOT / ".gitignore", repo / ".gitignore")
    (repo / "doc.md").write_text("protocol draft\n")
    git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false"]
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(git + ["add", "."], check=True)
    subprocess.run(git + ["commit", "-q", "-m", "init"], check=True)
    return repo


class OneEpisodeClient(L.Client):
    """One model call that costs 0.1 USD and makes no tool call. /auth/key returns scripted readings."""

    def __init__(self, usage):
        self.usage = list(usage)

    def chat(self, body):
        return 200, {"choices": [{"finish_reason": "stop", "message": {"tool_calls": []}}],
                     "usage": {"cost": 0.1}}

    def key_usage(self):
        return self.usage.pop(0) if len(self.usage) > 1 else self.usage[0]


def settle_fields(**wanted):
    """The settle fields, kept only where this launcher defines them (see the module docstring)."""
    fields = {f.name for f in dataclasses.fields(L.RunSettings)}
    return {k: v for k, v in wanted.items() if k in fields}


def test_run_records_the_settled_post_run_usage_not_the_early_one(tmp_path):
    # usage: pre-run 1.0; the first post-run read 1.05 is still settling; reads 2 and 3 agree at 1.10.
    client = OneEpisodeClient([1.0, 1.05, 1.10, 1.10])
    s = L.RunSettings(models=(MODEL,), run_label="lbl", soft_cap_usd=1.0, http_cap=10, estimate_usd=0.1,
                      expected_usage_usd=1.0, pre_usage_tolerance_usd=0.01, seed=7, campaign_cap_usd=10.0,
                      **settle_fields(settle_wait_s=0.0, settle_max_reads=3))
    repo = make_repo(tmp_path)
    try:
        res = L.run_study(client, [make_case("c1")], s, tmp_path / "runs", repo, repo / "doc.md",
                          now=lambda: FIXED, command_line=())
    except L.LaunchError as exc:
        pytest.fail(f"the run was refused, so the early post-run value was recorded and checked: {exc}")
    post = json.loads((res.run_dir / "auth_key_post.json").read_text())["usage_usd"]
    manifest = json.loads((res.run_dir / "run_manifest.json").read_text())
    assert res.status == "COMPLETE"
    assert post == pytest.approx(1.10)
    assert manifest["post_usage_usd"] == pytest.approx(1.10)
