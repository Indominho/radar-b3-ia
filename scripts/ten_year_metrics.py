import csv, datetime as dt, io, json, pathlib, time, urllib.request, zipfile
P=pathlib.Path('data/ranking.json');D=json.loads(P.read_text(encoding='utf-8'));items=D.get('items',[]);tickers={x['ticker'] for x in items};now=dt.date.today();end_year=now.year-1;start_year=end_year-9
HEAD={'User-Agent':'Mozilla/5.0 radar-b3-ia/4.1','Accept-Language':'pt-BR,pt;q=0.9'}
def get(url,timeout=240):
 last=None
 for delay in (0,4,12):
  if delay:time.sleep(delay)
  try:
   req=urllib.request.Request(url,headers=HEAD)
   with urllib.request.urlopen(req,timeout=timeout) as r:return r.read()
  except Exception as e:last=e
 raise last
def parse_num(v):
 if v is None or v=='':return None
 try:return float(str(v).replace('.','').replace(',','.'))
 except:return None
closes={t:{} for t in tickers}
for year in range(start_year,end_year+1):
 raw=get(f'https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A{year}.ZIP')
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  for line in io.TextIOWrapper(z.open(z.namelist()[0]),encoding='latin-1'):
   if not line.startswith('01') or line[10:12]!='02' or line[24:27]!='010':continue
   ticker=line[12:24].strip()
   if ticker not in closes:continue
   try:day=dt.datetime.strptime(line[2:10],'%Y%m%d').date();price=int(line[108:121])/100
   except:continue
   old=closes[ticker].get(year)
   if old is None or day>old[0]:closes[ticker][year]=(day,price)
def dividends(ticker):
 url=f'https://statusinvest.com.br/acao/companytickerprovents?ticker={ticker}&chartProventsType=2'
 try:data=json.loads(get(url,90).decode('utf-8'));events=data.get('assetEarningsModels',[])
 except Exception as e:print('proventos falharam',ticker,e);return None
 annual={y:0.0 for y in range(start_year,end_year+1)}
 for e in events:
  try:day=dt.datetime.strptime(e.get('ed',''),'%d/%m/%Y').date();value=float(e.get('v') or 0)
  except:continue
  if day.year in annual and value>=0:annual[day.year]+=value
 return annual
def historical_revenue(year):
 raw=get(f'https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_{year}.zip');out={}
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  name=next(n for n in z.namelist() if 'DRE_con' in n and n.endswith('.csv'))
  for r in csv.DictReader(io.TextIOWrapper(z.open(name),encoding='latin-1'),delimiter=';'):
   if r.get('CD_CONTA')!='3.01' or r.get('ORDEM_EXERC') not in ('ÚLTIMO','ULTIMO'):continue
   cd=r.get('CD_CVM');value=parse_num(r.get('VL_CONTA'));version=int(parse_num(r.get('VERSAO')) or 0);date=r.get('DT_REFER') or ''
   if value is None:continue
   value*=1000 if 'MIL' in (r.get('ESCALA_MOEDA') or '').upper() else 1
   if cd not in out or (date,version)>out[cd][:2]:out[cd]=(date,version,value)
 return {k:v[2] for k,v in out.items()}
old_revenue=historical_revenue(start_year);kept=[]
for x in items:
 annual=dividends(x['ticker']);prices=closes.get(x['ticker'],{});base=old_revenue.get(x.get('cvm_code'));current=x.get('revenue')
 if annual is None or len(prices)!=10 or base is None or current is None or base<=0 or current<=0:continue
 yields=[];history=[]
 for year in range(start_year,end_year+1):
  close=prices[year][1];paid=annual[year];dy=paid/close*100 if close>0 else None
  if dy is None:break
  yields.append(dy);history.append({'year':year,'dividends_per_share':round(paid,8),'year_end_price':round(close,4),'dy':round(dy,4)})
 if len(yields)!=10:continue
 x['dy_10y_avg']=sum(yields)/10;x['dy_5y_avg']=sum(yields[-5:])/5;x['dy_10y_history']=history;x['revenue_growth_10y']=((current/base)**(1/10)-1)*100;x['revenue_10y_base']=base;x['revenue_10y_current']=current
 x['dy_10y_source']='StatusInvest proventos por data ex + fechamento anual COTAHIST/B3';x['dy_5y_source']='StatusInvest proventos por data ex + fechamento anual COTAHIST/B3, últimos 5 exercícios';x['growth_10y_source']=f'CVM DFP consolidada {start_year} e {end_year}';x['ten_year_period']=f'{start_year}-{end_year}';kept.append(x)
if len(kept)<10:raise RuntimeError(f'Apenas {len(kept)} ações têm série completa de 10 anos')
D['items']=kept;D['universe_size']=len(kept);D['ten_year_period']=f'{start_year}-{end_year}';D['ten_year_coverage']=len(kept);D['message']=D.get('message','')+f' DY médio de 5 e 10 anos e crescimento de receita em 10 anos completos para {len(kept)} ações.'
P.write_text(json.dumps(D,ensure_ascii=False,allow_nan=False),encoding='utf-8');print('5 E 10 ANOS PASS',len(kept),start_year,end_year)
