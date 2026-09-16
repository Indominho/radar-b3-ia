import json, pathlib

P=pathlib.Path('data/ranking.json')
d=json.loads(P.read_text(encoding='utf-8'))
items=d.get('items',[])

for x in items:
    hist=sorted(x.get('dy_10y_history') or [], key=lambda r:r.get('year',0))
    usable=[r for r in hist if isinstance(r.get('year_end_price'),(int,float)) and r.get('year_end_price')>0 and isinstance(r.get('dy'),(int,float))]
    if len(usable)>=2:
        period=usable[-5:]
        first,last=period[0],period[-1]
        years=last['year']-first['year']
        x['dy_5y_avg']=sum(r['dy'] for r in period)/len(period)
        x['dy_5y_years']=len(period)
        x['dy_5y_period']=f"{first['year']}-{last['year']}"
        x['price_cagr_5y']=((last['year_end_price']/first['year_end_price'])**(1/years)-1)*100 if years>0 else 0.0
        x['price_return_5y']=(last['year_end_price']/first['year_end_price']-1)*100
        x['price_5y_from']=first['year_end_price'];x['price_5y_to']=last['year_end_price']
        x['passes_5y_strategy']=True
        x['five_year_combo_score']=round(min(max(x['dy_5y_avg'],0),40)/40*50+min(max(x['price_cagr_5y'],0),40)/40*50,1)
    else:
        x['dy_5y_avg']=None;x['dy_5y_years']=len(usable);x['dy_5y_period']='histórico insuficiente';x['price_cagr_5y']=None;x['price_return_5y']=None;x['passes_5y_strategy']=False

ranked=[x for x in items if x.get('passes_5y_strategy')]
ranked.sort(key=lambda x:(x.get('dy_5y_avg',float('-inf')),x.get('price_cagr_5y',float('-inf'))),reverse=True)
d['five_year_strategy']={'dy_5y_min':None,'price_cagr_5y_min':None,'definition':'Sem corte mínimo de DY; calcula a média dos últimos até 5 anos observados e exibe o período real de cada ativo.','eligible_count':len(ranked)}
d['five_year_picks']=ranked
d['message']=d.get('message','')+f' Ranking 5 anos corrigido: {len(ranked)} ações com pelo menos 2 exercícios observados.'
P.write_text(json.dumps(d,ensure_ascii=False,allow_nan=False),encoding='utf-8')
print('RANKING 5 ANOS CORRIGIDO',len(ranked))
