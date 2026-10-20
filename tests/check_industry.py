from pathlib import Path
import json,hashlib
from lxml import html
R=Path(__file__).resolve().parents[1]; S=R/'src'
data=json.loads((S/'data/industry/002.json').read_text());issue=json.loads((S/'data/issues/002.json').read_text())
assert len(data['items'])>=13
assert len({x['id'] for x in data['items']})==len(data['items'])
for x in data['items']:
 for key in ['entity','title','audience','sourceDate','stage','businessModel','pricingCosts','financials','financialBoundary','limits','followup','sources']:
  assert x[key],(x['id'],key)
 assert x['freshness'] in ['current','baseline']
 assert all(y['url'].startswith('https://') for y in x['sources'])
assert set(x['frontierCategory'] for x in issue['education']['items'])=={'技术与研究','教学实践','政策与评价'}
assert len(issue['education']['items'])==12 and len(issue['publicFigures'])==10
assert len([x for x in json.loads((S/'data/ideas.json').read_text())['items'] if x['firstIssue'] in ['001','002']])==27
assert len(json.loads((S/'data/shenzhen/002.json').read_text())['items'])==6
raw=html.fromstring((S/'index.html').read_text());snap=raw.get_element_by_id('issue-template-002')
assert len(snap.xpath('.//article[@class="industry-card"]'))==len(data['items'])
assert len(snap.xpath('.//section[@class="education-group"]'))==3
assert raw.xpath('//nav[@aria-label="周报页面"]/a/text()')==['本期预览','AI教育前沿','深圳专题','行业动态','公众人物言论','更新须知']
expected='45139fa95b6b9371d6db25431ffe2f9b2689ec8e'; b=(R/'snapshots/002_published_20261012.html').read_bytes(); assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==expected
original=json.loads((R/'snapshots/002_published_20261012.json').read_text())
for x in issue['education']['items']:x.pop('frontierCategory')
issue['revisionNote']=original['revisionNote']; assert issue==original,'Existing issue content changed'
print('PASS: six-tab order, 3 categories, industry evidence fields, 12 education / 10 people / 6 Shenzhen / 27 ideas, exact published 002 snapshot, unchanged original issue facts.')

assert len(data['courseComparison'])==4
assert len(snap.xpath('.//article[@class="industry-compare-card"]'))==4
assert '币种' in next(x for x in data['items'] if x['id']=='industry-juniorcodes')['pricingCosts']
assert '整套' in next(x for x in data['items'] if x['id']=='industry-codakid')['businessModel']
print('PASS: four course comparison cards and pricing scope/currency safeguards.')

assert data['items'][:9]==json.loads((R/'tests/v8-industry-baseline.json').read_text())
print('PASS: original nine industry cards unchanged against v8.')
