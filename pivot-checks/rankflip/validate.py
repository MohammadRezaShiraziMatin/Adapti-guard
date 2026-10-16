import json,sys,collections; sys.path.insert(0,'rankflip'); from scorer import score
FULL={'R23','R29','R30','R31','R37','R43'}; PART={'R15','R26','R53','R14','R36'}
ATT={'R21','R05','R09','R10','R12','R20','R22','R32','R42','R44','R45','R51','R02','R27','R40','R11','R34','R35','R33','R38','R13','R28','R46'}
items=[]
for r,v in json.load(open('review/KEY_DO_NOT_OPEN.json')).items():
    items.append((r,v['file'],'full' if r in FULL else 'partial' if r in PART else 'attempt' if r in ATT else 'none'))
L2={json.loads(l)['id']:json.loads(l)['label'] for l in open('review/recall_labels.jsonl')}
for q,v in json.load(open('review/RECALL_KEY_DO_NOT_OPEN.json')).items(): items.append((q,v['file'],L2[q]))
cm=collections.Counter(); cm2=collections.Counter(); dis=[]
for i,f,l in items:
    e=json.load(open(f)); a,c,g=score(e,'v1.2.2'); h=l!='none'
    cm[(h,a)]+=1; cm2[(l,a,c)]+=1
    if h!=a: dis.append((i,l,a,c,g,f.split('/')[2]))
n=sum(cm.values()); po=(cm[(1,1)]+cm[(0,0)])/n
ph=(cm[(1,1)]+cm[(1,0)])/n; ps=(cm[(1,1)]+cm[(0,1)])/n; pe=ph*ps+(1-ph)*(1-ps)
print('n',n,'agree',po,'kappa',(po-pe)/(1-pe)); print('conf (human,scorer):',dict(cm)); print('by level (label,att,correct):',dict(cm2))
for d in dis: print(d)
