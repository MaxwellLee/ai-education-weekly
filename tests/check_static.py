from pathlib import Path
from lxml import html as H
from urllib.parse import parse_qs
import json,base64,io,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]; S=ROOT/'src'; sys.path.insert(0,str(S)); import build
raw=(S/'index.html').read_text(); full=H.fromstring(raw)
manifest=json.loads((S/'data/issues.json').read_text()); latest=manifest['latestIssueId']; issues={i['id']:json.loads((S/'data'/i['file']).read_text()) for i in manifest['issues']}
ideas=json.loads((S/'data/ideas.json').read_text())['items']; profiles={p['id']:p for p in json.loads((S/'data/people.json').read_text())['items']}
assert latest=='004' and set(issues)=={'001','002','003','004'}
assert len({x['id'] for x in ideas})==len(ideas)
assert {x['id'] for x in ideas if x['firstIssue']==latest}==set(issues[latest]['newIdeaIds'])
assert all(x['firstIssue'] in issues for x in ideas)
byclass=lambda d,c:d.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," '+c+' ")]')
snapshots={i:full.get_element_by_id('issue-template-'+i) for i in issues}
reports={}
for key,snap in snapshots.items():
 ids=snap.xpath('.//*[@id]/@id'); assert len(ids)==len(set(ids)),('duplicate snapshot IDs',key)
 issue=issues[key]; people=issue['publicFigures']; assert len(people)>=10
 assert len({x.get('name',x.get('person')) for x in people})==len(people)
 assert len(snap.xpath('.//*[@data-weekly-page]'))==6
 assert len(snap.xpath('.//*[@data-weekly-page and not(@hidden)]'))==1
 assert not snap.xpath('.//*[@data-idea-id]')
 assert len(snap.xpath('.//article[contains(@class,"news-card")]'))==len(issue['education']['items'])
 assert len(snap.xpath('.//article[contains(@class,"person-card")]'))==len(people)
 for p in people:
  profile=profiles[p['id']]; assert 1<=len(profile['contributions'])<=2
  assert p.get('sources') or p.get('source_url')
  assert profile['profileUpdatedAt'] and profile['portrait']['sourcePage']
 local=json.loads((S/'data/shenzhen'/f'{key}.json').read_text())
 assert len(snap.xpath('.//article[@class="shenzhen-card"]'))==len(local['items'])
 cols,rows=build.distribution(issue['education']['items']); allids=[v for r in rows.values() for vs in r.values() for v in vs]
 assert len(allids)==len(set(allids))==len(issue['education']['items'])
 for td in snap.xpath('.//*[@data-count]'):assert int(td.get('data-count'))==len(rows[td.get('data-topic')][td.get('data-stage')])
 assert len(snap.xpath('.//article[@class="experiment-card"]'))==3
 reports[key]={'education':len(issue['education']['items']),'figures':len(people),'shenzhen':len(local['items']),'matrixTotal':len(allids)}
# Template IDs are intentionally repeated in inert snapshots; active DOM must be unique.
d=H.fromstring(raw)
for t in d.xpath('//template'):t.getparent().remove(t)
ids=d.xpath('//*[@id]/@id'); assert len(ids)==len(set(ids))
assert set(d.xpath('//select[@id="issue-select"]/option/@value'))==set(issues)
assert set(d.xpath('//nav[@aria-label="周报页面"]/a/text()'))=={'本期预览','AI教育前沿','深圳专题','行业动态','公众人物言论','更新须知'}
assert len(d.xpath('//nav[@aria-label="周报页面"]/a'))==6
library=d.get_element_by_id('library-panel'); assert 'hidden' in library.attrib
assert len(library.xpath('.//*[@data-idea-id]'))==len(ideas)
assert not d.get_element_by_id('weekly-panel').xpath('.//*[@data-idea-id]')
assert not d.xpath('//script[@src]|//link[@rel="stylesheet"]')
image_count=0
for img in full.xpath('//img'):
 assert img.get('alt')
 src=img.get('src','')
 if src.startswith('data:image/'): image=Image.open(io.BytesIO(base64.b64decode(src.split(',',1)[1])))
 else:
  p=(S/src).resolve(); assert p.is_relative_to((S/'assets').resolve()) and p.is_file()
  assert (ROOT/'docs'/src).read_bytes()==p.read_bytes()
  image=Image.open(p)
 image.verify();image_count+=1
for a in full.xpath('//a[@href]'):
 href=a.get('href');assert href not in ['#','https://','http://']
 if href.startswith('#issue='):
  q=parse_qs(href[1:]);assert q['issue'][0] in issues;assert q['page'][0] in ['preview','education','people','shenzhen','industry','updates']
  if q.get('focus'):assert q['focus'][0] in snapshots[q['issue'][0]].xpath('.//*[@id]/@id'),href
assert 'fixture-' not in raw
camel=lambda x:x.split('-')[0]+''.join(p.title() for p in x.split('-')[1:])
def info(e):return {'id':e.get('id'),'dataset':{camel(k[5:]):v for k,v in e.attrib.items() if k.startswith('data-')},'attrs':dict(e.attrib)}
extract=lambda xp:[info(e) for e in d.xpath(xp)]
out={'app':json.loads(d.get_element_by_id('app-data').text),'ids':ids,'facets':[info(e) for e in byclass(d,'facet')],'scope':[info(e) for e in byclass(d,'scope-button')],'nav':extract('//nav[@aria-label="周报页面"]/a'),'pages':extract('//*[@data-weekly-page]'),'cards':[info(e) for e in byclass(d,'creative-card')]}
(ROOT/'tests/dom.json').write_text(json.dumps(out,ensure_ascii=False))
report={'passed':True,'issues':reports,'latest':latest,'cumulativeIdeas':len(ideas),'newIdeas':sum(x['firstIssue']==latest for x in ideas),'decodedImageElementsIncludingTemplates':image_count,'htmlBytes':len(raw.encode()),'duplicateActiveIds':0,'brokenInternalRoutes':0,'browserVisualQA':'not covered by this script'}
(ROOT/'tests/static-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
