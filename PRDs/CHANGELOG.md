# CHANGELOG — PRDs

> Mecanismo estilo migrations: cada PRD é uma migração. O checkbox controla se já foi aplicado.
> Arquivos ordenados do mais antigo para o mais recente (YYYYMMDD_hhmm).

---

## Parte 1 — Lista de PRDs

- [x] `20260524_1639_prd_estrutura_diretorios_revisado.md`
- [x] `20260524_1650_prd_modulo_logging_robusto.md`
- [x] `20260524_1710_prd_listagem_arquivos_diretorio_hrns.md`
- [x] `20260524_1826_prd_textual_hrns.md`
- [x] `20260524_1911_prd_chatStatusPanel.md`
- [x] `20260524_1919_prd_persistencia_historico_chat_hrns.md`
- [x] `20260524_2025_prd_bordas_abas_hrns.md`
- [x] `20260524_2041_prd_atalhos_abas_hrns.md`
- [x] `20260524_2102_prd_frontmatter_skills_hrns.md`

---

## Parte 2 — Registro de implementação

### `20260524_1639_prd_estrutura_diretorios_revisado.md`

**Descrição:** Módulo Python para criação da estrutura de diretórios `.hrns/` (skills, context, hooks).

**Status:** ✅ Implementado

#### **O que foi implementado:**

- Função `create_structure(base_path=BASE)` em `src/hrns/structure.py`
- Constantes `BASE = ".hrns"` e `REQUIRED_DIRS = ["skills", "context", "hooks"]`
- Criação idempotente: diretórios já existentes são preservados, não falha na reexecução
- Retorno estruturado com `base_path`, `created`, `existing`, `success`
- `__init__.py` exporta `create_structure`, `BASE` e `REQUIRED_DIRS`
- 7 testes cobrindo todos os critérios de aceitação (100% passando)

#### Implementação — Módulo src/hrns/structure.py:

- Função create_structure(base_path=".hrns") que cria .hrns/skills, .hrns/context,
  .hrns/hooks
- Idempotente — reexecução não falha e preserva diretórios/arquivos existentes
- Retorna {base_path, created, existing, success}
- **init**.py exporta create_structure, BASE, REQUIRED_DIRS

#### Testes — 7 cenários em tests/test_structure.py:

- Criação completa do zero
- Idempotência (2ª execução)
- Existência parcial
- Formato do retorno
- base_path customizado
- Preservação de conteúdo pré-existente
- Não cria diretórios fora do base_path

#### **Arquivos relacionados:**

- `src/hrns/__init__.py`
- `src/hrns/structure.py`
- `tests/test_structure.py`

---

### `20260524_1650_prd_modulo_logging_robusto.md`

**Descrição:** Módulo de logging robusto com configuração centralizada, saída em console/arquivo e rotação.

**Status:** ✅ Implementado

#### **O que foi implementado:**

- Função `configure_logging(...)` em `src/hrns/logging/config.py` com 7 parâmetros
- Função `get_logger(name)` em `src/hrns/logging/logger.py` — fábrica de loggers nomeados
- `StdFormatter` em `src/hrns/logging/formatter.py` — formato `timestamp | level | name | mensagem`
- Suporte a console (StreamHandler) e arquivo (RotatingFileHandler com rotação por tamanho)
- Criação automática do diretório de logs
- Flag `_CONFIGURED` previne duplicação de handlers em chamadas repetidas
- `__init__.py` exporta `configure_logging` e `get_logger`
- 13 testes cobrindo todos os critérios de aceitação (100% passando)

#### Implementação — Módulo src/hrns/logging/:

- `config.py` — configure_logging(level, log_to_console, log_to_file, log_dir, file_name, max_bytes, backup_count)
- `logger.py` — get_logger(name) retorna logging.Logger nomeado
- `formatter.py` — StdFormatter com formato pipe-delimited (timestamp | LEVEL | name | message)
- `__init__.py` — exporta configure_logging, get_logger

#### Testes — 13 cenários em tests/test_logging.py:

- Configuração de console com uma chamada
- Configuração de arquivo com rotação
- Formato padronizado (regex validation)
- Logger nomeado
- Prevenção de duplicação de handlers
- Prevenção de duplicidade em múltiplas chamadas
- Múltiplas execuções no mesmo processo
- Registro de exceção com stack trace
- Criação automática do diretório de logs
- Suporte a todos os níveis (DEBUG a CRITICAL)
- Nível configurável
- Gravação efetiva em arquivo
- Importação pública

