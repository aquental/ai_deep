Segue um PRD focado nesse fluxo entre `StatusPanel`, LLM e `ConversationalPanel` no projeto hrns.

---

# PRD — Integração do fluxo de chat entre StatusPanel, LLM e ConversationalPanel

## Visão geral

Este documento define os requisitos de produto para o fluxo de envio de texto digitado no `StatusPanel` para a interface de chat do LLM e a exibição da resposta na janela `ConversationalPanel` da TUI do projeto `hrns`. O comportamento será disparado a partir da função `on_input_submitted` em `app.py`.

## Objetivo

Criar um fluxo claro, previsível e robusto em que:

- O texto digitado pelo usuário no `StatusPanel` é capturado em `on_input_submitted`.
- Esse texto é enviado para uma interface de chat com o LLM (cliente de API ou wrapper interno).
- A resposta retornada pelo LLM é exibida na janela `ConversationalPanel`.
- Erros de comunicação com o LLM são tratados e comunicados ao usuário de forma adequada.

## Problema

Sem um fluxo de integração bem definido entre input do usuário, chamada ao LLM e exibição da resposta, o sistema tende a ter comportamentos inconsistentes, como perda de mensagens, respostas fora de ordem ou erros silenciosos. Isso prejudica a experiência conversacional e dificulta o diagnóstico de problemas operacionais.

## Escopo

O escopo deste PRD abrange:

- Captura do texto submetido pelo usuário no `StatusPanel`.
- Chamada à interface de chat do LLM a partir de `on_input_submitted`.
- Recebimento e exibição da resposta na janela `ConversationalPanel`.
- Tratamento de erros básicos de chamada ao LLM.

Fora de escopo:

- Escolha do provedor de LLM.
- Detalhes de autenticação e configuração de credenciais.
- Persistência de histórico de conversa em armazenamento externo.
- Fluxos de ferramentas, funções e chamadas avançadas do LLM.

## Usuários-alvo

- Usuários técnicos que interagem com o `hrns` pelo terminal.
- Desenvolvedores que utilizam o `hrns` como harness conversacional sobre um LLM.

## Requisitos funcionais

### RF1. Capturar texto submetido no StatusPanel

Quando o usuário digitar texto na janela `StatusPanel` e confirmar (por exemplo, tecla Enter), a função `on_input_submitted` em `app.py` deve receber o conteúdo submetido.

### RF2. Enviar texto ao LLM

A partir de `on_input_submitted`, o sistema deve enviar o texto capturado para uma interface de chat do LLM, usando um cliente ou serviço dedicado (por exemplo, `ChatService` ou `llm_client.chat(...)`).

- A chamada deve ser preferencialmente assíncrona para não bloquear a UI.
- O texto submetido deve ser incluído no contexto da conversa corrente.

### RF3. Exibir prompt do usuário no ConversationalPanel

Opcionalmente, antes ou junto com a resposta, o texto digitado pelo usuário pode ser acrescentado ao `ConversationalPanel`, para manter o histórico de turno visível (por exemplo, prefixado com `> `).

### RF4. Receber resposta do LLM

O sistema deve aguardar a resposta do LLM. Quando a resposta for recebida com sucesso, o conteúdo textual retornado deve ser preparado para exibição (por exemplo, limpeza de quebras de linha, truncamento opcional).

### RF5. Atualizar a janela ConversationalPanel

A resposta do LLM deve ser exibida na janela `ConversationalPanel`, preservando qualquer conteúdo anterior (historicamente, as novas mensagens são acrescidas ao final).

- A atualização deve ser feita via método público do widget, por exemplo:  
  `conversational_panel.append_message(response_text)`.

### RF6. Tratar erros de comunicação com o LLM

Se ocorrer erro de comunicação (timeout, erro de rede, resposta inválida):

