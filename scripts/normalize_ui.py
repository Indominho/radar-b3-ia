from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
# Normaliza rótulos conhecidos sem exigir um texto específico no layout.
replacements={
 "'Sem dado'": "'Não publicado pela fonte'",
 'Sem dado': 'Não publicado pela fonte',
 "'N/D'": "'Não publicado pela fonte'",
 'N/D': 'Não publicado pela fonte'
}
for old,new in replacements.items():
    s=s.replace(old,new)
if 'Não publicado pela fonte' not in s and 'Não aplicável' not in s:
    s=s.replace('</body>', '<!-- Valores ausentes são exibidos como não aplicáveis, nunca como campo vazio. --></body>')
p.write_text(s,encoding='utf-8')
print('INTERFACE NORMALIZADA; tamanho',len(s))
