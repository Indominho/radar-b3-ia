import datetime as dt
import json
import pathlib
import re

CAT=pathlib.Path('data/catalog.json')
RANK=pathlib.Path('data/ranking.json')
REPORT=pathlib.Path('data/universe-audit.json')
cat=json.loads(CAT.read_text(encoding='utf-8'))
rank=json.loads(RANK.read_text(encoding='utf-8')) if RANK.exists() else {'items':[]}
items=cat.get('items',[])
rank_by={x.get('ticker'):x for x in rank.get('items',[]) if x.get('ticker')}
quote_fields=['price','change','volume','marketCap']
fundamental_fields=['dy','dy_5y_avg','dy_10y_avg','pe','pvp','roe','roic','margin','growth','revenue_growth_10y','debt_equity','ev_ebitda']

def valid_ticker(v): return isinstance(v,str) and bool(re.fullmatch(r'[A-Z0-9]{4,7}',v)) and any(c.isdigit() for c in v) and not v.endswith('F')
def numeric(v): return isinstance(v,(int,float)) and v==v and v not in (float('inf'),float('-inf'))

def status(v, source, label):
    if numeric(v): return {'status':'ok','value':v,'source':source}
    return {'status':'not_covered','value':None,'source':source,'reason':f'{label} não publicado pela fonte para este ativo'}

errors=[]; covered=0
for i,x in enumerate(items):
    t=x.get('ticker')
    if not valid_ticker(t): errors.append(f'{i}: ticker inválido {t!r}')
    if not x.get('name'): errors.append(f'{t}: nome ausente')
    y=rank_by.get(t)
    source='ranking fundamentalista' if y else 'não coberto no ranking fundamentalista'
    statuses={}
    for f in quote_fields:
        statuses[f]=status(x.get(f),'brapi','Cotação')
    for f in fundamental_fields:
        statuses[f]=status((y or {}).get(f),'CVM/Fundamentus/Status Invest','Indicador')
    x['data_quality']={
        'checked_at':dt.datetime.now(dt.timezone.utc).isoformat(),
        'status':'covered' if y else 'quote_only',
        'source':source,
        'fields':statuses,
        'blank_policy':'Nunca exibir célula vazia; usar valor ou motivo explícito.'
    }
    if y: covered+=1

if len({x.get('ticker') for x in items})!=len(items): errors.append('catálogo contém tickers duplicados')
if len(items)<250: errors.append(f'catálogo abaixo do mínimo operacional: {len(items)}')
report={'checked_at':dt.datetime.now(dt.timezone.utc).isoformat(),'catalog_count':len(items),'fundamental_coverage':covered,'quote_only':len(items)-covered,'errors':errors,'policy':{'never_invent':True,'never_blank':True,'missing_value_label':'Não publicado pela fonte para este ativo','per_asset_checks':['ticker válido','nome presente','sem duplicata','cotação com valor ou motivo','cada indicador com valor ou motivo','fonte identificada']}}
REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
CAT.write_text(json.dumps(cat,ensure_ascii=False,allow_nan=False),encoding='utf-8')
print('AUDITORIA UNIVERSO',len(items),'ações;',covered,'com cobertura fundamentalista;',len(errors),'erros estruturais')
if errors: raise SystemExit('\n'.join(errors))
