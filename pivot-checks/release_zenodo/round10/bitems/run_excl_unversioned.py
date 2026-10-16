"""B #19: rankflip/analyze.py logic unchanged (seed 20261015, B=2000); only input filter: drop AgentDojo episodes whose
raw run file has no benchmark_version (they were scored as v1 by assumption). MODE conf|all as in review/run.py."""
import json,glob,sys
mode=sys.argv[1]
unv=set()
for f in glob.glob('ad/runs/*/*/*/*/injection_task_*.json'):
    try: e=json.load(open(f))
    except Exception: continue
    if e.get('benchmark_version') is None:
        p=f.split('/'); unv.add((p[2],p[3],p[4],p[5],e['injection_task_id']))
print('unversioned AgentDojo files:',len(unv))
src=open('rankflip/analyze.py').read()
src=src.replace("    if r['score_err'] or r['executed'] is None: continue",
"    if r['score_err'] or r['executed'] is None: continue\n"
"    if r['bench']=='agentdojo' and (r['pipe'],r['suite'],r['ut'],r['attack'],r['inj']) in UNV: continue\n"
"    if MODE=='conf' and r['bench']=='agentdyn' and r['suite'] in ('shopping','github'): continue")
src=src.replace("'rankflip/results.json'","OUT")
g={'MODE':mode,'UNV':unv,'OUT':f'bitems/results_exclunv_{mode}.json'}; exec(src,g)
import math; res=g['res']
print(mode,'cells',len(res),'ATT cells with flip',sum(o['ATT']['nflip']>0 for o in res),'flips',sum(o['ATT']['nflip'] for o in res),'pairs',sum(math.comb(len(o['n']),2) for o in res))
