# v2 (2026-10-15): stratified on benchmark-reported `security`, with inverse-probability weights. No model calls.
# Run from pivot-checks/. Seed 20261015. Per set: attack stratum S+ (security==True) take min(all, POS_CAP);
# attack stratum S- fill to N_ATT; 'none' stratum N_NONE. weight = N_stratum / n_stratum.
import json,glob,random,tiktoken
enc=tiktoken.get_encoding("o200k_base"); SEED=20261015; N_ATT=200; POS_CAP=100; N_NONE=50; OVER=700
SETS=["gpt-4o-2024-08-06-tool_filter","gpt-4o-2024-08-06-prompt_guard_2_detector","gpt-4o-2024-08-06-repeat_user_prompt"]
rows=[]; tot=0
for p in SETS:
    rng=random.Random(f"{SEED}-{p}")
    fs=sorted(glob.glob(f"dyn/runs/{p}/*/*/*/*.json"))
    att=[f for f in fs if "/important_instructions/" in f]; none=[f for f in fs if "/none/" in f]
    lab={f:json.load(open(f)).get("security") for f in att}; miss=[f for f in att if lab[f] is None]
    if miss: print(p,"EXCLUDED (no security field):",miss)
    pos=[f for f in att if lab[f] is True]; neg=[f for f in att if lab[f] is False]
    k=min(len(pos),POS_CAP); sp=rng.sample(pos,k); sn=rng.sample(neg,N_ATT-k); so=rng.sample(none,N_NONE)
    for stratum,pop,s in [("att_pos",pos,sp),("att_neg",neg,sn),("none",none,so)]:
        for f in s:
            d=json.load(open(f)); t=len(enc.encode(json.dumps(d["messages"])))+OVER; tot+=t
            rows.append(dict(set=p,file=f,stratum=stratum,N_stratum=len(pop),n_stratum=len(s),weight=len(pop)/len(s),
                             checker_security=d.get("security"),checker_utility=d.get("utility"),est_tok=t))
        print(p,stratum,"N",len(pop),"n",len(s),"w",round(len(pop)/len(s),3))
json.dump(rows,open("judge_pilot/sample.json","w"),indent=0)
print("TOTAL",len(rows),"est input tok (o200k)",tot)
