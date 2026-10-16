import json,sys; sys.path.insert(0,'attarg'); sys.path.insert(0,'rankflip')
from constants import consts, ovr_tokens
import scorer
rows=set()
for l in open('rankflip/episodes.jsonl'):
    r=json.loads(l); rows.add((r['version'],r['suite'],r['inj']))
tab={}; exc=[]
for v,s,i in sorted(rows):
    try: C=sorted(set(consts(v,s,i))|set(ovr_tokens(s,i)))
    except Exception as e: C=None; err=repr(e)[:80]
    if (s,i) in scorer.OVR: T=sorted({g for g,_ in scorer.OVR[(s,i)]})
    else:
        try:
            from agentdojo.task_suite.load_suites import get_suite
            su=get_suite(v,s); ut=next(iter(su.user_tasks))
            T=sorted({f for f,_,_ in scorer.gt({'suite_name':s,'user_task_id':ut,'injection_task_id':i,'injections':{}},v)})
        except Exception as e: T=[]
    k=f"{v}|{s}|{i}"; tab[k]=dict(constants=C,targets=T)
    if not C or not T: exc.append(k)
json.dump(dict(table=tab,excluded=exc),open('attarg/constant_table.json','w'),indent=1)
print(len(tab),'task-versions;',len(exc),'excluded'); print('\n'.join(exc))
