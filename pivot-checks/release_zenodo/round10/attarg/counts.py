"""Descriptive counts for the manuscript (no new analysis): task-versions in the constant table, excluded ones, excluded episodes."""
import json,collections
t=json.load(open('attarg/constant_table.json'))
tab=t['table']; exc=[k for k,v in tab.items() if not v['constants'] or not v['targets']]
c=collections.Counter(); n=0
for l in open('attarg/episodes_attarg.jsonl'):
    r=json.loads(l); n+=1
    if r['attarg_excluded']: c[r['bench']]+=1
print(f"task_versions {len(tab)}\nexcluded_task_versions {len(exc)}\nepisodes {n}\nexcluded_episodes_agentdojo {c['agentdojo']}\nexcluded_episodes_agentdyn {c['agentdyn']}")
print("excluded:",sorted(exc))
