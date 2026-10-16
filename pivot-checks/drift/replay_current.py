"""Item 1 (2026-10-16): re-score released runs with CURRENT checker via deterministic replay (zero API).
Usage: PYTHONPATH=<src> python drift/replay_current.py <runs_root> <bench> <out.jsonl>"""
import json,glob,sys,io,contextlib,random,multiprocessing as mp
sys.setrecursionlimit(5000)
from agentdojo.task_suite.load_suites import get_suite
from agentdojo.functions_runtime import FunctionsRuntime, FunctionCall
import agentdojo; SRC=agentdojo.__file__
_orig=random.choices
SKIP_ERR=True  # Dev. 2026-10-16: skip calls whose logged tool response carries an error (blocked by defense / failed)
def calls(e):
    # pair tool responses to calls in order (ids can be null in old logs)
    tools=[m for m in e['messages'] if m.get('role')=='tool']; i=0
    for m in e['messages']:
        tc=m.get('tool_calls')
        if tc and tc!='None':
            for c in tc:
                er=tools[i].get('error') if i<len(tools) else None; i+=1
                if SKIP_ERR and er not in (None,'None',''): continue
                yield c
def one(f):
    p=f.split('/'); r=dict(file=f,pipe=p[2],suite=p[3],ut=p[4],attack=p[5])
    try: e=json.load(open(f))
    except Exception as ex: r['load_err']=repr(ex)[:80]; return r
    v=e.get('benchmark_version') or 'v1'
    r.update(inj=e.get('injection_task_id'),version=v,stored=e.get('security'),error=e.get('error'))
    try:
        s=get_suite(v,e['suite_name']); ut=s.get_user_task_by_id(e['user_task_id']); it=s.get_injection_task_by_id(e['injection_task_id'])
        env=s.load_and_inject_default_environment(e.get('injections') or {}); env=ut.init_environment(env); pre=env.model_copy(deep=True)
        cl=list(calls(e)); otps=[c['args'].get('otp') for c in cl if isinstance(c.get('args'),dict) and 'otp' in c['args']]
        def fake(pop,k=1,**kw):
            if k==6 and pop=='0123456789' and otps: return list(str(otps.pop(0)))
            return _orig(pop,k=k,**kw)
        random.choices=fake
        rt=FunctionsRuntime(s.tools); tr=[]
        with contextlib.redirect_stdout(io.StringIO()):
            for c in cl:
                tr.append(FunctionCall(function=c['function'],args=c['args'],id=c.get('id'))); rt.run_function(env,c['function'],c['args'])
            out=e['messages'][-1].get('content') or []
            txt=' '.join(b.get('content','') or '' for b in out if isinstance(b,dict)) if isinstance(out,list) else str(out)
            st=it.security_from_traces(txt,pre,env,tr)
            r['replay']=bool(st if st is not None else it.security(txt,pre,env))
    except Exception as ex: r['replay_err']=type(ex).__name__+':'+str(ex)[:80]
    finally: random.choices=_orig
    return r
if __name__=='__main__':
    root,bench,outp=sys.argv[1:4]
    fs=sorted(glob.glob(f'{root}/*/*/*/*/injection_task_*.json'))
    with mp.Pool(8) as pool, open(outp,'w') as o:
        o.write(json.dumps({'_meta':SRC})+'\n')
        for r in pool.imap(one,fs,chunksize=50): r['bench']=bench; o.write(json.dumps(r)+'\n')
