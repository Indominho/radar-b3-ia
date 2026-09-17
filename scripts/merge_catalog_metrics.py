from pathlib import Path
p=Path('index.html');s=p.read_text(encoding='utf-8')
old="cat=await(await fetch('data/catalog.json?'+t)).json();"
new="cat=await(await fetch('data/catalog.json?'+t)).json();const byTicker=new Map((db.items||[]).map(x=>[x.ticker,x]));cat.items=(cat.items||[]).map(x=>({...x,...(byTicker.get(x.ticker)||{}),price:x.price,change:x.change,volume:x.volume,marketCap:x.marketCap}));"
if old in s:s=s.replace(old,new)
else:
    if 'byTicker=new Map' not in s: raise SystemExit('load pattern not found')
p.write_text(s,encoding='utf-8');print('MERGE METRICS PASS')