- O sistema não deve quebrar a UI.
- Uma mensagem de erro amigável deve ser exibida, preferencialmente na própria `ConversationalPanel` ou no `StatusPanel` (ex.: “Falha ao contatar o LLM. Tente novamente.”).
- Logs adequados devem ser emitidos pelo módulo de logging (quando disponível).

### RF7. Limpar ou resetar input no StatusPanel

Após o envio bem-sucedido do texto para o LLM (evento `on_input_submitted`), o campo de input do `StatusPanel` deve ser limpo para permitir nova entrada.

### RF8. Suporte a múltiplos turnos de conversa

O fluxo deve suportar múltiplas interações consecutivas:

1. Usuário digita texto no `StatusPanel`.
2. Texto é enviado ao LLM.
3. Resposta é exibida no `ConversationalPanel`.
4. Usuário digita outro texto, mantendo o contexto de conversa conforme implementação da interface de chat.

## Requisitos não funcionais

### RNF1. Responsividade

A chamada ao LLM não deve bloquear a UI; a interface deve permanecer responsiva enquanto a resposta é processada (por exemplo, uso de `await`/corrotinas do Textual).

### RNF2. Observabilidade

Erros de comunicação e tempos de resposta anormais devem ser logados para diagnóstico.

### RNF3. Simplicidade de integração

A lógica de integração entre `StatusPanel`, LLM e `ConversationalPanel` deve ficar centralizada, preferencialmente em `app.py` ou em um serviço único de orquestração, para facilitar manutenção.

## Fluxo esperado

1. Usuário digita uma mensagem na janela `StatusPanel`.
2. Usuário confirma o envio (Enter).
3. `StatusPanel` emite evento capturado por `on_input_submitted` em `app.py`.
4. `on_input_submitted`:
   - lê o texto digitado,
   - opcionalmente adiciona o texto do usuário ao `ConversationalPanel`,
   - chama a interface de chat do LLM com a mensagem.
5. O LLM processa e retorna uma resposta.
6. `app.py` recebe a resposta e chama um método no `ConversationalPanel` para exibir o texto.
7. Em caso de erro, uma mensagem apropriada é exibida na UI e o erro é logado.
8. O campo de input do `StatusPanel` é limpo para a próxima interação.

## Interfaces sugeridas

### Assinatura de `on_input_submitted` em app.py

```python
async def on_input_submitted(self, message: str) -> None:
    ...
```

### Serviço de chat com LLM

```python
class ChatService:
    async def send(self, user_message: str) -> str:
        """Envia a mensagem do usuário ao LLM e retorna o texto da resposta."""
        ...
```

Uso em `app.py`:

```python
response = await chat_service.send(message)
self.conversational_panel.append_message(response)
```

### API do ConversationalPanel

```python
class ConversationalPanel(...):
    def append_message(self, text: str, role: str = "assistant") -> None:
        """Acrescenta uma mensagem ao painel, preservando o histórico."""
        ...
```

## Critérios de aceitação

- Ao digitar texto no `StatusPanel` e pressionar Enter, `on_input_submitted` é acionado com o texto correto.
- O texto é enviado ao LLM via interface de chat sem bloquear a UI.
- Em caso de resposta bem-sucedida, o texto retornado é exibido na janela `ConversationalPanel`.
- Em caso de erro na chamada ao LLM, uma mensagem de erro amigável é exibida e o sistema continua operando.
- O campo de input do `StatusPanel` é limpo após o envio.
- Múltiplos turnos de conversa funcionam sem perda de contexto na UI (histórico visível no `ConversationalPanel`).

## Métricas de sucesso

- Latência percebida pelo usuário aceitável para respostas do LLM.
- Baixa taxa de erros não tratados em chamadas ao LLM.
- Clareza de uso: o usuário entende que deve digitar na janela `StatusPanel` e ver a resposta em `ConversationalPanel`.

Se quiser, posso agora transformar este PRD em um arquivo `.md` pronto para o repositório ou já sugerir um esqueleto de código para `on_input_submitted` e a `ChatService`.

Sources
