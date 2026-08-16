import datetime as dt, html.parser, io, json, pathlib, re, urllib.request, zipfile

DATA = pathlib.Path('data/ranking.json')
HEADERS = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36','Accept-Language':'pt-BR,pt;q=0.9'}

def get(url, timeout=120):
    req=urllib.request.Request(url,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=timeout) as r:return r.read()

def br_number(value, percent=False):
    if value is None:return None
    text=str(value).replace('\xa0',' ').strip().replace('%','')
    if not text or text in ('-','—'):return None
    try:return float(text.replace('.','').replace(',','.'))
    except ValueError:return None

class Tables(html.parser.HTMLParser):
    def __init__(self):super().__init__();self.tables=[];self.table=None;self.row=None;self.cell=None
    def handle_starttag(self,tag,attrs):
        if tag=='table':self.table=[]
        elif tag=='tr' and self.table is not None:self.row=[]
        elif tag in ('td','th') and self.row is not None:self.cell=[]
    def handle_data(self,data):
        if self.cell is not None:self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split()));self.cell=None
        elif tag=='tr' and self.row is not None:
            if self.row:self.table.append(self.row)
            self.row=None
        elif tag=='table' and self.table is not None:
            self.tables.append(self.table);self.table=None

def fundamentus():
    parser=Tables();parser.feed(get('https://www.fundamentus.com.br/resultado.php').decode('latin-1','ignore'))
    table=next((t for t in parser.tables if t and any('Papel' in c for c in t[0]) and len(t)>20),[])
    if not table:return {}
    headers=table[0];out={}
    for row in table[1:]:
        if len(row)<len(headers):continue
        d=dict(zip(headers,row));ticker=d.get('Papel','').strip()
        if not re.fullmatch(r'[A-Z]{4}\d{1,2}',ticker):continue
        out[ticker]={'price_fundamentus':br_number(d.get('Cotação')),'pe_fundamentus':br_number(d.get('P/L')),'pvp':br_number(d.get('P/VP')),'dy':br_number(d.get('Div.Yield')),'ev_ebitda':br_number(d.get('EV/EBITDA')),'roe_fundamentus':br_number(d.get('ROE')),'roic_fundamentus':br_number(d.get('ROIC')),'liquidity_2m':br_number(d.get('Liq.2meses')),'revenue_growth_5y':br_number(d.get('Cresc. Rec.5a')),'net_debt_equity_fundamentus':br_number(d.get('Dív.Líq/ Patrim.'))}
    return out

def momentum_6m(tickers):
    year=dt.date.today().year
    url=f'https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A{year}.ZIP'
    raw=get(url);prices={t:[] for t in tickers}
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        name=zf.namelist()[0]
        for line in io.TextIOWrapper(zf.open(name),encoding='latin-1'):
            if not line.startswith('01') or line[10:12]!='02' or line[24:27]!='010':continue
            ticker=line[12:24].strip()
            if ticker not in prices:continue
            try:day=dt.datetime.strptime(line[2:10],'%Y%m%d').date();close=int(line[108:121])/100
            except ValueError:continue
            prices[ticker].append((day,close))
    cutoff=dt.date.today()-dt.timedelta(days=183);out={}
    for ticker,series in prices.items():
        series.sort();latest=series[-1] if series else None
        prior=min(series,key=lambda p:abs((p[0]-cutoff).days)) if series else None
        if latest and prior and prior[1]>0:out[ticker]={'momentum_6m':(latest[1]/prior[1]-1)*100,'price_6m_ago':prior[1],'momentum_from':prior[0].isoformat()}
    return out

