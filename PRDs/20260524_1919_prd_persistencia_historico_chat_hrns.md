# PRD - Persistencia de historico de chat com SQLite para o hrns

## Visao geral

Este documento define os requisitos de produto para implementar persistencia de historico de chat no projeto `hrns` usando SQLite. O sistema deve salvar automaticamente a mensagem do usuario e a resposta do LLM, e recarregar o historico ao iniciar a interface para que o `ConversationalPanel` nao comece vazio.

## Objetivo

Implementar um sistema de persistencia que:

- Salve sempre a mensagem do usuario e a resposta do LLM.
- Recarregue o historico ao iniciar a interface TUI.
- Garanta que o `ConversationalPanel` seja preenchido com o historico salvo.
- Use SQLite como armazenamento persistente.
- Seja simples, confiavel e reutilizavel por outros componentes do projeto.

## Problema

Sem persistencia, cada nova sessao do `hrns` comeca do zero, perdendo todo o historico de conversas anteriores. Isso prejudica a continuidade do trabalho, dificulta a revisao de decisoes e conversas passadas, e reduz a utilidade do sistema como assistente conversacional de longo prazo.

## Escopo

O sistema deve persistir historico de chat do projeto `hrns` usando SQLite.

Inclui:

- Criacao de banco de dados SQLite com tabela de mensagens
- Salvamento automatico da mensagem do usuario ao enviar
- Salvamento automatico da resposta do LLM ao receber
- Carregamento do historico ao iniciar a interface TUI
- Preenchimento do `ConversationalPanel` com mensagens salvas
- Suporte a multiplas conversas (opcional, via `conversation_id`)
- Consulta de historico por conversao por data

Nao inclui:

- Interface grafica para visualizacao de historico antigo
- Ferramentas de busca avanada ou filtragem complexa
- Sincronizacao com sistemas externos
- Criptografia ou protecao especial de dados sensiveis

## Usuarios-alvo

- Desenvolvedores operando o projeto `hrns` no terminal
- Usarios tecnicos que precisam de continuidade entre sessoes
- Qualquer pessoa que use o `hrns` como assistente conversacional

## Requisitos funcionais

### RF1. Criar banco de dados SQLite

O sistema deve criar um banco de dados SQLite em arquivo local, preferencialmente em `.hrns/chat_history.db`, com tabela de mensagens.

### RF2. Estrutura da tabela de mensagens

A tabela de mensagens deve conter pelo menos:

- `id` (inteiro, chave primaria, auto-incremento)
- `conversation_id` (texto, identificador da conversa)
- `role` (texto, "user" ou "assistant")
- `content` (texto, conteudo da mensagem)
- `timestamp` (texto ou datetime, data/hora da mensagem)

### RF3. Salvar mensagem do usuario

Sempre que o usuario enviar uma mensagem no `StatusPanel`, o sistema deve salvar imediatamente no banco de dados com `role="user"`.

### RF4. Salvar resposta do LLM

Sempre que o LLM retornar uma resposta, o sistema deve salvar imediatamente no banco de dados com `role="assistant"`.

### RF5. Recarregar historico ao iniciar

Ao iniciar a interface TUI, o sistema deve carregar o historico salvo do banco de dados antes de renderizar a interface.

### RF6. Prevenir ConversationalPanel vazio

Ao carregar o historico, o sistema deve preencher o `ConversationalPanel` com todas as mensagens salvas, garantindo que a janela nao comece vazia.

### RF7. Suportar multiplas conversas de conversa

O sistema deve suportar conversas com multiplas conversas, mantendo a ordem cronologica das mensagens.

### RF8. Consultar historico por conversa

O sistema deve permitir consultar mensagens filtradas por `conversation_id`, permitindo futuras implementacoes de multiplas conversas.

### RF9. Tratar erros de banco de dados

Se houver erro ao criar ou acessar o banco de dados, o sistema deve:

- Exibir mensagem de erro amigavel
- Logar o erro detalhadamente
- Nao quebrar a interface TUI
- Preferencialmente permitir uso limitado sem persistencia

## Requisitos nao funcionais

### RNF1. Simplicidade

A implementacao deve usar apenas `sqlite3` da biblioteca padrao do Python, sem dependencias externas.

### RNF2. Desempenho

Operacoes de salvamento e carregamento nao devem causar bloqueio perceptivel na interface TUI.

### RNF3. Confiabilidade

Dados devem ser persistidos corretamente mesmo em caso de fechamento inesperado da aplicacao.

### RNF4. Ordenacao temporal

As mensagens devem ser recuperadas na ordem cronologica correta (timestamp crescente).

### RNF5. Manutenibilidade

