import html.parser, io, json, pathlib, re, urllib.request, zipfile, datetime as dt
OUT=pathlib.Path('data/catalog.json');HEAD={'User-Agent':'Mozilla/5.0 radar-b3-ia/catalog','Accept-Language':'pt-BR'}
def get(url):
 req=urllib.request.Request(url,headers=HEAD)
 with urllib.request.urlopen(req,timeout=240) as r:return r.read()
def n(v):
 if v is None:return None
 t=str(v).replace('\xa0','').strip().replace('%','')
 if not t or t in ('-','—'):return None
 try:return float(t.replace('.','').replace(',','.'))
 except:return None
class Tables(html.parser.HTMLParser):
 def __init__(self):super().__init__();self.tables=[];self.table=self.row=self.cell=None
 def handle_starttag(self,t,a):
  if t=='table':self.table=[]
  elif t=='tr' and self.table is not None:self.row=[]
  elif t in ('td','th') and self.row is not None:self.cell=[]
 def handle_data(self,d):
  if self.cell is not None:self.cell.append(d)
 def handle_endtag(self,t):
  if t in ('td','th') and self.cell is not None:self.row.append(' '.join(''.join(self.cell).split()));self.cell=None
  elif t=='tr' and self.row is not None:
   if self.row:self.table.append(self.row)
   self.row=None
  elif t=='table' and self.table is not None:self.tables.append(self.table);self.table=None
p=Tables();p.feed(get('https://www.fundamentus.com.br/resultado.php').decode('latin-1','ignore'));table=next(t for t in p.tables if t and 'Papel' in t[0] and len(t)>100);headers=table[0];rows=[]
for row in table[1:]:
 if len(row)<len(headers):continue
 d=dict(zip(headers,row));ticker=d.get('Papel','').strip()
 if not re.fullmatch(r'[A-Z]{4}\d{1,2}',ticker):continue
 rows.append({'ticker':ticker,'name':ticker,'price':n(d.get('Cotação')),'pe':n(d.get('P/L')),'pvp':n(d.get('P/VP')),'dy':n(d.get('Div.Yield')),'roe':n(d.get('ROE')),'roic':n(d.get('ROIC')),'margin':n(d.get('Mrg. Líq.')),'growth':n(d.get('Cresc. Rec.5a')),'debt_equity':n(d.get('Dív.Líq/ Patrim.')),'ev_ebitda':n(d.get('EV/EBITDA')),'liquidity_2m':n(d.get('Liq.2meses')),'equity':n(d.get('Patrim. Líq'))})
# Nome de pregão oficial do COTAHIST mais recente disponível no ano
names={};year=dt.date.today().year
try:
 raw=get(f'https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A{year}.ZIP')
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  for line in io.TextIOWrapper(z.open(z.namelist()[0]),encoding='latin-1'):
   if line.startswith('01') and line[10:12]=='02' and line[24:27]=='010':
    ticker=line[12:24].strip()
    if re.fullmatch(r'[A-Z]{4}\d{1,2}',ticker):names[ticker]=line[27:39].strip()
except Exception as e:print('nomes COTAHIST indisponíveis',e)
for x in rows:x['name']=names.get(x['ticker'],x['ticker'])
rows.sort(key=lambda x:x['ticker']);OUT.write_text(json.dumps({'updated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'count':len(rows),'items':rows},ensure_ascii=False,allow_nan=False),encoding='utf-8');print('CATALOGO',len(rows))
