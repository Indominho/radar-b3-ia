import datetime as dt,json,os,pathlib,re,urllib.request

OUT=pathlib.Path('data/catalog.json')
TOKEN=os.getenv('BRAPI_TOKEN','').strip()

def get(url):
    headers={'User-Agent':'radar-b3-ia/6.0'}
    if TOKEN:
        headers['Authorization']=f'Bearer {TOKEN}'
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.load(r)


def is_market_action(symbol, row):
    if not symbol or not re.match(r'^[A-Z0-9]{4,7}$', symbol):
        return False
    # Sufixo F representa mercado fracionário, não uma nova ação.
    if symbol.endswith('F'):
        return False
    # Mantém papéis, units e preferenciais; remove registros sem código B3 útil.
    return any(ch.isdigit() for ch in symbol) and (row.get('assetType') in (None, 'stock'))

url='https://brapi.dev/api/v2/tickers?type=stock&subType=stock&sortBy=symbol&sortOrder=asc&page=1&limit=2000'
data=get(url)
rows=[]
seen=set()
for x in data.get('results',[]):
    symbol=(x.get('symbol') or '').upper().strip()
    if not x.get('isActive',True) or not is_market_action(symbol,x) or symbol in seen:
        continue
    seen.add(symbol)
    q=x.get('quote') or {}
    rows.append({
        'ticker':symbol,
        'name':x.get('name') or x.get('longName') or symbol,
        'longName':x.get('longName'),
        'sector':x.get('sector'),
        'subsector':x.get('subsector'),
        'assetType':x.get('assetType'),
        'subType':x.get('subType'),
        'logoUrl':x.get('logoUrl'),
        'price':q.get('lastPrice'),
        'change':q.get('changePercent'),
        'volume':q.get('volume'),
        'marketCap':q.get('marketCap'),
        'source':'brapi ticker catalog'
    })

if len(rows)<250:
    raise RuntimeError(f'Catálogo brapi incompleto: {len(rows)} ações')

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps({
    'updated_at':dt.datetime.now(dt.timezone.utc).isoformat(),
    'count':len(rows),
    'count_raw':len(data.get('results',[])),
    'items':rows,
    'source':'brapi /api/v2/tickers, papéis ativos sem sufixo F'
},ensure_ascii=False,allow_nan=False),encoding='utf-8')
print('CATALOGO B3 AÇÕES',len(rows),'de',len(data.get('results',[])),'registros brapi')
