"""Item 3 (2026-10-16). EXEC = stored security; ATT = rankflip scorer (attempted). Exploratory: ATT uses post-hoc target map (rankflip Dev.1)."""
import json,collections,random,math,sys
sys.path.insert(0,'drift'); from analyze_drift import split
STAGE={'spotlighting_with_delimiting':'input','repeat_user_prompt':'input','transformers_pi_detector':'input','piguard_detector':'input','prompt_guard_2_detector':'input',
       'tool_filter':'planning','camel':'planning','progent':'execution','drift':'execution'}
E=[json.loads(l) for l in open('rankflip/episodes.jsonl')]
def run(filt,label):
    S=collections.defaultdict(list)
    for e in E:
        if e['attack']!='important_instructions' or e['attempted'] is None or e['executed'] is None or e['error']: continue
        if not filt(e): continue
        m,d=split(e['pipe'])
        if d=='none' or d not in STAGE: continue
        S[(e['bench'],m,d)].append(int(e['attempted'])-int(e['executed']))
    models=collections.defaultdict(dict)
    for (b,m,d),v in S.items(): models[(b,m)][d]=v
    models={k:v for k,v in models.items() if len({STAGE[d] for d in v})>=2}
    def stat(mods,lab):
        acc=collections.defaultdict(list)
        for k,ds in mods.items():
            per=collections.defaultdict(list)
            for d,v in ds.items(): per[lab[k][d]].append(sum(v)/len(v))
            for st,g in per.items(): acc[st].append(sum(g)/len(g))
        return {st:sum(g)/len(g) for st,g in acc.items()}
    lab0={k:{d:STAGE[d] for d in ds} for k,ds in models.items()}
    obs=stat(models,lab0)
    def contrast(s,a,b): return s.get(a,float('nan'))-s.get(b,float('nan'))
    rng=random.Random(20261016); perm=collections.Counter(); B=5000
    cons=[('execution','input'),('planning','input'),('execution','planning')]
    o={c:contrast(obs,*c) for c in cons}
    for _ in range(B):
        lab={}
        for k,ds in models.items():
            ks=list(ds); st=[STAGE[d] for d in ks]; rng.shuffle(st); lab[k]=dict(zip(ks,st))
        s=stat(models,lab)
        for c in cons:
            v=contrast(s,*c)
            if not math.isnan(v) and abs(v)>=abs(o[c])-1e-12: perm[c]+=1
    # episode bootstrap within set for CI of contrasts
    bs={c:[] for c in cons}
    for _ in range(1000):
        mm={k:{d:[v[rng.randrange(len(v))] for _ in v] for d,v in ds.items()} for k,ds in models.items()}
        s=stat(mm,lab0)
        for c in cons: bs[c].append(contrast(s,*c))
    res=dict(label=label,n_models=len(models),models=sorted(map(list,models)),stage_mean_gap=obs,
             per_set={f'{k[0]}|{k[1]}|{d}':dict(stage=STAGE[d],n=len(v),gap=sum(v)/len(v)) for k,ds in models.items() for d,v in ds.items()},
             contrasts={f'{a}-{b}':dict(diff=o[(a,b)],perm_p_within_model=(perm[(a,b)]+1)/(B+1),
               boot95=sorted(x for x in bs[(a,b)] if not math.isnan(x))[25:976:950] if bs[(a,b)] else None) for a,b in cons})
    return res
out=[run(lambda e:True,'all suites (post-hoc target map for shopping/github)'),
     run(lambda e:e['bench']=='agentdyn' and e['suite']=='dailylife' and e['inj'] not in('injection_task_2','injection_task_6'),'sensitivity: AgentDyn dailylife only, ground_truth-valid tasks')]
json.dump(out,open('stage/stage_gap_results.json','w'),indent=1)
for r in out:
    print(r['label'],r['n_models'],{k:round(v,4) for k,v in r['stage_mean_gap'].items()})
    for c,v in r['contrasts'].items(): print('  ',c,round(v['diff'],4),'p=',round(v['perm_p_within_model'],4),[round(x,4) for x in (v['boot95'] or [])])