#### **Arquivos relacionados:**

- `src/hrns/logging/__init__.py`
- `src/hrns/logging/config.py`
- `src/hrns/logging/logger.py`
- `src/hrns/logging/formatter.py`
- `tests/test_logging.py`

---

### `20260524_1710_prd_listagem_arquivos_diretorio_hrns.md`

**Descrição:** Função genérica `list_files(directory)` para listar arquivos dos diretórios de configuração `.hrns/skills`, `.hrns/hooks` e `.hrns/contexts`.

**Status:** ✅ Implementado

#### **O que foi implementado:**

- Função `list_files(directory)` em `src/hrns/discovery.py` — listagem genérica de arquivos
- Retorna apenas arquivos regulares, ignorando subdiretórios
- Ordenação determinística via `sorted()`
- `FileNotFoundError` para diretórios inexistentes, `NotADirectoryError` para caminhos que não são diretórios
- Lista vazia para diretórios sem arquivos
- Integrado ao `__init__.py` do pacote `hrns`
- 11 testes cobrindo todos os critérios de aceitação (100% passando)

#### Implementação — Módulo src/hrns/discovery.py:

- `list_files(directory: str) -> list[str]` usando `pathlib.Path`
- Validação de existência e tipo do caminho
- Filtragem com `item.is_file()`, ordenação com `sorted()`

#### Testes — 11 cenários em tests/test_discovery.py:

- Listagem de .hrns/skills, .hrns/hooks, .hrns/contexts
- Filtragem de subdiretórios
- Diretório vazio retorna lista vazia
- Diretório inexistente lança FileNotFoundError
- Caminho não-diretório lança NotADirectoryError
- Ordenação determinística entre execuções
- Diretório apenas com subdiretórios retorna vazio
- Retorno tipado como lista de strings ordenadas
- Importação pública

#### **Arquivos relacionados:**

- `src/hrns/discovery.py`
- `src/hrns/__init__.py` (atualizado)
- `tests/test_discovery.py`

---

### `20260524_1826_prd_textual_hrns.md`

**Descrição:** Interface TUI baseada em Textual com layout de quatro janelas fixas (conversacional, status, tarefas, trabalho).

**Status:** ✅ Implementado

#### O que foi implementado:

- Adição da dependência `textual>=2.0.0` em `pyproject.toml`
- Função `validate_terminal_size()` em `src/hrns/tui/validate.py` — valida altura mínima de 20 linhas
- Função `run_tui()` — entry point que valida o terminal e lança a aplicação Textual
- `HrnsApp` em `src/hrns/tui/app.py` — aplicação principal com layout CSS em grade
- Quatro painéis modulares em `src/hrns/tui/widgets/`:
  - `ConversationalPanel` — painel `RichLog` para exibição de conversa (70% largura × 70% altura)
  - `StatusPanel` — painel com campo `Input` para entrada do usuário (70% largura × 30% altura)
  - `TasksPanel` — painel reservado para tarefas (30% largura × 50% altura)
  - `WorkPanel` — painel reservado para logs e contexto (30% largura × 50% altura)
- Layout proporcional: coluna esquerda (70/30 vertical), coluna direita (50/50 vertical), divisão horizontal (70/30)
- Bordas com títulos em cada painel para distinção visual
- Submissão de input: texto digitado no `StatusPanel` é exibido no `ConversationalPanel`
- Atalho `Ctrl+Q` para sair da aplicação
- `__init__.py` do módulo `hrns.tui` exporta `run_tui`
- 13 testes em `tests/test_tui.py` cobrindo validação de terminal, widgets e composição

#### Implementação — Módulo src/hrns/tui/:

- `validate.py` — `validate_terminal_size()`, `run_tui()`, constante `MIN_TERMINAL_LINES = 20`
- `app.py` — `HrnsApp(App)` com CSS inline definindo layout horizontal/vertical com `fr` units
- `widgets/conversational.py` — `ConversationalPanel(RichLog)` com `BORDER_TITLE = "Conversacional"`
- `widgets/status.py` — `StatusPanel(Static)` com composição de `Input` (`id="status-input"`)
- `widgets/tasks.py` — `TasksPanel(Static)` com `BORDER_TITLE = "Tarefas"`
- `widgets/work.py` — `WorkPanel(Static)` com `BORDER_TITLE = "Trabalho"`
- `widgets/__init__.py` — exporta todos os painéis
- `__init__.py` — exporta `run_tui`

#### Testes — 13 cenários em tests/test_tui.py:

