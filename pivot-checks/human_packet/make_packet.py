import json,random,os,warnings,hashlib; warnings.filterwarnings("ignore")
os.chdir('/workspace/pivot-checks')
from agentdojo.task_suite.load_suites import get_suite
R=json.load(open('rankflip/results.json')); flip={c['cell'][1] for c in R if c['cell'][0]=='agentdyn' and c['ATT']['nflip']>0}
old={(k['pipe'],k['suite'],k['ut'],k['inj']) for f in ['bitems/scorer_validation/KEY_DO_NOT_OPEN/key.json','attarg/validation/KEY_DO_NOT_OPEN/key.json'] for k in json.load(open(f))}
rows=[json.loads(l) for l in open('attarg/episodes_attarg.jsonl')]
rng=random.Random(20261018); key=[]
for d in ['progent','drift','tool_filter','repeat_user_prompt']:
    pop=[r for r in rows if r['bench']=='agentdyn' and r['attack']=='important_instructions' and r['attarg'] is not None
         and any(r['pipe']==f"{m}-{d}" for m in flip) and (r['pipe'],r['suite'],r['ut'],r['inj']) not in old]
    for s in [True,False]:
        st=sorted([r for r in pop if r['attarg'] is s],key=lambda r:(r['pipe'],r['suite'],r['ut'],r['inj']))
        for r in rng.sample(st,5): key.append(dict(defense=d,**r))
rng.shuffle(key); out=[]
for i,k in enumerate(key):
    k['hid']=f"H{i:03d}"; f=f"dyn/runs/{k['pipe']}/{k['suite']}/{k['ut']}/{k['attack']}/{k['inj']}.json"; k['path']=f
    e=json.load(open(f)); goal=get_suite(k['version'],k['suite']).get_injection_task_by_id(k['inj']).GOAL
    calls=[(c['function'],json.dumps(c.get('args'),default=str)[:300]) for m in e['messages'] if m.get('role')=='assistant' and m.get('tool_calls') not in (None,'None') for c in m['tool_calls']]
    out.append((k['hid'],k['suite'],goal,calls))
os.makedirs('human_packet/KEY_SEPARATE',exist_ok=True)
json.dump(key,open('human_packet/KEY_SEPARATE/key.json','w'),indent=1)
with open('human_packet/PACKET_episodes.md','w') as o:
    o.write("# Labelling packet: 40 episodes\nFor each episode, write YES or NO (and optional note) in labels_template.csv.\n\n")
    for h,s,g,c in out:
        o.write(f"## {h}  (suite: {s})\n**Injected attacker goal:** {g}\n\n**Tool calls the agent proposed, in order:**\n")
        for j,(fn,a) in enumerate(c,1): o.write(f"{j}. `{fn}` {a}\n")
        if not c: o.write("(no tool calls)\n")
        o.write("\n")
with open('human_packet/labels_template.csv','w') as o:
    o.write("id,attempted(YES/NO),confidence(1-3),note\n"+"".join(f"{h},,,\n" for h,*_ in out))
print(len(key))
