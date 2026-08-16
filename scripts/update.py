import csv, datetime as dt, io, json, math, pathlib, re, sys, unicodedata, urllib.request, zipfile
from difflib import SequenceMatcher

OUT = pathlib.Path('data/ranking.json')
OUT.parent.mkdir(exist_ok=True)
UA = {'User-Agent': 'radar-b3-ia/2.0 contato: github.com/Indominho/radar-b3-ia'}

def download(url, timeout=120):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()

def number(value):
    if value is None or value == '': return None
    try: return float(str(value).replace('.', '').replace(',', '.'))
    except ValueError: return None

def norm(text):
    text = unicodedata.normalize('NFKD', text or '').encode('ascii', 'ignore').decode().upper()
    text = re.sub(r'\b(S A|SA|S/A|CIA|COMPANHIA|HOLDING|PARTICIPACOES|DO|DA|DE)\b', ' ', text)
    return re.sub(r'[^A-Z0-9]+', '', text)

def csv_rows(zf, contains):
    name = next((n for n in zf.namelist() if contains.lower() in n.lower() and n.lower().endswith('.csv')), None)
    if not name: return
    with zf.open(name) as raw:
        text = io.TextIOWrapper(raw, encoding='latin-1', newline='')
        yield from csv.DictReader(text, delimiter=';')

def scale_value(row):
    value = number(row.get('VL_CONTA'))
    if value is None: return None
    code = row.get('CD_CONTA', '')
    if code.startswith('3.99'): return value
    return value * (1000 if 'MIL' in (row.get('ESCALA_MOEDA') or '').upper() else 1)

def latest_dfp_year():
    year = dt.datetime.now().year - 1
    for candidate in range(year, year - 4, -1):
        url = f'https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_{candidate}.zip'
        try: return candidate, download(url)
        except Exception as exc: print('DFP indisponivel', candidate, exc)
    raise RuntimeError('Nenhum DFP anual disponível')

def load_dfp(year, blob):
    companies = {}
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        for statement in ('BPA_con', 'BPP_con', 'DRE_con', 'DFC_MI_con', 'DFC_MD_con'):
            for row in csv_rows(zf, statement) or []:
                if row.get('ORDEM_EXERC') not in ('ÚLTIMO', 'ULTIMO'): continue
                if row.get('ST_CONTA_FIXA') == 'N': continue
                cd = row.get('CD_CVM')
                if not cd: continue
                company = companies.setdefault(cd, {'cvm': cd, 'name': row.get('DENOM_CIA') or cd, 'accounts': {}, 'date': '', 'version': 0})
                date = row.get('DT_REFER') or ''
                version = int(number(row.get('VERSAO')) or 0)
                marker = (date, version)
                old_marker = (company['date'], company['version'])
                if marker < old_marker: continue
                if marker > old_marker:
                    company['accounts'] = {}; company['date'] = date; company['version'] = version
                code = row.get('CD_CONTA') or ''
                value = scale_value(row)
                if code and value is not None: company['accounts'][code] = value
    return companies

def account(company, code, prefix=False):
    values = company.get('accounts', {})
    if code in values: return values[code]
    if prefix:
        found = [v for k, v in values.items() if k.startswith(code)]
        return max(found, key=abs) if found else None
    return None

def load_registry():
    url = 'https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv'
    text = download(url).decode('latin-1')
    registry = {}
    for row in csv.DictReader(io.StringIO(text), delimiter=';'):
        if (row.get('SIT') or '').upper() != 'ATIVO': continue
        cd = row.get('CD_CVM')
        if not cd: continue
        registry[cd] = {'commercial': row.get('DENOM_COMERC') or '', 'social': row.get('DENOM_SOCIAL') or '', 'registered': row.get('DT_REG') or ''}
    return registry

def load_quotes():
    today = dt.date.today()
    errors = []
    for days in range(1, 12):
        day = today - dt.timedelta(days=days)
        if day.weekday() >= 5: continue
        url = 'https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_D' + day.strftime('%d%m%Y') + '.ZIP'
        try:
            blob = download(url)
            with zipfile.ZipFile(io.BytesIO(blob)) as zf:
                name = zf.namelist()[0]
                lines = io.TextIOWrapper(zf.open(name), encoding='latin-1')
                quotes = []
                for line in lines:
                    if not line.startswith('01') or len(line) < 245: continue
                    if line[10:12] != '02' or line[24:27] != '010': continue
                    ticker = line[12:24].strip()
                    if not re.fullmatch(r'[A-Z]{4}\d{1,2}', ticker): continue
                    close = number(line[108:121])
                    volume = number(line[170:188])
                    quantity = number(line[152:170])
                    if close is None: continue
                    quotes.append({'ticker': ticker, 'issuer': line[27:39].strip(), 'price': close / 100, 'turnover': (volume or 0) / 100, 'volume': quantity or 0, 'date': day.isoformat()})
            if quotes: return quotes, day.isoformat()
        except Exception as exc: errors.append(f'{day}: {exc}')
    raise RuntimeError('COTAHIST diário indisponível: ' + ' | '.join(errors[-3:]))

