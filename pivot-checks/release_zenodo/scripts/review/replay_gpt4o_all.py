import json,collections,sys,io,contextlib,glob
sys.path.insert(0,'review'); from replay_security import replay
c=collections.Counter(); mism=[]
for f in sorted(glob.glob('dyn/runs/gpt-4o-2024-08-06*/*/*/important_instructions/*.json')):
    try:
        with contextlib.redirect_stdout(io.StringIO()): rec,sec,*_=replay(f)
    except Exception as ex: rec,sec='?','ERR'
    st=f.split('runs/')[1].split('/')
    c[(st[0],rec==sec)]+=1
    if rec!=sec: mism.append((st[0],st[1],st[2],st[4],rec,sec))
for k,v in sorted(c.items(),key=str): print(k,v)
for m in mism: print(m)
