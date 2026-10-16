# Diagnostic: per-pair estimates, cluster CIs, raw and Holm p for flip pairs under conf vs all. Same code path as clustered.py.
import json,numpy as np,re
src=open('clustered/clustered.py').read()
src=src.replace("            o[nm]=fl","            o[nm]=fl\n            o['diag_'+nm]=dict(pairs=[(ds[i],ds[j]) for i,j in pr],pE=pv(0).tolist(),pK=pv(k).tolist(),sE=sE.tolist(),sK=sK.tolist(),obsE=[obs[i,0]-obs[j,0] for i,j in pr],obsK=[obs[i,k]-obs[j,k] for i,j in pr],ciE=[np.nanpercentile(bs[:,i,0]-bs[:,j,0],[2.5,97.5]).tolist() for i,j in pr],ciK=[np.nanpercentile(bs[:,i,k]-bs[:,j,k],[2.5,97.5]).tolist() for i,j in pr])")
src=src.split("out={m:run(m)")[0]
g={}; exec(src,g)
R={m:g['run'](m) for m in ('conf','all')}
want={('google_gemini-2.5-pro',('drift','piguard_detector')),('gpt-4o-2024-08-06',('progent','tool_filter')),('gpt-4o-2024-08-06',('drift','tool_filter')),('meta-llama_llama-3.3-70b-instruct',('drift','progent')),('meta-llama_llama-3.3-70b-instruct',('progent','tool_filter')),('qwen_qwen3-235b-a22b-2507',('drift','none')),('qwen_qwen3-235b-a22b-2507',('drift','progent')),('gpt-4o-mini-2024-07-18',('progent','repeat_user_prompt'))}
rows=[]
for m in R:
  for o in R[m]['cells']:
    d=o['diag_ATT']; m_=o['pairs']
    for q,p in enumerate(d['pairs']):
      if (o['cell'][1],tuple(p)) in want:
        r=dict(data=m,cell=o['cell'][1],pair=p,ntasks=o['ntasks'],holm_m=m_,dE=round(d['obsE'][q],3),ciE=[round(x,3) for x in d['ciE'][q]],pE=d['pE'][q],sigE=d['sE'][q],dA=round(d['obsK'][q],3),ciA=[round(x,3) for x in d['ciK'][q]],pA=d['pK'][q],sigA=d['sK'][q])
        rows.append(r); print(r)
json.dump(rows,open('clustered/diag_results.json','w'),indent=1)
