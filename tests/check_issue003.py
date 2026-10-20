from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];D=R/'src/data'; old=Path('/workspace/scratch/f41a9fdb53c1/weekly_20261012/industry_revision/release')
load=lambda p:json.loads(p.read_text())
paths=['src/data/issues/001.json','src/data/issues/002.json','src/data/shenzhen/001.json','src/data/shenzhen/002.json','src/data/industry/002.json']+[str(p.relative_to(old)) for p in (old/'snapshots').glob('*') if p.is_file()]
for rel in paths:assert (R/rel).read_bytes()==(old/rel).read_bytes(),rel
for filename,key in [('ideas.json','items'),('people.json','items')]:
 a=load(old/'src/data'/filename)[key];b=load(D/filename)[key];assert b[:len(a)]==a,filename
assert load(D/'editorial.json')['issues']['001']==load(old/'src/data/editorial.json')['issues']['001']
assert load(D/'editorial.json')['issues']['002']==load(old/'src/data/editorial.json')['issues']['002']
i=load(D/'issues/003.json');assert i['cutoff']=='2026-10-19T09:00:00+08:00';assert len(i['publicFigures'])==10
assert len(i['education']['summaries']) in range(3,6)
assert len(i['newIdeaIds'])>=10
for n in i['education']['items']:
 if not n.get('isBackground'):assert '2026-10-12'<=n['date']<='2026-10-19',(n['id'],n['date'])
ind=load(D/'industry/003.json');assert {x['id'] for x in ind['items']} >= {x['id'] for x in load(D/'industry/002.json')['items']}
assert next(x for x in ind['items'] if x['id']=='industry-lingdong')['firstIssueId']=='003'
print('PASS: exact 001/002 source+snapshots preserved; old ideas, profiles and editorials unchanged; issue003 cutoff, counts, window, highlights and retained industry identities checked.')
