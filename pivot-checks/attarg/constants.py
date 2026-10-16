import re,json,functools,warnings,inspect; warnings.filterwarnings("ignore")
from agentdojo.task_suite.load_suites import get_suite
NAME=re.compile(r'ATTACKER|RECIPIENT|PARTICIPANT|PHISHING|TARGET|PASSWORD|CONTENT|IBAN|EMAIL|FILE|CODE|LEAK|WEB|USER')
RX=[r'[\w.+-]+@[\w-]+\.[\w.]+', r'(?:https?://)?www\.[^\s\'"]+', r'\b[A-Z]{2}\d{8,}\b', r'\bP\d{3}\b', r'ssh-rsa [A-Za-z0-9+/]+',
    r"'(/[^']+)'", r'(/system/[^\s\'"]+)']
def clean(x): return x.rstrip('.,;:!?)\'"').strip()
@functools.lru_cache(None)
def consts(version,suite,inj):
    t=get_suite(version,suite).get_injection_task_by_id(inj); goal=t.GOAL; gl=goal.lower(); C=set()
    for k,v in vars(type(t)).items():
        if k.startswith('_') and not k.startswith('__') and isinstance(v,(str,int)) and not isinstance(v,bool):
            try: sec=inspect.getsource(type(t).security)
            except Exception: sec=''
            if NAME.search(k) and 'MY_' not in k and 'SENDER' not in k and len(str(v))>=3 and (str(v).lower() in gl or ('self.'+k) in sec): C.add(str(v))
    for r in RX:
        for m in [clean(x) for x in re.findall(r,goal)]:
            if len(m)>=3: C.add(m)
    return sorted(C)

def ovr_tokens(suite,inj):
    import sys; sys.path.insert(0,'rankflip'); import scorer
    return sorted({tok for _,toks in scorer.OVR.get((suite,inj),[]) for tok in toks if len(tok)>=3})
