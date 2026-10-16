# LODO sensitivity per docs/SENSITIVITY_LODO.md. Reuses rankflip/analyze.py unchanged except input filters.
import json,math,io,contextlib
src0=open('rankflip/analyze.py').read()
src0=src0.replace("    if r['score_err'] or r['executed'] is None: continue",
"    if r['score_err'] or r['executed'] is None: continue\n    if MODE=='conf' and r['bench']=='agentdyn' and r['suite'] in ('shopping','github'): continue")
src0=src0.replace("    E[(r['bench'],m,r['attack'],d)].append(","    if d==DROP: continue\n    E[(r['bench'],m,r['attack'],d)].append(")
src0=src0.replace("json.dump(res,open('rankflip/results.json','w'),indent=1,default=str)","")
assert 'if d==DROP' in src0 and "MODE=='conf'" in src0
DEFS=['drift','piguard_detector','progent','prompt_guard_2_detector','repeat_user_prompt','spotlighting_with_delimiting','tool_filter','transformers_pi_detector','camel']
out={}
for mode in ('conf','all'):
  for drop in [None]+DEFS:
    g={'MODE':mode,'DROP':drop}
    with contextlib.redirect_stdout(io.StringIO()): exec(src0,g)
    res=g['res']; n=len(res)
    row=dict(eligible=n,pairs=sum(math.comb(len(o['n']),2) for o in res))
    for k in ('ATT','ATTCA'):
      c=sum(o[k]['nflip']>0 for o in res)
      row[k]=dict(cells=c,flips=sum(o[k]['nflip'] for o in res),ge25=bool(n and c/n>=0.25),flip_list=[[o['cell'][1]]+list(f) for o in res for f in o[k]['flips']])
    out[f'{mode}|{drop or "BASELINE"}']=row
    print(mode,drop,n,row['pairs'],'ATT',row['ATT']['cells'],row['ATT']['flips'],row['ATT']['ge25'],'CA',row['ATTCA']['cells'],row['ATTCA']['flips'])
json.dump(out,open('lodo/lodo_results.json','w'),indent=1,default=str)
