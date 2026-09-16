import csv, datetime as dt, io, json, pathlib, time, urllib.request, zipfile
P=pathlib.Path('data/ranking.json');D=json.loads(P.read_text(encoding='utf-8'));items=D.get('items',[]);tickers={x['ticker'] for x in items};now=dt.date.today();end_year=now.year-1;start_year=end_year-9
HEAD={'User-Agent':'Mozilla/5.0 radar-b3-ia/4.3','Accept-Language':'pt-BR,pt;q=0.9'}
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
 t=str(v).strip()
 try:return float(t.replace('.','').replace(',','.')) if ',' in t else float(t)
 except:return None
def cvm(v):return str(v or '').strip().zfill(6)
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
 try:data=json.loads(get(f'https://statusinvest.com.br/acao/companytickerprovents?ticker={ticker}&chartProventsType=2',90).decode());events=data.get('assetEarningsModels',[])
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
   cd=cvm(r.get('CD_CVM'));value=parse_num(r.get('VL_CONTA'));version=int(parse_num(r.get('VERSAO')) or 0);date=r.get('DT_REFER') or ''
   if value is None:continue
   value*=1000 if 'MIL' in (r.get('ESCALA_MOEDA') or '').upper() else 1
   if cd not in out or (date,version)>out[cd][:2]:out[cd]=(date,version,value)
 return {k:v[2] for k,v in out.items()}
old_revenue=historical_revenue(start_year)
kept=0
for x in items:
 annual=dividends(x['ticker']);prices=closes.get(x['ticker'],{});base=old_revenue.get(cvm(x.get('cvm_code')));current=x.get('revenue')
 history=[]
 if annual is not None:
  for year in range(start_year,end_year+1):
   if year not in prices:continue
   close=prices[year][1];paid=annual.get(year,0.0);dy=paid/close*100 if close>0 else None
   if dy is not None:history.append({'year':year,'dividends_per_share':round(paid,8),'year_end_price':round(close,4),'dy':round(dy,4),'source':'StatusInvest proventos + B3 COTAHIST'})
 x['dy_10y_history']=history
 if history:
  ys=[r['dy'] for r in history];x['dy_10y_avg']=sum(ys)/len(ys);x['dy_5y_avg']=sum(ys[-5:])/len(ys[-5:]);x['dy_10y_source']='StatusInvest + B3 COTAHIST';x['dy_5y_source']='StatusInvest + B3 COTAHIST, últimos anos disponíveis';x['ten_year_period']=f"{history[0]['year']}-{history[-1]['year']}";x['ten_year_years']=len(history);kept+=1
 else:
  x['dy_10y_avg']=None;x['dy_5y_avg']=None;x['ten_year_period']='sem histórico publicado';x['ten_year_years']=0
 if base and current and base>0 and current>0:
  x['revenue_growth_10y']=((current/base)**(1/10)-1)*100;x['revenue_10y_base']=base;x['revenue_10y_current']=current;x['growth_10y_source']=f'CVM DFP {start_year} e {end_year}'
 else:x['revenue_growth_10y']=None;x['growth_10y_source']='CVM DFP: histórico não disponível para este ativo'
D['items']=items;D['universe_size']=len(items);D['ten_year_period']=f'{start_year}-{end_year}';D['ten_year_coverage']=kept;D['message']=D.get('message','')+f' Históricos enriquecidos sem excluir ativos: {kept} com dados anuais, universo preservado em {len(items)}.'
P.write_text(json.dumps(D,ensure_ascii=False,allow_nan=False));print('HISTÓRICO SEM EXCLUSÃO',len(items),'ativos;',kept,'com histórico')
