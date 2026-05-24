# PRD — Módulo de logging robusto

## Visão geral

Este documento define os requisitos de produto para um módulo de logging robusto, projetado para aplicações Python que exigem rastreabilidade, observabilidade e suporte a diagnóstico em ambientes de desenvolvimento, teste e produção. O módulo deve oferecer uma interface consistente para emissão de logs, configuração centralizada e integração simples com diferentes partes do sistema.

## Objetivo

Implementar um módulo de logging que:

- Centralize a configuração de logs da aplicação.
- Padronize o formato e os níveis de severidade.
- Facilite depuração, auditoria e monitoramento operacional.
- Suporte múltiplos destinos de saída, como console e arquivo.
- Seja reutilizável por outros módulos e serviços.

## Problema

Sem um módulo de logging padronizado, aplicações tendem a gerar mensagens inconsistentes, difíceis de filtrar e pouco úteis para investigação de falhas. Isso aumenta o tempo de diagnóstico, reduz a visibilidade do comportamento do sistema e dificulta a operação em produção.

## Escopo

O módulo deve prover uma camada de logging configurável e reutilizável para aplicações Python.

Inclui:

- Configuração centralizada de logging
- Suporte a níveis padrão: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- Saída em console
- Saída em arquivo
- Formatação padronizada das mensagens
- Rotação básica de arquivos de log
- Criação de loggers nomeados por módulo
- Controle de nível por ambiente ou configuração

Não inclui:

- Integração direta com plataformas externas de observabilidade
- Dashboards de monitoramento
- Coleta distribuída de traces
- Persistência em banco de dados

## Usuários-alvo

- Desenvolvedores que precisam diagnosticar problemas em tempo de execução
- Equipes de operação que precisam inspecionar eventos do sistema
- Módulos internos que dependem de logs consistentes e reutilizáveis

## Requisitos funcionais

### RF1. Configuração centralizada

O módulo deve oferecer uma função principal de configuração, por exemplo `configure_logging(...)`, responsável por inicializar handlers, formatters e nível global de log.

### RF2. Logger reutilizável por módulo

O módulo deve permitir a obtenção de loggers nomeados, por exemplo via `get_logger(name: str)`, para que cada componente da aplicação registre eventos com identidade própria.

### RF3. Suporte a múltiplos níveis

O módulo deve suportar os níveis padrão de logging do ecossistema Python:

- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`
- `CRITICAL`

### RF4. Saída em console

O módulo deve permitir emissão de logs para o terminal, com formatação legível e adequada para uso em desenvolvimento e execução local.

### RF5. Saída em arquivo

O módulo deve permitir gravação de logs em arquivo configurável, com criação automática do diretório de destino quando necessário.

### RF6. Rotação de arquivos

O módulo deve suportar rotação de arquivos de log para evitar crescimento ilimitado, preferencialmente por tamanho, com retenção configurável de arquivos antigos.

### RF7. Formato padronizado

Cada linha de log deve conter, no mínimo:

- timestamp
- nível de severidade
- nome do logger
- mensagem

Formato de referência:

```text
2026-05-24 16:48:00 | INFO | api.auth | Usuário autenticado com sucesso
```

### RF8. Configuração por ambiente

O módulo deve permitir ajuste do nível de log e dos destinos de saída por configuração, para acomodar diferentes necessidades em desenvolvimento, teste e produção.

### RF9. Prevenção de duplicidade

O módulo deve evitar configuração duplicada de handlers quando inicializado mais de uma vez no mesmo processo.

### RF10. Tratamento de exceções

O módulo deve oferecer suporte simples para registrar exceções, incluindo stack trace quando apropriado.

Exemplo de uso esperado:

```python
logger.exception("Falha ao processar requisição")
```

## Requisitos não funcionais

### RNF1. Simplicidade de integração

A adoção do módulo deve exigir poucas linhas de código e baixa curva de aprendizado.

### RNF2. Baixa dependência

A implementação deve priorizar a biblioteca padrão do Python, evitando dependências externas sempre que possível.

### RNF3. Confiabilidade

O módulo deve ser estável, previsível e seguro para uso em aplicações de longa duração.

### RNF4. Performance adequada

O logging não deve introduzir overhead desproporcional para operações comuns da aplicação.

### RNF5. Legibilidade

O código do módulo deve ser organizado, documentado e fácil de manter.

## Fluxo esperado

1. A aplicação chama a função de configuração do módulo no bootstrap.
2. O módulo inicializa handlers, formatter e nível de severidade.
3. Os componentes da aplicação obtêm loggers nomeados.
4. Os eventos são registrados no console, em arquivo ou em ambos os destinos.
5. Arquivos de log são rotacionados automaticamente conforme a configuração.

## Interface sugerida

```python
def configure_logging(
    level: str = "INFO",
    log_to_console: bool = True,
    log_to_file: bool = False,
    log_dir: str = "./logs",
    file_name: str = "application.log",
    max_bytes: int = 5_000_000,
    backup_count: int = 5,
) -> None:
    ...


def get_logger(name: str):
    ...
```

## Estrutura sugerida

```text
logging_module/
├── __init__.py
├── config.py
├── formatter.py
└── logger.py
```

## Critérios de aceitação

- O módulo deve configurar logging para console com uma única chamada.
- O módulo deve configurar logging para arquivo com rotação habilitada.
- O módulo deve permitir recuperar loggers nomeados sem duplicar handlers.
- Logs emitidos devem seguir um formato padronizado.
- O módulo deve funcionar corretamente em múltiplas execuções no mesmo processo.
- O módulo deve permitir registrar exceções com stack trace.
- O módulo deve criar automaticamente o diretório de logs, se ele não existir.

## Exemplo de implementação esperada

```python
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_CONFIGURED = False


def configure_logging(
    level: str = "INFO",
    log_to_console: bool = True,
    log_to_file: bool = False,
    log_dir: str = "./logs",
    file_name: str = "application.log",
    max_bytes: int = 5_000_000,
    backup_count: int = 5,
) -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_to_file:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            Path(log_dir) / file_name,
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
```

## Métricas de sucesso

- Redução do tempo de diagnóstico de falhas
- Padronização das mensagens de log em toda a aplicação
- Menor incidência de logs duplicados ou mal formatados
- Facilidade de adoção por módulos existentes e novos

## Evoluções futuras

Possíveis extensões futuras do módulo:

- Saída estruturada em JSON
- Correlação por request ID ou trace ID
- Máscara de dados sensíveis
- Integração com sistemas externos de observabilidade
- Enriquecimento automático de contexto por execução
