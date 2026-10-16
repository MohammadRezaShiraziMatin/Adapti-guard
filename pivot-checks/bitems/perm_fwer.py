"""B #14 (EXPLORATORY, not preregistered): permutation max-statistic family-wise check of EXEC-vs-ATT reversals.
Per cell: keep (user_task, injection_task) blocks present for every defense. Statistic per defense pair (i,j):
R_ij = min(|dEXEC_ij|, |dATT_ij|) if the two ASR differences have opposite signs, else 0 (unstudentized).
Null: defense labels exchangeable within each block (permute the k defense labels per block, jointly for EXEC and ATT).
Family = all pairs in the cell. Pair flagged if R_obs > 95th percentile of max_ij R under permutation (Westfall-Young maxT,
single step). P=2000 permutations, seed 20261016. MODE conf|all (conf drops AgentDyn shopping/github; post hoc subset)."""
import json,collections,sys,numpy as np
MODE=sys.argv[1]; P=2000; rng=np.random.default_rng(20261016)
DEFS=['drift','piguard_detector','progent','prompt_guard_2_detector','repeat_user_prompt','spotlighting_with_delimiting','tool_filter','transformers_pi_detector','camel']
E=collections.defaultdict(dict)
for l in open('rankflip/episodes.jsonl'):
    r=json.loads(l)
    if r['score_err'] or r['executed'] is None: continue
    if MODE=='conf' and r['bench']=='agentdyn' and r['suite'] in ('shopping','github'): continue
    m,d=r['pipe'],'none'
    for x in DEFS:
        if m.endswith('-'+x): m,d=m[:-len(x)-1],x
    E[(r['bench'],m,r['attack'])].setdefault(d,{})[(r['suite'],r['ut'],r['inj'])]=(float(bool(r['executed'])),float(bool(r['attempted'])))
out=[]
for c,D in sorted(E.items()):
    if len(D)<3: continue
    ds=sorted(D); blocks=sorted(set.intersection(*[set(D[d]) for d in ds]))
    X=np.array([[D[d][b] for d in ds] for b in blocks])  # (nb,k,2)
    nb,k,_=X.shape; iu=np.triu_indices(k,1)
    def stat(Y):
        m=Y.mean(0); dE=(m[:,0][:,None]-m[:,0][None,:])[iu]; dA=(m[:,1][:,None]-m[:,1][None,:])[iu]
        return np.where(np.sign(dE)*np.sign(dA)<0, np.minimum(abs(dE),abs(dA)), 0.0)
    R=stat(X); mx=np.empty(P)
    for p in range(P):
        perm=np.argsort(rng.random((nb,k)),axis=1); mx[p]=stat(np.take_along_axis(X,perm[:,:,None],1)).max()
    thr=np.percentile(mx,95)
    fl=[(ds[iu[0][q]],ds[iu[1][q]],round(float(R[q]),3),round(float((mx>=R[q]).mean()),4)) for q in range(len(R)) if R[q]>thr]
    out.append(dict(cell=c,blocks=nb,k=k,thr=round(float(thr),4),flags=fl))
    print(c[1],'blocks',nb,'k',k,'thr',round(float(thr),4),'flags',fl)
print(MODE,'cells with >=1 FWER-flagged reversal:',sum(bool(o['flags']) for o in out),'/',len(out),'flags',sum(len(o['flags']) for o in out))
json.dump(out,open(f'bitems/perm_fwer_{MODE}.json','w'),indent=1)
