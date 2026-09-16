from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Interface nova: o ranking é renderizado pelo próprio index.html.
s=s.replace('Renda + alta em 5 anos','Ranking 5 anos')
s=s.replace('Renda + valorização','Ranking de 5 anos')
s=s.replace('Filtro combinado: DY médio de 5 anos ≥15% e CAGR do preço ≥10%.','Ordenado pelo maior DY médio de 5 anos; a valorização média anual aparece junto para comparação.')
s=s.replace('Nenhum ativo passou pelos dois cortes nesta atualização.','Nenhum ativo possui simultaneamente histórico de DY médio e valorização média de 5 anos nesta atualização.')

# Compatibilidade com a interface legada, caso ela seja restaurada.
if '<section class="panel"><h2>Top 10 de longo prazo' in s and 'id="fiveYearRows"' not in s:
    anchor='<section class="panel"><h2>Top 10 de longo prazo'
    block='''<section class="panel"><h2>Ranking de 5 anos <span class="subhead">Ordenado por DY médio de 5 anos e valorização média anual</span></h2><div class="table"><table><thead><tr><th>Empresa</th><th>DY médio 5a</th><th>Valorização total 5a</th><th>Valorização média anual</th><th>P/L</th><th>ROE</th><th>Score auxiliar</th></tr></thead><tbody id="fiveYearRows"></tbody></table></div></section>'''
    s=s.replace(anchor,block+anchor)

p.write_text(s,encoding='utf-8')
assert 'Ranking de 5 anos' in s or 'Ranking 5 anos' in s
print('UI ranking 5 anos pronta')
