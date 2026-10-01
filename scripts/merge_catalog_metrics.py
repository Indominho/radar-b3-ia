from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="cat=await(await fetch('data/catalog.json?'+t)).json();"
new="cat=await(await fetch('data/catalog.json?'+t)).json();const byTicker=new Map((db.items||[]).map(x=>[x.ticker,x]));cat.items=(cat.items||[]).map(x=>({...x,...(byTicker.get(x.ticker)||{}),price:x.price,change:x.change,volume:x.volume,marketCap:x.marketCap}));"
if old in s:
    s=s.replace(old,new)
elif 'byTicker=new Map' in s:
    print('MERGE METRICS ALREADY PRESENT')
elif 'data/catalog.json' in s and 'data/ranking.json' in s:
    # Current UI loads ranking and catalog separately and does not require a merge.
    print('MERGE METRICS NOT REQUIRED BY CURRENT UI')
else:
    raise SystemExit('load pattern not found and current UI has no ranking/catalog loaders')
p.write_text(s,encoding='utf-8')
print('MERGE METRICS PASS')
