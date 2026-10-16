"""Stratified sample for ATTEMPTED-scorer validation. Seed 20261016. Population: AgentDyn episodes (full data, all
suites) in the ATT flip cells (rankflip/results.json, full data) for defenses progent and drift.
Strata per defense: scorer ATT True / False, N_PER episodes each. Blind file hides executed/attempted/correct.
Key file is written separately and must not be opened until labels are hash-locked."""
import json, random, os
SEED, N_PER = 20261016, 20
R = json.load(open('rankflip/results.json'))
flipcells = {c['cell'][1] for c in R if c['cell'][0]=='agentdyn' and c['ATT']['nflip'] > 0}
rows=[json.loads(l) for l in open('rankflip/episodes.jsonl')]
rng = random.Random(SEED); blind=[]; key=[]
for d in ['progent','drift']:
    pop=[r for r in rows if r['bench']=='agentdyn' and r['attack']=='important_instructions' and r['score_err'] is None
         and any(r['pipe']==f"{m}-{d}" for m in flipcells)]
    for s in [True, False]:
        st=sorted([r for r in pop if r['attempted'] is s], key=lambda r:(r['pipe'],r['suite'],r['ut'],r['inj']))
        pick=rng.sample(st, N_PER)
        for r in pick: key.append(dict(defense=d, stratum_scorer_att=s, pop_stratum=len(st), pop_defense=len(pop), **r))
rng.shuffle(key)
for i,k in enumerate(key):
    k['sid']=f"S{i:03d}"
    f=f"dyn/runs/{k['pipe']}/{k['suite']}/{k['ut']}/{k['attack']}/{k['inj']}.json"
    e=json.load(open(f)); k['path']=f
    from agentdojo.task_suite.load_suites import get_suite
    goal=get_suite('v1',k['suite']).get_injection_task_by_id(k['inj']).GOAL
    tr=[]
    for m in e['messages']:
        if m.get('role')=='assistant' and m.get('tool_calls') not in (None,'None'):
            for c in m['tool_calls']: tr.append(('CALL', c['function'], json.dumps(c.get('args'),default=str)[:300]))
        elif m.get('role')=='tool':
            c=m.get('content'); c=c if isinstance(c,str) else json.dumps(c,default=str)
            tr.append(('RESULT', '', (c or '')[:160].replace('\n',' ')))
    blind.append(dict(sid=k['sid'], defense=k['defense'], suite=k['suite'], injection_goal=goal, trace=tr))
os.makedirs('bitems/scorer_validation/KEY_DO_NOT_OPEN', exist_ok=True)
json.dump(key, open('bitems/scorer_validation/KEY_DO_NOT_OPEN/key.json','w'), indent=1)
with open('bitems/scorer_validation/blind.jsonl','w') as f:
    for b in sorted(blind,key=lambda b:b['sid']): f.write(json.dumps(b)+'\n')
print("flip cells:", sorted(flipcells)); print("n blind:", len(blind))
