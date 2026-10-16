"""Re-verify numbers in MANUSCRIPT_DRAFT_v2.md against cited sources. Offline.
Part 1: hard recomputations from result JSONs (exact expected values).
Part 2: for every paragraph/table row carrying [src: ...] or [v1 §...], each numeric token
must occur in at least one cited file (normalised text search; JSON numbers also matched
after rounding). Unmatched tokens are listed as MISMATCH candidates for manual triage."""
import re,json,math,os,glob,sys
os.chdir('/workspace/pivot-checks')
MS=sys.argv[1] if len(sys.argv)>1 else 'MANUSCRIPT_DRAFT_v2.md'; V1='/workspace/adapti-guard/docs/paper/negative_result/MANUSCRIPT_DRAFT_v1.md'
out=[]; P=lambda *a: out.append(' '.join(str(x) for x in a))
# ---------- Part 1
def summ(path):
    r=json.load(open(path)); pairs=sum(math.comb(len(o['n']),2) for o in r)
    return {k:(sum(o[k]['nflip']>0 for o in r),sum(o[k]['nflip'] for o in r),pairs,len(r)) for k in ('ATT','ATTCA')}
exp={'review/results_conf.json':{'ATT':(3,4,290,9),'ATTCA':(2,2,290,9)},
     'rankflip/results.json':{'ATT':(4,6,299,9),'ATTCA':(3,4,299,9)},
     'review/results_droperr_conf.json':{'ATT':(3,4,290,9),'ATTCA':(2,2,290,9)},
     'review/results_droperr_all.json':{'ATT':(4,6,299,9),'ATTCA':(3,4,299,9)}}
hard_bad=0
for f,e in exp.items():
    g=summ(f)
    for k in e:
        ok=g[k]==e[k]; hard_bad+=not ok; P('HARD',f,k,'(cells,flips,pairs,eligible)=',g[k],'expected',e[k],'OK' if ok else 'MISMATCH')
c=json.load(open('clustered/clustered_results.json'))
for m,e in (('conf',(3,4,290)),('all',(1,1,299))):
    s=c[m]['summary']; g=(s['ATT']['cells_with_flip'],s['ATT']['flips'],s['pairs']); ok=g==e; hard_bad+=not ok
    P('HARD clustered',m,g,'expected',e,'OK' if ok else 'MISMATCH')
L=json.load(open('lodo/lodo_results.json'))
for k,e in (('conf|progent',(1,1,227)),('all|progent',(1,1,235))):
    r=L[k]; g=(r['ATT']['cells'],r['ATT']['flips'],r['pairs']); ok=g==e; hard_bad+=not ok
    P('HARD LODO',k,g,'expected',e,'OK' if ok else 'MISMATCH')
import hashlib
h=hashlib.sha256(open('docs/DESIGN_VARIANCE_STUDY.PREREG_2026-10-15_2240.md','rb').read()).hexdigest()
rec=open('review/PREREG_RANKFLIP.sha256').read().split()[0]
ok=h==rec; hard_bad+=not ok; P('HARD prereg hash',h[:12],'recorded',rec[:12],'OK' if ok else 'MISMATCH')
for f in ('docs/SENSITIVITY_LODO','docs/SENSITIVITY_CLUSTERED'):
    h=hashlib.sha256(open(f+'.md','rb').read()).hexdigest(); rec=open(f+'.sha256').read().split()[0]
    ok=h==rec; hard_bad+=not ok; P('HARD lock',f,'OK' if ok else 'MISMATCH (file changed after lock)')
sp=open('judge_pilot/SPEND_LOG.csv').read().strip().splitlines()[-1].split(',')
ok=abs(float(sp[6])-0.3787)<5e-5 and abs(float(sp[7])-0.3746)<5e-5; hard_bad+=not ok
P('HARD spend',sp[6],sp[7],'OK' if ok else 'MISMATCH')
gt=json.load(open('drift/gt_audit_agentdyn_v1.json'))
dyn=[x for x in gt if x['suite'] in ('dailylife','shopping','github')]
g=(len(dyn),sum(not x['security_after_gt'] for x in dyn)); ok=g==(28,20); hard_bad+=not ok
P('HARD gt_audit AgentDyn-specific (tasks,fail)=',g,'expected (28, 20)','OK' if ok else 'MISMATCH')
g=(len(gt),sum(not x['security_after_gt'] for x in gt)); ok=g==(55,21); hard_bad+=not ok
ad=[x for x in gt if x['suite'] in ('workspace','travel','banking','slack')]
g2=(len(ad),sum(not x['security_after_gt'] for x in ad)-sum(1 for x in ad if x['suite']=='travel' and x['inj']=='injection_task_6' and not x['gt_calls'] and not x['security_after_gt'])); ok2=g2==(27,0); hard_bad+=not ok2
P('HARD gt_audit AgentDojo v1 (tasks,defects excl. text-only travel inj6)=',g2,'expected (27, 0)','OK' if ok2 else 'MISMATCH')
P('HARD gt_audit all v1 (tasks,fail)=',g,'manuscript says (55, 21) [erratum 2026-10-16; was 70]','OK' if ok else 'MISMATCH: JSON has only %d task records'%len(gt))
# ---------- Part 1b (added 2026-10-16 audit round): new offline evidence
sv=json.load(open('bitems/scorer_validation/comparison.json'))
s=open('bitems/scorer_validation/labels_AI.json').read()
ok=hashlib.sha256(s.encode()).hexdigest()==open('bitems/scorer_validation/labels_AI.sha256').read().split()[0]; hard_bad+=not ok
P('HARD scorer-validation label lock','OK' if ok else 'MISMATCH')
for d,e in (('progent',(40,37,0.85)),('drift',(40,30,0.5))):
    g=(sv[d]['n'],sv[d]['agree'],sv[d]['kappa']); ok=g==e; hard_bad+=not ok; P('HARD scorer validation',d,g,'expected',e,'OK' if ok else 'MISMATCH')
