import json,sys,io,contextlib
sys.path.insert(0,'drift'); import replay_current as rc
from agentdojo.task_suite.load_suites import get_suite
from agentdojo.functions_runtime import FunctionsRuntime
f=sys.argv[1]; e=json.load(open(f)); print(f,'stored',e['security'],'ver',e.get('benchmark_version'),'util',e.get('utility'))
tools=[m for m in e['messages'] if m['role']=='tool']
s=get_suite(e.get('benchmark_version') or 'v1',e['suite_name']); ut=s.get_user_task_by_id(e['user_task_id'])
env=ut.init_environment(s.load_and_inject_default_environment(e.get('injections') or {})); rt=FunctionsRuntime(s.tools); i=0
for m in e['messages']:
    for c in (m.get('tool_calls') or []) if m.get('tool_calls')!='None' else []:
        with contextlib.redirect_stdout(io.StringIO()): r,err=rt.run_function(env,c['function'],c['args'])
        lg=tools[i] if i<len(tools) else {}; i+=1
        print(' ',c['function'],str(c['args'])[:90],'| LOG err:',str(lg.get('error'))[:50],'| REPLAY err:',str(err)[:60],'| out same:',str(r)[:40]==str(lg.get('content'))[:40] if not isinstance(lg.get('content'),list) else '?')
print('replay', rc.one(f).get('replay'))
