"""Same logic as TaskSuite.check() (task_suite.py L423-480, 5353cf7) but each task wrapped in try/except
so one crash does not hide later tasks. check_injectable path skipped (see notes). Offline, no LLM."""
import json, traceback, warnings
warnings.filterwarnings("ignore")
from agentdojo.task_suite.load_suites import get_suites
from agentdojo.agent_pipeline.ground_truth_pipeline import GroundTruthPipeline
res = {}
for name, s in get_suites("v1").items():
    inj_defaults = s.get_injection_vector_defaults()
    env = s.load_and_inject_default_environment({k: f"---CANARY_{k}---" for k in inj_defaults})
    r = {"user": {}, "inj": {}}
    for ut in s.user_tasks.values():
        try:
            u, _ = s.run_task_with_pipeline(GroundTruthPipeline(ut), ut, injection_task=None, injections={}, environment=env.copy(deep=True))
            r["user"][ut.ID] = bool(u)
        except Exception as e:
            r["user"][ut.ID] = f"EXC {type(e).__name__}: {str(e)[:200]}"
    ut0 = next(iter(s.user_tasks.values()))
    for it in s.injection_tasks.values():
        try:
            _, sec = s.run_task_with_pipeline(GroundTruthPipeline(it), ut0, injection_task=it, injections={}, environment=env.copy(deep=True))
            r["inj"][it.ID] = bool(sec)
        except Exception as e:
            r["inj"][it.ID] = f"EXC {type(e).__name__}: {str(e)[:200]}"
    res[name] = r
    uf = {k: v for k, v in r["user"].items() if v is not True}; jf = {k: v for k, v in r["inj"].items() if v is not True}
    print(f"{name}: user {len(r['user'])-len(uf)}/{len(r['user'])} pass; inj {len(r['inj'])-len(jf)}/{len(r['inj'])} pass")
    for k, v in {**uf, **jf}.items(): print("   FAIL", k, str(v)[:160])
json.dump(res, open("c_items/taskSuite_check_pertask.json", "w"), indent=1)
