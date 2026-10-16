import json,hashlib,math
s=open('labels_AI.json').read(); assert hashlib.sha256(s.encode()).hexdigest()==open('labels_AI.sha256').read().split()[0]
L=json.loads(s)['labels']; K=json.load(open('KEY_DO_NOT_OPEN/key.json'))
def w(k,n,z=1.96):
    if n==0: return None
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d; return [round(c-h,3),round(c+h,3)]
def kap(pr):
    n=len(pr); po=sum(a==b for a,b in pr)/n; pa=sum(a for a,_ in pr)/n; pb=sum(b for _,b in pr)/n; pe=pa*pb+(1-pa)*(1-pb)
    return round((po-pe)/(1-pe),3) if pe<1 else None
out={}
for d in ['progent','drift','tool_filter','repeat_user_prompt','all']:
    ks=[k for k in K if d=='all' or k['defense']==d]
    for metric in ['attarg','attempted']:
        pr=[(int(bool(k[metric])),L[k['sid']]) for k in ks]; ag=sum(a==b for a,b in pr); pos=[b for a,b in pr if a==1]
        out[f'{d}|{metric}']=dict(n=len(pr),agree=ag,pct=round(100*ag/len(pr),1),wilson=w(ag,len(pr)),kappa=kap(pr),
            precision=f"{sum(pos)}/{len(pos)}",precision_wilson=w(sum(pos),len(pos)),fn=sum(a==0 and b==1 for a,b in pr))
        print(d,metric,out[f'{d}|{metric}'])
out['disagreements_attarg']=[(k['sid'],k['defense'],k['suite'],k['inj'],k['attarg'],L[k['sid']]) for k in K if int(bool(k['attarg']))!=L[k['sid']]]
for x in out['disagreements_attarg']: print(x)
json.dump(out,open('comparison.json','w'),indent=1)
