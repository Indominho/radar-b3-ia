from pathlib import Path
p=Path('index.html');s=p.read_text(encoding='utf-8')
# Rankings na tela usam somente a base fundamentalista disponível para cada período.
s=s.replace("function pick5(){let a=[...db.items].sort((x,y)=>(y.dy_5y_avg??y.dy??-Infinity)-(x.dy_5y_avg??x.dy??-Infinity));return a.slice(0,10)}", "function pick5(){return [...db.items].filter(x=>typeof x.dy_5y_avg==='number'&&typeof x.price_cagr_5y==='number').sort((x,y)=>(y.dy_5y_avg-x.dy_5y_avg)||(y.price_cagr_5y-x.price_cagr_5y)).slice(0,10)}")
s=s.replace("function pick10(){let a=[...db.items].sort((x,y)=>(y.dy_10y_avg??y.dy_5y_avg??y.dy??-Infinity)-(x.dy_10y_avg??x.dy_5y_avg??x.dy??-Infinity));return a.slice(0,10)}", "function pick10(){return [...db.items].filter(x=>typeof x.dy_10y_avg==='number'&&typeof x.revenue_growth_10y==='number').sort((x,y)=>(y.dy_10y_avg-x.dy_10y_avg)||(y.revenue_growth_10y-x.revenue_growth_10y)).slice(0,10)}")
# No fallback from 5y to current DY inside the 5y Top.
s=s.replace("x.dy_5y_avg??x.dy", "x.dy_5y_avg")
s=s.replace("x.dy_10y_avg??x.dy_5y_avg??x.dy", "x.dy_10y_avg")
p.write_text(s,encoding='utf-8')
print('RANKINGS PERIOD-SAFE PASS')
