import json,glob,collections,re
L=lambda p:[json.loads(l) for l in open(p)]
P="experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/"
V="experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/"
tracks={"B":(P+"B0/B0_predictions.jsonl",P+"PHASE1-CORE/PHASE1-CORE_predictions.jsonl","datasets/frozen/phase1_confirm_v1/dataset.jsonl"),
"A":(V+"B0/B0_predictions.jsonl",V+"VNEXT-ADAPT/VNEXT-ADAPT_predictions.jsonl","datasets/frozen/vnext_confirm_v1/dataset.jsonl")}
tot=0;treq=0
for t,(b0,d,ds) in tracks.items():
  D={r['id']:r for r in L(ds)}
  spec=lambda r:(r.get('tool_call') or r['metadata'].get('tool_call'))
  for arm,p in (("B0",b0),("DEF",d)):
    R=L(p); tot+=len(R)
    nreq=sum('TOOL_REQUEST' in (r.get('target_response') or '') for r in R); treq+=nreq
    gr=sum(bool((r.get('generation_raw') or {}).get('tool_call')) for r in R)
    att=[r for r in R if r['label']=='attack']; ben=[r for r in R if r['label']=='benign']
    ex=sum((r.get('tool_turn') or {}).get('executed') is True for r in att)
    reasons=collections.Counter((r.get('tool_turn') or {}).get('reason') for r in att)
    acts=collections.Counter(r.get('defense_action') for r in att)
    judge=sum(r['attack_succeeded'] for r in att)
    def det(r):
      s=spec(D[r['id']]); tt=r.get('tool_turn') or {}
      if tt.get('executed') is not True or tt.get('tool')!=s['name']: return False
      k=s['arguments'].get('kind') or s['arguments'].get('to'); return bool(k) and k in tt.get('observation','')
    detn=sum(det(r) for r in att)
    tb=[r for r in ben if r.get('tool_turn')]
    tbex=sum(r['tool_turn'].get('executed') is True for r in tb)
    denied_useful=sum(r['tool_turn'].get('executed') is not True and r['utility_success'] for r in tb)
    jutil=sum(r['utility_success'] is True for r in ben)
    named=sum(spec(D[r['id']])['name'] in re.sub(r'\[TOOL_RESULT\][\s\S]*','',r['target_response'] or '') for r in att)
    toolres=sum('[TOOL_RESULT]' in (r['target_response'] or '') for r in att)
    print(t,arm,"n",len(R),"TOOL_REQUEST",nreq,"genraw",gr,"att",len(att),"exec",ex,"det",detn,"judge",judge,dict(reasons),dict(acts),"| benign tool",len(tb),"exec",tbex,"denied&judgedUseful",denied_useful,"judgeUtil",jutil,"| model named tool",named,"TOOL_RESULT appended",toolres)
  a=[r for r in D.values() if r['label']=='attack']
  print(t,"threat_surface/direct",collections.Counter(r['metadata'].get('threat_surface') or r['metadata'].get('direct_or_indirect') for r in a))
  print(t,"tool names",collections.Counter(spec(r)['name'] for r in a), "kind/to",sum(bool(spec(r)['arguments'].get('kind') or spec(r)['arguments'].get('to')) for r in a))
print("total",tot,"TOOL_REQUEST",treq)
