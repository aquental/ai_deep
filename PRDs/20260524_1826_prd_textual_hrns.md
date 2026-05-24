# PRD — Integração do Textual ao projeto hrns

## Visão geral

Este documento define os requisitos de produto para adicionar uma interface TUI baseada em Textual ao projeto `hrns`. A interface deve ocupar todo o terminal e organizar a aplicação em quatro janelas funcionais: conversacional, status, tarefas e trabalho.

A proposta busca oferecer uma experiência interativa de terminal com melhor separação visual das áreas do sistema, facilitando a operação, o acompanhamento do estado corrente e a visualização das respostas geradas.

## Objetivo

Implementar uma interface Textual para o projeto `hrns` que:

- Use todo o espaço disponível do terminal.
- Organize a tela em quatro janelas fixas.
- Valide o tamanho mínimo do terminal antes da execução.
- Capture a entrada do usuário pela janela `status`.
- Exiba a saída conversacional na janela `conversacional`.
- Reserve áreas específicas para exibição de tarefas e trabalho.

## Problema

Uma interface baseada apenas em terminal linear dificulta o acompanhamento simultâneo de entrada, saída, estado e execução de tarefas. Em um sistema com características conversacionais e operacionais, a ausência de áreas dedicadas reduz a clareza, prejudica a ergonomia e dificulta a visualização contínua do contexto de execução.

## Escopo

A implementação deve introduzir uma TUI com Textual para o projeto `hrns`, com layout dividido em quatro regiões e comportamento mínimo de entrada e saída.

Inclui:

- Inicialização de aplicação com Textual
- Verificação de altura mínima do terminal antes da execução
- Encerramento controlado caso o terminal tenha menos de 20 linhas
- Layout com quatro janelas ocupando 100% do terminal
- Entrada do usuário via janela `status`
- Exibição da saída da conversa na janela `conversacional`
- Áreas dedicadas para `tarefas` e `trabalho`

Não inclui:

- Persistência de histórico de conversa
- Motor conversacional interno
- Execução real de tarefas
- Gerenciamento avançado de redimensionamento além das regras básicas de layout
- Temas complexos ou personalização visual avançada

## Usuários-alvo

- Desenvolvedores operando o projeto `hrns` no terminal
- Usuários técnicos que precisam acompanhar conversa, status e execução em uma única tela

## Requisitos funcionais

### RF1. Inicializar a interface Textual

O sistema deve iniciar uma aplicação TUI baseada em Textual como interface principal do projeto `hrns`.

### RF2. Validar tamanho mínimo do terminal

Antes de iniciar a interface principal, o sistema deve verificar a altura do terminal. Se o terminal tiver menos de 20 linhas, o sistema deve exibir uma mensagem informando que não é possível executar a interface e encerrar a aplicação.

Mensagem de referência:

```text
Não é possível iniciar o hrns: o terminal precisa ter pelo menos 20 linhas.
```

### RF3. Ocupar todo o terminal

A interface deve ocupar 100% da área disponível do terminal durante a execução.

### RF4. Exibir quatro janelas fixas

A interface deve conter exatamente quatro janelas visíveis:

1. `conversacional`
2. `status`
3. `tarefas`
4. `trabalho`

### RF5. Respeitar o layout proporcional definido

As janelas devem seguir a distribuição abaixo:

- `conversacional`: 70% da largura e 70% da altura, posicionada no lado esquerdo superior
- `status`: 70% da largura e 30% da altura, posicionada abaixo da janela `conversacional`
- `tarefas`: 30% da largura e 50% da altura, posicionada no topo direito
- `trabalho`: 30% da largura e 50% da altura, posicionada abaixo da janela `tarefas`

### RF6. Capturar input na janela `status`

A janela `status` deve conter o campo de entrada principal do usuário. O sistema deve ler o input digitado nessa área.

### RF7. Exibir a saída da conversa na janela `conversacional`

Toda saída conversacional gerada pelo sistema deve ser exibida na janela `conversacional`.

### RF8. Reservar área de tarefas

A janela `tarefas` deve ser reservada para visualização de tarefas, fila, passos correntes ou informações equivalentes relacionadas à execução.

### RF9. Reservar área de trabalho

A janela `trabalho` deve ser reservada para exibição de informações de trabalho em andamento, logs operacionais, detalhes da execução ou contexto técnico complementar.

### RF10. Encerrar com segurança

Caso a validação de tamanho mínimo falhe, o sistema deve encerrar sem iniciar a interface parcial e sem deixar o terminal em estado inconsistente.

## Requisitos não funcionais

### RNF1. Clareza visual

As quatro janelas devem ser visualmente distintas, com bordas, títulos ou outras pistas visuais claras.

### RNF2. Responsividade básica

