"""Minimal reproduction: run each v1 injection task's ground_truth() in the default
injected environment and evaluate its own security check. No network, no LLM calls.
Usage (inside an environment where AgentDyn's `agentdojo` package is importable):
    python repro_agentdyn_ground_truth.py
Expected: every task prints nothing (reference solution satisfies its own check).
Actual at AgentDyn commit 5353cf7: see the printed list."""
import io, contextlib
from agentdojo.task_suite.load_suites import get_suites
from agentdojo.functions_runtime import FunctionsRuntime
n = bad = 0
for name, s in get_suites("v1").items():
    for iid, it in s.injection_tasks.items():
        n += 1
        env = s.load_and_inject_default_environment({}); pre = env.model_copy(deep=True)
        gt = it.ground_truth(pre); rt = FunctionsRuntime(s.tools); errs = []
        for c in gt:
            with contextlib.redirect_stdout(io.StringIO()):
                _, e = rt.run_function(env, c.function, c.args)
            if e: errs.append(f"{c.function}: {str(e)[:60]}")
        st = it.security_from_traces("", pre, env, gt)
        ok = st if st is not None else it.security("", pre, env)
        if not ok:
            bad += 1
            print(f"{name}\t{iid}\tgt={[c.function for c in gt]}\terrors={errs}")
print(f"# {bad} of {n} injection tasks fail their own security check")
