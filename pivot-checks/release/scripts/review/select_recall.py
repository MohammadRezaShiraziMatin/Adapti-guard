"""Checker recall review: selection + blind packet. Seed 20261017. No API calls."""
import json,random,collections,sys
sys.argv=['x']; exec(open('review/select.py').read().split('key={}')[0])  # reuse S,J,task_src,fmt
prior={v['file'] for v in json.load(open('review/KEY_DO_NOT_OPEN.json')).values()}
strat=collections.defaultdict(list)
for f in sorted(J):
    s=S[f]
    if s['stratum']=='none' or s['checker_security']: continue
    if len(J[f])==2 and all(v=='no' for v in J[f].values()) and f not in prior:
        strat[s['set'].split('2024-08-06-')[1]].append(f)
rng=random.Random(20261017); sel=[]
for d in ['tool_filter','prompt_guard_2_detector','repeat_user_prompt']:
    sel+=[(f,d) for f in rng.sample(strat[d],20)]
rng.shuffle(sel); key={}
with open('review/RECALL_PACKET.md','w') as w:
    w.write('# Recall blind packet (Q01..Q60)\n')
    for i,(f,d) in enumerate(sel,1):
        q=f'Q{i:02d}'; e=json.load(open(f))
        key[q]=dict(file=f,defense=d,N_stratum_agreefail=len(strat[d]),weight=S[f]['weight'])
        w.write(f"## {q} (suite: {e['suite_name']}, {e['injection_task_id']})\n```python\n{task_src(e['suite_name'],e['injection_task_id'])}\n```\n```\n{fmt(e)}\n```\n\n")
json.dump(key,open('review/RECALL_KEY_DO_NOT_OPEN.json','w'),indent=1)
print({d:len(v) for d,v in strat.items()})
