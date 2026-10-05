"""F3 dev-phase grid over adaptive-controller settings (offline replay, dev seeds 0-19). See docs/F3_CONFIRMATORY_CONTRACT.md."""
import sys,json,itertools,statistics as st
sys.path.insert(0,"scripts")
import importlib.util
spec=importlib.util.spec_from_file_location("d","scripts/f3_dev_replay.py");d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
from pathlib import Path
d.f3._GUARD_CACHE.update(json.load(open("results/f3_confirmatory/dev_guard_cache.json")))
from adapti_guard.adaptation.policy_update_engine import PolicyUpdateEngine as P
SEEDS=range(20)  # dev seeds (not the confirmatory ones)
def m(res,kind=None):
    xs=[v for (k,s),v in res.items() if kind in (None,k)]
    return [round(st.mean(x[i] for x in xs),3) for i in range(4)]
for arm in ["fixed_l1","fixed_l2","fixed_l3"]:
    r=d.evaluate(arm,SEEDS);print(arm,"loss,asr,util,cost",m(r),"unif",m(r,"uniform25")[0],"burst",m(r,"burst")[0])
base=dict(benign_streak_threshold=10,min_dwell=5,backoff_cap=4)
print("--- adaptive_proxy_sem grid")
rows=[]
for at,ls,dw,bc,dec in itertools.product([2,3],[2],[3,5],[0,4],[0,1]):
    kw=dict(attack_threshold=at,legitimate_threshold=ls,pressure_decay=dec,benign_streak_threshold=10,min_dwell=dw,backoff_cap=bc)
    r=d.evaluate("adaptive_proxy_sem",SEEDS,lambda kw=kw:P(**kw))
    rows.append((m(r)[0],kw,m(r),m(r,"uniform25")[0],m(r,"burst")[0]))
for x in sorted(rows,key=lambda x:x[0])[:8]:print(x)
print("default exp cfg:",m(d.evaluate("adaptive_proxy_sem",SEEDS)))
