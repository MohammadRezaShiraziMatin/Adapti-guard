import sys,json,warnings,traceback,io,contextlib,os; warnings.filterwarnings("ignore")
SRC,OUT=sys.argv[1],sys.argv[2]; sys.path.insert(0,SRC)
import agentdojo; assert agentdojo.__file__.startswith(os.path.abspath(SRC)),agentdojo.__file__
from agentdojo.task_suite.load_suites import _SUITES
from agentdojo.agent_pipeline.ground_truth_pipeline import GroundTruthPipeline
res={'src':SRC,'agentdojo_file':agentdojo.__file__}; seen={}
for ver,suites in _SUITES.items():
  for sn,s in suites.items():
    key=f'{ver}|{sn}'; ids=id(s)
    if ids in seen: res[key]={'same_object_as':seen[ids]}; continue
    seen[ids]=key; r={}
    try:
        with contextlib.redirect_stdout(io.StringIO()): ok,(u,i)=s.check()
        r['check']={'ok':ok,'inj_fail':[k for k,v in i.items() if not v],'user_not_injectable':sum(1 for v in u.values() if v[1]=='The task is not injectable'),'n_user':len(u)}
    except Exception as e: r['check']={'exception':f'{type(e).__name__}: {str(e)[:200]}'}
    try:
        env=s.load_and_inject_default_environment({k:f'---CANARY_{k}---' for k in s.get_injection_vector_defaults()})
        it_res={}; ut0=next(iter(s.user_tasks.values()))
        for it in s.injection_tasks.values():
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    _,sec=s.run_task_with_pipeline(GroundTruthPipeline(it),ut0,injection_task=it,injections={},environment=env.copy(deep=True))
                it_res[it.ID]=bool(sec)
            except Exception as e: it_res[it.ID]=f'EXC {type(e).__name__}: {str(e)[:160]}'
        u_res={}
        for ut in s.user_tasks.values():
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    ok,_=s.run_task_with_pipeline(GroundTruthPipeline(ut),ut,injection_task=None,injections={},environment=env.copy(deep=True))
                u_res[ut.ID]=bool(ok)
            except Exception as e: u_res[ut.ID]=f'EXC {type(e).__name__}'
        r['inj']=it_res; r['user']=u_res
    except Exception as e: r['pertask_exception']=f'{type(e).__name__}: {str(e)[:200]}'
    res[key]=r
    f=lambda d:(sum(v is True for v in d.values()),len(d))
    print(key,'check:',r['check'].get('ok',r['check'].get('exception','')[:60]),'| inj pass %d/%d'%f(r.get('inj',{})),'| user pass %d/%d'%f(r.get('user',{})),
          '| fails:',{k:v for k,v in r.get('inj',{}).items() if v is not True})
json.dump(res,open(OUT,'w'),indent=1)
