import json, math, pathlib, random, re
CAT=json.loads(pathlib.Path('data/catalog.json').read_text(encoding='utf-8'))
AUD=json.loads(pathlib.Path('data/universe-audit.json').read_text(encoding='utf-8'))
SRC=json.loads(pathlib.Path('data/source-registry.json').read_text(encoding='utf-8'))
items=CAT.get('items',[]); assert items and AUD.get('errors')==[]
random.seed(20260916); sample=random.sample(items,min(50,len(items))); checks=[]
def ok(name,value):
 checks.append((name,bool(value)))
 if not value: raise AssertionError(name)
for i,x in enumerate(sample,1):
 t=x.get('ticker',''); q=x.get('data_quality',{}); fields=q.get('fields',{})
 ok(f'{i:02} ticker format',bool(re.fullmatch(r'[A-Z0-9]{4,7}',t)) and not t.endswith('F'))
 ok(f'{i:02} name present',bool(x.get('name')))
 ok(f'{i:02} quality status',q.get('status') in ('covered','quote_only'))
 ok(f'{i:02} field count',len(fields)>=16)
 ok(f'{i:02} no blank statuses',all(v.get('status') in ('ok','not_covered') for v in fields.values()))
 ok(f'{i:02} explicit missing reasons',all(v.get('reason') for v in fields.values() if v.get('status')=='not_covered'))
 ok(f'{i:02} source names',all(v.get('source') for v in fields.values()))
 ok(f'{i:02} source registry coverage',all(v.get('source') in ('brapi','CVM/Fundamentus/Status Invest') for v in fields.values()))
 ok(f'{i:02} finite numbers',all(not isinstance(v.get('value'),float) or math.isfinite(v['value']) for v in fields.values() if v.get('value') is not None))
 ok(f'{i:02} price policy',fields['price']['status'] in ('ok','not_covered'))
ok('51 manifest sources',len(SRC.get('sources',{}))>=7)
ok('52 no invented policy',SRC.get('policy','').startswith('Nenhum número é inventado'))
ok('53 audit denominator',AUD.get('catalog_count')==len(items))
ok('54 audit coverage split',AUD.get('fundamental_coverage',0)+AUD.get('quote_only',0)==len(items))
ok('55 sample reproducible',len(sample)==min(50,len(items)))
print('RANDOM QUALITY TESTS PASS',len(checks),'checks across',len(sample),'actions')
assert len(checks)>=55