for m,e in (('conf',(3,4,280,8)),('all',(4,6,289,8))):
    g=summ(f'bitems/results_exclunv_{m}.json')['ATT']; ok=g==e; hard_bad+=not ok; P('HARD excl-unversioned',m,g,'expected',e,'OK' if ok else 'MISMATCH')
for m,e in (('conf',(4,8)),('all',(5,12))):
    r=json.load(open(f'bitems/perm_fwer_{m}.json')); g=(sum(bool(o['flags']) for o in r),sum(len(o['flags']) for o in r)); ok=g==e; hard_bad+=not ok
    P('HARD perm FWER',m,g,'expected',e,'OK' if ok else 'MISMATCH')
ck=json.load(open('c_items/taskSuite_check_pertask.json'))
g=sum(v is not True for s_ in ('shopping','github','dailylife') for v in ck[s_]['inj'].values()); g2=sum(len(ck[s_]['inj']) for s_ in ('shopping','github','dailylife'))
ok=(g2,g)==(28,20); hard_bad+=not ok; P('HARD TaskSuite.check per-task AgentDyn (tasks,fail)=',(g2,g),'expected (28, 20)','OK' if ok else 'MISMATCH')
g=sum(v is not True for s_ in ('workspace','travel','banking','slack') for v in ck[s_]['inj'].values()); ok=g==0; hard_bad+=not ok
P('HARD TaskSuite.check per-task AgentDojo suites injection failures=',g,'expected 0','OK' if ok else 'MISMATCH')
ok='security after GT + OTP step: True' in open('c_items/inj2_rootcause.txt').read() and 'security after GT only: False' in open('c_items/inj2_rootcause.txt').read(); hard_bad+=not ok
P('HARD inj2 root cause (GT False, GT+OTP True)','OK' if ok else 'MISMATCH')
# ---------- Part 2
def norm(t): return t.replace('\u2212','-').replace('\u2013','-').replace(',','').replace('\u2009','')
cache={}
def text(path):
    if path in cache: return cache[path]
    fs=[path] if os.path.isfile(path) else sorted(glob.glob(path+'/*')) if os.path.isdir(path) else []
    t=''
    for f in fs:
        if os.path.isfile(f) and os.path.getsize(f)<60e6:
            try: t+=open(f,errors='ignore').read()
            except: pass
    cache[path]=norm(t); return cache[path]
jsnum={}
def jnums(path):
    if path in jsnum: return jsnum[path]
    vals=set()
    if path.endswith('.json') or path.endswith('.py') and os.path.isfile(path):
        for x in re.findall(r'-?\d+\.\d+|-?\d+',text(path)): 
            try: vals.add(float(x))
            except: pass
    jsnum[path]=vals; return vals
def found(tok,paths):
    t=norm(tok)
    for p in paths:
        T=text(p)
        if t in T: return True
        if '/' in t:
            a,b=t.split('/',1)
            if re.search(r'\b%s\s*/\s*%s\b'%(re.escape(a),re.escape(b)),T) or re.search(r'\b%s of %s\b'%(re.escape(a),re.escape(b)),T): return True
        try:
            v=float(t.rstrip('%'))
            for w in jnums(p):
                if abs(round(w,3)-v)<1e-9 or abs(round(w,2)-v)<1e-9 or abs(round(w*100,1)-v)<1e-9 or abs(round(w,4)-v)<1e-9: return True
        except: pass
        if t.startswith('-') and t[1:] in T: return True
        if t.startswith('+') and t[1:] in T: return True
        if t.endswith('%') and t[:-1] in T: return True
    return False
