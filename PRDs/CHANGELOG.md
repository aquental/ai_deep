# CHANGELOG — PRDs

> Mecanismo estilo migrations: cada PRD é uma migração. O checkbox controla se já foi aplicado.
> Arquivos ordenados do mais antigo para o mais recente (YYYYMMDD_hhmm).

---

## Parte 1 — Lista de PRDs

- [x] `20260524_1639_prd_estrutura_diretorios_revisado.md`
- [x] `20260524_1650_prd_modulo_logging_robusto.md`
- [x] `20260524_1710_prd_listagem_arquivos_diretorio_hrns.md`

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
