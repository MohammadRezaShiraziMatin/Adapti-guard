"""Item 2 (2026-10-16): execute each injection task's ground_truth() in default injected env; check security(). Zero API."""
import json,sys,io,contextlib,inspect,re
from agentdojo.task_suite.load_suites import get_suites
from agentdojo.functions_runtime import FunctionsRuntime, FunctionCall
import agentdojo; print('src',agentdojo.__file__,file=sys.stderr)
ver=sys.argv[1] if len(sys.argv)>1 else 'v1'; rows=[]
for sn,s in get_suites(ver).items():
    tools={t.name for t in s.tools}
    for iid,it in s.injection_tasks.items():
        r=dict(version=ver,suite=sn,inj=iid,goal=it.GOAL[:160])
        env=s.load_and_inject_default_environment({}); pre=env.model_copy(deep=True)
        try:
            gt=it.ground_truth(pre); r['gt_calls']=[(c.function,{k:str(v)[:60] for k,v in c.args.items()}) for c in gt]
            r['gt_unknown_tool']=[c.function for c in gt if c.function not in tools]
            rt=FunctionsRuntime(s.tools); errs=[]
            with contextlib.redirect_stdout(io.StringIO()):
                for c in gt:
                    _,err=rt.run_function(env,c.function,c.args); errs.append(err)
                st=it.security_from_traces('',pre,env,gt); sec=st if st is not None else it.security('',pre,env)
            r['gt_exec_errors']=[e for e in errs if e]; r['security_after_gt']=bool(sec)
        except Exception as ex: r['exc']=type(ex).__name__+':'+str(ex)[:100]
        src=inspect.getsource(type(it).security)+(inspect.getsource(type(it).security_from_traces) if 'security_from_traces' in type(it).__dict__ else '')
        r['sec_mentions_tools']=sorted(t for t in tools if re.search(r'\b'+t+r'\b',src))
        rows.append(r)
json.dump(rows,sys.stdout,indent=1)
