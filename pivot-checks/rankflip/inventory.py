import json,glob,os,collections,csv
rows=collections.Counter(); err=collections.Counter(); sec=collections.Counter()
for bench,root in [('agentdojo','ad/runs'),('agentdyn','dyn/runs')]:
    for f in glob.glob(f'{root}/*/*/*/*/*.json'):
        p=f.split('/'); pipe,suite,ut,att,inj=p[2:7]
        if att=='none' or not inj.startswith('injection_task'): continue
        try: e=json.load(open(f))
        except Exception: err[(bench,pipe,att,'unparseable')]+=1; continue
        k=(bench,pipe,att); rows[k]+=1
        if e.get('error') not in (None,'None'): err[k]+=1
        if e.get('security') is True: sec[k]+=1
with open('rankflip/inventory.csv','w') as fh:
    w=csv.writer(fh); w.writerow(['benchmark','pipeline','attack','n','n_error','n_security_true'])
    for k in sorted(rows): w.writerow([*k,rows[k],err[k],sec[k]])
print(len(rows),sum(rows.values()),sum(err.values()))
