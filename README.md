# Projeto: Agentic Harness

## Visão geral

Um _agentic harness_ é a camada de orquestração que transforma um modelo de linguagem — que isoladamente apenas prevê o próximo token — em um agente capaz de executar tarefas reais de forma autônoma.

O princípio central é o **loop agêntico**: o modelo raciocina sobre o estado atual, decide uma ação, o harness executa essa ação no ambiente, devolve o resultado, e o ciclo se repete até a tarefa estar concluída ou um critério de parada ser atingido. Tudo o que está em volta desse loop — segurança, contexto,
ferramentas, memória — é responsabilidade do harness.

Este documento define a arquitetura de um harness genérico, voltado a tarefas de programação e automação, mas extensível a outros domínios.

---

## 1. O loop de execução (núcleo)

É o coração do harness. Um laço que, a cada iteração:

1. Monta o prompt a partir do estado atual (instrução do usuário, histórico, contexto, memória).
2. Chama o modelo e recebe a resposta, com texto e/ou chamadas de ferramenta.
3. Se houver chamada de ferramenta, valida-a contra as políticas de segurança, executa, e captura o resultado (incluindo erros).
4. Devolve o resultado ao modelo como nova entrada.
5. Avalia critérios de parada: tarefa concluída, limite de iterações, limite de tokens/custo, erro irrecuperável ou pedido explícito de confirmação.

O loop precisa ser resiliente: _timeouts_ por ferramenta, _retry_ com _backoff_ em falhas transitórias, e captura estruturada de erros para que o modelo possa se auto-corrigir em vez de travar.

---

## 2. Skills (ferramentas e capacidades)

_Skills_ são as capacidades discretas que o agente pode invocar — o vocabulário de ações disponíveis. Cada skill deve ser uma unidade autocontida com:

- **Schema declarado**: nome, descrição, parâmetros tipados e valores de retorno. É isso que o modelo lê para decidir _quando_ e _como_ usar a skill; a descrição deve ser orientada ao _quando usar_, não só ao _o que faz_.
- **Implementação isolada**: a lógica de execução, sem efeitos colaterais ocultos.
- **Metadados de risco**: classificação do nível de permissão (ação livre, requer confirmação, proibida).

Skills típicas para programação: ler/escrever arquivos, executar comandos de shell, busca na web, busca semântica no código, execução de testes, interação com Git, chamadas a APIs externas via MCP (Model Context Protocol).

Dois padrões importantes:

- **Descoberta tardia (_lazy loading_)**: com dezenas de skills, colocar todos os schemas no prompt desperdiça contexto. Um mecanismo de busca de ferramentas carrega apenas os schemas relevantes para a tarefa atual.
- **Skills como pacotes de conhecimento**: além de funções executáveis, uma skill pode ser um conjunto de instruções/melhores práticas (ex.: um arquivo `SKILL.md`) que o agente lê antes de agir em um domínio específico.

---

## 3. Hooks (pontos de extensão do loop)

_Hooks_ são ganchos que interceptam o loop agêntico em momentos definidos, permitindo injetar comportamento sem alterar o núcleo. São o principal mecanismo de customização e governança.

Pontos de hook recomendados:

- **`pre-prompt`**: antes de montar o prompt — injetar contexto dinâmico ou políticas.
- **`pre-tool` / `post-tool`**: antes e depois de cada chamada de ferramenta — validação, _logging_, sanitização de entrada, transformação de saída.
- **`stop`**: quando o modelo sinaliza que terminou — verificar se a tarefa realmente foi concluída (rodar testes, checar _lint_) e, se não, reinjetar o agente no loop.
- **`on-error`**: ao capturar uma exceção — decide entre _retry_, escalar ao usuário ou abortar.
- **`pre-commit` / ações irreversíveis**: forçam confirmação do usuário antes de operações destrutivas.

Cada hook deve poder _modificar_, _bloquear_ ou _aprovar_ a ação em curso, e ser configurável por projeto (qual hook roda e em que ordem).

