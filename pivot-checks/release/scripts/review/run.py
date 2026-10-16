# Reuses rankflip/analyze.py logic unchanged; only filters input episodes. seed 20261015.
import json,sys,os,io
mode=sys.argv[1]
src=open('rankflip/analyze.py').read()
src=src.replace("    if r['score_err'] or r['executed'] is None: continue",
"    if r['score_err'] or r['executed'] is None: continue\n    if MODE=='conf' and r['bench']=='agentdyn' and r['suite'] in ('shopping','github'): continue")
src=src.replace("'rankflip/results.json'","OUT")
g={'MODE':mode,'OUT':f'/workspace/rf_split/results_{mode}.json'}
exec(src,g)
res=g['res']
import math
pairs=sum(math.comb(len(o['n']),2) for o in res)
for nm in ('ATT','ATTCA'):
  print(mode,nm,'flips',sum(o[nm]['nflip'] for o in res),'pairs',pairs)
