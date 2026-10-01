import datetime as dt
import json
import math
from pathlib import Path

DATA=Path('data/ranking.json')
CAT=Path('data/catalog.json')
HTML=Path('index.html')
VERSION=Path('VERSION.json')

def finite(value):
    return isinstance(value,(int,float)) and math.isfinite(value)

d=json.loads(DATA.read_text(encoding='utf-8'))
cat=json.loads(CAT.read_text(encoding='utf-8'))
h=HTML.read_text(encoding='utf-8')
v=json.loads(VERSION.read_text(encoding='utf-8'))
items=d.get('items',[])
market=cat.get('items',[])
assert v.get('version')=='v1.0.8', 'VERSION.json não está em v1.0.8'
assert v['version'] in h, 'versão do HTML divergente'
assert len(items)>=10 and len({x.get('ticker') for x in items})==len(items), 'ranking inválido'
assert len(market)>=300 and cat.get('count')==len(market), 'catálogo inválido'
assert len({x.get('ticker') for x in market})==len(market), 'ticker duplicado no catálogo'
assert bool(d.get('quote_date')) and bool(d.get('updated_at')), 'timestamps ausentes'
assert (dt.date.today()-dt.date.fromisoformat(d['quote_date'])).days<=7, 'cotação fora da janela de frescor'
raw=DATA.read_text(encoding='utf-8')
assert 'NaN' not in raw and 'Infinity' not in raw, 'ranking contém número não finito'
assert all(finite(x.get('score')) and 0<=x['score']<=100 for x in items), 'score inválido'
ui=['id="q"','id="minPrice"','id="maxPrice"','id="minDy"','id="maxDy"','id="order"','value="priceAsc"','value="priceDesc"','value="dyAsc"','value="dyDesc"','id="clear"','id="catalogRows"','id="rankRows"','id="detail"','id="bars"','id="bets"','@media(max-width:520px)','data/catalog.json','data/ranking.json','filteredCatalog()','renderCatalog()','renderRank()']
assert all(token in h for token in ui), 'interface atual sem filtro/ranking/ficha obrigatório'
assert 'DY médio 5a' in h and 'DY médio 10a' in h and 'Cresc. receita 10a' in h, 'rótulo de período ausente'
assert "filter(x=>finite(x.dy_5y_avg)&&finite(x.price_cagr_5y))" in h, 'Top 5 sem campos próprios'
assert "filter(x=>finite(x.dy_10y_avg)&&finite(x.revenue_growth_10y))" in h, 'Top 10 sem campos próprios'
assert h.count('slice(0,10)')>=2, 'rankings não limitados a Top 10'
print('RELEASE CURRENT PASS',v['version'],'catalog',len(market),'ranking',len(items),'quote_date',d['quote_date'])