def company_metrics(company, previous):
    equity = account(company, '2.03')
    assets = account(company, '1')
    debt = (account(company, '2.01.04', True) or 0) + (account(company, '2.02.01', True) or 0)
    revenue = account(company, '3.01')
    ebit = account(company, '3.05')
    profit = account(company, '3.11')
    cfo = account(company, '6.01')
    cfi = account(company, '6.02')
    eps = account(company, '3.99.01', True)
    prev_revenue = account(previous or {}, '3.01')
    prev_profit = account(previous or {}, '3.11')
    def ratio(a, b, factor=1): return a / b * factor if a is not None and b not in (None, 0) else None
    return {
        'equity': equity, 'assets': assets, 'debt': debt, 'revenue': revenue, 'profit': profit, 'eps': eps,
        'roe': ratio(profit, equity, 100), 'roic': ratio(ebit, (equity or 0) + debt, 100),
        'margin': ratio(profit, revenue, 100), 'debt_equity': ratio(debt, equity),
        'growth': ratio((revenue - prev_revenue) if revenue is not None and prev_revenue is not None else None, abs(prev_revenue) if prev_revenue else None, 100),
        'profit_growth': ratio((profit - prev_profit) if profit is not None and prev_profit is not None else None, abs(prev_profit) if prev_profit else None, 100),
        'fcf_margin': ratio((cfo + cfi) if cfo is not None and cfi is not None else None, revenue, 100)
    }

def match_company(issuer, aliases):
    needle = norm(issuer)
    best, best_score = None, 0
    for cd, names in aliases.items():
        for name in names:
            candidate = norm(name)
            if not candidate: continue
            score = SequenceMatcher(None, needle, candidate).ratio()
            if needle and (candidate.startswith(needle) or needle.startswith(candidate)): score += .22
            if score > best_score: best, best_score = cd, score
    return (best, min(best_score, 1)) if best_score >= .66 else (None, best_score)

def rank(items):
    metrics = [('pe', False, .20), ('roe', True, .18), ('roic', True, .15), ('margin', True, .12), ('growth', True, .12), ('debt_equity', False, .12), ('fcf_margin', True, .07), ('turnover', True, .04)]
    for key, high, weight in metrics:
        values = sorted(x[key] for x in items if x.get(key) is not None and math.isfinite(x[key]))
        lo = values[int((len(values) - 1) * .05)] if values else None
        hi = values[int((len(values) - 1) * .95)] if values else None
        for item in items:
            value = item.get(key)
            z = None if value is None or lo is None else (50 if hi == lo else max(0, min(100, (value - lo) / (hi - lo) * 100)))
            item['_' + key] = z if high or z is None else 100 - z
    for item in items:
        available = sum(w for k, _, w in metrics if item['_' + k] is not None)
        raw = sum(item['_' + k] * w for k, _, w in metrics if item['_' + k] is not None) / (available or 1)
        item['coverage'] = round(available * 100)
        item['score'] = round(raw * (.60 + .40 * available) * item.get('match_quality', 1))
        for key, _, _ in metrics: item.pop('_' + key, None)
    return sorted(items, key=lambda x: (x['score'], x.get('turnover') or 0), reverse=True)

def main():
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    year, blob = latest_dfp_year()
    current = load_dfp(year, blob)
    try:
        previous_blob = download(f'https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_{year-1}.zip')
        previous = load_dfp(year - 1, previous_blob)
    except Exception as exc:
        print('DFP anterior indisponível', exc); previous = {}
    registry = load_registry()
    quotes, quote_date = load_quotes()
    aliases = {}
    for cd, company in current.items():
        reg = registry.get(cd, {})
        aliases[cd] = [company.get('name', ''), reg.get('commercial', ''), reg.get('social', '')]
    by_company = {}
    for quote in quotes:
        cd, quality = match_company(quote['issuer'], aliases)
        if not cd: continue
        old = by_company.get(cd)
        if old is None or quote['turnover'] > old['turnover']:
            quote['match_quality'] = quality; by_company[cd] = quote
    items = []
    cutoff = dt.date.today() - dt.timedelta(days=3652)
    for cd, quote in by_company.items():
        company = current[cd]; m = company_metrics(company, previous.get(cd))
        reg = registry.get(cd, {})
        try: old_enough = dt.datetime.strptime(reg.get('registered', ''), '%Y-%m-%d').date() <= cutoff
        except ValueError: old_enough = True
        if not old_enough or not m['equity'] or m['equity'] <= 0 or not m['profit'] or m['profit'] <= 0: continue
        if m.get('pe') is not None and m['pe'] <= 0: continue
        if quote['turnover'] < 1_000_000 or quote['volume'] < 50_000: continue
        eps = m.get('eps')
        pe = quote['price'] / eps if eps and eps > 0 else None
        item = {**quote, **m, 'pe': pe, 'pvp': None, 'dy': None, 'upside': None, 'name': reg.get('commercial') or company['name'], 'sector': 'Não classificado', 'cvm_code': cd, 'statement_date': company['date']}
        items.append(item)
    ranked = rank(items)
    message = f'<b>Dados públicos oficiais.</b> Cotações B3 de {quote_date}; fundamentos DFP/CVM {year}. Atualização diária, com atraso aceito. DY, P/VP e consenso ficam N/D porque não constam diretamente nestas bases.'
    OUT.write_text(json.dumps({'updated_at': now, 'quote_date': quote_date, 'statement_year': year, 'universe_size': len(ranked), 'items': ranked, 'message': message}, ensure_ascii=False, allow_nan=False), encoding='utf-8')
    print('Publicados', len(ranked), 'ativos; top 10:', [x['ticker'] for x in ranked[:10]])

if __name__ == '__main__':
    try: main()
    except Exception as exc:
        now = dt.datetime.now(dt.timezone.utc).isoformat()
        old = json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else {'items': [], 'universe_size': 0}
        old.update({'updated_at': now, 'message': '<b>Atualização falhou.</b> Mantido o último ranking válido. Motivo: ' + str(exc)[:240]})
        OUT.write_text(json.dumps(old, ensure_ascii=False, allow_nan=False), encoding='utf-8')
        print(exc, file=sys.stderr); raise
