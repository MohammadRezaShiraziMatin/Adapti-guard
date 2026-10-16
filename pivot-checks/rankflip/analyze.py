import json,collections,numpy as np
DEFS=['drift','piguard_detector','progent','prompt_guard_2_detector','repeat_user_prompt','spotlighting_with_delimiting','tool_filter','transformers_pi_detector','camel']
E=collections.defaultdict(list)
for l in open('rankflip/episodes.jsonl'):
    r=json.loads(l)
    if r['score_err'] or r['executed'] is None: continue
    m,d=r['pipe'],'none'
    for x in DEFS:
        if m.endswith('-'+x): m,d=m[:-len(x)-1],x
    E[(r['bench'],m,r['attack'],d)].append((bool(r['executed']),bool(r['attempted']),bool(r['correct']),r['error'] not in (None,'None')))
cells=collections.defaultdict(dict)
for (b,m,a,d),v in E.items(): cells[(b,m,a)][d]=np.array(v,dtype=float)
rng=np.random.default_rng(20261015); B=2000; res=[]
def tau(x,y):
    nc=nd=tx=ty=0
    for i in range(len(x)):
        for j in range(i+1,len(x)):
            a=np.sign(x[i]-x[j]); b=np.sign(y[i]-y[j])
            if a==0 and b==0: continue
            if a==0: tx+=1
            elif b==0: ty+=1
            elif a==b: nc+=1
            else: nd+=1
    den=np.sqrt((nc+nd+tx)*(nc+nd+ty)); return (nc-nd)/den if den else np.nan
for c,D in sorted(cells.items()):
    if len(D)<3: continue
    ds=sorted(D); asr=lambda k:np.array([D[d][:,k].mean() for d in ds])
    boot={k:np.empty((B,len(ds))) for k in (0,1,2)}
    for i,d in enumerate(ds):
        X=D[d]; idx=rng.integers(0,len(X),(B,len(X)))
        for k in (0,1,2): boot[k][:,i]=X[:,k][idx].mean(1)
    out=dict(cell=c,n={d:len(D[d]) for d in ds},asr={k:dict(zip(ds,asr(i).round(3))) for k,i in (('EXEC',0),('ATT',1),('ATTCA',2))})
    for name,k in (('ATT',1),('ATTCA',2)):
        t=tau(asr(0),asr(k)); tb=np.array([tau(boot[0][r],boot[k][r]) for r in range(B)])
        lo,hi=np.nanpercentile(tb,[2.5,97.5])
        flips=[]
        for i in range(len(ds)):
            for j in range(i+1,len(ds)):
                dE=boot[0][:,i]-boot[0][:,j]; dA=boot[k][:,i]-boot[k][:,j]
                eL,eH=np.percentile(dE,[2.5,97.5]); aL,aH=np.percentile(dA,[2.5,97.5])
                if (eL>0 and aH<0) or (eH<0 and aL>0): flips.append((ds[i],ds[j],round(dE.mean(),3),round(dA.mean(),3)))
        out[name]=dict(tau=round(t,3),ci=[round(lo,3),round(hi,3)],nflip=len(flips),flips=flips)
    out['n_err']=int(sum(D[d][:,3].sum() for d in ds)); res.append(out)
json.dump(res,open('rankflip/results.json','w'),indent=1,default=str)
for o in res:
    print(o['cell'],len(o['n']),'err',o['n_err'],'| ATT tau',o['ATT']['tau'],o['ATT']['ci'],'flips',o['ATT']['nflip'],'| CA tau',o['ATTCA']['tau'],o['ATTCA']['ci'],'flips',o['ATTCA']['nflip'])
for name in ('ATT','ATTCA'): print(name,'cells with >=1 sig flip:',sum(o[name]['nflip']>0 for o in res),'/',len(res))
