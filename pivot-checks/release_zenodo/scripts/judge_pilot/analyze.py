import json,random,itertools,collections
S={x['file']:x for x in json.load(open('judge_pilot/sample.json')) if x['stratum']!='none'}
J={}
for l in open('judge_pilot/judgments.jsonl'):
    r=json.loads(l)
    if r['parsed']: J[(r['file'],r['model'])]=r['parsed'].get('attack_executed')
M=["google/gemini-2.5-flash-lite","anthropic/claude-haiku-5.5"]; SETS=sorted({x['set'] for x in S.values()})
def stats(rows,m,partial=0):
    W=lambda c:sum(r['weight'] for r in rows if c(r))
    jy=lambda r:{'yes':1,'partial':partial}.get(J[(r['file'],m)],0)
    c=lambda r:1 if r['checker_security'] else 0
    n=W(lambda r:1); a=W(lambda r:jy(r)&c(r)); b=W(lambda r:jy(r)&(1-c(r))); cc=W(lambda r:(1-jy(r))&c(r)); d=n-a-b-cc
    po=(a+d)/n; pj=(a+b)/n; pc=(a+cc)/n; pe=pj*pc+(1-pj)*(1-pc)
    return dict(FPR=b/(b+d),FNR=cc/(a+cc),kappa=(po-pe)/(1-pe) if pe<1 else float('nan'),ASR_j=pj,ASR_c=pc,dASR=pj-pc,disagree=1-po)
def boot(set_rows,rng):
    out=[]
    for st in ('att_pos','att_neg'):
        g=[r for r in set_rows if r['stratum']==st]; out+= [rng.choice(g) for _ in g]
    return out
rng=random.Random(1); B=2000
by={s:[r for r in S.values() if r['set']==s] for s in SETS}
res={};bs={}
for p in (0,1):
  for m in M:
    for s in SETS:
        res[(p,m,s)]=stats(by[s],m,p)
        bs[(p,m,s)]=[stats(boot(by[s],rng),m,p) for _ in range(B)]
def ci(v,lo=.025,hi=.975): v=sorted(v); return v[int(lo*len(v))],v[int(hi*len(v))-1]
L=[]
for p in (0,1):
  L.append(f"\n### partial counted as {'success' if p else 'failure'}\n| judge | defense | FPR (95% CI) | FNR (95% CI) | κ (95% CI) | ASR checker | ASR judge | ΔASR 90% CI | TOST ±3pp |\n|---|---|---|---|---|---|---|---|---|")
  for m in M:
    for s in SETS:
        r=res[(p,m,s)];b=bs[(p,m,s)];f=lambda k:"%.3f (%.3f–%.3f)"%((r[k],)+ci([x[k] for x in b]))
        d90=ci([x['dASR'] for x in b],.05,.95)
        L.append(f"| {m.split('/')[1]} | {s.split('08-06-')[1]} | {f('FPR')} | {f('FNR')} | {f('kappa')} | {r['ASR_c']:.3f} | {r['ASR_j']:.3f} | {d90[0]:+.3f} to {d90[1]:+.3f} | {'equivalent' if -0.03<d90[0] and d90[1]<0.03 else 'not shown'} |")
  # ranking flips
  for m in M:
    for a,c in itertools.combinations(SETS,2):
        dc=res[(p,m,a)]['ASR_c']-res[(p,m,c)]['ASR_c']
        flips=sum(((x['ASR_j']-y['ASR_j'])*dc)<0 for x,y in zip(bs[(p,m,a)],bs[(p,m,c)]))/B
        dd=[(x['ASR_j']-y['ASR_j'])-(x['ASR_c']-y['ASR_c']) for x,y in zip(bs[(p,m,a)],bs[(p,m,c)])]
        L.append(f"- {m.split('/')[1]}: {a.split('08-06-')[1]} vs {c.split('08-06-')[1]}: checker Δ={dc:+.3f}, judge Δ={res[(p,m,a)]['ASR_j']-res[(p,m,c)]['ASR_j']:+.3f}, P(flip)={flips:.3f}, DiD 95% CI {ci(dd)[0]:+.3f} to {ci(dd)[1]:+.3f}")
# raw counts and judge-judge agreement
cnt=collections.Counter((m.split('/')[1],r['set'].split('08-06-')[1],r['stratum'],J[(r['file'],m)]) for m in M for r in S.values())
L.append("\n### Raw (unweighted) judge labels by checker stratum\n"+"\n".join(f"- {k}: {v}" for k,v in sorted(cnt.items())))
agree=sum(J[(f,M[0])]==J[(f,M[1])] for f in S)/len(S); L.append(f"\nJudge–judge exact label agreement (unweighted, 600 items): {agree:.3f}")
open('judge_pilot/_results_tables.md','w').write("\n".join(L)); print("\n".join(L))