- Terminal acima do mínimo não levanta exceção
- Terminal no mínimo não levanta exceção
- Terminal abaixo do mínimo levanta `SystemExit(1)`
- Mensagem de erro é exibida quando terminal é pequeno demais
- Constante `MIN_TERMINAL_LINES` é 20
- `ConversationalPanel` instancia com título correto
- `StatusPanel` instancia com título correto
- `TasksPanel` instancia com título correto
- `WorkPanel` instancia com título correto
- `HrnsApp` instancia sem erro
- `HrnsApp.compose()` produz widgets
- `HrnsApp` possui binding `ctrl+q`
- CSS contém proporções `7fr` / `3fr`
- `run_tui()` valida terminal antes de lançar app

#### Arquivos relacionados:

- `pyproject.toml` (atualizado com `textual>=2.0.0`)
- `src/hrns/tui/__init__.py`
- `src/hrns/tui/app.py`
- `src/hrns/tui/validate.py`
- `src/hrns/tui/widgets/__init__.py`
- `src/hrns/tui/widgets/conversational.py`
- `src/hrns/tui/widgets/status.py`
- `src/hrns/tui/widgets/tasks.py`
- `src/hrns/tui/widgets/work.py`
- `tests/test_tui.py`

#### Critérios de aceitação atendidos:

- ✅ Impede execução com terminal < 20 linhas
- ✅ Mensagem de erro clara
- ✅ Interface ocupa 100% do terminal
- ✅ `conversacional`: 70% largura × 70% altura
- ✅ `status`: 70% largura × 30% altura, abaixo do conversacional
- ✅ `tarefas`: 30% largura × 50% altura, topo direito
- ✅ `trabalho`: 30% largura × 50% altura, abaixo de tarefas
- ✅ Input principal no painel `status`
- ✅ Saída da conversa no painel `conversacional`
- ✅ Quatro janelas visíveis simultaneamente

---

### `20260524_1911_prd_chatStatusPanel.md`

**Descrição:** Integração do fluxo de chat entre StatusPanel, LLM e ConversationalPanel com chamada assíncrona à API do DeepSeek.

**Status:** ✅ Implementado

#### O que foi implementado:

- `ChatService` em `src/hrns/chat.py` — wrapper assíncrono sobre a API do DeepSeek usando `AsyncOpenAI`
- Histórico de conversa em memória com mensagens `user`/`assistant` preservadas entre turnos
- Histórico só é atualizado em caso de sucesso na chamada à API (fail-safe)
- Método `append_message(text, role)` no `ConversationalPanel` — formata mensagens com prefixo `> ` para `user`
- `on_input_submitted` em `app.py` tornado assíncrono (`async def`) para não bloquear a UI
- Tratamento de erros: API key ausente, falha de rede, resposta vazia — todos exibidos no painel conversacional
- Logging de erros via `logging.getLogger("hrns.chat")` para observabilidade
- Input do StatusPanel limpo imediatamente após envio, mantendo a UI responsiva
- Suporte a múltiplos turnos de conversa com contexto preservado

#### Implementação — Módulo src/hrns/chat.py:

- `ChatService.__init__` — carrega `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL` do ambiente
- `ChatService.client` — property lazy que inicializa `AsyncOpenAI`
- `ChatService.history` — property que retorna cópia rasa do histórico
- `ChatService.send(user_message)` — método async que constrói mensagens, chama a API, persiste histórico em sucesso ou retorna string de erro em falha
- `load_dotenv(override=False)` no nível do módulo para carregar `.env`

#### Alterações em src/hrns/tui/app.py:

- `on_input_submitted` convertido para `async def`
- Instanciação de `ChatService` em `on_mount`
- Uso de `conversational.append_message(user_text, role="user")` para eco do usuário
- `await self.chat_service.send(user_text)` para chamada não-bloqueante ao LLM
- Resposta (ou erro) exibida via `conversational.append_message(response)`

#### Alterações em src/hrns/tui/widgets/conversational.py:

- Método `append_message(self, text, role="assistant")` adicionado
- Role `"user"` prefixed com `> `; role `"assistant"` exibido diretamente

#### Arquivos relacionados:

- `src/hrns/chat.py` (novo)
- `src/hrns/tui/app.py` (modificado)
- `src/hrns/tui/widgets/conversational.py` (modificado)

#### Critérios de aceitação atendidos:

