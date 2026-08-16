import datetime as dt, io, json, pathlib, urllib.request, zipfile
P=pathlib.Path('data/ranking.json');D=json.loads(P.read_text());items=D.get('items',[]);tickers={x['ticker'] for x in items};today=dt.date.today();cutoff=today-dt.timedelta(days=730);series={t:[] for t in tickers}
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'radar-b3-ia/3.0'})
 with urllib.request.urlopen(req,timeout=180) as r:return r.read()
for year in range(cutoff.year,today.year+1):
 raw=get(f'https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A{year}.ZIP')
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  for line in io.TextIOWrapper(z.open(z.namelist()[0]),encoding='latin-1'):
   if not line.startswith('01') or line[10:12]!='02' or line[24:27]!='010':continue
   ticker=line[12:24].strip()
   if ticker not in series:continue
   try:day=dt.datetime.strptime(line[2:10],'%Y%m%d').date();price=int(line[108:121])/100
   except ValueError:continue
   series[ticker].append((day,price))
for x in items:
 s=sorted(series[x['ticker']])
 if not s:continue
 old=min(s,key=lambda p:abs((p[0]-cutoff).days));new=s[-1]
 if old[1]>0:x['momentum_2y']=(new[1]/old[1]-1)*100;x['price_2y_ago']=old[1];x['momentum_2y_from']=old[0].isoformat();x['momentum_2y_to']=new[0].isoformat()
bets=[x for x in items if x.get('momentum_2y') is not None and x['momentum_2y']>=30 and x.get('growth',-999)>=5 and x.get('roe',-999)>=12 and x.get('pe') is not None and 0<x['pe']<=35 and (x.get('debt_equity') is None or x['debt_equity']<=2)]
bets.sort(key=lambda x:(x['momentum_2y'],x['score']),reverse=True);D['emerging_bets']=bets[:10];D['bets_period']='2 anos';D['momentum_2y_coverage']=sum(1 for x in items if x.get('momentum_2y') is not None);D['message']=D.get('message','')+f' Apostas: filtro de 2 anos, {len(bets)} elegíveis.';P.write_text(json.dumps(D,ensure_ascii=False,allow_nan=False));print('Apostas 2 anos',[(x['ticker'],round(x['momentum_2y'],1)) for x in bets[:10]])
