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
        x['price_5y_from']=hist[0]['year_end_price']
        x['price_5y_to']=hist[-1]['year_end_price']
    else:
        x['price_cagr_5y']=None
        x['price_return_5y']=None

    dy=x.get('dy_5y_avg')
    cagr=x.get('price_cagr_5y')
    x['passes_income_5y']=isinstance(dy,(int,float))
    x['passes_appreciation_5y']=isinstance(cagr,(int,float))
    x['passes_5y_strategy']=x['passes_income_5y'] and x['passes_appreciation_5y']
    if isinstance(dy,(int,float)) and isinstance(cagr,(int,float)):
        # Score apenas para leitura auxiliar, sem eliminar DY ou valorização baixos.
        x['five_year_combo_score']=round(min(max(dy,0),40)/40*50+min(max(cagr,0),40)/40*50,1)

ranked=[x for x in items if x.get('passes_5y_strategy')]
ranked.sort(key=lambda x:(x.get('dy_5y_avg',float('-inf')),x.get('price_cagr_5y',float('-inf'))),reverse=True)

d['five_year_strategy']={
    'dy_5y_min':None,
    'price_cagr_5y_min':None,
    'definition':'Ações ordenadas pelo DY médio de 5 anos, com valorização média anual do preço em 5 anos exibida como critério complementar; sem corte mínimo.',
    'eligible_count':len(ranked)
}
d['five_year_picks']=ranked[:50]
d['message']=d.get('message','')+f' Ranking 5 anos: {len(ranked)} ações com DY médio e valorização média anual disponíveis, ordenadas por DY decrescente e valorização decrescente.'
P.write_text(json.dumps(d,ensure_ascii=False,allow_nan=False),encoding='utf-8')
print('RANKING 5 ANOS',len(ranked),[(x['ticker'],round(x['dy_5y_avg'],1),round(x['price_cagr_5y'],1)) for x in ranked[:10]])