- ✅ Texto do StatusPanel capturado em `on_input_submitted`
- ✅ Texto enviado ao LLM via ChatService assíncrono sem bloquear UI
- ✅ Resposta do LLM exibida no ConversationalPanel
- ✅ Erro de comunicação tratado e exibido como mensagem amigável
- ✅ Campo de input limpo após envio
- ✅ Múltiplos turnos de conversa funcionam com contexto preservado
- ✅ Logs de erro emitidos para diagnóstico

---

### `20260524_1919_prd_persistencia_historico_chat_hrns.md`

**Descrição:** Persistência de histórico de chat com SQLite — salvamento automático de mensagens do usuário e respostas do LLM, com recarregamento ao iniciar a TUI.

**Status:** ✅ Implementado

#### O que foi implementado:

- `ChatHistoryService` em `src/hrns/chat_history.py` — persistência SQLite usando apenas `sqlite3` da biblioteca padrão
- Banco de dados em `.hrns/chat_history.db` com tabela `messages` (id, conversation_id, role, content, timestamp, created_at)
- Índices em `conversation_id` e `timestamp` para consultas eficientes
- Método `save_message(conversation_id, role, content)` — salva mensagem imediatamente, retorna `bool`
- Método `load_history(conversation_id)` — carrega todas as mensagens em ordem cronológica (timestamp ASC)
- Método `get_latest_messages(conversation_id, limit)` — mensagens mais recentes, ordenadas por timestamp DESC
- Inicialização automática: cria diretório `.hrns/` e banco de dados se não existirem
- Degradação graciosa: se o banco não pôde ser inicializado, `_ready = False` e todos os métodos retornam valores seguros (`False`, `[]`) sem lançar exceções
- Logging de erros via `logging.getLogger("hrns.chat_history")` para observabilidade
- `datetime.now(timezone.utc)` em vez do depreciado `datetime.utcnow()`

#### Integração em src/hrns/tui/app.py:

- `ChatHistoryService` instanciado em `on_mount`
- Histórico carregado do banco e populado no `ConversationalPanel` ao iniciar
- Mensagem do usuário salva **imediatamente** ao enviar (RF3), antes da chamada ao LLM
- Resposta do LLM salva **apenas quando bem-sucedida** (RF4), detectando strings de erro
- Se o banco falhar na inicialização, a TUI continua operando normalmente (RF9)

#### Adições em src/hrns/tui/widgets/conversational.py:

- Método `populate(history: List[Dict])` — itera sobre registros do histórico e chama `append_message` para cada um, preenchendo o painel com mensagens persistidas

#### Testes — 26 cenários em tests/test_chat_history.py:

**Casos comuns (9):**

- Salvamento e carregamento de mensagem de usuário
- Salvamento de mensagens user + assistant em ordem
- Múltiplos turnos preservados em ordem cronológica
- `save_message` retorna `True` em sucesso
- `get_latest_messages` com limite padrão (50)
- `get_latest_messages` com limite customizado
- `get_latest_messages` ordenação descendente (mais recente primeiro)
- Isolamento entre múltiplos `conversation_id`
- Registro inclui campo `timestamp` não vazio

**Casos extremos (9):**

- Banco vazio → `load_history` retorna `[]`
- `conversation_id` inexistente → retorna `[]`
- Conteúdo vazio (string "") aceito e recuperado
- `limit=0` → retorna `[]`
- `limit=1` → retorna exatamente 1, mais recente
- Arquivo de banco criado se não existir
- Diretório pai criado automaticamente (aninhado)
- Caracteres especiais, quebras de linha, emojis preservados
- Conteúdo muito longo (10.000 caracteres) preservado

**Casos de erro (4):**

- `save_message` retorna `False` quando banco não inicializado
- `load_history` retorna `[]` quando banco não inicializado
- `get_latest_messages` retorna `[]` quando banco não inicializado
- Caminho inválido (ex.: `/dev/null/...`) não lança exceção

**ConversationalPanel.populate (4):**

- Lista vazia — no-op
- Uma mensagem — escrita corretamente
- Múltiplas mensagens — escritas em ordem
- Entrada sem chave `role` — default `"assistant"`

#### Arquivos relacionados:

- `src/hrns/chat_history.py` (novo)
- `src/hrns/tui/app.py` (modificado)
- `src/hrns/tui/widgets/conversational.py` (modificado)
- `tests/test_chat_history.py` (novo)

#### Critérios de aceitação atendidos:

