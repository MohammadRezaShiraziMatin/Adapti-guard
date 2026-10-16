"""Probe why user-task ground truths fail check() in AgentDyn suites: replay GT calls, record tool results that look like errors/gates."""
import warnings, json; warnings.filterwarnings("ignore")
from agentdojo.task_suite.load_suites import get_suites
from agentdojo.functions_runtime import FunctionsRuntime
S=get_suites("v1"); res={}
for sn in ['shopping','github','dailylife','workspace']:
    s=S[sn]; env0=s.load_and_inject_default_environment(s.get_injection_vector_defaults()); rt=FunctionsRuntime(s.tools)
    for ut in s.user_tasks.values():
        pre=ut.init_environment(env0.copy(deep=True)); post=pre.copy(deep=True); notes=[]
        try:
            for c in ut.ground_truth(pre.copy(deep=True)):
                r,err=rt.run_function(post,c.function,dict(c.args))
                txt=str(err or r)
                if err or any(w in txt.lower() for w in ['otp','verify','not found','error','please login','incorrect','insufficient','required']):
                    notes.append(f"{c.function}: {txt[:110]}")
            u=ut.utility(getattr(ut,'GROUND_TRUTH_OUTPUT','') or '', pre, post)
        except Exception as e: u=f"EXC {type(e).__name__}"
        if u is not True: res[f"{sn}/{ut.ID}"]=dict(utility=str(u),gt_has_output=bool(getattr(ut,'GROUND_TRUTH_OUTPUT','')),notes=notes[:3])
for k,v in res.items(): print(k,v)
json.dump(res,open('c_items/usertask_probe.json','w'),indent=1)
