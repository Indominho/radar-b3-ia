import datetime as dt,json,os,pathlib,urllib.request
TOKEN=os.getenv('BRAPI_TOKEN','').strip();OUT=pathlib.Path('data/brapi-status.json');OUT.parent.mkdir(exist_ok=True)
if not TOKEN:raise SystemExit('BRAPI_TOKEN não está disponível no GitHub Actions')
req=urllib.request.Request('https://brapi.dev/api/v2/stocks/quote?symbols=PETR4',headers={'Authorization':f'Bearer {TOKEN}','User-Agent':'radar-b3-ia/verify'})
with urllib.request.urlopen(req,timeout=30) as r:
 data=json.load(r)
results=data.get('results',[])
if not results:raise SystemExit('A brapi respondeu sem cotação')
OUT.write_text(json.dumps({'connected':True,'verified_at':dt.datetime.now(dt.timezone.utc).isoformat(),'test_symbol':'PETR4','provider':'brapi','plan_note':'limites definidos pela conta conectada'},ensure_ascii=False),encoding='utf-8')
print('BRAPI CONNECTED',results[0].get('symbol') or results[0].get('requestedSymbol'))