ms=open(MS).read()
units=[u for u in re.split(r'\n(?=\S)',ms)]  # paragraphs, bullets, table rows
SRC=re.compile(r'\[src: ([^\]]+)\]'); V1T=re.compile(r'\[v1 §')
NUM=re.compile(r'(?<![\w.#`/])[+\-\u2212]?\d[\d,]*(?:\.\d+)?(?:/\d[\d,]*)?%?(?![\w`])')
DERIVED={'3/9','1/9','2/9','4/9','4/4','290','299','227','235','97bdb074'}  # Part-1 verified counts
# Resolved text-search flags (token, context substring) -> justification. See review/FLAG_RESOLUTIONS.md
ALLOW={
 ('12','Hash check (re-run 2026-10-16 12:2x'):'clock time 12:2x Tehran of the hash re-run, not a data value',
 ('28','Of the 28 AgentDyn-specific injection tasks'):'= dailylife 10 + shopping 9 + github 9; HARD-checked (28,20) in Part 1 from gt_audit_agentdyn_v1.json',
 ('28','all in the 28 AgentDyn-specific tasks'):'same 28 as above; HARD-checked in Part 1',
 ('27','0 in the 27 AgentDojo v1 tasks'):'= workspace 6 + travel 7 + banking 9 + slack 5 (55-28); HARD-checked (27,0) in Part 1',
 ('40','Each AgentDyn cell adds 40 shopping/github user tasks'):'shopping 20 + github 20 user tasks (get_suites v1); = ntasks 60 (all) - 20 (conf) in clustered/diag_results.json',
 ('40','each AgentDyn cell adds 40 shopping/github user tasks'):'same 40 as the allowlisted entry above (lower-case sentence position)',
 ('7.1','7.1 pp'):'7.1 pp = 0.071 x 100, the largest per-set drift shift (-0.071) in drift/DRIFT_RESULTS.md',
 ('0.3787','separate from the $0.3787 for the re-analysis'):'cross-ref to judge pilot spend; matches judge_pilot/RESULTS.md line 2 (cited at §5.3/§8), not a v1 number',
}
checked=0; bad=[]
for u in units:
    srcs=[]
    for m in SRC.finditer(u):
        tag=re.sub(r'(\S*)\{([^}]*)\}(\S*)',lambda q:' '.join(q.group(1)+x+q.group(3) for x in q.group(2).split(',')),m.group(1))
        for part in re.split(r'[;,]|→|\s',tag):
            part=part.strip().strip('`').strip(',.')
            if '/' not in part and not part.endswith(('.md','.json','.csv','.txt','.py')): continue
            if part.startswith('review/*'): continue
            if '{' in part:
                a,b=part.split('{'); b,c=b.split('}'); srcs+= [a+x+c for x in b.split(',')]
            elif part: srcs.append(part)
    if V1T.search(u): srcs.append(V1)
    if not srcs: continue
    # also allow source paths cited in a table row's last cell
    body=SRC.sub('',u); body=re.sub(r'`[^`]*`','',body); body=re.sub(r'§\s?[\dA-Z.\-–, ]+','',body)
    body=re.sub(r'\b(20\d\d-\d\d-\d\d|\d{4}\.\d{5})\b','',body)
    for tok in NUM.findall(body):
        bare=norm(tok).lstrip('+-').rstrip('%')
        if re.fullmatch(r'\d',bare) or re.fullmatch(r'20\d\d',bare): continue  # small ints / years
        if bare in DERIVED: continue  # verified exactly in Part 1
        if any(bare==a and c in u for (a,c) in ALLOW): continue  # resolved flag, see ALLOW / review/FLAG_RESOLUTIONS.md
        checked+=1
        if not found(tok,srcs): bad.append((tok,srcs[:3],u[:90].replace('\n',' ')))
P(f'\nPART 2: {checked} numeric tokens checked against cited sources; {len(bad)} not found:')
for b in bad: P('MISMATCH?',b[0],'| sources:',', '.join(b[1]),'| context:',b[2])
# ---------- Part 3: untagged front matter (abstract, highlights) must reuse numbers present in the tagged body
fm_bad=[]
if '## Abstract' in ms and '## 1 Introduction' in ms:
    fm=ms[ms.index('## Abstract'):ms.index('## 1 Introduction')]; rest=norm(ms[ms.index('## 1 Introduction'):])
    words={'one':'1','three':'3','nine':'9','twenty':'20'}
    for tok in NUM.findall(re.sub(r'\(Pathade et al\., 2026\)','',fm)):
        t=norm(tok).lstrip('+')
        if re.fullmatch(r'\d',t): continue
        alt=[t, t.replace(' of ','/')]
        if not any(a in rest for a in alt): fm_bad.append(tok)
    for m in re.finditer(r'(\d+) of (\d+)',fm):
        if m.group(1)+'/'+m.group(2) not in rest and m.group(0) not in rest: fm_bad.append(m.group(0))
P(f'\nPART 3: front-matter numbers not found in tagged body: {fm_bad}')
P(f'\nSUMMARY: hard checks mismatches={hard_bad}; text-search unmatched={len(bad)}; front-matter unmatched={len(fm_bad)}')
open(sys.argv[2] if len(sys.argv)>2 else 'review/verify_numbers_out.txt','w').write('\n'.join(out)+'\n'); print('\n'.join(out[-60:]))
