import json,glob,os,sys,statistics as st,csv
tok=None
try:
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(sys.argv[2])
except Exception as e: print("no tokenizer",e)
root=sys.argv[1]; rows=[]
for f in glob.glob(f"{root}/*/*/*/injection_task_*.json"):
    if 'detector' in f or 'drift' in f or 'progent' in f: continue
    d=json.load(open(f)); inj=d.get('injections') or {}
    for m in d['messages']:
        if m['role']!='tool': continue
        c=m["content"] or ""; txt=c if isinstance(c,str) else "".join(b.get("content","") for b in c if b.get("type")=="text")
        for k,v in inj.items():
            probe=v.strip()[:60]
            # yaml may rewrap; probe with first line chunk
            probe=[l for l in v.split('\n') if l.strip()][0].strip()[:40]
            i=txt.find(probe)
            if i<0: continue
            n=len(txt); r=dict(file=f,suite=d['suite_name'],vec=k,chars=n,inj_char_start=i,rel=i/n)
            if tok:
                ids=tok(txt,add_special_tokens=False)['input_ids']; pre=tok(txt[:i],add_special_tokens=False)['input_ids']
                r.update(tokens=len(ids),inj_tok_start=len(pre),beyond510=len(pre)>510)
            rows.append(r); break
w=csv.DictWriter(open(sys.argv[3],'w'),fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(len(rows))
