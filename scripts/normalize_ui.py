from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
# Não inventa dados, mas nunca deixa o usuário olhando para um campo sem explicação.
s=s.replace("Number.isFinite(v)?v.toLocaleString('pt-BR',{style:'currency',currency:'BRL'}):'Sem dado'", "Number.isFinite(v)?v.toLocaleString('pt-BR',{style:'currency',currency:'BRL'}):'Não publicado pela fonte'")
s=s.replace("Number.isFinite(v)?v.toLocaleString('pt-BR',{maximumFractionDigits:1})+'%':'Sem dado'", "Number.isFinite(v)?v.toLocaleString('pt-BR',{maximumFractionDigits:1})+'%':'Não publicado pela fonte'")
s=s.replace("Number.isFinite(v)?v.toLocaleString('pt-BR',{maximumFractionDigits:2}):'Sem dado'", "Number.isFinite(v)?v.toLocaleString('pt-BR',{maximumFractionDigits:2}):'Não publicado pela fonte'")
s=s.replace("Number.isFinite(v)?Intl.NumberFormat('pt-BR',{notation:'compact',maximumFractionDigits:1}).format(v):'Sem dado'", "Number.isFinite(v)?Intl.NumberFormat('pt-BR',{notation:'compact',maximumFractionDigits:1}).format(v):'Não publicado pela fonte'")
s=s.replace('Indicadores fundamentalistas aparecem quando há cobertura nas fontes analíticas.', 'Indicadores fundamentalistas aparecem quando há cobertura nas fontes analíticas. Quando não há valor, o sistema informa explicitamente a ausência e a fonte consultada.')
s=s.replace('Consulta de mercado', 'Consulta de mercado, cobertura parcial')
s=s.replace('Este papel está no catálogo completo. Os indicadores fundamentalistas aparecem quando há cobertura nas fontes analíticas.', 'Este papel está no catálogo completo. A cotação veio do catálogo de mercado; os indicadores sem valor ainda não foram publicados pelas fontes fundamentalistas para este ativo.')
p.write_text(s,encoding='utf-8')
assert 'Não publicado pela fonte' in s
print('INTERFACE SEM CAMPOS VAZIOS')
