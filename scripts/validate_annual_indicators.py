import json, math, pathlib
D=json.loads(pathlib.Path('data/ranking.json').read_text(encoding='utf-8'))
items=D.get('items',[]); failures=[]; checked=0

def finite(v): return isinstance(v,(int,float)) and math.isfinite(v)
def fail(msg): failures.append(msg)
for x in items:
    a=x.get('annual_indicators')
    if not isinstance(a,dict): fail(f"{x.get('ticker')}: annual_indicators ausente"); continue
    hist=a.get('dy',{}); raw=[]
    for row in (x.get('dy_10y_history') or []):
        dy=row.get('dy'); price=row.get('year_end_price'); paid=row.get('dividends_per_share')
        if not finite(dy) and finite(price) and price>0 and finite(paid): dy=paid/price*100
        if finite(dy): raw.append(dy)
    value=hist.get('value')
    if raw:
        expected=sum(raw)/len(raw)
        if not finite(value) or abs(value-expected)>1e-8: fail(f"{x.get('ticker')}: média DY divergente")
        if hist.get('years')!=len(raw): fail(f"{x.get('ticker')}: quantidade de anos divergente")
    else:
        if value is not None or hist.get('years')!=0: fail(f"{x.get('ticker')}: ausência mal rotulada")
    if not hist.get('formula') or not hist.get('source') or not hist.get('label'): fail(f"{x.get('ticker')}: proveniência incompleta")
    checked+=1
if failures: raise SystemExit('\n'.join(failures[:20]))
print('ANNUAL VALIDATOR PASS',checked,'ações; falhas',len(failures))
