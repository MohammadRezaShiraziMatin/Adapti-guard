"""Run episode-bootstrap (analyze.py), clustered (clustered.py) and LODO (lodo.py) logic unchanged, on the ATT-ARG reduced set,
for metric in {attarg, namematch}. Input: attarg/episodes_attarg.jsonl rows with attarg not None (excluded tasks dropped).
'attempted' field is set to the chosen metric. Outputs attarg/out/<metric>_{episode_all,episode_conf,clustered,lodo}.json"""
import json,os,sys,re
os.makedirs('attarg/out',exist_ok=True)
for metric in ['attarg','namematch']:
    tmp=f'attarg/out/episodes_{metric}.jsonl'
    with open(tmp,'w') as o:
        for l in open('attarg/episodes_attarg.jsonl'):
            r=json.loads(l)
            if r['attarg'] is None: continue
            if metric=='attarg': r['attempted']=r['attarg']
            o.write(json.dumps(r)+'\n')
    for mode in ['all','conf']:
        src=open('rankflip/analyze.py').read().replace("'rankflip/episodes.jsonl'",repr(tmp))
        src=src.replace("    if r['score_err'] or r['executed'] is None: continue","    if r['score_err'] or r['executed'] is None: continue\n    if MODE=='conf' and r['bench']=='agentdyn' and r['suite'] in ('shopping','github'): continue")
        src=src.replace("'rankflip/results.json'",repr(f'attarg/out/{metric}_episode_{mode}.json'))
        exec(src,{'MODE':mode})
    src=open('clustered/clustered.py').read().replace("'rankflip/episodes.jsonl'",repr(tmp)).replace("'clustered/clustered_results.json'",repr(f'attarg/out/{metric}_clustered.json'))
    exec(src,{'__name__':'__main__'})
    src=open('lodo/lodo.py').read().replace("'lodo/lodo_results.json'",repr(f'attarg/out/{metric}_lodo.json'))
    src=src.replace("src0=open('rankflip/analyze.py').read()","src0=open('rankflip/analyze.py').read().replace(\"'rankflip/episodes.jsonl'\","+repr(repr(tmp))+")")
    exec(src,{'__name__':'__main__'})
