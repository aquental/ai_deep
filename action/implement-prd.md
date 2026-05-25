## Arquivos

- **ARQUIVO**: `./PRDs/20260524_2102_prd_frontmatter_skills_hrns.md`
  — o PRD cujas mudanças devem ser implementadas.
- **CHANGELOG**: `./PRDs/CHANGELOG.md` — índice de PRDs e registro de
  implementação. Todas as edições de status e registro acontecem AQUI,
  nunca no ARQUIVO.

## Contexto do CHANGELOG

O CHANGELOG tem duas partes:

- Uma lista de PRDs com checkboxes. Checkbox marcado = status "Implementado";
  checkbox vazio = status "Pendente".
- Uma seção "Parte 2 — Registro de implementação", com uma subseção por PRD
  (formato `### <nome-do-arquivo>` e subitens) descrevendo o que foi feito.

## Tarefa

1. Implemente as mudanças descritas no ARQUIVO.

2. Adicione testes que validem a implementação. A suíte deve cobrir:
   - **Casos comuns**: entradas válidas e o fluxo principal de uso.
   - **Casos extremos** (no mínimo): entradas vazias ou nulas, valores nos
     limites (mínimo/máximo), entradas inválidas ou malformadas, condições
     de erro, e coleções com zero, um e muitos elementos.
     Se algum desses casos não estiver coberto, crie os testes faltantes.

3. Rode a suíte completa de testes.

## Se — e somente se — todos os testes passarem

No arquivo CHANGELOG:

1. Marque o checkbox correspondente ao ARQUIVO na lista de PRDs
   (status passa a "Implementado").
2. Na "Parte 2 — Registro de implementação", localize a subseção do ARQUIVO.
   Se ela não existir, crie-a seguindo o formato das subseções anteriores
   (`### <nome-do-arquivo>` e seus subitens).
3. Preencha essa subseção com o registro do que foi feito: mudanças
   implementadas, testes adicionados e quais casos (comuns/extremos) foram
   cobertos.

## Se algum teste falhar

Não altere o CHANGELOG. Relate quais testes falharam e por quê.
