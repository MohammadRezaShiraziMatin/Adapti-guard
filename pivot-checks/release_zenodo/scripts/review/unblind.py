"""Run only after reviewer_labels.jsonl is frozen (LABELS_FROZEN.sha256)."""
import json,collections,math
K=json.load(open('review/KEY_DO_NOT_OPEN.json'))
L={json.loads(l)['id']:json.loads(l) for l in open('review/reviewer_labels.jsonl')}
def wil(k,n,z=1.96):
    if n==0: return (float('nan'),)*2
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d; return (max(0,c-h),min(1,c+h))
rows=[]
for rid,k in sorted(K.items()):
    t=L[rid]['label']; T={'executed':1,'not_executed':0}.get(t)
    ch=int(k['checker_security']); js={m:(1 if v in('yes','partial') else 0) for m,v in k['judges'].items()}
    if T is None: who='unclear'
    elif k['direction']=='agree': who='both right' if ch==T else 'both wrong'
    else:
        dis=[m for m,v in js.items() if v!=ch]
        who='checker right' if ch==T else 'judge right'
    rows.append(dict(id=rid,defense=k['defense'],direction=k['direction'],checker=ch,judges=k['judges'],review=t,who=who,ev=L[rid]['ev']))
json.dump(rows,open('review/unblinded.json','w'),indent=1)
out=[]
cnt=collections.Counter((r['defense'],r['direction'],r['who']) for r in rows)
for dfn in ['tool_filter','prompt_guard_2_detector','repeat_user_prompt']:
    for dr in ['J+C-','J-C+','agree']:
        n=sum(v for (a,b,c),v in cnt.items() if a==dfn and b==dr)
        if not n: continue
        parts=[]
        for c in ['judge right','checker right','both wrong','both right','unclear']:
            k=cnt[(dfn,dr,c)]
            if k: lo,hi=wil(k,n); parts.append(f"{c} {k}/{n} ({lo:.2f}–{hi:.2f})")
        out.append(f"| {dfn} | {dr} | {n} | "+"; ".join(parts)+" |")
# per judge accuracy on disagreement items
pj=collections.Counter()
for r in rows:
    T={'executed':1,'not_executed':0}.get(r['review'])
    if T is None or r['direction']=='agree': continue
    for m,v in r['judges'].items():
        lab=1 if v in('yes','partial') else 0
        pj[(m,r['defense'],'right' if lab==T else ('wrong-partial' if v=='partial' else 'wrong'))]+=1
print('\n'.join(out)); print(sorted(pj.items()))
for r in rows:
    if r['direction']!='agree' or r['who']!='both right': print(r['id'],r['defense'],r['direction'],r['checker'],r['judges'],r['review'],r['who'])
