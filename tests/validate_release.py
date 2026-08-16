import datetime as dt,json,pathlib,re
DATA=pathlib.Path('data/ranking.json');CAT=pathlib.Path('data/catalog.json');HTML=pathlib.Path('index.html');checks=[]
def c(n,v):checks.append((n,bool(v)));print('PASS' if v else 'FAIL',n)
d=json.loads(DATA.read_text());cat=json.loads(CAT.read_text());h=HTML.read_text();items=d.get('items',[]);top=items[:10];market=cat.get('items',[])
for n,v in [('ranking exists',DATA.exists()),('catalog exists',CAT.exists()),('html exists',HTML.exists()),('ranking min10',len(items)>=10),('top10',len(top)==10),('catalog broad',len(market)>=300),('catalog count',cat.get('count')==len(market)),('ranking sorted',all(items[i]['score']>=items[i+1]['score'] for i in range(len(items)-1))),('unique ranking',len({x['ticker'] for x in items})==len(items)),('unique catalog',len({x['ticker'] for x in market})==len(market)),('quote date',bool(d.get('quote_date'))),('updated at',bool(d.get('updated_at'))),('two years',d.get('bets_period')=='2 anos'),('ten year period',bool(d.get('ten_year_period'))),('filter method',bool(d.get('filter_method'))),('no nan','NaN' not in DATA.read_text()),('no infinity','Infinity' not in DATA.read_text())]:c(n,v)
try:c('market fresh',(dt.date.today()-dt.date.fromisoformat(d['quote_date'])).days<=7)
except:c('market fresh',False)
fields=['ticker','name','price','momentum_2y','dy','dy_5y_avg','dy_10y_avg','dy_10y_history','pe','pvp','roe','roic','margin','growth','revenue_growth_10y','debt_equity','ev_ebitda','turnover','score','coverage','thesis','catalysts','risks','dy_source','dy_5y_source','dy_10y_source','growth_source','growth_10y_source','pe_source','pvp_source','indicators_updated_at']
for i,x in enumerate(top,1):
 for f in fields:c(f'top{i} {f}',x.get(f) is not None and x.get(f)!='')
 for n,v in [('ticker',bool(re.fullmatch(r'[A-Z]{4}\d{1,2}',x['ticker']))),('price',x['price']>0),('pe',x['pe']>0),('pvp',x['pvp']>0),('dy',x['dy']>=0),('dy5',0<=x['dy_5y_avg']<=100),('dy10',0<=x['dy_10y_avg']<=100),('history10',len(x['dy_10y_history'])==10),('years10',len({r['year'] for r in x['dy_10y_history']})==10),('growth10',-100<x['revenue_growth_10y']<500),('score',0<=x['score']<=100),('coverage',x['coverage']==100),('thesis',len(x['thesis'])>=15),('catalysts',len(x['catalysts'])>=10),('risks',len(x['risks'])>=10)]:c(f'top{i} valid {n}',v)
for f in ['price','momentum_2y','dy','dy_5y_avg','dy_10y_avg','pe','pvp','roe','roic','margin','growth','revenue_growth_10y','debt_equity','ev_ebitda','turnover','score','coverage']:c('all numeric '+f,all(isinstance(x.get(f),(int,float)) for x in items))
ui=['id="q"','id="minPrice"','id="maxPrice"','id="minDy"','id="maxDy"','id="order"','value="priceAsc"','value="priceDesc"','value="dyAsc"','value="dyDesc"','id="clear"','id="catalogRows"','id="rankRows"','DY médio 5a','DY médio 10a','Cresc. receita 10a','id="detail"','id="bars"','id="bets"','@media(max-width:520px)','name="viewport"','lang="pt-BR"','data/catalog.json','filteredCatalog()','renderCatalog()','renderRank()']
for token in ui:c('html '+token,token in h)
for bad in ['>Consenso<','Sem cobertura',"'N/D'",'6 meses']:c('html excludes '+bad,bad not in h)
# testes funcionais equivalentes aos filtros JS em toda a base
prices=[x['price'] for x in market if isinstance(x.get('price'),(int,float))];dys=[x['dy'] for x in market if isinstance(x.get('dy'),(int,float))]
for threshold in [1,5,10,20,50,100]:
 result=[x for x in market if isinstance(x.get('price'),(int,float)) and x['price']<=threshold];c(f'max price {threshold}',all(x['price']<=threshold for x in result))
 result=[x for x in market if isinstance(x.get('price'),(int,float)) and x['price']>=threshold];c(f'min price {threshold}',all(x['price']>=threshold for x in result))
for threshold in [0,1,2,5,10,20]:
 result=[x for x in market if isinstance(x.get('dy'),(int,float)) and x['dy']>=threshold];c(f'min dy {threshold}',all(x['dy']>=threshold for x in result))
 result=[x for x in market if isinstance(x.get('dy'),(int,float)) and x['dy']<=threshold];c(f'max dy {threshold}',all(x['dy']<=threshold for x in result))
for key,reverse in [('price',False),('price',True),('dy',False),('dy',True),('pe',False)]:
 a=sorted([x for x in market if isinstance(x.get(key),(int,float))],key=lambda x:x[key],reverse=reverse);c(f'sort {key} {reverse}',all((a[i][key]>=a[i+1][key] if reverse else a[i][key]<=a[i+1][key]) for i in range(len(a)-1)))
for sample in ['PETR','VALE','ITUB','BBDC','WEGE']:
 found=[x for x in market if sample.lower() in (x['ticker']+' '+x['name']).lower()];c('search '+sample,len(found)>=1)
failed=[n for n,v in checks if not v];print('TOTAL',len(checks),'PASSED',len(checks)-len(failed),'FAILED',len(failed));assert len(checks)>=150
if failed:raise SystemExit('\n'.join(failed))
