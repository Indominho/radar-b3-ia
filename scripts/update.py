import os,json,urllib.request,datetime,math,pathlib
TOKEN=os.getenv('BRAPI_TOKEN','').strip(); OUT=pathlib.Path('data/ranking.json'); OUT.parent.mkdir(exist_ok=True)
def get(url):
 req=urllib.request.Request(url,headers={'Authorization':f'Bearer {TOKEN}','User-Agent':'radar-b3-ia/1.0'})
 with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)
def val(o,*keys):
 for k in keys:
  v=o
  for p in k.split('.'):
   v=v.get(p) if isinstance(v,dict) else None
  if isinstance(v,dict):v=v.get('raw')
  if isinstance(v,(int,float)) and math.isfinite(v):return float(v)
 return None
def pct(v):return v*100 if v is not None and abs(v)<1 else v
def norm(sym,q,s,f):
 price=val(q,'regularMarketPrice','price'); target=val(f,'targetMeanPrice');
 return {'ticker':sym,'name':q.get('longName') or q.get('shortName') or sym,'sector':f.get('sector') or q.get('sector') or 'Não informado','price':price,'upside':((target/price-1)*100 if target and price else None),'dy':pct(val(s,'dividendYield','trailingAnnualDividendYield')),'pe':val(s,'trailingPE','priceEarnings'),'pvp':val(s,'priceToBook'),'roe':pct(val(f,'returnOnEquity','roe')),'roic':pct(val(f,'returnOnInvestedCapital','roic')),'debt_equity':val(f,'debtToEquity'),'margin':pct(val(f,'profitMargins','netMargin')),'growth':pct(val(f,'earningsGrowth','revenueGrowth')),'volume':val(q,'regularMarketVolume','averageDailyVolume10Day'),'market_cap':val(q,'marketCap')}
def rank(items):
 metrics=[('pe',False,.16),('pvp',False,.10),('dy',True,.16),('roe',True,.16),('roic',True,.14),('debt_equity',False,.10),('margin',True,.08),('growth',True,.06),('volume',True,.04)]
 for key,high,w in metrics:
  xs=sorted(x[key] for x in items if x.get(key) is not None); lo=xs[max(0,int(len(xs)*.05)-1)] if xs else None; hi=xs[min(len(xs)-1,int(len(xs)*.95))] if xs else None
  for x in items:
   v=x.get(key); z=None if v is None or lo is None else (50 if hi==lo else max(0,min(100,(v-lo)/(hi-lo)*100)));x['_'+key]=(z if high or z is None else 100-z)
 for x in items:
  got=sum(w for k,h,w in metrics if x['_'+k] is not None); raw=sum(x['_'+k]*w for k,h,w in metrics if x['_'+k] is not None)/(got or 1);x['coverage']=round(got*100);x['score']=round(raw*(.55+.45*got));[x.pop('_'+k,None) for k,h,w in metrics]
 return sorted(items,key=lambda x:x['score'],reverse=True)
def main():
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 if not TOKEN:
  OUT.write_text(json.dumps({'updated_at':now,'universe_size':0,'items':[],'message':'<b>Chave pendente.</b> Configure BRAPI_TOKEN nos Secrets do GitHub para ativar toda a B3.'},ensure_ascii=False));return
 cat=get('https://brapi.dev/api/v2/tickers?type=stock&active=true&limit=1000'); raw=cat.get('tickers') or cat.get('results') or cat.get('data') or []
 syms=[]
 for x in raw:
  s=x if isinstance(x,str) else x.get('symbol') or x.get('ticker')
  if s and s[-1:].isdigit():syms.append(s)
 syms=list(dict.fromkeys(syms)); items=[]
 for i in range(0,len(syms),20):
  batch=','.join(syms[i:i+20])
  try:
   q=get('https://brapi.dev/api/v2/stocks/quote?symbols='+batch).get('results',[]);st=get('https://brapi.dev/api/v2/stocks/statistics?symbols='+batch+'&mode=current').get('results',[]);fi=get('https://brapi.dev/api/v2/stocks/financial-data?symbols='+batch+'&mode=current').get('results',[])
   qm={x.get('symbol'):x for x in q};sm={x.get('symbol'):x for x in st};fm={x.get('symbol'):x for x in fi}
   for sym in syms[i:i+20]:
    if sym in qm:items.append(norm(sym,qm[sym],sm.get(sym,{}),fm.get(sym,{})))
  except Exception as e:print('batch failed',batch,e)
 clean=[x for x in items if x.get('price') and x.get('market_cap') and x.get('volume') and x['volume']>=50000]
 OUT.write_text(json.dumps({'updated_at':now,'universe_size':len(clean),'items':rank(clean),'message':'<b>Varredura concluída.</b> Empresas sem liquidez mínima ou preço válido foram excluídas.'},ensure_ascii=False))
if __name__=='__main__':main()