A interface deve manter a proporção funcional entre as janelas quando o terminal tiver dimensão suficiente, respeitando o layout proposto.

### RNF3. Robustez

A aplicação não deve iniciar em condições mínimas inválidas, evitando renderização quebrada ou sobreposição ilegível.

### RNF4. Manutenibilidade

A implementação deve organizar o layout e a lógica de widgets de forma modular para facilitar evolução futura.

### RNF5. Compatibilidade

A solução deve ser compatível com Python moderno e com o ecossistema Textual suportado pelo projeto.

## Fluxo esperado

1. O usuário inicia o projeto `hrns` em modo TUI.
2. O sistema verifica a altura do terminal.
3. Se a altura for menor que 20 linhas, o sistema informa a limitação e encerra.
4. Se a altura for válida, a interface Textual é carregada.
5. As quatro janelas são renderizadas ocupando todo o terminal.
6. O usuário digita comandos ou mensagens na janela `status`.
7. O sistema processa o input.
8. A resposta conversacional é exibida na janela `conversacional`.
9. As janelas `tarefas` e `trabalho` exibem informações auxiliares do sistema.

## Layout esperado

```text
┌───────────────────────────────────────────────┬───────────────────────┐
│                                               │       tarefas         │
│               conversacional                  │                       │
│                 70% x 70%                     │       30% x 50%       │
│                                               │                       │
├───────────────────────────────────────────────┼───────────────────────┤
│                  status                       │       trabalho        │
│                 70% x 30%                     │       30% x 50%       │
│                                               │                       │
└───────────────────────────────────────────────┴───────────────────────┘
```

## Estrutura sugerida

```text
hrns/
├── tui/
│   ├── app.py
│   ├── layout.py
│   ├── widgets/
│   │   ├── conversational.py
│   │   ├── status.py
│   │   ├── tasks.py
│   │   └── work.py
│   └── styles.tcss
```

## Componentes sugeridos

- `HrnsApp`: classe principal da aplicação Textual
- `ConversationalPanel`: widget para exibir a conversa
- `StatusPanel`: widget com input do usuário
- `TasksPanel`: widget para listar tarefas
- `WorkPanel`: widget para mostrar execução ou contexto técnico

## Assinatura e comportamento sugeridos

```python
def run_tui() -> None:
    ...
```

Comportamento esperado:

- validar tamanho mínimo do terminal antes de abrir a aplicação
- iniciar a app Textual se o terminal for compatível
- encerrar com mensagem amigável se o terminal for incompatível

## Critérios de aceitação

- O sistema deve impedir a execução da interface quando o terminal tiver menos de 20 linhas.
- A mensagem de erro deve ser clara e suficiente para indicar o motivo do encerramento.
- A interface deve abrir ocupando todo o terminal.
- A janela `conversacional` deve ocupar 70% da largura e 70% da altura da área total.
- A janela `status` deve ficar abaixo da `conversacional`, com 70% da largura e 30% da altura.
- A janela `tarefas` deve ocupar o topo direito, com 30% da largura e 50% da altura.
- A janela `trabalho` deve ficar abaixo da `tarefas`, com 30% da largura e 50% da altura.
- O input principal deve ser digitado na janela `status`.
- A saída da conversa deve aparecer na janela `conversacional`.
- As quatro janelas devem estar visíveis simultaneamente.

## Exemplo de abordagem de implementação

```python
from shutil import get_terminal_size

MIN_TERMINAL_LINES = 20


def validate_terminal_size() -> None:
    size = get_terminal_size()
    if size.lines < MIN_TERMINAL_LINES:
        print("Não é possível iniciar o hrns: o terminal precisa ter pelo menos 20 linhas.")
        raise SystemExit(1)


def run_tui() -> None:
    validate_terminal_size()
    # iniciar aplicação Textual
```

## Diretrizes de layout no Textual

A implementação deve utilizar containers horizontais e verticais para reproduzir o grid proposto:

- coluna esquerda com `conversacional` acima de `status`
- coluna direita com `tarefas` acima de `trabalho`
- proporção horizontal entre colunas: 70 / 30
- proporção vertical na esquerda: 70 / 30
- proporção vertical na direita: 50 / 50

## Métricas de sucesso

- Melhor leitura simultânea de conversa, entrada e estado operacional
- Redução de confusão visual durante uso do `hrns`
- Melhoria na ergonomia da operação em terminal
- Base preparada para evolução futura da TUI

## Evoluções futuras

Possíveis extensões futuras:

- Histórico navegável na janela conversacional
- Atualização em tempo real da lista de tarefas
- Logs detalhados e estruturados na janela trabalho
- Suporte a atalhos de teclado entre painéis
- Temas visuais e configuração de layout
