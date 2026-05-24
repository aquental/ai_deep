# PRD — Módulo para listagem de arquivos de diretórios de configuração

## Visão geral

Este documento define os requisitos de produto para implementar uma função genérica responsável por listar todos os arquivos de um diretório informado. A função será utilizada pelo conjunto de configurações localizado em `./hrns`, cobrindo especificamente os diretórios `skills`, `hooks` e `contexts`.

O objetivo é padronizar a descoberta de arquivos dentro da estrutura de configuração do projeto, oferecendo uma interface simples, reutilizável e previsível para consumo por outros módulos.

## Objetivo

Implementar uma função genérica em Python que:

- Receba um diretório como entrada.
- Liste todos os arquivos presentes nesse diretório.
- Possa ser reutilizada para os diretórios `./hrns/skills`, `./hrns/hooks` e `./hrns/contexts`.
- Retorne dados consistentes para uso por componentes de carregamento, validação ou indexação.

## Problema

Sem uma função padronizada para descoberta de arquivos, cada parte do sistema pode implementar sua própria lógica de listagem, resultando em inconsistência, duplicação de código e maior risco de erro. Em uma estrutura baseada em diretórios de configuração como `./hrns`, isso dificulta a manutenção e a evolução do sistema.

## Escopo

O módulo deve oferecer uma função genérica para listar arquivos de um diretório arbitrário, com foco principal no uso pelos diretórios de configuração em `./hrns`.

Inclui:

- Listagem de arquivos de um diretório informado
- Reutilização da mesma função para `skills`, `hooks` e `contexts`
- Retorno estruturado com caminhos ou nomes de arquivos
- Tratamento de diretórios inexistentes ou inválidos
- Filtragem para retornar apenas arquivos, ignorando subdiretórios

Não inclui:

- Leitura do conteúdo dos arquivos
- Parsing de arquivos de configuração
- Validação semântica do conteúdo
- Monitoramento de alterações em tempo real
- Busca recursiva em subdiretórios, salvo se adicionada como evolução futura

## Usuários-alvo

- Módulos de bootstrap e carregamento de configuração
- Componentes que precisam descobrir arquivos de skills, hooks e contexts
- Desenvolvedores que desejam uma interface única para navegação dos diretórios de configuração

## Requisitos funcionais

### RF1. Receber diretório como parâmetro

A função deve aceitar um caminho de diretório como entrada, por exemplo `list_files(directory: str)`.

### RF2. Retornar apenas arquivos

A função deve listar apenas arquivos regulares do diretório informado, ignorando subdiretórios e outros tipos de entrada.

### RF3. Ser genérica e reutilizável

A mesma função deve ser utilizável para qualquer diretório, incluindo explicitamente:

- `./hrns/skills`
- `./hrns/hooks`
- `./hrns/contexts`

### RF4. Retornar estrutura previsível

A função deve retornar uma coleção padronizada, preferencialmente uma lista de caminhos ou nomes de arquivos ordenados.

Exemplo de retorno:

```python
[
    "./hrns/skills/load_context.py",
    "./hrns/skills/register_tools.py"
]
```

### RF5. Ordenação determinística

O retorno deve ser ordenado de forma determinística para evitar comportamento inconsistente entre execuções.

### RF6. Tratar diretório inexistente

Se o diretório informado não existir, a função deve lançar uma exceção clara ou retornar um erro estruturado, conforme a estratégia adotada pelo projeto.

### RF7. Tratar diretório vazio

Se o diretório existir, mas não contiver arquivos, a função deve retornar uma lista vazia sem falhar.

### RF8. Suporte a integração com o conjunto `hrns`

O módulo deve permitir uso simples em chamadas como:

```python
skills = list_files("./hrns/skills")
hooks = list_files("./hrns/hooks")
contexts = list_files("./hrns/contexts")
```

## Requisitos não funcionais

### RNF1. Simplicidade

A implementação deve ser pequena, legível e sem dependências externas.

### RNF2. Reusabilidade

A função deve poder ser usada por qualquer módulo do sistema sem acoplamento ao domínio de `skills`, `hooks` ou `contexts`.

### RNF3. Previsibilidade

O comportamento deve ser consistente entre ambientes e execuções, especialmente quanto à ordenação e filtragem.

### RNF4. Segurança operacional

A função deve ser somente leitura, sem criar, modificar, mover ou excluir arquivos.

### RNF5. Compatibilidade

A implementação deve ser compatível com Python 3.10+.

## Fluxo esperado

1. Um módulo consumidor informa o caminho de um diretório.
2. A função valida se o caminho existe e se representa um diretório.
3. A função identifica os itens presentes no caminho.
4. A função filtra apenas arquivos regulares.
5. A função ordena o resultado.
6. A função retorna a lista final.

## Interface sugerida

```python
def list_files(directory: str) -> list[str]:
    ...
```

## Estrutura sugerida

```text
.hrns/
├── skills/
├── hooks/
└── contexts/
```

## Critérios de aceitação

- A função deve listar corretamente todos os arquivos de `./hrns/skills`.
- A função deve listar corretamente todos os arquivos de `./hrns/hooks`.
- A função deve listar corretamente todos os arquivos de `./hrns/contexts`.
- A função não deve retornar subdiretórios.
- A função deve retornar lista vazia para diretórios válidos sem arquivos.
- A função deve falhar de maneira clara para diretórios inexistentes.
- O retorno deve ser ordenado de maneira consistente.

## Exemplo de implementação esperada

```python
from pathlib import Path


def list_files(directory: str) -> list[str]:
    path = Path(directory)

    if not path.exists():
        raise FileNotFoundError(f"Diretório não encontrado: {directory}")

    if not path.is_dir():
        raise NotADirectoryError(f"Caminho não é um diretório: {directory}")

    files = [str(item) for item in path.iterdir() if item.is_file()]
    return sorted(files)
```

## Exemplo de uso

```python
skills = list_files("./hrns/skills")
hooks = list_files("./hrns/hooks")
contexts = list_files("./hrns/contexts")
```

## Métricas de sucesso

- Redução de duplicação de lógica de descoberta de arquivos
- Consistência no carregamento de arquivos de configuração
- Menor incidência de erros em módulos que dependem da estrutura `hrns`
- Facilidade de manutenção e reaproveitamento da função em novos diretórios

## Evoluções futuras

Possíveis extensões futuras:

- Suporte a busca recursiva
- Filtro por extensão
- Retorno opcional apenas com nomes de arquivo
- Retorno enriquecido com metadados, como tamanho e data de modificação
- Função auxiliar para listar automaticamente todos os arquivos dos grupos `skills`, `hooks` e `contexts`
