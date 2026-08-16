import json,pathlib,re
D=json.loads(pathlib.Path('data/ranking.json').read_text());H=pathlib.Path('index.html').read_text();items=D['items'];checks=[]
def c(n,v):checks.append((n,bool(v)));print('PASS' if v else 'FAIL',n)
c('period format',bool(re.fullmatch(r'\d{4}-\d{4}',D.get('ten_year_period',''))));c('coverage min 10',D.get('ten_year_coverage',0)>=10);c('items min 10',len(items)>=10);c('ui dy 10y','DY médio 10a' in H);c('ui growth 10y','Cresc. receita 10a' in H);c('ui formula','proventos por ação' in H);c('ui cagr','CAGR' in H)
for i,x in enumerate(items[:10],1):
 c(f'{i} dy avg numeric',isinstance(x.get('dy_10y_avg'),(int,float)));c(f'{i} dy avg sane',0<=x.get('dy_10y_avg',-1)<=100);c(f'{i} growth numeric',isinstance(x.get('revenue_growth_10y'),(int,float)));c(f'{i} growth sane',-100<x.get('revenue_growth_10y',-999)<500);c(f'{i} history 10 years',len(x.get('dy_10y_history',[]))==10);c(f'{i} years unique',len({r['year'] for r in x.get('dy_10y_history',[])})==10);c(f'{i} prices positive',all(r.get('year_end_price',0)>0 for r in x.get('dy_10y_history',[])));c(f'{i} dividends nonnegative',all(r.get('dividends_per_share',-1)>=0 for r in x.get('dy_10y_history',[])));c(f'{i} source dy',bool(x.get('dy_10y_source')));c(f'{i} source growth',bool(x.get('growth_10y_source')));c(f'{i} revenue base positive',x.get('revenue_10y_base',0)>0);c(f'{i} revenue current positive',x.get('revenue_10y_current',0)>0)
failed=[n for n,v in checks if not v];print('10Y TESTS',len(checks),'FAILED',len(failed));assert len(checks)>=100
if failed:raise SystemExit('\n'.join(failed))
