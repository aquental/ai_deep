# PRD — Módulo Python para criação de estrutura de diretórios

## Visão geral

Este documento define os requisitos de produto para um módulo em Python responsável por criar uma estrutura inicial de pastas para um projeto baseado em harness agêntico. A estrutura deve ser criada sob o diretório base `.hrns`, que centraliza os arquivos e diretórios de configuração do projeto. O objetivo do módulo é padronizar a preparação do ambiente local, reduzindo erros manuais e acelerando a inicialização de projetos.

## Objetivo

Criar um módulo simples, previsível e reutilizável que:

- Crie a estrutura base de diretórios sob `BASE = ".hrns"`.
- Garanta a existência dos subdiretórios `skills`, `context` e `hooks` dentro de `.hrns`.
- Seja seguro para reexecução, sem falhar quando os diretórios já existirem.
- Possa ser reutilizado por scripts, CLIs ou outros módulos Python.

## Problema

A criação manual da estrutura inicial de um projeto é repetitiva e sujeita a inconsistências. Em projetos que seguem uma arquitetura com separação entre skills, contexto e hooks, pequenas diferenças de nomenclatura ou localização de pastas podem gerar confusão, retrabalho e erros de integração. Centralizar essa estrutura sob `.hrns` reduz dispersão de arquivos e melhora a organização do projeto.

## Escopo

O módulo deve atuar apenas sobre a estrutura local do projeto, considerando `.hrns` como diretório base padrão para criação dos artefatos.

Inclui:

- Criação de `.hrns/skills`
- Criação de `.hrns/context`
- Criação de `.hrns/hooks`
- Criação do diretório `.hrns`, se ele ainda não existir
- Retorno estruturado informando o que foi criado e o que já existia

Não inclui:

- Criação de arquivos dentro dessas pastas
- Geração de conteúdo inicial
- Validação de convenções internas de cada pasta
- Operações fora do diretório base definido

## Usuários-alvo

- Desenvolvedores que estão iniciando um novo projeto
- Ferramentas internas de bootstrap
- CLIs que precisam preparar a estrutura mínima de um harness

## Requisitos funcionais

### RF1. Criar estrutura no diretório base `.hrns`

O módulo deve usar `BASE = ".hrns"` como raiz padrão e criar os diretórios `skills`, `context` e `hooks` diretamente dentro desse caminho.

### RF2. Garantir a existência do diretório base

Se o diretório `.hrns` não existir, o módulo deve criá-lo antes de criar os subdiretórios necessários.

### RF3. Ser idempotente

Se um ou mais diretórios já existirem, o módulo não deve falhar. Ele deve preservar a estrutura existente e seguir a execução normalmente.

### RF4. Expor interface simples

O módulo deve disponibilizar uma função principal, por exemplo `create_structure(base_path=BASE)`, para facilitar uso programático.

### RF5. Retornar resultado estruturado

A função deve retornar um resultado com informações como:

- caminho base utilizado
- diretórios criados
- diretórios já existentes
- status final da operação

Exemplo de retorno:

```python
{
    "base_path": ".hrns",
    "created": ["skills", "context"],
    "existing": ["hooks"],
    "success": True
}
```

### RF6. Tratar erros de sistema

Se houver erro de permissão, caminho inválido ou falha de IO, o módulo deve gerar uma exceção clara ou retornar erro estruturado, de acordo com a abordagem definida na implementação.

## Requisitos não funcionais

### RNF1. Simplicidade

A implementação deve ser pequena, legível e sem dependências externas.

### RNF2. Compatibilidade

O módulo deve ser compatível com versões modernas de Python, preferencialmente Python 3.10+.

### RNF3. Reusabilidade

A lógica deve poder ser importada e utilizada em outros contextos, sem depender de interação via terminal.

### RNF4. Segurança operacional

O módulo não deve apagar, mover ou sobrescrever diretórios existentes.

## Fluxo esperado

1. O consumidor chama a função principal do módulo.
2. O módulo resolve o caminho base, usando `BASE = ".hrns"` por padrão.
3. O módulo garante a existência do diretório `.hrns`.
4. O módulo verifica a existência de `skills`, `context` e `hooks` dentro de `.hrns`.
5. O módulo cria apenas os diretórios ausentes.
6. O módulo retorna um resumo do resultado.

## Estrutura sugerida

```text
.hrns/
├── skills/
├── context/
└── hooks/
```

## Constante sugerida

```python
BASE = ".hrns"
```

## Assinatura sugerida

```python
BASE = ".hrns"


def create_structure(base_path: str = BASE) -> dict:
    ...
```

## Critérios de aceitação

- Ao executar o módulo em um projeto sem diretório `.hrns`, a pasta base deve ser criada com sucesso.
- Ao executar o módulo, as pastas `.hrns/skills`, `.hrns/context` e `.hrns/hooks` devem ser criadas com sucesso.
- Ao executar novamente no mesmo local, nenhuma falha deve ocorrer.
- O retorno deve indicar com clareza quais diretórios foram criados e quais já existiam.
- O módulo não deve criar diretórios fora do caminho base informado.
- O módulo não deve remover nem alterar diretórios preexistentes.

## Exemplo de implementação esperada

```python
from pathlib import Path

BASE = ".hrns"
REQUIRED_DIRS = ["skills", "context", "hooks"]


def create_structure(base_path: str = BASE) -> dict:
    base = Path(base_path)
    base.mkdir(parents=True, exist_ok=True)

    created = []
    existing = []

    for name in REQUIRED_DIRS:
        path = base / name
        if path.exists():
            existing.append(name)
        else:
            path.mkdir(parents=True, exist_ok=True)
            created.append(name)

    return {
        "base_path": str(base),
        "created": created,
        "existing": existing,
        "success": True,
    }
```

## Revisão do documento

A revisão aplica as seguintes correções e melhorias:

- Substitui o diretório atual (`.`) por `BASE = ".hrns"` como raiz padrão.
- Alinha escopo, requisitos, fluxo, critérios de aceitação e exemplo de implementação ao novo diretório base.
- Explicita a criação do diretório `.hrns` como parte do comportamento esperado.
- Torna o documento mais consistente com a organização de um conjunto de configuração centralizado.

## Métricas de sucesso

- Redução do tempo de setup inicial do projeto
- Eliminação de inconsistências na estrutura base
- Melhor organização dos artefatos de configuração sob `.hrns`
- Facilidade de integração com scripts de bootstrap e automação

## Evoluções futuras

Possíveis extensões futuras do módulo:

- Criação opcional de arquivos como `README.md` em cada pasta
- Suporte a estruturas configuráveis
- Exposição via CLI
- Geração de templates iniciais para cada diretório
