import datetime as dt, json, pathlib, re, sys
DATA=pathlib.Path('data/ranking.json');HTML=pathlib.Path('index.html');checks=[]
def check(name,condition):
 checks.append((name,bool(condition)))
 if not condition:print('FAIL',name)
d=json.loads(DATA.read_text(encoding='utf-8'));h=HTML.read_text(encoding='utf-8');items=d.get('items',[]);top=items[:10]
check('dataset exists',DATA.exists());check('html exists',HTML.exists());check('minimum 10 stocks',len(items)>=10);check('top exactly available',len(top)==10);check('updated_at present',bool(d.get('updated_at')));check('quote_date present',bool(d.get('quote_date')));check('statement year present',isinstance(d.get('statement_year'),int));check('bets period two years',d.get('bets_period')=='2 anos');check('methodology present',bool(d.get('filter_method')));check('items sorted',all(items[i]['score']>=items[i+1]['score'] for i in range(len(items)-1)));check('ticker unique',len({x['ticker'] for x in items})==len(items));check('top ticker unique',len({x['ticker'] for x in top})==10)
try:check('market data fresh', (dt.date.today()-dt.date.fromisoformat(d['quote_date'])).days<=7)
except:check('market data fresh',False)
try:check('pipeline fresh',(dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(d['updated_at'])).total_seconds()<=129600)
except:check('pipeline fresh',False)
fields=['ticker','name','price','momentum_2y','dy','pe','pvp','roe','roic','margin','growth','debt_equity','ev_ebitda','turnover','score','coverage','thesis','catalysts','risks','dy_source','growth_source','pe_source','pvp_source','indicators_updated_at']
for pos,x in enumerate(top,1):
 for field in fields:check(f'top{pos} {field}',x.get(field) is not None and x.get(field)!='')
 check(f'top{pos} ticker format',bool(re.fullmatch(r'[A-Z]{4}\d{1,2}',x['ticker'])))
 check(f'top{pos} price positive',x['price']>0);check(f'top{pos} pe positive',x['pe']>0);check(f'top{pos} pvp positive',x['pvp']>0);check(f'top{pos} dy nonnegative',x['dy']>=0);check(f'top{pos} score range',0<=x['score']<=100);check(f'top{pos} coverage range',0<=x['coverage']<=100);check(f'top{pos} thesis useful',len(x['thesis'])>=15);check(f'top{pos} catalysts useful',len(x['catalysts'])>=10);check(f'top{pos} risks useful',len(x['risks'])>=10)
required_numeric=['price','momentum_2y','dy','pe','pvp','roe','roic','margin','growth','debt_equity','ev_ebitda','turnover','score','coverage']
for field in required_numeric:check(f'all stocks have {field}',all(isinstance(x.get(field),(int,float)) for x in items))
for field in ['thesis','catalysts','risks','dy_source','growth_source','pe_source','pvp_source']:check(f'all stocks explain {field}',all(isinstance(x.get(field),str) and x[field].strip() for x in items))
check('html search field','id="q"' in h);check('html price filter','id="maxPrice"' in h);check('html dy filter','id="minDy"' in h);check('html table','<table>' in h);check('html detail panel','id="detail"' in h);check('html bets','id="bets"' in h);check('html methodology','Filtros usados no Top 10' in h);check('html two years','2 anos' in h);check('html no six months','6 meses' not in h);check('html no consensus column','>Consenso<' not in h);check('html no uncovered label','Sem cobertura' not in h);check('html mobile breakpoint','@media(max-width:520px)' in h);check('html viewport','name="viewport"' in h);check('html portuguese','lang="pt-BR"' in h);check('html safe escape','const $' in h and 'esc=' in h);check('no NaN data','NaN' not in DATA.read_text());check('no Infinity data','Infinity' not in DATA.read_text());check('at least one bet',len(d.get('emerging_bets',[]))>=1);check('max ten bets',len(d.get('emerging_bets',[]))<=10);check('bet fields',all(x.get('momentum_2y') is not None and x.get('pe') is not None for x in d.get('emerging_bets',[])))
failed=[n for n,ok in checks if not ok];print(f'TOTAL TESTS: {len(checks)} | PASSED: {len(checks)-len(failed)} | FAILED: {len(failed)}')
if len(checks)<50:raise SystemExit('Test suite below 50 checks')
if failed:print('\n'.join(failed));raise SystemExit(1)
