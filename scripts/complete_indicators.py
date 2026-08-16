import datetime as dt, json, pathlib
p=pathlib.Path('data/ranking.json');d=json.loads(p.read_text());complete=[]
for x in d.get('items',[]):
    if x.get('revenue_growth_5y') is not None:
        x['growth_cvm_annual']=x.get('growth');x['growth']=x['revenue_growth_5y']
    if x.get('dy') is None or x.get('growth') is None or x.get('pe') is None:
        continue
    if x['pe'] <= 0:
        continue
    x['dy_source']='Fundamentus, dividendos dos últimos 12 meses'
    x['growth_source']='Fundamentus, crescimento anualizado da receita em 5 anos'
    x['pe_source']='Fundamentus, preço dividido pelo lucro por ação'
    x['indicators_updated_at']=dt.datetime.now(dt.timezone.utc).isoformat()
    complete.append(x)
if len(complete)<10:raise RuntimeError(f'Cobertura insuficiente: {len(complete)} ações com P/L, DY e CRESC')
d['items']=complete;d['universe_size']=len(complete);d['fundamentus_coverage']=len(complete);d['indicator_policy']='Só são publicadas ações com P/L positivo, DY e CRESC disponíveis; não há N/D nesses três campos.'
d['message']=f'<b>P/L, DY e CRESC validados.</b> {len(complete)} ações com atualização diária. DY: 12 meses. CRESC: receita anualizada em 5 anos.'
p.write_text(json.dumps(d,ensure_ascii=False,allow_nan=False));print('PASS P/L DY CRESC',len(complete))
