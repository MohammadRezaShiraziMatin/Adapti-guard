"""ATT-ARG validation sample per attarg/PROCEDURE_ATTARG.md. seed 20261017, 10 per (defense x ATT-ARG label), n=80,
excluding episodes already in bitems/scorer_validation. Blind file shows goal + tool calls only (no defense, no labels)."""
import json,random,os,warnings; warnings.filterwarnings("ignore")
from agentdojo.task_suite.load_suites import get_suite
R=json.load(open('rankflip/results.json')); flipcells={c['cell'][1] for c in R if c['cell'][0]=='agentdyn' and c['ATT']['nflip']>0}
old={(k['pipe'],k['suite'],k['ut'],k['inj']) for k in json.load(open('bitems/scorer_validation/KEY_DO_NOT_OPEN/key.json'))}
rows=[json.loads(l) for l in open('attarg/episodes_attarg.jsonl')]
rng=random.Random(20261017); key=[]
for d in ['progent','drift','tool_filter','repeat_user_prompt']:
    pop=[r for r in rows if r['bench']=='agentdyn' and r['attack']=='important_instructions' and r['attarg'] is not None
         and any(r['pipe']==f"{m}-{d}" for m in flipcells) and (r['pipe'],r['suite'],r['ut'],r['inj']) not in old]
    for s in [True,False]:
        st=sorted([r for r in pop if r['attarg'] is s],key=lambda r:(r['pipe'],r['suite'],r['ut'],r['inj']))
        for r in rng.sample(st,10): key.append(dict(defense=d,pop_stratum=len(st),pop_defense=len(pop),**r))
rng.shuffle(key); blind=[]
for i,k in enumerate(key):
    k['sid']=f"A{i:03d}"; f=f"dyn/runs/{k['pipe']}/{k['suite']}/{k['ut']}/{k['attack']}/{k['inj']}.json"; k['path']=f
    e=json.load(open(f)); goal=get_suite(k['version'],k['suite']).get_injection_task_by_id(k['inj']).GOAL
    calls=[(c['function'],json.dumps(c.get('args'),default=str)[:400]) for m in e['messages'] if m.get('role')=='assistant' and m.get('tool_calls') not in (None,'None') for c in m['tool_calls']]
    blind.append(dict(sid=k['sid'],suite=k['suite'],injection_goal=goal,calls=calls))
os.makedirs('attarg/validation/KEY_DO_NOT_OPEN',exist_ok=True)
json.dump(key,open('attarg/validation/KEY_DO_NOT_OPEN/key.json','w'),indent=1)
with open('attarg/validation/blind_render.txt','w') as o:
    for b in sorted(blind,key=lambda b:b['sid']):
        o.write(f"## {b['sid']} {b['suite']} GOAL: {b['injection_goal'][:240]}\n")
        for fn,a in b['calls']: o.write(f"   {fn} {a[:200]}\n")
print(len(key))
