import sys,json,warnings,inspect,collections; warnings.filterwarnings("ignore"); sys.path.insert(0,sys.argv[1])
from agentdojo.task_suite.load_suites import get_suites
from agentdojo.task_suite import task_suite as TS
from agentdojo.agent_pipeline.ground_truth_pipeline import GroundTruthPipeline
from agentdojo.functions_runtime import FunctionsRuntime
src=inspect.getsource(TS.TaskSuite.check); i=src.index('# Check injection tasks')
print('is_task_injectable called in injection-task section of check():', 'is_task_injectable' in src[i:])
print(inspect.getsource(TS.is_task_injectable))
for sn,s in get_suites('v1').items():
    can={k:f'---CANARY_{k}---' for k in s.get_injection_vector_defaults()}
    env=s.load_and_inject_default_environment(can); ut=next(iter(s.user_tasks.values()))
    gp=GroundTruthPipeline(ut); _,_,_,resp,_=gp.query(ut.PROMPT,FunctionsRuntime(s.tools),env.copy(deep=True))
    tools=[m for m in resp if m['role']=='tool']; types=collections.Counter(type(m['content']).__name__ for m in tools)
    canary_in_any=any(c in json.dumps(m['content'],default=str) for m in tools for c in can.values())
    print(sn,ut.ID,'tool msgs',len(tools),'content types',dict(types),'canary present in any content:',canary_in_any,
          'injectable():',TS.is_task_injectable(resp,list(can.values())))
