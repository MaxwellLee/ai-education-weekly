from pathlib import Path
from lxml import html as H
import json,base64,io,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];S=ROOT if (ROOT/'data').is_dir() else ROOT/'src'
sys.path.insert(0,str(S));import build
raw=(S/'index.html').read_text();d=H.fromstring(raw)
for t in d.xpath('//template'):t.getparent().remove(t)
ids=d.xpath('//*[@id]/@id');assert len(ids)==len(set(ids))
byclass=lambda c:d.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," '+c+' ")]')
assert len(byclass('news-card'))==13 and len(byclass('x-card'))==13 and len(byclass('creative-card'))==15
assert d.xpath('count(//select[@id="issue-select"]/option)')==1
assert d.xpath('//nav/a/text()')==['本期预览','AI教育前沿','公众人物言论','更新须知']
assert len(d.xpath('//*[@data-weekly-page]'))==4
assert len(d.xpath('//*[@data-weekly-page and not(@hidden)]'))==1
assert d.xpath('//*[@data-weekly-page and not(@hidden)]')[0].get('data-weekly-page')=='preview'
weekly=d.get_element_by_id('weekly-panel');library=d.get_element_by_id('library-panel')
assert not weekly.xpath('.//*[@data-idea-id]')
assert len(library.xpath('.//*[@data-idea-id]'))==15
assert not d.xpath('//*[@id="archive" or @id="weekly-tab" or @id="library-tab" or @id="featured" or @id="watchlist"]')
assert 'hidden' in library.attrib
assert d.xpath('//*[@id="open-library"]')[0].getparent().get('class')=='eyebrow'
assert not d.xpath('//script[@src] | //link[@rel="stylesheet"]')
assert 'fetch(' not in raw and 'XMLHttpRequest' not in raw
for a in d.xpath('//a[starts-with(@href,"#")]'):
 target=a.get('href')[1:]
 if target.startswith('issue='):
  from urllib.parse import parse_qs
  q=parse_qs(target);assert q['issue']==['001'];assert q['page'][0] in ['preview','education','people','updates']
  if q.get('focus'):assert q['focus'][0] in ids
 else:assert target in ids,target
for img in d.xpath('//img'):
 assert img.get('alt') and img.get('src').startswith('data:image/')
 im=Image.open(io.BytesIO(base64.b64decode(img.get('src').split(',',1)[1])));im.verify()
profiles=json.loads((S/'data/people.json').read_text())['items']
portrait_count=sum(bool(p['portrait'].get('path')) for p in profiles)
creative_count=sum(bool(x['image'].get('localPath')) for x in json.loads((S/'data/ideas.json').read_text())['items'])
assert len(library.xpath('.//img'))==creative_count
assert len(weekly.xpath('.//img'))==portrait_count
assert len(d.xpath('//img'))==creative_count+portrait_count
assert len(byclass('person-profile'))==13 and len(byclass('profile-details'))==13
assert not d.xpath('//details[contains(@class,"profile-details")][@open]')
assert len(byclass('portrait-placeholder'))==13-portrait_count
for p in profiles:
 card=d.get_element_by_id(p['id']);assert card.get('class')=='x-card person-card'
 profile=card.xpath('.//*[@data-profile-id]')[0]
 assert profile.get('data-profile-id')==p['id']
 assert len(profile.xpath('.//p[@class="person-bio"]/span'))==2
 assert p['profileUpdatedAt'] in profile.text_content()
 assert profile.xpath('.//time/@datetime')==[p['profileUpdatedAt']]
 assert 1<=len(profile.xpath('.//ol[@class="contribution-list"]/li'))<=2
 assert len(card.xpath('./div[@class="person-update"]'))==1
 assert profile.getnext().get('class')=='person-update'
 assert '本期动态' in profile.getnext().text_content()
 for a in profile.xpath('.//a'):
  assert a.get('href','').startswith('https://') and (a.text_content().strip() or a.get('aria-label'))
 for img in profile.xpath('.//img'):
  assert img.get('loading')=='lazy' and img.get('width')=='88' and img.get('height')=='104'
for src in d.xpath('//a/@href'):
 assert src and src not in ['#','https://','http://'],src
