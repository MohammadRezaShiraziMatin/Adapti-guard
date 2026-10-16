"""Deterministic, zero-API replay: re-execute recorded tool calls in a fresh env, then evaluate security()."""
import json,sys
from agentdojo.task_suite.load_suites import get_suite
from agentdojo.functions_runtime import FunctionsRuntime, FunctionCall
def replay(f,verbose=False):
    e=json.load(open(f)); s=get_suite('v1.2.2',e['suite_name'])
    ut=s.get_user_task_by_id(e['user_task_id']); it=s.get_injection_task_by_id(e['injection_task_id'])
    env=s.load_and_inject_default_environment(e.get('injections') or {})
    env=ut.init_environment(env); pre=env.model_copy(deep=True)
    import random as _r
    otps=[c['args'].get('otp') for m in e['messages'] for c in ((m.get('tool_calls') or []) if m.get('tool_calls')!='None' else []) if 'otp' in c['args']]
    _orig=_r.choices
    def fake(pop,k=1,**kw):
        if k==6 and pop=='0123456789' and otps: return list(str(otps.pop(0)))
        return _orig(pop,k=k,**kw)
    _r.choices=fake  # OTP generation is random; feed the OTP the agent later submitted (assumes agent read the correct OTP)
    rt=FunctionsRuntime(s.tools); traces=[]
    for m in e['messages']:
        for c in (m.get('tool_calls') or []) if m.get('tool_calls')!='None' else []:
            fc=FunctionCall(function=c['function'],args=c['args'],id=c.get('id')); traces.append(fc)
            r,err=rt.run_function(env,c['function'],c['args'])
            if verbose: print(' ',c['function'],str(c['args'])[:80],'->',str(err or r)[:120])
    out=e['messages'][-1].get('content') or []
    txt=' '.join(b.get('content','') for b in out if isinstance(b,dict)) if isinstance(out,list) else str(out)
    st=it.security_from_traces(txt,pre,env,traces)
    sec=st if st is not None else it.security(txt,pre,env)
    return e.get('security'),sec,pre,env,it
if __name__=='__main__':
    for f in sys.argv[1:]:
        rec,sec,pre,env,it=replay(f,verbose=True); print('RECORDED',rec,'REPLAY',sec,f)
