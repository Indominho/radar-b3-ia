import csv,datetime as dt,io,json,pathlib,time,urllib.request,zipfile
from concurrent.futures import ThreadPoolExecutor,as_completed
P=pathlib.Path('data/ranking.json');D=json.loads(P.read_text(encoding='utf-8'));items=D.get('items',[]);tickers={x['ticker'] for x in items};today=dt.date.today();end_year=today.year-1;start_year=end_year-9
HEAD={'User-Agent':'radar-b3-ia/4.4','Accept-Language':'pt-BR,pt;q=0.9'}
def get_raw(url,timeout=240,retries=2):
 for attempt in range(retries+1):
  try:
   req=urllib.request.Request(url,headers=HEAD)
   with urllib.request.urlopen(req,timeout=timeout) as r: return r.read()
  except Exception as e:
   if attempt==retries: print('FONTE INDISPONÍVEL',url,e);return None
   time.sleep(3*(attempt+1))
def get_zip(url,timeout=240,retries=2):
 raw=get_raw(url,timeout,retries)
 if raw is not None and not raw.startswith(b'PK'): print('RESPOSTA NÃO ZIP',url);return None
 return raw
def parse_num(v):
 try:
  t=str(v or '').strip();return float(t.replace('.','').replace(',','.')) if ',' in t else float(t)
 except:return None
def cvm(v):return str(v or '').strip().zfill(6)
closes={t:{} for t in tickers}
for year in range(start_year,end_year+1):
 raw=get_zip(f'https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A{year}.ZIP')
 if not raw:continue
 try:
  with zipfile.ZipFile(io.BytesIO(raw)) as z:
   for line in io.TextIOWrapper(z.open(z.namelist()[0]),encoding='latin-1'):
    if not line.startswith('01') or line[10:12]!='02' or line[24:27]!='010':continue
    ticker=line[12:24].strip()
    if ticker not in closes:continue
    try:day=dt.datetime.strptime(line[2:10],'%Y%m%d').date();price=int(line[108:121])/100
    except:continue
    old=closes[ticker].get(year)
    if old is None or day>old[0]:closes[ticker][year]=(day,price)
 except zipfile.BadZipFile: print('ZIP B3 inválido',year)
def dividends(ticker):
 url=f'https://statusinvest.com.br/acao/companytickerprovents?ticker={ticker}&chartProventsType=2';raw=get_raw(url,30,retries=0)
 if not raw:return None
 try:events=json.loads(raw.decode()).get('assetEarningsModels',[])
 except:return None
 annual={y:0.0 for y in range(start_year,end_year+1)}
 for e in events:
  try:day=dt.datetime.strptime(e.get('ed',''),'%d/%m/%Y').date();value=float(e.get('v') or 0)
  except:continue
  if day.year in annual and value>=0:annual[day.year]+=value
 return annual
def historical_revenue(year):
 raw=get_zip(f'https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_{year}.zip');out={}
 if not raw:return out
 try:
  with zipfile.ZipFile(io.BytesIO(raw)) as z:
   name=next((n for n in z.namelist() if 'DRE_con' in n and n.endswith('.csv')),None)
   if not name:return out
   for r in csv.DictReader(io.TextIOWrapper(z.open(name),encoding='latin-1'),delimiter=';'):
    if r.get('CD_CONTA')!='3.01' or r.get('ORDEM_EXERC') not in ('ÚLTIMO','ULTIMO'):continue
    cd=cvm(r.get('CD_CVM'));value=parse_num(r.get('VL_CONTA'));version=int(parse_num(r.get('VERSAO')) or 0);date=r.get('DT_REFER') or ''
    if value is None:continue
    value*=1000 if 'MIL' in (r.get('ESCALA_MOEDA') or '').upper() else 1
    if cd not in out or (date,version)>out[cd][:2]:out[cd]=(date,version,value)
 except Exception as e:print('CVM DFP inválido',year,e)
 return {k:v[2] for k,v in out.items()}
old_revenue=historical_revenue(start_year);kept=0
dividend_data={}
workers=min(8,max(1,len(items)))
with ThreadPoolExecutor(max_workers=workers) as pool:
 futures={pool.submit(dividends,x['ticker']):x['ticker'] for x in items}
 for future in as_completed(futures):
  ticker=futures[future]
  try:dividend_data[ticker]=future.result()
  except Exception as exc:
   print('PROVENTOS INDISPONÍVEIS',ticker,exc);dividend_data[ticker]=None
for x in items:
 annual=dividend_data.get(x['ticker']);prices=closes.get(x['ticker'],{});base=old_revenue.get(cvm(x.get('cvm_code')));current=x.get('revenue');history=[]
 if annual is not None:
  for year in range(start_year,end_year+1):
   if year not in prices:continue
   close=prices[year][1];paid=annual.get(year,0.0);dy=paid/close*100 if close>0 else None
   if dy is not None:history.append({'year':year,'dividends_per_share':round(paid,8),'year_end_price':round(close,4),'dy':round(dy,4),'source':'StatusInvest proventos + B3 COTAHIST'})
 x['dy_10y_history']=history
 if history:
  ys=[r['dy'] for r in history];x['dy_10y_avg']=sum(ys)/len(ys);x['dy_5y_avg']=sum(ys[-5:])/len(ys[-5:]);x['dy_10y_source']='StatusInvest + B3 COTAHIST';x['dy_5y_source']='StatusInvest + B3 COTAHIST';x['ten_year_period']=f'{history[0]["year"]}-{history[-1]["year"]}';x['ten_year_years']=len(history);kept+=1
 else:x['dy_10y_avg']=None;x['dy_5y_avg']=None;x['ten_year_period']='sem histórico publicado';x['ten_year_years']=0
 if base and current and base>0 and current>0:x['revenue_growth_10y']=((current/base)**.1-1)*100;x['revenue_10y_base']=base;x['revenue_10y_current']=current;x['growth_10y_source']=f'CVM DFP {start_year} e {end_year}'
 else:x['revenue_growth_10y']=None;x['growth_10y_source']='CVM DFP: histórico não disponível'
D['items']=items;D['universe_size']=len(items);D['ten_year_period']=f'{start_year}-{end_year}';D['ten_year_coverage']=kept;D['message']=D.get('message','')+f' Histórico protegido: {kept} ativos com série; universo preservado em {len(items)}.';P.write_text(json.dumps(D,ensure_ascii=False,allow_nan=False));print('HISTÓRICO PROTEGIDO',len(items),kept)
