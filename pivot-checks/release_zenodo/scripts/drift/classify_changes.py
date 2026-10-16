"""Classify each changed (non-error, non-DoS) episode by replay divergence. Run once per benchmark src."""
import json,sys,io,contextlib,collections
from agentdojo.task_suite.load_suites import get_suite
from agentdojo.functions_runtime import FunctionsRuntime
bench=sys.argv[1]; out=[]
for l in open(f'drift/replay_{bench}.jsonl'):
    r=json.loads(l)
    if '_meta' in r or r.get('replay') is None or r.get('stored') is None or r.get('error') or 'dos' in r['attack'] or r['replay']==r['stored']: continue
    e=json.load(open(r['file'])); tools=[m for m in e['messages'] if m['role']=='tool']
    s=get_suite(r['version'],e['suite_name']); ut=s.get_user_task_by_id(e['user_task_id'])
    env=ut.init_environment(s.load_and_inject_default_environment(e.get('injections') or {})); rt=FunctionsRuntime(s.tools); i=0; div=[]
    for m in e['messages']:
        for c in (m.get('tool_calls') or []) if m.get('tool_calls')!='None' else []:
            lg=tools[i] if i<len(tools) else {}; i+=1
            if lg.get('error') not in (None,'None',''): continue
            with contextlib.redirect_stdout(io.StringIO()): res,err=rt.run_function(env,c['function'],c['args'])
            if err: div.append((c['function'],err.split(':')[0]))
    cat='tool_missing_now' if any(d[1]=='ToolNotFoundError' for d in div) else ('replay_error_on_logged_ok_call' if div else 'no_exec_divergence(checker/state logic or unlogged nondeterminism)')
    out.append(dict(r,category=cat,divergences=div[:5]))
json.dump(out,open(f'drift/changes_classified_{bench}.json','w'),indent=0)
c=collections.Counter((o['suite'],o['inj'],o['category'],'T->F' if o['stored'] else 'F->T') for o in out)
for k,v in c.most_common(): print(k,v)
print(collections.Counter(o['category'] for o in out)); print(collections.Counter(d for o in out for d in o['divergences']).most_common(10))
