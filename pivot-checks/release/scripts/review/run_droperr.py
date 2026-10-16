# Preregistered drop-errors sensitivity: as review/run.py, additionally drop episodes with non-null error.
import json,sys,math,io,contextlib
mode=sys.argv[1]
src=open('rankflip/analyze.py').read()
a="    if r['score_err'] or r['executed'] is None: continue"
assert a in src
src=src.replace(a,a+"\n    if r['error'] not in (None,'None'): continue\n    if MODE=='conf' and r['bench']=='agentdyn' and r['suite'] in ('shopping','github'): continue")
src=src.replace("'rankflip/results.json'","OUT")
g={'MODE':mode,'OUT':f'review/results_droperr_{mode}.json'}
with contextlib.redirect_stdout(io.StringIO()): exec(src,g)
res=g['res']; pairs=sum(math.comb(len(o['n']),2) for o in res)
for nm in ('ATT','ATTCA'):
  print(mode,nm,'cells',len(res),'withflip',sum(o[nm]['nflip']>0 for o in res),'flips',sum(o[nm]['nflip'] for o in res),'pairs',pairs,[[o['cell'][1]]+list(f) for o in res for f in o[nm]['flips']])
