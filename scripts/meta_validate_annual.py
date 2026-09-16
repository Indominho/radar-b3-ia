import json, math, pathlib, random
D=json.loads(pathlib.Path('data/ranking.json').read_text(encoding='utf-8'))
items=D.get('items',[]); random.seed(20260916); sample=random.sample(items,min(25,len(items))); failures=[]
def finite(v): return isinstance(v,(int,float)) and math.isfinite(v)
for x in sample:
    hist=x.get('dy_10y_history') or []; values=[]
    for row in hist:
        p=row.get('year_end_price'); div=row.get('dividends_per_share'); reported=row.get('dy')
        calc=reported if finite(reported) else (div/p*100 if finite(div) and finite(p) and p>0 else None)
        if finite(calc): values.append(calc)
    expected=sum(values)/len(values) if values else None
    actual=((x.get('annual_indicators') or {}).get('dy') or {}).get('value')
    if expected is None:
        if actual is not None: failures.append(f"{x.get('ticker')}: deveria ser não aplicável")
    elif not finite(actual) or abs(expected-actual)>1e-8:
        failures.append(f"{x.get('ticker')}: meta-média divergente")
    if len(values)!=((x.get('annual_indicators') or {}).get('dy') or {}).get('years',-1): failures.append(f"{x.get('ticker')}: meta-contagem divergente")
if failures: raise SystemExit('\n'.join(failures))
print('META VALIDATOR PASS',len(sample),'ações verificadas independentemente')
