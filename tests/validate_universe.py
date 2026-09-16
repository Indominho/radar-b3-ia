import json, pathlib, re

CAT=pathlib.Path('data/catalog.json')
AUDIT=pathlib.Path('data/universe-audit.json')
HTML=pathlib.Path('index.html')
cat=json.loads(CAT.read_text(encoding='utf-8'))
audit=json.loads(AUDIT.read_text(encoding='utf-8'))
h=HTML.read_text(encoding='utf-8')
items=cat.get('items',[])
assert len(items)>=250, 'universo abaixo do mínimo'
assert cat.get('count')==len(items), 'contador divergente'
assert len({x.get('ticker') for x in items})==len(items), 'ticker duplicado'
assert all(re.fullmatch(r'[A-Z0-9]{4,7}',x.get('ticker','')) and not x['ticker'].endswith('F') for x in items), 'ticker inválido ou fracionário'
assert all(x.get('name') for x in items), 'ação sem nome'
assert audit.get('catalog_count')==len(items), 'auditoria fora de sincronia'
assert audit.get('errors')==[], 'auditoria encontrou erros estruturais'
assert audit.get('policy',{}).get('never_blank') is True
assert audit.get('policy',{}).get('never_invent') is True
assert 'Não publicado pela fonte' in h
assert 'Sem dado' not in h
assert 'data_quality' in items[0]
for x in items:
    q=x['data_quality'];assert q['status'] in ('covered','quote_only')
    for f,v in q['fields'].items():
        assert v['status'] in ('ok','not_covered'),f'{x["ticker"]}:{f}'
        if v['status']=='not_covered': assert v.get('reason')
print('UNIVERSE PASS',len(items),'ações auditadas;',audit.get('fundamental_coverage'),'com cobertura fundamentalista')