---

## 4. Context (gestão de contexto)

O modelo só "sabe" o que está na janela de contexto, que é finita e cara. Este subsistema decide o que entra no prompt a cada iteração. Componentes:

- **Prompt de sistema / instruções base**: identidade do agente, regras de comportamento, políticas de segurança.
- **Contexto da tarefa**: a instrução do usuário e o estado relevante do ambiente (arquivos abertos, estrutura do projeto, saídas recentes).
- **Histórico da conversa**: as iterações anteriores do loop. Como cresce sem limite, precisa de estratégia de gestão:
  - _Compactação_: resumir trechos antigos mantendo o essencial.
  - _Truncamento por relevância_: descartar resultados já consumidos.
  - _Recuperação sob demanda_: indexar o histórico e buscar só o relevante.
- **Orçamento de tokens**: rastrear o uso, priorizar o que cabe, degradar graciosamente perto do limite.

Regra prática: contexto é um recurso escasso a ser curado ativamente, não um depósito onde tudo é jogado.

---

## 5. Memória (persistência entre sessões)

Enquanto o _context_ vive dentro de uma execução, a _memória_ persiste entre sessões. Sem ela, o agente recomeça do zero toda vez. Camadas recomendadas:

- **Memória de trabalho**: o estado da tarefa atual (já no contexto).
- **Memória episódica**: registro de tarefas/sessões passadas — o que foi feito, o que funcionou, o que falhou.
- **Memória semântica / de conhecimento**: fatos duráveis sobre o usuário, o projeto ou o domínio (convenções de código, decisões de arquitetura, preferências). Tipicamente um _key-value store_ ou índice vetorial.
- **Memória procedural**: padrões de "como fazer" que o agente aprendeu — efetivamente skills emergentes.

Decisões de projeto importantes:

- **Escrita explícita vs. automática**: o agente decide o que guardar, ou o harness extrai memórias ao fim de cada sessão? (Podem coexistir.)
- **Recuperação**: por similaridade, por _tags_ ou por recência.
- **Higiene**: memórias conflitantes ou desatualizadas precisam de correção e expiração. Memória ruim é pior que ausência de memória.
- **Escopo e privacidade**: separar memória por projeto/usuário; permitir inspeção e remoção.

---

## 6. Componentes de suporte

Um harness de produção precisa, além dos quatro pilares:

- **Segurança e permissões**: classificação de ações em níveis (livre / requer confirmação / proibida), defesa contra _prompt injection_ vindo de conteúdo não confiável (resultados de ferramentas, páginas web), e _sandboxing_ da execução.
- **Observabilidade**: _logging_ estruturado de cada iteração, _tracing_ das chamadas de ferramenta, métricas de custo e latência.
- **Configuração**: um formato declarativo por projeto que define skills habilitadas, hooks ativos, limites e políticas.
- **Interface com o usuário**: pontos de _check-in_ — o agente pausa e pede confirmação em decisões de alto risco em vez de adivinhar.
- **Avaliação**: um _eval harness_ acoplado, para medir regressões de comportamento ao mudar prompts, modelos ou skills.

---

## Arquitetura em resumo

```
                        USUÁRIO
                           |
                    LOOP AGÊNTICO
       monta prompt -> chama modelo -> executa -> repete
       |          |          |          |          |
    SKILLS      HOOKS     CONTEXT     MEMÓRIA    SEGURANÇA
   ferramentas  ganchos   janela      persist.   + observ.
                do loop   curada      entre
                                      sessões
```

A divisão de responsabilidades é clara:

- **Skills** definem _o que_ o agente pode fazer.
- **Hooks** definem _como o loop se comporta_.
- **Context** governa _o que o modelo vê agora_.
- **Memória** governa _o que persiste no tempo_.

Os componentes de suporte garantem que tudo isso seja seguro, observável e
configurável.