O codigo de persistencia deve ser modular, documentado e facil de manter.

## Fluxo esperado

### Ao iniciar a interface

1. O sistema inicia a aplicacao TUI do `hrns`.
2. O sistema carrega o historico do banco de dados SQLite.
3. O sistema popula o `ConversationalPanel` com as mensagens salvas.
4. A interface e exibida com o historico ja visivel.

### Ao enviar mensagem

1. O usuario digita texto no `StatusPanel` e pressiona Enter.
2. A funcao `on_input_submitted` em `app.py` e capturada o texto.
3. O sistema salva a mensagem do usuario com `role="user"` no banco de dados.
4. O sistema exibe a mensagem do usuario no `ConversationalPanel`.
5. O sistema envia a mensagem para a interface de chat do LLM.
6. O sistema recebe a resposta do LLM.
7. O sistema salva a resposta com `role="assistant"` no banco de dados.
8. O sistema exibe a resposta do LLM no `ConversationalPanel`.

## Estrutura do banco de dados

```sql
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL DEFAULT 'default',
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp);
```

## Interface de servico sugerida

```python
from typing import List, Dict
from pathlib import Path

DB_PATH = Path(".hrns") / "chat_history.db"


class ChatHistoryService:
    def __init__(self, db_path: Path = DB_PATH):
        '''Inicializa o servico de historico de chat.'''
        ...

    def save_message(self, conversation_id: str, role: str, content: str) -> None:
        '''Salva uma mensagem no banco de dados.'''
        ...

    def load_history(self, conversation_id: str = "default") -> List[Dict]:
        '''Carrega o historico de uma conversa, ordenado por timestamp.'''
        ...

    def get_latest_messages(self, conversation_id: str = "default", limit: int = 50) -> List[Dict]:
        '''Retorna as mensagens mais recentes de uma conversa.'''
        ...
```

## Assinatura de uso em app.py

```python
chat_history = ChatHistoryService()

# Ao iniciar
history = chat_history.load_history("default")
conversational_panel.populate(history)

# Ao enviar mensagem do usuario
chat_history.save_message("default", "user", user_message)

# Ao receber resposta do LLM
chat_history.save_message("default", "assistant", llm_response)
```

## Criterios de aceitacao

- O banco de dados SQLite deve ser criado automaticamente ao iniciar o sistema.
- A tabela de mensagens deve existir com os campos corretos.
- A mensagem do usuario deve ser salva imediatamente ao ser enviada.
- A resposta do LLM deve ser salva imediatamente ao ser recebida.
- Ao reiniciar a interface, o historico deve ser carregado do banco de dados.
- O `ConversationalPanel` deve ser preenchido com o historico salvo, nao iniciando vazio.
- As mensagens devem aparecer na ordem cronologica correta.
- O sistema nao deve quebrar se o banco de dados ja existir.
- O sistema deve tratar erros de banco de dados de forma elegante.

## Exemplo de implementacao esperada

```python
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict

DB_PATH = Path(".hrns") / "chat_history.db"


class ChatHistoryService:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        '''Cria o banco de dados e a tabela se nao existirem.'''
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL DEFAULT 'default',
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversation_id ON messages(conversation_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)")
        conn.commit()
        conn.close()

    def save_message(self, conversation_id: str, role: str, content: str) -> None:
        '''Salva uma mensagem no banco de dados.'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (conversation_id, role, content, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()

    def load_history(self, conversation_id: str = "default") -> List[Dict]:
        '''Carrega o historico de uma conversa, ordenado por timestamp.'''
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC",
            (conversation_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
```

## Revisao do documento

A revisao aplica as seguintes correcoes e melhorias:

- Garante que a mensagem do usuario e a resposta do LLM sejam sempre salvas.
- Garante que o historico seja recarregado ao iniciar a interface.
- Garante que o `ConversationalPanel` nao comece vazio.
- Usa SQLite como especificado, com estrutura clara e indices para consultas eficientes.
- Organiza o fluxo de forma modular e reutilizavel.

## Metricas de sucesso

- Governo de historico entre sessoes sem perda de dados
- Reducao do tempo de reconfiguracao entre sessoes
- Maior utilidade do sistema como assistente conversacional de longo prazo
- Melhoria na experiencia de uso do `hrns`

## Evolucoes futuras

Possiveis extensoes futuras:

- Suporte a multiplas conversas simultaneas (conversation_id dinamico)
- Interface para listar e recuperar conversas antigas
- Busca textual no historico de mensagens
- Exportacao de historico para JSON ou CSV
- Criptografia de dados sensiveis no banco de dados
- Limpeza automatica de historico antigo (retencao configuravel)
