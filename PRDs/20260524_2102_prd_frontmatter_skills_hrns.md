# PRD - Ler frontmatter de arquivos de skills e exibir nome na aba

## Visao geral

Este documento define os requisitos de produto para ler o frontmatter de cada arquivo do diretorio `.hrns/skills` e exibir o nome lido do frontmatter ao lado do arquivo na aba skills da interface TUI do projeto `hrns`.

O frontmatter contem tres metadados: `nome`, `description` e `trigger`.

## Objetivo

Implementar um sistema que:

- Leia o frontmatter YAML de cada arquivo no diretorio skills
- Extraia os metadados `name`, `description` e `trigger`
- Exiba o nome do frontmatter ao lado do arquivo na aba skills
- Lidere com arquivos sem frontmatter ou com metadados faltantes de forma graceful

## Problema

Sem leitura de frontmatter, os arquivos sao listados apenas pelo nome do arquivo, o que pode nao ser informativo para o usuario. O frontmatter contem metadados estruturados como `name`, `description` e `trigger` que fornecem contexto adicional sobre o que cada skill faz. Exibir o nome do frontmatter melhora a usabilidade e clareza da interface [cite:68].

## Escopo

O sistema deve ler frontmatter de arquivos em `.hrns/skills` e exibir o nome na aba skills.

Inclui:

- Leitura de frontmatter YAML de arquivos markdown ou texto
- Extraicao dos metadados `name`, `description` e `trigger`
- Exibicao do nome do frontmatter ao lado do arquivo na aba skills
- Tratamento de arquivos sem frontmatter
- Tratamento de metadados faltantes ou invalidos

Nao inclui:

- Edicao de frontmatter pelos usuarios
- Exibicao de `description` e `trigger` na interface (futuro)
- Validacao rigorosa do formato do frontmatter
- Suporte a outros formatos de frontmatter alem de YAML

## Usuarios-alvo

- Desenvolvedores operando o projeto `hrns` no terminal
- Usuarios tecnicos que precisam identificar skills rapidamente pelo nome descritivo
- Qualquer pessoa que use o hrns para gerenciar skills

## Requisitos funcionais

### RF1. Ler frontmatter de arquivos YAML

O sistema deve ler o frontmatter YAML de cada arquivo no diretorio `.hrns/skills` usando a biblioteca `python-frontmatter` [web:104][web:106].

### RF2. Estrutura do frontmatter

O frontmatter deve conter pelo menos os metadados:

- `name`: nome descritivo da skill
- `description`: descricao curta da skill
- `trigger`: tipo de trigger ou gatilho da skill

Exemplo de frontmatter:

    ---
    name: Carregar Contexto
    description: Carrega o contexto do projeto para o LLM
    trigger: on_load
    ---

    # Conteudo do arquivo...

### RF3. Exibir nome do frontmatter na aba skills

Na aba skills, cada arquivo deve ser exibido com o nome do frontmatter ao lado:

    arquivo.py - Name no Frontmatter

### RF4. Lidar com arquivos sem frontmatter

Se um arquivo nao tiver frontmatter, exibir apenas o nome do arquivo:

    arquivo.py

### RF5. Lidar com metadados faltantes

Se o frontmatter existir mas o campo `name` estiver faltando, exibir apenas o nome do arquivo [cite:68].

### RF6. Ordenar arquivos alfabeticamente pelo nome do arquivo

A listagem deve ser ordenada alfabeticamente pelo nome do arquivo, nao pelo nome do frontmatter [cite:68].

### RF7. Usar list_files do PRD de listagem

O sistema deve usar a funcao `list_files(directory: str)` do PRD de listagem de arquivos para obter a lista de arquivos do diretorio [cite:68].

## Requisitos nao funcionais

### RNF1. Simplicidade

A implementacao deve usar a biblioteca `python-frontmatter` para parsing, sem reescrever o parser [web:104][web:106].

### RNF2. Performance

A leitura de frontmatter nao deve causar atraso perceptivel ao carregar a aba skills.

### RNF3. Robustez

O sistema nao deve falhar se um arquivo for invalido ou corrompido [cite:68].

### RNF4. Compatibilidade

Suportar arquivos markdown (.md) e Python (.py) com frontmatter YAML [web:104][web:106].

## Biblioteca recomendada

### python-frontmatter

Instalacao:

    pip install python-frontmatter

Uso basico:

    import frontmatter

    # Carregar arquivo
    post = frontmatter.load('arquivo.md')
    name = post.get('name', None)
    description = post.get('description', None)
    trigger = post.get('trigger', None)
    content = post.content

    # Ou parsear texto
    metadata, content = frontmatter.parse(texto)
    name = metadata.get('name', None)

## Funcao list_files do PRD de listagem

A funcao `list_files` do PRD de listagem de arquivos deve ser usada:

