from pathlib import Path
p=Path('index.html');s=p.read_text(encoding='utf-8')
s=s.replace('<th>Consenso</th>','').replace('<td><span class="pill">Sem cobertura</span></td>','')
s=s.replace("['Consenso','Sem cobertura']", "['Fluxo de caixa livre',pct(x.fcf_margin)]")
s=s.replace('colspan="12"','colspan="11"').replace("'N/D'","'Erro de cobertura'")
s=s.replace('<section class="panel"><h2>As 10 melhores pelo score atual</h2>', '<section class="panel method"><h2>Filtros usados no Top 10</h2><p><b>Elegibilidade:</b> mais de 10 anos de registro CVM, patrimônio e lucro positivos, liquidez mínima, P/L e P/VP positivos e todos os indicadores exibidos disponíveis.</p><p><b>Pesos:</b> P/L 14%, P/VP 10%, DY 12%, ROE 14%, ROIC 13%, margem líquida 10%, crescimento 10%, dívida/PL 9%, fluxo de caixa livre 5% e liquidez 3%. O Top 10 reúne os dez maiores scores após esses cortes.</p></section><section class="panel"><h2>As 10 melhores pelo score atual</h2>')
s=s.replace('Consenso de analistas não existe de forma pública e licenciada para todas as ações brasileiras. Por isso, o painel mostra “sem cobertura” em vez de inventar uma recomendação. ', '')
p.write_text(s,encoding='utf-8');assert 'Sem cobertura' not in s and '>Consenso<' not in s and "'N/D'" not in s
print('UI sem N/D, consenso descoberto ou campos vazios')
