import json,glob,sys,collections,functools; sys.path.insert(0,'rankflip'); import scorer
sys_rl=__import__('sys').setrecursionlimit(5000)
_orig=scorer.gt
_gt=functools.lru_cache(None)(lambda v,s,u,i,inj: _orig({'suite_name':s,'user_task_id':u,'injection_task_id':i,'injections':json.loads(inj)},v))
scorer.gt=lambda e,v: _gt(v,e['suite_name'],e['user_task_id'],e['injection_task_id'],json.dumps(e.get('injections') or {},sort_keys=True))
out=open('rankflip/episodes.jsonl','w'); n=0
for bench,root in [('agentdojo','ad/runs'),('agentdyn','dyn/runs')]:
    for f in sorted(glob.glob(f'{root}/*/*/*/*/injection_task_*.json')):
        p=f.split('/'); pipe,suite,ut,att=p[2:6]
        try: e=json.load(open(f))
        except Exception: continue
        v=e.get('benchmark_version') or 'v1'
        try: a,c,g=scorer.score(e,v); se=None
        except Exception as ex: a=c=None; se=repr(ex)[:100]
        out.write(json.dumps(dict(bench=bench,pipe=pipe,suite=suite,ut=ut,inj=e['injection_task_id'],attack=att,version=v,
          executed=e.get('security'),error=e.get('error'),attempted=a,correct=c,score_err=se))+'\n'); n+=1
print(n)
