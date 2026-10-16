# Seeded stratified sample for the judge pilot (no model calls). 250 important_instructions + 50 none per set.
import json,glob,random,tiktoken,statistics as st,sys
enc=tiktoken.get_encoding("o200k_base"); PROMPT_OVERHEAD=700; OUT=150
SETS=["gpt-4o-2024-08-06-tool_filter","gpt-4o-2024-08-06-prompt_guard_2_detector","gpt-4o-2024-08-06-repeat_user_prompt"]
tot_in=0; rows=[]
for p in SETS:
    fs=sorted(glob.glob(f"dyn/runs/{p}/*/*/*/*.json")); att=[f for f in fs if "/important_instructions/" in f]; none=[f for f in fs if "/none/" in f]
    rng=random.Random(20261015); s=rng.sample(att,250)+rng.sample(none,50)
    L=[len(enc.encode(json.dumps(json.load(open(f))["messages"])))+PROMPT_OVERHEAD for f in s]
    tot_in+=sum(L); rows+= [dict(set=p,file=f) for f in s]
    print(p,len(s),"judge-input tok: sum",sum(L),"median",st.median(L),"max",max(L))
json.dump(rows,open("judge_pilot/sample.json","w"),indent=0)
print("TOTAL judgments",len(rows),"input tok",tot_in,"output tok (150 each)",OUT*len(rows))
