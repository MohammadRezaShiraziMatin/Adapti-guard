"""Run TaskSuite.check() on every AgentDyn v1 suite (local clone 5353cf7, installed editable). Offline, no LLM."""
import json, io, contextlib, traceback, subprocess
from agentdojo.task_suite.load_suites import get_suites
out = {"agentdyn_commit": subprocess.run(["git","-C","dyn","rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()}
for name, s in get_suites("v1").items():
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            ok, (ut, it) = s.check()
        out[name] = dict(ok=ok,
            user_fail={k: v[1] for k, v in ut.items() if not v[0]},
            n_user=len(ut), injection_fail=sorted(k for k, v in it.items() if not v), n_inj=len(it))
    except Exception as e:
        out[name] = dict(exception=f"{type(e).__name__}: {str(e)[:300]}", tb=traceback.format_exc()[-800:])
    print(name, {k: (v if k != 'tb' else '...') for k, v in out[name].items()})
json.dump(out, open("c_items/taskSuite_check.json","w"), indent=1)
