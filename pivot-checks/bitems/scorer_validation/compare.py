import json,hashlib,math
s=open('labels_AI.json').read(); assert hashlib.sha256(s.encode()).hexdigest()==open('labels_AI.sha256').read().split()[0]
L=json.loads(s)['labels']; K=json.load(open('KEY_DO_NOT_OPEN/key.json'))
def wilson(k,n,z=1.96):
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d; return round(c-h,3),round(c+h,3)
def kappa(pairs):
    n=len(pairs); po=sum(a==b for a,b in pairs)/n; pa=sum(a for a,_ in pairs)/n; pb=sum(b for _,b in pairs)/n
    pe=pa*pb+(1-pa)*(1-pb); return round((po-pe)/(1-pe),3) if pe<1 else None
out={}
for d in ['progent','drift','all']:
    ks=[k for k in K if d=='all' or k['defense']==d]
    pr=[(int(k['attempted']),L[k['sid']]) for k in ks]; agree=sum(a==b for a,b in pr); n=len(pr)
    tab={'scorer1_ai1':sum(a==1 and b==1 for a,b in pr),'scorer1_ai0':sum(a==1 and b==0 for a,b in pr),
         'scorer0_ai1':sum(a==0 and b==1 for a,b in pr),'scorer0_ai0':sum(a==0 and b==0 for a,b in pr)}
    out[d]=dict(n=n,agree=agree,pct=round(100*agree/n,1),wilson95=wilson(agree,n),kappa=kappa(pr),**tab,
        ai1_executed=sum(L[k['sid']]==1 and bool(k['executed']) for k in ks))
    print(d,out[d])
out['disagreements']=[dict(sid=k['sid'],defense=k['defense'],suite=k['suite'],inj=k['inj'],scorer=k['attempted'],ai=L[k['sid']],executed=k['executed'],pipe=k['pipe']) for k in K if int(k['attempted'])!=L[k['sid']]]
for x in out['disagreements']: print(x)
out['population']={d:{str(k['stratum_scorer_att']):k['pop_stratum'] for k in K if k['defense']==d} for d in ['progent','drift']}
print(out['population'])
json.dump(out,open('comparison.json','w'),indent=1)
