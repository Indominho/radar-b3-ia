import datetime as dt,json,os,pathlib,urllib.parse,urllib.request
OUT=pathlib.Path('data/catalog.json');TOKEN=os.getenv('BRAPI_TOKEN','').strip()
def get(url):
 headers={'User-Agent':'radar-b3-ia/5.0'}
 if TOKEN:headers['Authorization']=f'Bearer {TOKEN}'
 req=urllib.request.Request(url,headers=headers)
 with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)
url='https://brapi.dev/api/v2/tickers?type=stock&subType=stock&sortBy=symbol&sortOrder=asc&page=1&limit=2000'
data=get(url);rows=[]
for x in data.get('results',[]):
 if not x.get('isActive',True):continue
 q=x.get('quote') or {}
 rows.append({'ticker':x.get('symbol'),'name':x.get('name') or x.get('longName') or x.get('symbol'),'longName':x.get('longName'),'sector':x.get('sector'),'subsector':x.get('subsector'),'assetType':x.get('assetType'),'subType':x.get('subType'),'logoUrl':x.get('logoUrl'),'price':q.get('lastPrice'),'change':q.get('changePercent'),'volume':q.get('volume'),'marketCap':q.get('marketCap'),'source':'brapi ticker catalog'})
if len(rows)<300:raise RuntimeError(f'Catálogo brapi incompleto: {len(rows)} ações')
OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps({'updated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'count':len(rows),'items':rows,'source':'brapi /api/v2/tickers'},ensure_ascii=False,allow_nan=False),encoding='utf-8');print('CATALOGO BRAPI',len(rows))
