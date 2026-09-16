from pathlib import Path
p=Path('index.html');s=p.read_text(encoding='utf-8')
anchor='<section class="panel"><h2>Top 10 de longo prazo'
block='''<section class="panel"><h2>Renda + valorização em 5 anos <span class="subhead">DY médio ≥15% ao ano e valorização CAGR ≥10% ao ano</span></h2><div class="table"><table><thead><tr><th>Empresa</th><th>DY médio 5a</th><th>Valorização total 5a</th><th>Valorização média anual</th><th>P/L</th><th>ROE</th><th>Score combinado</th></tr></thead><tbody id="fiveYearRows"></tbody></table></div></section>'''
if 'id="fiveYearRows"' not in s:s=s.replace(anchor,block+anchor)
s=s.replace("function renderRank(){", "function renderFiveYear(){let a=db.five_year_picks||[];$('#fiveYearRows').innerHTML=a.length?a.map(x=>`<tr onclick=\"show('${x.ticker}')\"><td class=\"ticker\">${x.ticker}<span>${esc(x.name)}</span></td><td>${pct(x.dy_5y_avg)}</td><td class=\"${x.price_return_5y>=0?'up':'down'}\">${pct(x.price_return_5y)}</td><td class=\"${x.price_cagr_5y>=0?'up':'down'}\">${pct(x.price_cagr_5y)}</td><td>${num(x.pe)}</td><td>${pct(x.roe)}</td><td class=\"score\">${num(x.five_year_combo_score,1)}</td></tr>`).join(''):'<tr><td colspan=\"7\" class=\"empty\">Nenhuma ação passou simultaneamente pelos dois cortes nesta atualização.</td></tr>'}function renderRank(){")
s=s.replace('renderCatalog();renderRank()', 'renderCatalog();renderFiveYear();renderRank()')
p.write_text(s,encoding='utf-8');assert 'fiveYearRows' in s and 'renderFiveYear()' in s
print('UI estratégia 5 anos pronta')