```python
from pathlib import Path

def list_files(directory: str) -> list[str]:
    """Lista todos os arquivos de um diretorio, ordenados alfabeticamente."""
    path = Path(directory)

    if not path.exists():
        raise FileNotFoundError(f"Diretorio nao encontrado: {directory}")

    if not path.is_dir():
        raise NotADirectoryError(f"Caminho nao e um diretorio: {directory}")

    files = [str(item) for item in path.iterdir() if item.is_file()]
    return sorted(files)
```

## Exemplo de uso na aba skills

```python
import frontmatter
from pathlib import Path
from textual.widgets import ListView, ListItem, Label

def get_skill_display_name(file_path: str) -> str:
    """Retorna o nome de exibicao da skill com o nome do frontmatter."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        metadata, _ = frontmatter.parse(content)
        name = metadata.get('name', None)

        if name:
            file_name = Path(file_path).name
            return f"{file_name} - {name}"
        else:
            return Path(file_path).name

    except Exception:
        # Se houver erro ao ler, retorna apenas o nome do arquivo
        return Path(file_path).name

def _create_skills_list(directory: str) -> ComposeResult:
    """Cria a lista de skills com nomes do frontmatter."""
    try:
        files = list_files(directory)
        if not files:
            yield Label(f"nao existem arquivos em {directory}")
            return

        for file_path in files:
            display_name = get_skill_display_name(file_path)
            yield ListItem(Label(display_name))

    except (FileNotFoundError, NotADirectoryError):
        yield Label(f"nao existem arquivos em {directory}")
```

## Formato esperado do frontmatter

```yaml
---
name: Carregar Contexto
description: Carrega o contexto do projeto para o LLM
trigger: on_load
---
# Conteudo do arquivo de skill...
```

## Criterios de aceitacao

- Cada arquivo em `.hrns/skills` deve ter seu frontmatter lido
- O metadado `name` do frontmatter deve ser exibido ao lado do arquivo
- Formato de exibicao: `arquivo.py - Nome do Frontmatter`
- Arquivos sem frontmatter devem exibir apenas o nome do arquivo
- Metadados faltantes nao devem causar erro
- A listagem deve ser ordenada alfabeticamente pelo nome do arquivo
- A aba skills deve usar a funcao `list_files` do PRD de listagem

## Exemplo de implementacao completa

```python
import frontmatter
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import TabbedContent, TabPane, Label, ListView, ListItem


def list_files(directory: str) -> list[str]:
    """Lista todos os arquivos de um diretorio, ordenados alfabeticamente."""
    path = Path(directory)

    if not path.exists():
        raise FileNotFoundError(f"Diretorio nao encontrado: {directory}")

    if not path.is_dir():
        raise NotADirectoryError(f"Caminho nao e um diretorio: {directory}")

    files = [str(item) for item in path.iterdir() if item.is_file()]
    return sorted(files)


def get_skill_display_name(file_path: str) -> str:
    """Retorna o nome de exibicao da skill com o nome do frontmatter."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        metadata, _ = frontmatter.parse(content)
        name = metadata.get('name', None)

        if name:
            file_name = Path(file_path).name
            return f"{file_name} - {name}"
        else:
            return Path(file_path).name

    except Exception:
        return Path(file_path).name


def _create_skills_list(directory: str) -> ComposeResult:
    """Cria a lista de skills com nomes do frontmatter."""
    try:
        files = list_files(directory)
        if not files:
            yield Label(f"nao existem arquivos em {directory}")
            return

        for file_path in files:
            display_name = get_skill_display_name(file_path)
            yield ListItem(Label(display_name))

    except (FileNotFoundError, NotADirectoryError):
        yield Label(f"nao existem arquivos em {directory}")


class HrnsApp(App):
    def compose(self) -> ComposeResult:
        with TabbedContent(initial="skills"):
            with TabPane("skills", id="skills"):
                yield from _create_skills_list(".hrns/skills")
            with TabPane("context", id="context"):
                yield Label("conteudo de context")
            with TabPane("hooks", id="hooks"):
                yield Label("conteudo de hooks")


if __name__ == "__main__":
    HrnsApp().run()
```

## Revisao do documento

A revisao aplica as seguintes correcoes e melhorias:

- Garante leitura de frontmatter YAML usando `python-frontmatter` [web:104][web:106]
- Garante extracao dos metadados `name`, `description` e `trigger`
- Garante exibicao do nome ao lado do arquivo na aba skills [cite:68]
- Garante tratamento de arquivos sem frontmatter graceful [cite:68]
- Garante uso da funcao `list_files` do PRD de listagem [cite:68]

## Metricas de sucesso

- Maior clareza na identificacao das skills na interface
- Reducao de confusao entre arquivos com nomes similares
- Melhoria na experiencia de uso do hrns
- Usuarios conseguem identificar skills rapidamente pelo nome descritivo

## Evolucoes futuras

Possiveis extensoes futuras:

- Exibir `description` como tooltip ou linha adicional
- Exibir `trigger` como badge ou indicador de cor
- Filtro por `trigger` ou por palavra-chave na `description`
- Edicao de frontmatter diretamente na interface
- Validacao de frontmatter obrigatorio para skills
- sorted por `name` do frontmatter em vez do nome do arquivo