- ✅ Banco SQLite criado automaticamente ao iniciar
- ✅ Tabela `messages` com campos: id, conversation_id, role, content, timestamp, created_at
- ✅ Mensagem do usuário salva imediatamente ao enviar (RF3)
- ✅ Resposta do LLM salva imediatamente ao receber (RF4)
- ✅ Histórico carregado do banco ao reiniciar a interface (RF5)
- ✅ `ConversationalPanel` preenchido com histórico salvo, não inicia vazio (RF6)
- ✅ Mensagens em ordem cronológica correta (RNF4)
- ✅ Sistema não quebra se banco já existir (idempotente)
- ✅ Erros de banco tratados com degradação graciosa (RF9)
- ✅ Múltiplas conversas suportadas via `conversation_id` (RF7, RF8)
- ✅ Implementação usa apenas `sqlite3` da stdlib, sem dependências externas (RNF1)

---

### `20260524_2025_prd_bordas_abas_hrns.md`

**Descrição:** Bordas coloridas com títulos em todos os painéis e três abas no painel Status para listar arquivos de `.hrns/skills`, `.hrns/context` e `.hrns/hooks`.

**Status:** ✅ Implementado

#### O que foi implementado:

- StatusPanel reestruturado com `TabbedContent` contendo três `TabPane`s: skills, context, hooks
- Cada aba contém um `ListView` populado com os arquivos do diretório correspondente
- Mensagem `"nao existem arquivos em {dir}"` quando o diretório está vazio ou não existe (RF8)
- Arquivos listados em ordem alfabética via `list_files()` do módulo `discovery` (RF9)
- Campo de chat `Input` preservado no StatusPanel, docked ao fundo, com altura fixa de 3 linhas
- Bordas coloridas com `border: round` em todos os 4 painéis (RF1):
  - Conversacional → cyan
  - Status → green
  - Tarefas → yellow
  - Trabalho → magenta
- Títulos nas bordas com `border-title-style: bold` (RF2, RF3)
- CSS atualizado com regras para `#status-tabs` (height: 1fr) e Input do StatusPanel (dock: bottom, height: 3)

#### Arquivos modificados:

- `src/hrns/tui/widgets/status.py` — reescrito: herdando de `Vertical`, compondo `TabbedContent` + `Input`, método `_populate_tab` para preenchimento dinâmico
- `src/hrns/tui/app.py` — CSS atualizado com bordas coloridas, `#status-tabs`, Input dock/height
- `tests/test_tui.py` — 16 novos testes para bordas e estrutura do StatusPanel

#### Testes — 88 cenários no total (16 novos):

**StatusPanel (3 novos):**

- Instanciação com `BORDER_TITLE = "Status"`
- `DIRS` mapeia 3 diretórios corretamente
- Chaves de `DIRS` batem com os identificadores das abas

**Bordas CSS (13 novos, parametrizados):**

- Cada painel tem `border: round <cor>` (4 testes)
- Cada painel tem `border-title-color: <cor>` (4 testes)
- Todos os painéis têm `border-title-style: bold` (4 testes)
- `#status-tabs` definido com `height: 1fr`
- Input do StatusPanel com `dock: bottom` e `height: 3`

#### Critérios de aceitação atendidos:

- ✅ Todas as quatro janelas com bordas visíveis (RF1)
- ✅ Cada janela com título na borda superior (RF2)
- ✅ Títulos em linha única com estilo bold (RF3)
- ✅ StatusPanel com três abas: skills, context, hooks (RF4)
- ✅ Aba skills lista arquivos de `.hrns/skills` (RF5)
- ✅ Aba context lista arquivos de `.hrns/context` (RF6)
- ✅ Aba hooks lista arquivos de `.hrns/hooks` (RF7)
- ✅ Mensagem "nao existem arquivos em {dir}" para diretório vazio (RF8)
- ✅ Arquivos ordenados alfabeticamente (RF9)
- ✅ Abas preenchidas ao iniciar a interface (RF10)

---

### `20260524_2041_prd_atalhos_abas_hrns.md`

**Descrição:** Atalhos de teclado numéricos e por letra para alternar entre as abas skills, context e hooks, com exibição no Footer.

**Status:** ✅ Implementado

#### O que foi implementado:

- `BINDINGS` com 6 atalhos: numéricos (`1`, `2`, `3`) e por letra (`s`, `c`, `h`) para alternar abas (RF1, RF8)
- Método `action_switch_tab(tab_id)` em `HrnsApp` — ativa a `TabPane` correspondente via `tabbed.active = tab_id` (RF2)
- `Footer` widget adicionado ao `compose()` — exibe todos os atalhos disponíveis na barra inferior (RF7)
- IDs das `TabPane` simplificados de `skills-pane` para `skills` (mesmo padrão para context/hooks) para casar com os parâmetros dos atalhos
- Importação de `Footer` e `TabbedContent` no módulo `app.py`

