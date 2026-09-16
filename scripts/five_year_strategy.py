import json, pathlib
P=pathlib.Path('data/ranking.json');d=json.loads(P.read_text(encoding='utf-8'));items=d.get('items',[])
for x in items:
    hist=sorted(x.get('dy_10y_history',[]),key=lambda r:r['year'])[-6:]
    if len(hist)>=6 and hist[0].get('year_end_price',0)>0 and hist[-1].get('year_end_price',0)>0:
        years=hist[-1]['year']-hist[0]['year']
        x['price_cagr_5y']=((hist[-1]['year_end_price']/hist[0]['year_end_price'])**(1/years)-1)*100 if years>0 else None
        x['price_return_5y']=(hist[-1]['year_end_price']/hist[0]['year_end_price']-1)*100
        x['price_5y_from']=hist[0]['year_end_price'];x['price_5y_to']=hist[-1]['year_end_price']
    else:
        x['price_cagr_5y']=None;x['price_return_5y']=None
    dy=x.get('dy_5y_avg');cagr=x.get('price_cagr_5y')
    x['passes_income_5y']=isinstance(dy,(int,float)) and dy>=15
    x['passes_appreciation_5y']=isinstance(cagr,(int,float)) and cagr>=10
    x['passes_5y_strategy']=x['passes_income_5y'] and x['passes_appreciation_5y']
    if isinstance(dy,(int,float)) and isinstance(cagr,(int,float)):
        x['five_year_combo_score']=round(min(dy,40)/40*50+max(0,min(cagr,40))/40*50,1)
strict=[x for x in items if x.get('passes_5y_strategy')]
strict.sort(key=lambda x:(x.get('five_year_combo_score',0),x.get('score',0)),reverse=True)
d['five_year_strategy']={'dy_5y_min':15,'price_cagr_5y_min':10,'definition':'DY médio anual de 5 anos >= 15% e valorização anual composta do preço em 5 anos >= 10%','eligible_count':len(strict)}
d['five_year_picks']=strict[:10]
d['message']=d.get('message','')+f' Estratégia 5 anos: {len(strict)} ações passaram em DY médio >=15% e valorização anual >=10%.'
P.write_text(json.dumps(d,ensure_ascii=False,allow_nan=False),encoding='utf-8')
print('ESTRATEGIA 5 ANOS',len(strict),[(x['ticker'],round(x['dy_5y_avg'],1),round(x['price_cagr_5y'],1)) for x in strict[:10]])