def explain(x):
    positives=[];risks=[]
    if x.get('roe') is not None and x['roe']>=18:positives.append(f"ROE de {x['roe']:.1f}%")
    if x.get('roic') is not None and x['roic']>=15:positives.append(f"ROIC de {x['roic']:.1f}%")
    if x.get('debt_equity') is not None and x['debt_equity']<=.8:positives.append('endividamento controlado')
    if x.get('growth') is not None and x['growth']>=10:positives.append(f"receita cresceu {x['growth']:.1f}%")
    if x.get('margin') is not None and x['margin']>=10:positives.append(f"margem líquida de {x['margin']:.1f}%")
    if x.get('dy') is not None and x['dy']>=5:positives.append(f"DY de {x['dy']:.1f}%")
    if x.get('pvp') is not None and 0<x['pvp']<=2:positives.append(f"P/VP de {x['pvp']:.2f}x")
    if x.get('momentum_6m') is not None and x['momentum_6m']>=20:positives.append(f"alta de {x['momentum_6m']:.1f}% em 6 meses")
    if x.get('debt_equity') is not None and x['debt_equity']>2:risks.append('dívida elevada')
    if x.get('growth') is not None and x['growth']<0:risks.append('receita em retração')
    if x.get('pvp') is not None and x['pvp']>4:risks.append('P/VP exigente')
    if x.get('momentum_6m') is not None and x['momentum_6m']>80:risks.append('alta muito rápida pode corrigir')
    return {'thesis':'; '.join(positives[:5]) or 'qualidade relativa favorável dentro da amostra','risks':'; '.join(risks[:3]) or 'execução, setor e ciclo econômico','catalysts':'; '.join([p for p in positives if 'cresceu' in p or 'alta' in p][:2]) or 'manutenção da rentabilidade e geração de caixa'}

def score(items):
    metrics=[('pe',False,.14),('pvp',False,.10),('dy',True,.12),('roe',True,.14),('roic',True,.13),('margin',True,.10),('growth',True,.10),('debt_equity',False,.09),('fcf_margin',True,.05),('turnover',True,.03)]
    for key,high,w in metrics:
        vals=sorted(x[key] for x in items if isinstance(x.get(key),(int,float)))
        lo=vals[int((len(vals)-1)*.05)] if vals else None;hi=vals[int((len(vals)-1)*.95)] if vals else None
        for x in items:
            v=x.get(key);z=None if not isinstance(v,(int,float)) or lo is None else (50 if hi==lo else max(0,min(100,(v-lo)/(hi-lo)*100)))
            x['_'+key]=z if high or z is None else 100-z
    for x in items:
        got=sum(w for k,h,w in metrics if x['_'+k] is not None);raw=sum(x['_'+k]*w for k,h,w in metrics if x['_'+k] is not None)/(got or 1)
        x['coverage']=round(got*100);x['score']=round(raw*(.62+.38*got));x.update(explain(x))
        for k,h,w in metrics:x.pop('_'+k,None)
    items.sort(key=lambda x:(x['score'],x.get('turnover') or 0),reverse=True)

def main():
    db=json.loads(DATA.read_text(encoding='utf-8'));items=db.get('items',[]);fund=fundamentus();mom=momentum_6m({x['ticker'] for x in items})
    for x in items:
        f=fund.get(x['ticker'],{});x.update({k:v for k,v in f.items() if v is not None});x.update(mom.get(x['ticker'],{}))
        if f.get('pe_fundamentus') is not None:x['pe']=f['pe_fundamentus']
        if f.get('roe_fundamentus') is not None:x['roe']=f['roe_fundamentus']
        if f.get('roic_fundamentus') is not None:x['roic']=f['roic_fundamentus']
        if f.get('net_debt_equity_fundamentus') is not None:x['debt_equity']=f['net_debt_equity_fundamentus']
    score(items)
    eligible=[x for x in items if (x.get('momentum_6m') or -999)>=20 and (x.get('growth') or -999)>=8 and (x.get('roe') or -999)>=12 and (x.get('debt_equity') is None or x['debt_equity']<=2)]
    eligible.sort(key=lambda x:((x.get('momentum_6m') or 0),x['score']),reverse=True)
    db['items']=items;db['emerging_bets']=eligible[:10];db['fundamentus_coverage']=sum(1 for x in items if x.get('pvp') is not None);db['momentum_coverage']=sum(1 for x in items if x.get('momentum_6m') is not None)
    db['message']=f"<b>Base enriquecida.</b> {len(items)} ações elegíveis; DY/P/VP em {db['fundamentus_coverage']}; momentum de 6 meses em {db['momentum_coverage']}. Consenso aparece somente quando houver fonte licenciada, pois dados de analistas não são públicos para todas as ações."
    DATA.write_text(json.dumps(db,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    print('Top 10',[(x['ticker'],x['score']) for x in items[:10]]);print('Apostas',[(x['ticker'],round(x.get('momentum_6m',0),1)) for x in eligible[:10]])
if __name__=='__main__':main()