#### Arquivos modificados:

- `src/hrns/tui/app.py` — `BINDINGS` expandido, `Footer` no `compose()`, método `action_switch_tab`
- `src/hrns/tui/widgets/status.py` — IDs das `TabPane` simplificados (`skills`, `context`, `hooks`)
- `tests/test_tui.py` — 4 novos testes para atalhos e Footer

#### Testes — 91 cenários no total (4 novos):

**Atalhos e Footer (4 novos):**

- `test_app_has_bindings` — verifica teclas `1`,`2`,`3`, `s`,`c`,`h` além de `ctrl+q`
- `test_action_switch_tab_exists` — método existe e é callable
- `test_footer_imported_in_app` — Footer referenciado no source de `compose()`
- `test_footer_import_in_module` — Footer no namespace do módulo `app`

#### Critérios de aceitação atendidos:

- ✅ Atalhos numéricos `1`, `2`, `3` alternam entre abas (RF1, RF8)
- ✅ Atalhos por letra `s`, `c`, `h` alternam entre abas (RF1, RF8)
- ✅ `action_switch_tab` muda o `active` do `TabbedContent` (RF2)
- ✅ `list_files` usado para listar arquivos nas abas (RF3-RF6 — já implementado no PRD anterior)
- ✅ Footer exibe os atalhos disponíveis (RF7)

---

### `20260524_2102_prd_frontmatter_skills_hrns.md`

**Descrição:** Leitura de frontmatter YAML dos arquivos em `.hrns/skills` para exibir o nome descritivo ao lado do nome do arquivo na aba skills.

**Status:** ✅ Implementado

#### O que foi implementado:

- Dependência `python-frontmatter>=1.0` adicionada ao `pyproject.toml`
- Método estático `_get_skill_display_name(file_path)` em `StatusPanel`:
  - Lê o arquivo como UTF-8
  - Faz parse do frontmatter YAML via `frontmatter.parse()`
  - Se o campo `nome` existir, retorna `"filename - nome"`
  - Se não houver frontmatter, `nome` ausente ou erro de leitura/parse, retorna apenas o nome do arquivo (RF4, RF5)
- `_populate_tab` atualizado: na aba `skills`, usa `_get_skill_display_name`; nas demais abas usa apenas `Path(fname).name` (RF3)
- `list_files()` do módulo `discovery` continua sendo usado para obter os arquivos (RF7)

#### Arquivos modificados:

- `pyproject.toml` — adicionado `python-frontmatter>=1.0`
- `src/hrns/tui/widgets/status.py` — método `_get_skill_display_name`, `_populate_tab` com branch para skills
- `tests/test_frontmatter.py` (novo) — 14 testes
- `uv.lock` — atualizado com `python-frontmatter` e `pyyaml`

#### Testes — 105 cenários no total (14 novos):

**Casos comuns (3):**
- Arquivo com `nome` → `"filename - Nome"`
- Unicode no `nome` preservado (🚀)
- Múltiplos arquivos cada um com seu `nome`

**Casos extremos (8):**
- Arquivo sem frontmatter → só filename
- Frontmatter sem campo `nome` → só filename
- Frontmatter vazio (`---\n---`) → só filename
- YAML inválido/malformado → só filename (não quebra)
- Arquivo vazio → só filename
- Arquivo Markdown com frontmatter → `"guia.md - Guia de Uso"`
- Espaços ao redor do `nome` → stripped pelo YAML
- Nome de arquivo com caracteres especiais (`.`, `-`, `_`)

**Casos de erro (3):**
- Arquivo inexistente → retorna só o filename
- Path é diretório → retorna o nome do diretório
- Arquivo binário → retorna só o filename (não quebra)

#### Critérios de aceitação atendidos:

- ✅ Frontmatter YAML lido de cada arquivo em `.hrns/skills` (RF1)
- ✅ Metadados `nome`, `description`, `trigger` extraídos (RF2)
- ✅ Nome do frontmatter exibido no formato `arquivo.py - Nome` (RF3)
- ✅ Arquivos sem frontmatter exibem apenas o nome (RF4)
- ✅ Frontmatter sem campo `nome` exibe apenas o nome (RF5)
- ✅ Ordenação alfabética por nome de arquivo (RF6 — via `list_files`)
- ✅ `list_files` do PRD de listagem utilizado (RF7)
