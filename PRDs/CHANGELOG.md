# CHANGELOG — PRDs

> Mecanismo estilo migrations: cada PRD é uma migração. O checkbox controla se já foi aplicado.
> Arquivos ordenados do mais antigo para o mais recente (YYYYMMDD_hhmm).

---

## Parte 1 — Lista de PRDs

- [x] `20260524_1639_prd_estrutura_diretorios_revisado.md`
- [x] `20260524_1650_prd_modulo_logging_robusto.md`
- [x] `20260524_1710_prd_listagem_arquivos_diretorio_hrns.md`
- [x] `20260524_1826_prd_textual_hrns.md`
- [ ] `20260524_1911_prd_chatStatusPanel.md`
- [ ] `20260524_1919_prd_persistencia_historico_chat_hrns.md`

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
