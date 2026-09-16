import json, pathlib

P=pathlib.Path('data/ranking.json')
d=json.loads(P.read_text(encoding='utf-8'))
items=d.get('items',[])

for x in items:
    hist=sorted(x.get('dy_10y_history',[]),key=lambda r:r['year'])[-6:]
    if len(hist)>=6 and hist[0].get('year_end_price',0)>0 and hist[-1].get('year_end_price',0)>0:
        years=hist[-1]['year']-hist[0]['year']
        x['price_cagr_5y']=((hist[-1]['year_end_price']/hist[0]['year_end_price'])**(1/years)-1)*100 if years>0 else None
        x['price_return_5y']=(hist[-1]['year_end_price']/hist[0]['year_end_price']-1)*100
        x['price_5y_from']=hist[0]['year_end_price'];x['price_5y_to']=hist[-1]['year_end_price']
    else:
        x['price_cagr_5y']=None;x['price_return_5y']=None
    x['passes_income_5y']=isinstance(x.get('dy_5y_avg'),(int,float))
    x['passes_appreciation_5y']=isinstance(x.get('price_cagr_5y'),(int,float))
    x['passes_5y_strategy']=x['passes_income_5y'] and x['passes_appreciation_5y']
    if x['passes_5y_strategy']:
        x['five_year_combo_score']=round(min(max(x['dy_5y_avg'],0),40)/40*50+min(max(x['price_cagr_5y'],0),40)/40*50,1)

ranked=[x for x in items if x.get('passes_5y_strategy')]
ranked.sort(key=lambda x:(x.get('dy_5y_avg',float('-inf')),x.get('price_cagr_5y',float('-inf'))),reverse=True)
d['five_year_strategy']={'dy_5y_min':None,'price_cagr_5y_min':None,'definition':'Todos os ativos com histórico de DY médio e valorização média anual de 5 anos disponível; sem corte mínimo de DY. Ordenação: DY médio 5a decrescente, valorização 5a decrescente.','eligible_count':len(ranked)}
d['five_year_picks']=ranked
d['message']=d.get('message','')+f' Ranking 5 anos sem corte de DY: {len(ranked)} ações, ordenadas por DY médio e valorização.'
P.write_text(json.dumps(d,ensure_ascii=False,allow_nan=False),encoding='utf-8')
print('RANKING 5 ANOS SEM CORTE',len(ranked))
