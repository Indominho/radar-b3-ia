from pathlib import Path

p=Path('index.html'); s=p.read_text(encoding='utf-8')
# O layout atual já separa os cards no JavaScript; não falhar se o padrão antigo não existir.
if 'function card(x,i){' in s:
    s=s.replace('r.slice(0,50).map((x,i)=>card(x,i))','r.slice(0,50).map((x,i)=>card(x,i,true))')
    s=s.replace('top.map((x,i)=>card(x,i))','top.map((x,i)=>card(x,i,false))')
else:
    print('layout atual já está separado; nenhuma substituição necessária')
s=s.replace('Sem histórico anual suficiente.','Nenhuma ação possui histórico anual suficiente nesta atualização.')
p.write_text(s,encoding='utf-8')
print('UI CARD FIX PASS')
