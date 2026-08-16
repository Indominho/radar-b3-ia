from pathlib import Path
p=Path('index.html');s=p.read_text(encoding='utf-8')
replacements={
'crescimento dos últimos seis meses':'crescimento dos últimos dois anos',
'Maior alta em 6 meses':'Maior alta em 2 anos',
"['6 meses',pct(x.momentum_6m)]":"['2 anos',pct(x.momentum_2y)]",
'<th>6 meses</th>':'<th>2 anos</th>',
'Principais apostas: crescimento forte em 6 meses':'Principais apostas: crescimento forte em 2 anos',
'altas de seis meses são um sinal de momentum':'altas de dois anos são um sinal de momentum',
'momentum_6m':'momentum_2y'
}
for old,new in replacements.items():s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
assert 'momentum_6m' not in s
assert '2 anos' in s
print('UI ajustada para apostas de 2 anos')
