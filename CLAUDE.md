# CLAUDE.md — ai_deep (HRNS)

## Visão Geral

**Nome do pacote:** `hrns` (Harness)  
**Descrição:** Harness para API do DeepSeek — infraestrutura base para sistemas agênticos  
**Python:** 3.12  
**Gerenciador de pacotes:** `uv`  
**Licença:** MIT

---

## Estrutura do Projeto

```
ai_deep/
├── main.py                     # CLI: lê stdin, chama DeepSeek API
├── pyproject.toml
├── uv.lock
├── .env                        # Não versionado
├── .env.example                # Template de variáveis de ambiente
├── .env.gpg                    # .env encriptado (versionado)
├── PRDs/                       # Product Requirements Documents
│   └── CHANGELOG.md            # Rastreamento de PRDs implementados
├── src/
│   └── hrns/                   # Módulo principal
│       ├── __init__.py         # Exporta: create_structure, list_files, BASE, REQUIRED_DIRS
│       ├── structure.py        # Criação idempotente de .hrns/
│       ├── discovery.py        # Listagem de arquivos em diretório
│       └── logging/
│           ├── config.py       # configure_logging()
│           ├── formatter.py    # StdFormatter
│           └── logger.py       # get_logger(name)
└── tests/
    ├── test_structure.py       # 7 testes
    ├── test_logging.py         # 13 testes
    └── test_discovery.py       # 11 testes
```

---

## Comandos Essenciais

### Setup

```bash
uv sync                   # Instalar dependências
cp .env.example .env      # Configurar variáveis de ambiente
uv run task decrypt       # Ou descriptografar .env.gpg com GPG
```

### Testes

```bash
uv run pytest             # Todos os testes
uv run pytest -v          # Verbose
uv run pytest tests/test_structure.py   # Arquivo específico
uv run pytest --cov=src   # Com cobertura
```

### Executar CLI

```bash
echo "sua pergunta" | uv run main.py
```

### Tarefas (taskipy)

```bash
uv run task encrypt       # Encripta .env → .env.gpg (GPG)
uv run task decrypt       # Descriptografa .env.gpg → .env (GPG)
```

---

## Variáveis de Ambiente

```env
DEEPSEEK_API_KEY=sk-...                    # Obrigatório; deve começar com "sk-"
DEEPSEEK_BASE_URL=https://api.deepseek.com # Base URL da API
DEEPSEEK_MODEL=deepseek-chat               # Ou deepseek-reasoner
```

---

## Dependências

| Pacote | Uso |
|--------|-----|
| `openai>=2.38.0` | SDK compatível com DeepSeek API |
| `python-dotenv>=1.2.2` | Carregamento de `.env` |
| `taskipy>=1.14.0` | Runner de tarefas (encrypt/decrypt) |
| `pytest>=9.0.3` | Framework de testes (dev) |

---

## API Pública do Módulo `hrns`

### `create_structure(base_path=".hrns") -> dict`
Cria estrutura de diretórios idempotente. Retorna:
```python
{"base_path": str, "created": list[str], "existing": list[str], "success": bool}
```
Subdiretórios criados: `skills/`, `context/`, `hooks/`

### `list_files(directory: str) -> list[str]`
Lista apenas arquivos regulares (ignora subdiretórios). Retorno ordenado.  
Lança `FileNotFoundError` se o diretório não existe; `NotADirectoryError` se o caminho não é diretório.

### Logging

```python
from hrns.logging import configure_logging, get_logger

configure_logging(level="INFO", log_to_file=True, log_dir="./logs")
logger = get_logger("meu.modulo")
logger.info("mensagem")
```

Formato de saída: `YYYY-MM-DD HH:MM:SS | LEVEL | logger_name | message`

---

## Arquitetura Agêntica (README)

O projeto documenta um harness agêntico com os seguintes componentes planejados:

- **Agentic Loop** — raciocínio → ação → execução → feedback
- **Skills** — capacidades discretas com schema declarado e níveis de permissão
- **Hooks** — interceptores `pre-prompt`, `pre-tool`, `post-tool`, `stop`, `on-error`, `pre-commit`
- **Context** — system prompts, histórico, gestão de budget de tokens
- **Memory** — persistência entre sessões (working, episódica, semântica, procedural)

---

## Fluxo de Desenvolvimento com PRDs

Novos módulos seguem o padrão:
1. Criar PRD em `PRDs/YYYYMMDD_HHMM_prd_<nome>.md`
2. Implementar em `src/hrns/`
3. Criar testes em `tests/`
4. Registrar em `PRDs/CHANGELOG.md` com `✅ Implemented`

---

## Próximas Evoluções (Backlog)

- Loader de skills (`hrns/skills_loader.py`)
- Framework de hooks (`hrns/hooks.py`)
- Gestão de contexto (`hrns/context.py`)
- Loop agêntico principal
- Sistema de segurança e permissões
- Camada de memória persistente
- Métricas de observabilidade
