"""Agreement between owner blind labels and the AI reviewer on the 16-item owner subset.
Runs only when review/owner_labels.jsonl exists (format as owner_labels.TEMPLATE.jsonl:
{"id": "R03", "label": "<same label vocabulary as reviewer_labels.jsonl>", "ev": "..."}).
Outputs raw agreement %, Wilson 95% CI for agreement, Cohen's kappa, and the disagreement list.
Writes review/owner_agreement.json. Offline; invents nothing (exits if file is missing or incomplete)."""
import json, math, os, sys, collections
os.chdir('/workspace/pivot-checks')
P = 'review/owner_labels.jsonl'
if not os.path.exists(P):
    sys.exit('review/owner_labels.jsonl not found; owner labels pending. Nothing computed.')
ids = json.load(open('review/owner_subset_ids.json'))
own = {r['id']: r['label'].strip() for r in map(json.loads, open(P)) if r.get('label', '').strip()}
ai = {r['id']: r['label'].strip() for r in map(json.loads, open('review/reviewer_labels.jsonl'))}
missing = [i for i in ids if i not in own]
if missing:
    sys.exit(f'Owner labels missing for {missing}; nothing computed.')
pairs = [(own[i], ai[i]) for i in ids]
n = len(pairs); k = sum(a == b for a, b in pairs); po = k / n
z = 1.959964; c = (po + z*z/(2*n)) / (1 + z*z/n); h = z*math.sqrt(po*(1-po)/n + z*z/(4*n*n)) / (1 + z*z/n)
co, ca = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
pe = sum(co[l]*ca[l] for l in set(co) | set(ca)) / (n*n)
kappa = (po - pe) / (1 - pe) if pe < 1 else float('nan')
res = dict(n=n, agree=k, raw_pct=round(100*po, 1), wilson95=[round(c-h, 3), round(c+h, 3)],
           cohen_kappa=round(kappa, 3), disagreements=[dict(id=i, owner=own[i], ai=ai[i]) for i in ids if own[i] != ai[i]])
json.dump(res, open('review/owner_agreement.json', 'w'), indent=1); print(json.dumps(res, indent=1))