assert (S/'index.html').stat().st_size<4_000_000,'Offline HTML exceeded 4 MB budget'
css=(S/'styles.css').read_text();assert '.profile-details summary{min-height:44px' in css
assert '.profile-heading{grid-template-columns:68px minmax(0,1fr)' in css
import hashlib
items=json.loads((S/'data/issues/001.json').read_text())['education']['items']
cols,rows=build.distribution(items);assert sum(len(a) for r in rows.values() for a in r.values())==13
allids=[id for row in rows.values() for vals in row.values() for id in vals];assert len(allids)==len(set(allids))==13
counts={c:sum(len(r[c]) for r in rows.values()) for c in cols};assert counts=={'学前教育':0,'小学教育':1,'初中教育':0,'高中阶段教育':0,'高等教育':3,'跨学段':7,'未限定':2}
for td in d.xpath('//*[@data-count]'):assert int(td.get('data-count'))==len(rows[td.get('data-topic')][td.get('data-stage')])
fixtures=[{'id':'one','category':'A','educationLevels':['小学教育','小学教育'],'scopeTags':[]},{'id':'two','category':'A','educationLevels':['小学教育','高等教育'],'scopeTags':[]},{'id':'three','category':'B','educationLevels':['高等教育'],'scopeTags':['跨学段']},{'id':'four','category':'B','educationLevels':[],'scopeTags':['未限定']}]
c,r=build.distribution(fixtures);assert r['A']['小学教育']==['one'] and r['A']['跨学段']==['two'] and r['B']['跨学段']==['three'] and r['B']['未限定']==['four']
editorial=json.loads((S/'data/editorial.json').read_text())['issues']['001']
assert len(byclass('experiment-card'))==3
assert len(d.xpath('//*[@data-changes-status="baseline"]'))==1
assert not byclass('change-card')
assert len(d.xpath('//ol[@class="revision-log"]/li'))==3
assert len(byclass('no-corrections'))==1
assert not editorial['factCorrections']
preview=d.get_element_by_id('page-preview');updates=d.get_element_by_id('page-updates')
assert len(preview.xpath('.//article[@class="experiment-card"]'))==3
assert len(updates.xpath('.//ol[@class="revision-log"]'))==1
for experiment in editorial['experiments']:
 card=d.get_element_by_id(experiment['id'])
 for key in ['audience','estimatedMinutes','verificationGoal','status']:
  assert experiment[key] in card.text_content()
for c in byclass('experiment-card'):
 assert c.xpath('.//a[@data-focus]')
assert '首期建立基线' in preview.text_content()
assert 'fixture-' not in raw
camel=lambda x: x.split('-')[0]+''.join(p.title() for p in x.split('-')[1:])
def info(e):return {'id':e.get('id'),'dataset':{camel(k[5:]):v for k,v in e.attrib.items() if k.startswith('data-')},'attrs':dict(e.attrib)}
extract=lambda xp:[info(e) for e in d.xpath(xp)]
out={'app':json.loads(d.get_element_by_id('app-data').text),'ids':ids,'facets':[info(e) for e in byclass('facet')],'scope':[info(e) for e in byclass('scope-button')],'nav':extract('//nav/a'),'pages':extract('//*[@data-weekly-page]'),'cards':[info(e) for e in byclass('creative-card')]}
(ROOT/'tests/dom.json').write_text(json.dumps(out,ensure_ascii=False))
report={'passed':True,'issues':1,'pages':4,'education':13,'publicFigures':13,'creative':15,'creativeImages':creative_count,'portraitImages':portrait_count,'portraitPlaceholders':13-portrait_count,'collapsedProfileDetails':13,'htmlBytes':len(raw.encode()),'matrixTotal':13,'matrixStageTotals':counts,'allOriginalArticlesRetained':True,'onlyLibraryHasCreativeCards':True,'sourceLinkedUntestedSuggestions':3,'changeStatus':'baseline','versionRevisions':3,'factCorrections':0,'brokenLinks':0,'duplicateActiveIds':0,'externalRuntimeDependencies':0}
(ROOT/'tests/static-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(report)
