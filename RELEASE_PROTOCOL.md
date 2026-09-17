# Protocolo automático de release

## Objetivo
Nenhuma correção é considerada pronta até passar por cobertura, QA funcional e publicação verificável.

## Ordem obrigatória
1. **Coverage Casey**: cruza cada ticker do catálogo com ranking e fontes; verifica campos, período, fórmula e URL.
2. **Filter Finch**: testa busca, ordenação, paginação, Top 10 de 5 anos, Top 10 de 10 anos e ficha individual; confirma que não há fallback entre períodos.
3. **Release Riley**: compara branch, `VERSION.json`, `index.html`, `ranking.json`, `catalog.json` e site Pages ao vivo; confirma timestamps e conteúdo realmente publicado.

## Gate de publicação
O Release Ranger só libera a versão quando os três pareceres passarem. Se qualquer agente encontrar falha, a release fica bloqueada, a causa é registrada e a correção volta ao ciclo.

## Versionamento
Cada correção aprovada incrementa a versão patch em `VERSION.json` e registra escopo, commit, testes e status do Pages.

## Limite operacional
O ClickUp não fornece um gatilho nativo para iniciar agentes automaticamente a cada edição feita pelo Brain. O Ranger roda de hora em hora e pode ser acionado imediatamente por DM ou @menção; o protocolo deve ser seguido pelo Brain ao final de cada correção.
