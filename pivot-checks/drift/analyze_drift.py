import json,collections,math
DEF=['repeat_user_prompt','spotlighting_with_delimiting','transformers_pi_detector','piguard_detector','prompt_guard_2_detector','tool_filter','camel','drift','progent','tool_knowledge']
def split(p):
    for d in DEF:
        if p.endswith('-'+d): return p[:-len(d)-1],d
    return p,'none'
def wilson(k,n,z=1.96):
    if n==0: return (float('nan'),)*2
    p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return c-h,c+h
def newcombe_paired(a,b,c,n):  # Newcombe 1998 method 10; a=both1,b=stored1 replay0,c=stored0 replay1; diff=replay-stored
    p1=(a+c)/n;p2=(a+b)/n;l1,u1=wilson(a+c,n);l2,u2=wilson(a+b,n);d=p1-p2
    A=(a+b)*(c+(n-a-b-c))*(a+c)*(b+(n-a-b-c)); phi=0 if A==0 else ((a*(n-a-b-c)-b*c))/math.sqrt(A)
    phi=max(phi,0) if False else phi
    dl=math.sqrt(max(0,(p1-l1)**2-2*phi*(p1-l1)*(u2-p2)+(u2-p2)**2)); du=math.sqrt(max(0,(u1-p1)**2-2*phi*(u1-p1)*(p2-l2)+(p2-l2)**2))
    return d,d-dl,d+du
R=[]
for b in ['agentdojo','agentdyn']:
    for l in open(f'drift/replay_{b}.jsonl'):
        r=json.loads(l)
        if '_meta' not in r: R.append(r)
sets=collections.defaultdict(list)
for r in R: sets[(r['bench'],r['pipe'],r['attack'])].append(r)
rows=[];chg=collections.Counter();errs=collections.Counter()
for k,rs in sorted(sets.items()):
    if 'dos' in k[2]: rows.append(dict(bench=k[0],model=split(k[1])[0],defense=split(k[1])[1],attack=k[2],n=len(rs),excluded='DoS attack: stored security = not utility (benchmark.py L149), injection security() replay not comparable')); continue
    errep=[r for r in rs if r.get('error') and 'replay' in r]; err_chg=sum(r['replay']!=r['stored'] for r in errep)
    ok=[r for r in rs if 'replay' in r and r.get('stored') is not None and not r.get('error')]; n=len(ok)
    a=sum(r['stored'] and r['replay'] for r in ok); bb=sum(r['stored'] and not r['replay'] for r in ok); c=sum((not r['stored']) and r['replay'] for r in ok)
    d,lo,hi=newcombe_paired(a,bb,c,n) if n else (0,0,0)
    m,df=split(k[1])
    rows.append(dict(bench=k[0],model=m,defense=df,attack=k[2],n=len(rs),n_replay_err=len(rs)-n,n_err_episodes=sum(1 for r in rs if r.get('error')),
      n_changed=bb+c,n_err_replayed=len(errep),n_err_changed=err_chg,T2F=bb,F2T=c,asr_stored=(a+bb)/n if n else None,asr_replay=(a+c)/n if n else None,
      wilson_stored=wilson(a+bb,n),wilson_replay=wilson(a+c,n),diff=d,newcombe=(lo,hi)))
    for r in ok:
        r['_cnt']=1
        if r['stored']!=r['replay']: chg[(k[0],r['suite'],r['inj'],r['version'],'T->F' if r['stored'] else 'F->T')]+=1
    for r in rs:
        if 'replay_err' in r: errs[(k[0],r['suite'],r['inj'],r['version'],r['replay_err'][:60])]+=1
# rankings per cell
cells=collections.defaultdict(list)
rows_all=rows; rows=[x for x in rows if 'excluded' not in x]
for x in rows: cells[(x['bench'],x['model'],x['attack'])].append(x)
rk=[]
for k,xs in cells.items():
    if len(xs)<2: continue
    o1=[x['defense'] for x in sorted(xs,key=lambda x:(x['asr_stored'],x['defense']))]; o2=[x['defense'] for x in sorted(xs,key=lambda x:(x['asr_replay'],x['defense']))]
    pairs=[(x['defense'],y['defense']) for i,x in enumerate(xs) for y in xs[i+1:] if (x['asr_stored']-y['asr_stored'])*(x['asr_replay']-y['asr_replay'])<0 or ((x['asr_stored']==y['asr_stored'])!=(x['asr_replay']==y['asr_replay']))]
    rk.append(dict(cell=k,ndef=len(xs),order_stored=o1,order_replay=o2,changed=o1!=o2,pair_changes=pairs))
json.dump(dict(sets=rows_all,changes=[[*k,v] for k,v in chg.most_common()],replay_errors=[[*k,v] for k,v in errs.most_common()],rankings=rk),open('drift/drift_results.json','w'),indent=1)
print('sets',len(rows),'episodes',len(R),'replayed',sum('replay' in r for r in R),'changed',sum(x['n_changed'] for x in rows))
for b in ['agentdojo','agentdyn']: print(b,'changed',sum(x['n_changed'] for x in rows if x['bench']==b),'T2F',sum(x['T2F'] for x in rows if x['bench']==b),'F2T',sum(x['F2T'] for x in rows if x['bench']==b),'replayerr',sum(x['n_replay_err'] for x in rows if x['bench']==b),'sets w/ change',sum(x['n_changed']>0 for x in rows if x['bench']==b))
print('CHANGES by task');[print(k,v) for k,v in chg.most_common(40)]
print('REPLAY ERRS');[print(k,v) for k,v in errs.most_common(15)]
print('sig sets (CI excl 0):',[(x['bench'],x['model'],x['defense'],x['attack'],round(x['diff'],4),[round(v,4) for v in x['newcombe']]) for x in rows if x['newcombe'][0]>0 or x['newcombe'][1]<0])
print('max |diff|',max(rows,key=lambda x:abs(x['diff']))['diff'])
for r in rk:
    if r['changed']: print('RANK',r['cell'],r['pair_changes'])
print('cells ranked',len(rk),'changed',sum(r['changed'] for r in rk))

print('error episodes replayed',sum(x['n_err_replayed'] for x in rows),'changed',sum(x['n_err_changed'] for x in rows))
