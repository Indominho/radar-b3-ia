import datetime as dt, json, math, pathlib

P=pathlib.Path('data/ranking.json'); d=json.loads(P.read_text(encoding='utf-8'))
now=dt.datetime.now(dt.timezone.utc).isoformat(); calculated=0

def finite(v): return isinstance(v,(int,float)) and math.isfinite(v)
def avg(values): return sum(values)/len(values) if values else None

def metric(values, label, formula, source):
    clean=[v for v in values if finite(v)]
    if not clean:
        return {'value':None,'display':'Não aplicável: histórico não publicado','years':0,'label':label,'formula':formula,'source':source}
    return {'value':avg(clean),'display':f'{avg(clean):.4f}','years':len(clean),'label':label,'formula':formula,'source':source}

for x in d.get('items',[]):
    hist=sorted(x.get('dy_10y_history') or [],key=lambda r:r.get('year',0))
    annual={}
    for row in hist:
        year=row.get('year'); price=row.get('year_end_price'); paid=row.get('dividends_per_share')
        dy=row.get('dy')
        if not finite(dy) and finite(price) and price>0 and finite(paid): dy=paid/price*100
        if year is not None: annual[str(year)]={'dividends_per_share':paid,'year_end_price':price,'dy':dy,'source':row.get('source') or x.get('dy_10y_source') or 'B3 COTAHIST + histórico de proventos'}
    dYs=[r.get('dy') for r in annual.values()]
    prices=[r.get('year_end_price') for r in annual.values() if finite(r.get('year_end_price')) and r.get('year_end_price')>0]
    x['annual_indicators']={'checked_at':now,'years_available':len(annual),'year_from':min(annual) if annual else None,'year_to':max(annual) if annual else None,'dy':metric(dYs,'DY anual','proventos por ação / preço de fechamento anual × 100','B3 COTAHIST + proventos publicados'),'price':metric(prices,'Preço anual','fechamento anual do ativo','B3 COTAHIST'),'provenance_policy':'valor bruto da fonte ou cálculo explícito; nunca estimado'}
    if len(dYs)>=1:
        x['dy_available_avg']=avg(dYs);x['dy_available_years']=len(dYs);x['dy_available_period']=f"{min(annual)}-{max(annual)}"
    else:
        x['dy_available_avg']=None;x['dy_available_years']=0;x['dy_available_period']='sem histórico publicado'
    calculated+=1

d['annual_indicator_engine']={'version':'1.0','calculated_at':now,'items_processed':calculated,'policy':'Calcular somente a partir de observações anuais existentes; períodos curtos são rotulados.'}
P.write_text(json.dumps(d,ensure_ascii=False,allow_nan=False),encoding='utf-8')
print('ANNUAL ENGINE PASS',calculated)
