#!/usr/bin/env python3
"""Validate production data with the Python standard library; no third-party install."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
manifest=load(ROOT/'data/issues.json');catalog=load(ROOT/'data/ideas.json')
issues=manifest['issues'];ideas=catalog['items']
assert issues and ideas
assert len({x['id'] for x in issues})==len(issues),'Duplicate issues'
assert len({x['id'] for x in ideas})==len(ideas),'Duplicate idea IDs'
assert [x['date'] for x in issues]==sorted(x['date'] for x in issues),'Issue order must be chronological'
assert manifest['latestIssueId']==issues[-1]['id'],'Latest issue must be last chronologically'
assert manifest['libraryAsOf']==catalog['asOf'],'Library dates must agree'
issue_ids={x['id'] for x in issues};idea_ids={x['id'] for x in ideas}
required=['id','title','firstIssue','firstSeen','originalDate','updatedAt','lastVerified','categories','tools','difficulty','difficultyGroup','uses','educationLevels','audienceTypes','scopeTags','stageBasis','sources']
for x in ideas:
 assert all(k in x for k in required),('Missing creative field',x['id'])
 assert x['firstIssue'] in issue_ids,('Unknown firstIssue',x['id'])
 for k,allowed in [('categories',catalog['categoryOrder']),('educationLevels',catalog['educationLevelOrder']),('audienceTypes',catalog['audienceTypeOrder']),('scopeTags',catalog['scopeTagOrder'])]:
  assert isinstance(x[k],list) and len(x[k])==len(set(x[k])) and set(x[k])<=set(allowed),(x['id'],k)
 assert x['categories'] and x['tools'] and x['uses']
 assert x['difficultyGroup'] in ['入门','进阶','分层']
 for k in ['firstSeen','updatedAt','lastVerified']:assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',x[k]),(x['id'],k)
 for s in x['sources']:assert s['url'].startswith('https://'),x['id']
 image=x.get('image',{});local=image.get('localPath')
 if local:
  p=(ROOT/local).resolve();assert p.is_relative_to(ROOT.resolve()) and p.is_file(),('Image missing',local)
for index in issues:
 p=(ROOT/'data'/index['file']).resolve();assert p.is_relative_to((ROOT/'data/issues').resolve())
 x=load(p);assert x['id']==index['id'] and x['date']==index['date']
 assert len(x.get('publicFigures',[]))>=10,'Fewer than 10 specific people updates'
 assert len({p['name'] for p in x['publicFigures']})==len(x['publicFigures'])
 for p in x['publicFigures']:
  assert p.get('title') and p.get('summary') and p.get('date') and p.get('verification')
  assert p.get('source_url','').startswith('https://') or p.get('sources')
 new={i['id'] for i in ideas if i['firstIssue']==x['id']}
 assert set(x['newIdeaIds'])==new,('New idea IDs disagree with firstIssue',x['id'])
 assert set(i['id'] for i in x.get('creativeSnapshots',[]))<=idea_ids
 assert x['education']['items']
 for n in x['education']['items']:
  assert n.get('sources') and n.get('date')
  assert set(n.get('educationLevels',[]))<=set(catalog['educationLevelOrder'])
print(f'PASS: {len(issues)} issue(s), {len(ideas)} cumulative ideas; production data and references are consistent.')

profiles=load(ROOT/'data/people.json')
assert profiles['schemaVersion']==1 and profiles['publicationStatus'] in ['public-edition','private-preview']
assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',profiles['asOf'])
profile_ids={p['id'] for p in profiles['items']}
assert len(profile_ids)==len(profiles['items'])
all_people={p['id'] for index in issues for p in load(ROOT/'data'/index['file'])['publicFigures']}
assert profile_ids==all_people,('Profiles must match current issue people',profile_ids^all_people)
portrait_count=0
for p in profiles['items']:
 for k in ['id','name','identity','bio','contributions','followReason','profileUpdatedAt','profileSources','portrait']:assert p.get(k),('Missing profile field',p['id'],k)
 assert len(p['bio'])==2 and all(isinstance(b,str) and b.strip() for b in p['bio'])
 assert 1<=len(p['contributions'])<=2
 sources=list(p['profileSources'])
 for c in p['contributions']:
  assert c.get('text') and c.get('source');sources.append(c['source'])
 for s in sources:assert s.get('title') and s.get('url','').startswith('https://'),('Profile source gap',p['id'])
 assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',p['profileUpdatedAt']),p['id']
 im=p['portrait'];assert all(k in im for k in ['path','sourcePage','imageUrl','credit','alt','rightsStatus'])
 assert im['rightsStatus'].strip()
 if im['path']:
  path=(ROOT/im['path']).resolve();assert path.is_relative_to((ROOT/'assets/portraits').resolve()) and path.is_file()
  assert im['sourcePage'].startswith('https://')
  assert im.get('imageUrl') is None or im['imageUrl'].startswith('https://')
  assert im['credit'].strip() and im['alt'].strip()
  assert path.stat().st_size<=150_000,('Oversized portrait',p['id'])
  portrait_count+=1
 else:assert im.get('missingReason'),('Missing portrait reason',p['id'])
print(f'PASS: {len(profiles["items"])} person profiles, {portrait_count} source-backed portraits, {len(profiles["items"])-portrait_count} explicit photo placeholders; dates and sources separated from issue updates.')

editorials=load(ROOT/'data/editorial.json')['issues']
assert set(editorials)==issue_ids
all_issues={i['id']:load(ROOT/'data'/i['file']) for i in issues}
for iid,e in editorials.items():
 issue=all_issues[iid];ids={n['id'] for n in issue['education']['items']}
 assert len(e['experiments'])==3 and len({a['id'] for a in e['experiments']})==3
 for a in e['experiments']:
  for key in ['title','audience','estimatedMinutes','steps','verificationGoal']:assert a[key].strip()
  assert '估计' in a['estimatedMinutes'] and a['status']=='编辑建议，未实测'
  assert a['sourceIds'] and set(a['sourceIds'])<=ids
 changes=e['changes'];assert changes['baselineIssue'] in issue_ids
 assert changes['baselineDate']==all_issues[changes['baselineIssue']]['date']
 assert changes['status'] in ['baseline','compared','no-verified-change']
 if len(issues)==1:assert changes['status']=='baseline' and not changes['items']
 if changes['status']!='compared':assert not changes['items']
 for c in changes['items']:
  for key in ['title','previous','current','changeType','sourceDate']:assert c[key]
  assert c['sources'] and all(z['url'].startswith('https://') for z in c['sources'])
  for k,j in [('firstIssue','firstItemId'),('previousIssue','previousItemId')]:
   assert c[k] in all_issues and c[j] in {n['id'] for n in all_issues[c[k]]['education']['items']}
 for log in e['revisionLog']:assert all(log.get(k) for k in ['date','version','type','summary'])
 for correction in e['factCorrections']:assert all(correction.get(k) for k in ['itemId','date','before','after','reason','sources'])
print('PASS: three source-linked, untested editorial suggestions per issue; valid baseline/change references; version revisions separated from factual corrections.')
for iid,e in editorials.items():
 people={p['id']:p for p in all_issues[iid]['publicFigures']}
 for u in e.get('evidenceUpdates',[]):
  assert u['itemId'] in people and set(u['after'])<= {'role','caveat'}
  assert set(u['before'])==set(u['after'])
  assert all(people[u['itemId']][k]==v for k,v in u['before'].items())
  assert u['sources'] and all(s['url'].startswith('https://') and s.get('title') for s in u['sources'])
for p in profiles['items']:
 if p['portrait'].get('path'):
  assert p['portrait'].get('publicReuseCleared') is False
  assert '未确认' in p['portrait']['rightsStatus']
print('PASS: evidence supplements retain exact prior values; all portrait sources and unconfirmed reuse-permission status are explicit.')

for index in issues:
 issue=load(ROOT/'data'/index['file']);p=ROOT/'data/shenzhen'/f'{issue["id"]}.json'
 if not p.exists():continue
 local=load(p);assert local['issueId']==issue['id'] and local['schemaVersion']==1
 assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',local['verifiedAt'])
 assert len({n['id'] for n in local['items']})==len(local['items'])
 for n in local['items']:
  for key in ['id','districts','type','stage','title','publishedDate','eventDate','organizations','peopleCompanies','summary','relevance','limits','sources','freshness']:assert n.get(key),(n.get('id'),key)
  assert n['freshness'] in ['current','baseline']
  assert all(z['url'].startswith('https://') for z in n['sources'])
  assert n['publishedDate']<=local['verifiedAt']
  if n['freshness']=='current':assert issue['window']['start']<=n['publishedDate']<=issue['window']['end']
  else:assert n['publishedDate']<issue['window']['start']
print('PASS: Shenzhen dates, issue isolation, freshness labels and required evidence fields.')

for path in (ROOT/'data/industry').glob('*.json'):
 data=load(path)
 assert data['issue'] in issue_ids
 assert len({x['id'] for x in data['items']})==len(data['items'])
 for x in data['items']:
  assert all(x.get(k) for k in ['entity','title','sourceDate','audience','stage','businessModel','pricingCosts','financials','financialBoundary','sources','limits','followup'])
  assert x['freshness'] in ['current','baseline']
  assert all(s['url'].startswith('https://') for s in x['sources'])
print('PASS: industry identity, evidence dates, model and financial boundaries.')
