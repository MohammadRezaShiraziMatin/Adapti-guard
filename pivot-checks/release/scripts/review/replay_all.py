import json,collections,sys,io,contextlib
sys.path.insert(0,'review'); from replay_security import replay
S=json.load(open('judge_pilot/sample.json')); c=collections.Counter(); mism=[]; res={}
for s in S:
    if s['stratum']=='none': continue
    try:
        with contextlib.redirect_stdout(io.StringIO()): rec,sec,*_=replay(s['file'])
    except Exception as ex: rec,sec=s['checker_security'],'ERR:'+type(ex).__name__
    d=s['set'].split('-06-')[1]; c[(d,rec,sec)]+=1; res[s['file']]=sec
    if rec!=sec: mism.append((d,s['file'].split(d+'/')[1],rec,sec))
for k,v in sorted(c.items(),key=str): print(k,v)
for m in mism: print(m)
json.dump(res,open('review/replay_results.json','w'))
