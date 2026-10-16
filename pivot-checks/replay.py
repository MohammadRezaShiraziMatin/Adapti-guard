from agentdojo.task_suite.load_suites import get_suites
from agentdojo.agent_pipeline import GroundTruthPipeline
from agentdojo.functions_runtime import FunctionsRuntime
import collections
M="ZQXJMARKERQZX"
s=get_suites("v1"); stats=collections.Counter()
for sn in ['shopping','github','dailylife','workspace','travel','banking','slack']:
    suite=s[sn]; inj={k:M for k in suite.get_injection_vector_defaults()}
    for uid,ut in suite.user_tasks.items():
        try:
            env=suite.load_and_inject_default_environment(inj)
            _,_,_,msgs,_=GroundTruthPipeline(ut).query(ut.PROMPT,FunctionsRuntime(suite.tools),env)
            stats[sn,'ok']+=1
            outs=[m for m in msgs if m["role"]=="tool"]
            stats[sn,'tool_outputs']+=len(outs)
            stats[sn,'outputs_with_marker']+=sum(M in ("".join(b.get("content","") for b in m["content"]) if not isinstance(m["content"],str) else m["content"]) for m in outs)
        except Exception as e:
            stats[sn,'fail']+=1; stats[sn,'err:'+type(e).__name__]+=1
for k,v in sorted(stats.items()): print(k,v)
