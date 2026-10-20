from pathlib import Path
import json,hashlib
from lxml import html
R=Path(__file__).resolve().parents[1]
OLD=Path('/workspace/shared/issue003/release')
load=lambda p:json.loads(p.read_text())
a=load(OLD/'src/data/industry/003.json');b=load(R/'src/data/industry/003.json')
assert b['items'][:13]==a['items']
assert len(b['items'])==18
expected={'industry-lingdong','industry-aiyou','industry-shengtong','industry-aiscratch','industry-ideali'}
assert {x['id'] for x in b['items'][13:]}==expected
for x in b['items'][13:]:
 assert x['firstIssueId']=='003' and x['firstCollected']=='2026-10-20' and x['freshness']=='baseline'
 assert all(x[k] for k in ['sources','limits','financialBoundary','pricingCosts','verificationNote'])
for f in (OLD/'snapshots').glob('*'):
 assert (R/'snapshots'/f.name).read_bytes()==f.read_bytes()
assert (R/'src/data/issues/003.json').read_bytes()==(OLD/'src/data/issues/003.json').read_bytes()
tree=html.fromstring((R/'docs/index.html').read_text());cards=tree.xpath('//article[@class="industry-card" and not(ancestor::template)]')
new=[x for x in cards if x.attrib.get('id') in expected]
assert len(new)==5
for x in new:assert '003期 · 2026-10-20' in x.text_content()
assert (R/'src/index.html').read_bytes()==(R/'docs/index.html').read_bytes()
print('PASS: 18 industry cards; all13 prior entries exact; five additions dated003/Oct20 and baseline; old snapshots and003 core unchanged; HTML provenance and build exact.')
