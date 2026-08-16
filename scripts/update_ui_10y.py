from pathlib import Path
p=Path('index.html');s=p.read_text(encoding='utf-8')
s=s.replace('<th>Score</th>','<th>DY médio 10a</th><th>Cresc. receita 10a</th><th>Score</th>')
s=s.replace("['Fluxo de caixa livre',pct(x.fcf_margin)]", "['Fluxo de caixa livre',pct(x.fcf_margin)],['DY médio 10 anos',pct(x.dy_10y_avg)],['Cresc. receita 10 anos',pct(x.revenue_growth_10y)]")
s=s.replace('<td class="score">${x.score}</td>', '<td>${pct(x.dy_10y_avg)}</td><td class="${(x.revenue_growth_10y||0)>=0?\'up\':\'down\'}">${pct(x.revenue_growth_10y)}</td><td class="score">${x.score}</td>')
s=s.replace('colspan="11"','colspan="13"')
s=s.replace('<section class="panel method"><h2>Filtros usados no Top 10</h2>', '<section class="panel method"><h2>Leitura dos indicadores de 10 anos</h2><p><b>DY médio 10a:</b> média simples dos Dividend Yields anuais de 10 exercícios completos. Cada ano usa os proventos por ação com data ex no ano divididos pelo fechamento do último pregão daquele ano.</p><p><b>Cresc. receita 10a:</b> CAGR da receita consolidada entre o primeiro e o último exercício da janela de 10 anos, usando DFP/CVM.</p></section><section class="panel method"><h2>Filtros usados no Top 10</h2>')
p.write_text(s,encoding='utf-8');assert 'DY médio 10a' in s and 'Cresc. receita 10a' in s and 'dy_10y_avg' in s and 'revenue_growth_10y' in s
print('UI 10 anos pronta')
