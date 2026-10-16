# Per docs/SENSITIVITY_CLUSTERED.md (hash-locked before running).
import json,collections,math,numpy as np
DEFS=['drift','piguard_detector','progent','prompt_guard_2_detector','repeat_user_prompt','spotlighting_with_delimiting','tool_filter','transformers_pi_detector','camel']
B=10000
def holm(p,a=0.05):
    p=np.asarray(p); o=np.argsort(p); m=len(p); sig=np.zeros(m,bool)
    for r,i in enumerate(o):
        if p[i]<=a/(m-r): sig[i]=True
        else: break
    return sig
def run(mode):
    E=collections.defaultdict(lambda: collections.defaultdict(list))
    for l in open('rankflip/episodes.jsonl'):
        r=json.loads(l)
        if r['score_err'] or r['executed'] is None: continue
        if mode=='conf' and r['bench']=='agentdyn' and r['suite'] in ('shopping','github'): continue
        m,d=r['pipe'],'none'
        for x in DEFS:
            if m.endswith('-'+x): m,d=m[:-len(x)-1],x
        E[(r['bench'],m,r['attack'])][(d,(r['suite'],r['ut']))].append((bool(r['executed']),bool(r['attempted']),bool(r['correct'])))
    rng=np.random.default_rng(20261015); res=[]
    for c in sorted(E):
        G=E[c]; ds=sorted({d for d,_ in G}); 
        if len(ds)<3 or 'none' not in ds: continue
        T=sorted({t for _,t in G}); ti={t:i for i,t in enumerate(T)}
        S=np.zeros((len(ds),3,len(T))); N=np.zeros((len(ds),len(T)))
        for (d,t),v in G.items():
            a=np.array(v,float); S[ds.index(d),:,ti[t]]=a.sum(0); N[ds.index(d),ti[t]]=len(a)
        obs=S.sum(2)/N.sum(1)[:,None]            # (def,3)
        W=rng.multinomial(len(T),np.full(len(T),1/len(T)),size=B).astype(float)  # (B,T)
        den=W@N.T                                 # (B,def)
        bs=np.einsum('bt,dkt->bdk',W,S)/den[:,:,None]
        pr=[(i,j) for i in range(len(ds)) for j in range(i+1,len(ds))]
        def pv(k):
            out=[]
            for i,j in pr:
                dl=bs[:,i,k]-bs[:,j,k]; dl=dl[~np.isnan(dl)]
                out.append(min(1,2*min((dl<=0).mean(),(dl>=0).mean())))
            return np.array(out)
        sE=holm(pv(0)); o=dict(cell=c,ndef=len(ds),ntasks=len(T),pairs=len(pr))
        for nm,k in (('ATT',1),('ATTCA',2)):
            sK=holm(pv(k)); fl=[]
            for q,(i,j) in enumerate(pr):
                dE=obs[i,0]-obs[j,0]; dK=obs[i,k]-obs[j,k]
                if sE[q] and sK[q] and np.sign(dE)*np.sign(dK)<0: fl.append([ds[i],ds[j],round(dE,3),round(dK,3)])
            o[nm]=fl
        res.append(o)
    summ=dict(cells=len(res),pairs=sum(o['pairs'] for o in res))
    for nm in ('ATT','ATTCA'):
        cw=sum(bool(o[nm]) for o in res); summ[nm]=dict(cells_with_flip=cw,flips=sum(len(o[nm]) for o in res),ge25=cw/len(res)>=0.25)
    return dict(summary=summ,cells=res)
out={m:run(m) for m in ('conf','all')}
json.dump(out,open('audit/rerun/clustered.json','w'),indent=1,default=str)
for m in out:
    print(m,out[m]['summary'])
    for o in out[m]['cells']:
        if o['ATT'] or o['ATTCA']: print('  ',o['cell'][1],o['ntasks'],'ATT',o['ATT'],'CA',o['ATTCA'])
