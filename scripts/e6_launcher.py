"""E6 launcher around the harness-native runner (offline/mock by default; live execution is guarded and cannot run today).

The runner `scripts/run_harness_v2_pilot.py` is NOT edited. The launcher patches the E6 interfaces at runtime and restores them:
  * `_episode_id`: appends `/r1` for the A0 replicate (the plan row carries `replicate`);
  * scenario registries: the rendered attack and `<family>__noinj` ids are added to the catalog and delivery registries;
  * `load_templates` / `templates_sha256`: return the rendered scenario file and its scenario-set hash instead of the E3 template files;
  * `CRITERIA` / `PREREG`: point at the E6 protocol file, so the runner never needs the private approval document and records the
    protocol hash as its criteria hash;
  * the pilot-label check (`harness_v2_pilot_N`) is bypassed.
Before any run it verifies the system prompt and tool hashes against `e6/harness_constants.json`. A live run is refused unless the
freeze checklist is complete, the owner's approval record exists with budget caps, and an API key is present.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import e6_manifest  # noqa: E402
import e6_render  # noqa: E402
import e6_run_plan  # noqa: E402

PROTOCOL_REL = "docs/paper/negative_result/PROTOCOL_CONFIRMATORY_E6_DRAFT.md"
PILOT_LABEL = "e6_confirmatory"
MODEL_ALIAS = "deepseek"
MODEL_ID = "deepseek/deepseek-v3.2"


def load_runner(root: Path = ROOT):
    spec = importlib.util.spec_from_file_location("run_harness_v2_pilot", root / "scripts/run_harness_v2_pilot.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def harness_constants_report(root: Path = ROOT) -> dict:
    """Recompute the system-prompt and tools hashes from the importable harness and compare them with e6/harness_constants.json."""
    from adapti_guard.evaluation.harness_v2.tool_definitions import HARNESS_V2_SYSTEM_PROMPT, HARNESS_V2_TOOLS
    exp = json.loads((root / "e6/harness_constants.json").read_text())
    got = {"system_prompt_sha256": hashlib.sha256(HARNESS_V2_SYSTEM_PROMPT.encode()).hexdigest(),
           "tools_sha256": hashlib.sha256(e6_render.canonical_bytes(HARNESS_V2_TOOLS)).hexdigest(),
           "tool_names": [t["function"]["name"] for t in HARNESS_V2_TOOLS]}
    return {**got, "matches": all(got[k] == exp[k] for k in got)}


def e6_episode_id(row: dict) -> str:
    base = f"{row['scenario_id']}/i{row['instance_index']}/{row['family']}/{row['condition']}"
    return base + ("/r1" if row.get("replicate") else "")


@contextlib.contextmanager
def install_e6(runner, rendered: dict, protocol_path: Path):
    """Patch the runner and harness registries for E6 and restore everything on exit."""
    from adapti_guard.evaluation.harness_v2 import delivery_verification as dv
    from adapti_guard.evaluation.harness_v2 import scenario_catalog as cat
    ids = tuple(sorted(rendered["scenarios"]))
    set_sha = e6_render.rendered_sha256(rendered)
    saved = {"cat": (cat.ALL_ATTACK_SCENARIOS, cat.INDEPENDENT_ATTACK_SCENARIOS), "dv_all": dv.ALL_ATTACK_SCENARIOS,
             "dv_dicts": (dict(dv.DELIVERY_CHANNELS), dict(dv.PREREQUISITE_TOOL)),
             "runner": {k: getattr(runner, k) for k in ("_episode_id", "load_templates", "templates_sha256", "CRITERIA", "PREREG", "pilot_number_from_label")}}
    try:
        cat.ALL_ATTACK_SCENARIOS = tuple(cat.ALL_ATTACK_SCENARIOS) + ids
        cat.INDEPENDENT_ATTACK_SCENARIOS = tuple(cat.INDEPENDENT_ATTACK_SCENARIOS) + ids
        dv.ALL_ATTACK_SCENARIOS = cat.ALL_ATTACK_SCENARIOS
        for sid, b in rendered["scenarios"].items():
            dv.DELIVERY_CHANNELS[sid] = ("tool",)
            dv.PREREQUISITE_TOOL[sid] = b["channel"]
        runner._episode_id = e6_episode_id
        runner.load_templates = lambda *a, **k: rendered
        runner.templates_sha256 = lambda *a, **k: set_sha
        runner.CRITERIA = runner.PREREG = str(protocol_path)
        runner.pilot_number_from_label = lambda label: 0
        yield
    finally:
        cat.ALL_ATTACK_SCENARIOS, cat.INDEPENDENT_ATTACK_SCENARIOS = saved["cat"]
        dv.ALL_ATTACK_SCENARIOS = saved["dv_all"]
        dv.DELIVERY_CHANNELS.clear(), dv.DELIVERY_CHANNELS.update(saved["dv_dicts"][0])
        dv.PREREQUISITE_TOOL.clear(), dv.PREREQUISITE_TOOL.update(saved["dv_dicts"][1])
        for k, v in saved["runner"].items():
            setattr(runner, k, v)


def defense_factories() -> dict:
    """Fresh real pre-target defenses (one per replayed episode), for the diagnostic replay."""
    from adapti_guard.evaluation.harness_v2.harness_v2_b3_pretarget_wrapper import HarnessV2B3EpisodeContext
    return {c: (lambda c=c: HarnessV2B3EpisodeContext.for_condition(c).defense_fn) for c in ("B3", "CORE")}


def executor_factory(sid: str, rec: dict):
    from adapti_guard.evaluation.harness_v2.scenario_catalog import build_mock_executor_config
    from adapti_guard.evaluation.harness_v2.scenario_mock_executor import ScenarioMockToolExecutor
    return ScenarioMockToolExecutor(scenario_id=sid, config=build_mock_executor_config(sid, rec))


class MockTransport:
    """Offline stand-in for the provider: follows the injection exactly when its full carrier text reaches the model (plumbing test only).

    No API call is made. A scripted 'model' calls the carrier tool, then, if the tool message contains the attack twin's complete
    carrier text and a deterministic coin allows it, makes the attacker-specified call; otherwise it answers. Instances listed in
    `error_prompts` return a provider error so the error paths can be exercised.
    """

    def __init__(self, rendered: dict, rate: float = 0.6, error_prompts: frozenset = frozenset()):
        import httpx  # local import: only the mock needs it
        self.httpx = httpx
        self.rate, self.error_prompts, self.requests = rate, error_prompts, 0
        self.index = {}
        for sid, b in rendered["scenarios"].items():
            if b["kind"] == "attack":
                for r in b["instances"]:
                    self.index[self._norm(r["user_prompt"])] = (b, r)

    @staticmethod
    def _norm(s: str) -> str:
        return s.rstrip(" .")

    def _calls(self, name, args, n):
        return {"id": f"call_{n}", "choices": [{"message": {"role": "assistant", "content": "", "tool_calls": [
            {"id": f"call_{n}", "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}]}, "finish_reason": "tool_calls"}],
            "usage": {"prompt_tokens": 20, "completion_tokens": 10, "cost": 0.00017}}

    def _stop(self, n):
        return {"id": f"gen-{n}", "choices": [{"message": {"role": "assistant", "content": "Done."}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 20, "completion_tokens": 6, "cost": 0.00017}}

    def respond(self, body: dict):
        self.requests += 1
        msgs = body["messages"]
        user = next((m for m in msgs if m["role"] == "user"), {"content": ""})["content"]
        hit = self.index.get(self._norm(user))
        if hit is None:
            return self._stop(self.requests)
        b, r = hit
        if self._norm(user) in self.error_prompts:
            return {"error": {"message": "mock gateway timeout", "code": 504}}
        done = [c["function"]["name"] for m in msgs if m["role"] == "assistant" for c in m.get("tool_calls") or []]
        tools = [m for m in msgs if m["role"] == "tool"]
        if not done:
            return self._calls(r["prerequisite_tool"], {{"retrieve_document": "doc_id", "get_weather": "city"}[r["prerequisite_tool"]]: r["prerequisite_arg"]}, self.requests)
        carrier = r["injection_doc_body"] or r["weather_poison_suffix"]
        coin = int(hashlib.sha256(r["marker"].encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
        if r["attack_tool"] not in done and tools and carrier in (tools[-1].get("content") or "") and coin < self.rate:
            free = [p for p in e6_render.TOOL_PARAMS[r["attack_tool"]] if p not in r["required_args"]][0]
            return self._calls(r["attack_tool"], {**r["required_args"], free: f"forwarding {r['marker']}"}, self.requests)
        return self._stop(self.requests)

    def make(self):
        outer = self

        class T(self.httpx.AsyncBaseTransport):
            async def handle_async_request(self, request):
                return outer.httpx.Response(200, json=outer.respond(json.loads(request.content)))
        return T()


def build_plan(rendered: dict, m: dict | None = None) -> tuple[list, int]:
    ids = [sid for sid, b in rendered["scenarios"].items() if b["kind"] == "attack"]
    seed = e6_run_plan.seed_from_hashes(e6_render.rendered_sha256(rendered), e6_manifest.sha(e6_manifest.SCHEMA), e6_manifest.analysis_sha())
    return e6_run_plan.make_plan(ids, rendered["instances_per_scenario"], seed), seed


def assert_live_allowed(manifest: dict) -> None:
    items = e6_manifest.checklist(manifest)
    missing = [i for i, ok, _ in items if not ok]
    appr = json.loads(e6_manifest.APPROVAL.read_text()) if e6_manifest.APPROVAL.is_file() else {}
    caps = appr.get("budget_authorization") or {}
    if missing or not (isinstance(caps.get("usd_soft_cap"), (int, float)) and isinstance(caps.get("http_hard_cap"), int)):
        raise SystemExit("LIVE REFUSED: freeze checklist incomplete or approval record without budget caps:\n- " + "\n- ".join(missing or ["budget caps"]))
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit("LIVE REFUSED: OPENROUTER_API_KEY not set")


def run_e6(plan: list, rendered: dict, out_dir: Path, *, usd_cap: float, http_cap: int, transport=None, root: Path = ROOT,
           manifest: dict | None = None, live: bool = False, wall_timeout_s=None, rate_limit_backoffs=None) -> dict:
    report = harness_constants_report(root)
    if not report["matches"]:
        raise SystemExit("harness system prompt or tools differ from e6/harness_constants.json: " + json.dumps(report))
    runner = load_runner(root)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "e6_plan.json").write_bytes(e6_render.canonical_bytes(plan))
    (out_dir / "e6_rendered.json").write_bytes(e6_render.canonical_bytes(rendered))
    sm = root / "SANITIZED_MANIFEST.json"
    run_manifest = {**(manifest or {}), "plan_file_sha256": e6_run_plan.plan_sha256(plan), "episodes": len(plan), "usd_cap": usd_cap, "http_cap": http_cap,
                    "model_id": MODEL_ID, "harness_constants_check": report, "runner_script_sha256": e6_manifest.sha(root / "scripts/run_harness_v2_pilot.py"),
                    "launcher_script_sha256": e6_manifest.sha(root / "scripts/e6_launcher.py"),
                    "harness_tree_sha256": json.loads(sm.read_text())["tree_sha256"] if sm.is_file() else e6_manifest.NOT_SET, "mode": "live" if live else "mock"}
    (out_dir / "e6_manifest.json").write_text(json.dumps(run_manifest, indent=1, sort_keys=True, default=str) + "\n")
    from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop
    with install_e6(runner, rendered, root / PROTOCOL_REL):
        async def main():
            return await runner.run_pilot_async(out_dir, pilot_label=PILOT_LABEL, usd_cap=usd_cap, http_cap_override=http_cap, http_transport=transport,
                                                schedule_override=plan, skip_preflight=True, reconcile_at_end=live, wall_timeout_s=wall_timeout_s,
                                                rate_limit_backoffs=rate_limit_backoffs)
        summary = run_harness_event_loop(main)
    log = out_dir / "progress.log"  # `*.log` is git-ignored in the project; keep a committable copy
    if log.is_file():
        (out_dir / "progress_log.txt").write_bytes(log.read_bytes())
    return summary


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    mk = sub.add_parser("mock", help="offline end-to-end run on the mock transport (no API)")
    mk.add_argument("--authoring", type=Path, required=True)
    mk.add_argument("--h4-policy", choices=e6_render.H4_POLICIES, required=True)
    mk.add_argument("--out", type=Path, required=True)
    mk.add_argument("--limit", type=int, help="run only the first N plan entries (smoke)")
    mk.add_argument("--error-instances", type=int, default=0, help="inject provider errors into N instances (exercise error paths)")
    sub.add_parser("selfcheck", help="verify harness constants and registry patching offline").add_argument("--out", type=Path)
    rp = sub.add_parser("replay", help="offline diagnostic replay (never a gate) on the rendered scenarios; optional post-run consistency")
    rp.add_argument("--rendered", type=Path, required=True)
    rp.add_argument("--out", type=Path, required=True, help="pre-run replay summary (its file hash is the manifest's replay hash)")
    rp.add_argument("--episodes", type=Path, help="live or mock episodes.jsonl for the post-run consistency check")
    rp.add_argument("--post-run-out", type=Path)
    lv = sub.add_parser("live", help="guarded; refuses unless frozen, approved and keyed")
    lv.add_argument("--rendered", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.cmd == "selfcheck":
        rep = harness_constants_report()
        runner = load_runner()
        probe = {"instances_per_scenario": 1, "scenarios": {"x": {"kind": "attack", "family_id": "x", "channel": "retrieve_document", "instances": []}}}
        with install_e6(runner, probe, ROOT / PROTOCOL_REL):
            patched = runner._episode_id({"scenario_id": "x", "instance_index": 0, "family": "deepseek", "condition": "A0", "replicate": 1}) == "x/i0/deepseek/A0/r1"
        restored = runner._episode_id({"scenario_id": "x", "instance_index": 0, "family": "deepseek", "condition": "A0"}) == "x/i0/deepseek/A0"
        res = {"harness_constants": rep, "episode_id_patch": patched, "patch_restored": restored,
               "passed": bool(rep["matches"] and patched and restored),
               "harness_tree_sha256": json.loads((ROOT / "SANITIZED_MANIFEST.json").read_text())["tree_sha256"] if (ROOT / "SANITIZED_MANIFEST.json").is_file() else e6_manifest.NOT_SET}
        if a.out:
            a.out.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
        print(json.dumps(res, indent=1))
        return 0 if res["passed"] else 1
    if a.cmd == "replay":
        import e6_replay
        rendered = json.loads(a.rendered.read_text())
        facs = defense_factories()
        rows = e6_replay.diagnostic_rows(e6_replay.units_from_rendered(rendered, executor_factory), facs)
        pre = {"replay_sha256": e6_replay.replay_sha256(rows), "scenario_set_sha256": e6_render.rendered_sha256(rendered), "summary": e6_replay.summarize(rows),
               "gate": "none: diagnostic only"}
        a.out.write_text(json.dumps(pre, indent=1, sort_keys=True) + "\n")
        if a.episodes:
            eps = [json.loads(x) for x in a.episodes.read_text().splitlines() if x.strip()]
            a0 = [r for r in eps if r.get("arm") == "A0"]
            post = {d: e6_replay.consistency(a0, [r for r in eps if r.get("arm") == d], facs[d]) for d in ("B3", "CORE")}
            post["carrier_call_consistency"] = e6_replay.carrier_call_consistency([r for r in eps if r.get("arm") != "NOINJ"], rendered)
            if a.post_run_out:
                a.post_run_out.write_text(json.dumps(post, indent=1, sort_keys=True, default=str) + "\n")
            print(json.dumps({"pre": pre["summary"], "post": {k: {x: v for x, v in d.items() if x != "mismatch_examples"} for k, d in post.items()}}, default=str)[:1500])
        else:
            print(json.dumps(pre["summary"])[:1500])
        return 0
    if a.cmd == "live":
        rendered = json.loads(a.rendered.read_text())
        assert_live_allowed(e6_manifest.build_manifest(rendered_path=a.rendered))
        raise SystemExit("live execution is not implemented in this offline build; it requires the frozen public harness and owner approval")
    pack = json.loads(a.authoring.read_text())
    rep = e6_render.validate_authoring(pack, h4_policy=a.h4_policy)
    if not rep["structure_ok"]:
        raise SystemExit("authoring pack invalid: " + json.dumps(rep["errors"][:5]))
    rendered = e6_render.render(pack, a.h4_policy)
    plan, seed = build_plan(rendered)
    if a.limit:
        plan = plan[:a.limit]
    errs = frozenset()
    if a.error_instances:
        att = [r for b in rendered["scenarios"].values() if b["kind"] == "attack" for r in b["instances"]]
        errs = frozenset(MockTransport._norm(r["user_prompt"]) for r in att[:a.error_instances])
    tr = MockTransport(rendered, error_prompts=errs)
    manifest = {"seed": seed, "scenario_set_sha256": e6_render.rendered_sha256(rendered), "scoring_schema_sha256": e6_manifest.sha(e6_manifest.SCHEMA),
                "analysis_sha": e6_manifest.analysis_sha(), "authoring_sha256": rep["authoring_sha256"], "h4_policy": a.h4_policy,
                "synthetic_pack": rep["synthetic"], "protocol_sha256": e6_manifest.sha(ROOT / PROTOCOL_REL)}
    summary = run_e6(plan, rendered, a.out, usd_cap=1.5, http_cap=6000, transport=tr.make(), manifest=manifest,
                     wall_timeout_s=5.0, rate_limit_backoffs=(0.0, 0.0))
    print(json.dumps({"stopped_reason": summary["stopped_reason"], "episodes": len(summary["episodes"]), "http_used": summary["http_used"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
