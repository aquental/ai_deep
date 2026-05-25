# PRD - Bordas, titulos e abas nas janelas Textual do hrns

## Visao geral

Este documento define os requisitos de produto para adicionar bordas com titulos em todas as janelas da interface TUI do projeto `hrns` usando Textual, e incluir tres abas na janela `Status` para listar arquivos dos subdiretorios `.hrns/skills`, `.hrns/context` e `.hrns/hooks`.

## Objetivo

Implementar uma interface com:

- Bordas visiveis em todas as janelas com titulo e linha
- Tres abas na janela `Status`: skills, context e hooks
- Listagem de arquivos em cada aba correspondente
- Mensagem de aviso quando nenhum arquivo existir no diretorio

## Problema

Sem bordas e titulos, as janelas ficam visualmente fundidas, dificultando a identificacao de cada area. Sem abas organizadas, o usuario nao tem acesso rapido aos arquivos de configuracao de skills, context e hooks, prejudicando a usabilidade e a navegacao no sistema.

## Escopo

O sistema deve adicionar bordas com titulos em todas as janelas e implementar abas na janela `Status`.

Inclui:

- Bordas em todas as quatro janelas: conversacional, status, tarefas e trabalho
- Titulo em cada borda identificando a janela
- Tres abas na janela `Status`: skills, context, hooks
- Listagem de arquivos de `.hrns/skills` na aba skills
- Listagem de arquivos de `.hrns/context` na aba context
- Listagem de arquivos de `.hrns/hooks` na aba hooks
- Mensagem "nao existem arquivos em {dir}" quando diretorio estiver vazio

Nao inclui:

- Acao ao clicar nos arquivos (futuro)
- Edicao de arquivos diretamente na interface
- Filtros ou busca nos arquivos listados
- Criacao de novos arquivos pela interface

## Usuarios-alvo

- Desenvolvedores operando o projeto `hrns` no terminal
- Usuarios tecnicos que precisam visualizar arquivos de configuracao rapidamente

## Requisitos funcionais

### RF1. Adicionar bordas em todas as janelas

Cada janela deve ter uma borda visivel usando o estilo `border` do Textual.

### RF2. Adicionar titulo em cada borda

Cada janela deve exibir um titulo na borda superior identificando a janela:

- `conversacional`
- `status`
- `tarefas`
- `trabalho`

O titulo deve usar `border_title`.

### RF3. Usar linha no titulo

O titulo deve ser exibido em uma linha unica, usando o primeiro linha do texto se necessario.

### RF4. Adicionar tres abas na janela Status

A janela `Status` deve conter tres abas:

1. skills
2. context
3. hooks

Usando `TabbedContent` do Textual.

### RF5. Listar arquivos na aba skills

A aba skills deve listar todos os arquivos existentes em `.hrns/skills`.

### RF6. Listar arquivos na aba context

A aba context deve listar todos os arquivos existentes em `.hrns/context`.

### RF7. Listar arquivos na aba hooks

A aba hooks deve listar todos os arquivos existentes em `.hrns/hooks`.

### RF8. Mostrar mensagem quando diretorio vazio

Se um diretorio nao tiver arquivos, mostrar:

    nao existem arquivos em {dir}

onde `{dir}` e o caminho do diretorio.

### RF9. Ordenar arquivos alfabetica mente

A listagem de arquivos deve ser ordenada alfabeticamente por nome para consistencia.

### RF10. Atualizar abas dinamicamente

As abas devem ser preenchidas ao iniciar a interface, carregando os arquivos atuais dos diretorios.

## Requisitos nao funcionais

### RNF1. Simplicidade visual

As bordas devem ser claras mas nao excessivamente pesadas visualmente (ex.: `border: round` ou `border: heavy`).

### RNF2. Responsividade

A interface deve manter o layout com bordas mesmo ao redimensionar o terminal.

### RNF3. Performance

A listagem de arquivos nao deve causar atraso perceptivel ao iniciar a interface.

### RNF4. Compatibilidade

Usar widgets padrao do Textual: `TabbedContent`, `TabPane`, `ListView`, `Label`.

## Layout esperado

    + conversacional ----------------------------+--+ tarefas --------+
    |                                            |                  |
    |               historico da conversa        |   skills (aba)   |
    |                                            |                  |
    +--------------------------------------------+------------------+
    | + status --------------------------------+ |   trabalho (aba) |
    | | [skills] [context] [hooks]             | |                  |
    | |                                        | |                  |
    | |   (conteudo da aba selecionada)        | |                  |
    | |                                        | |                  |
    | +----------------------------------------+ |                  |
    +------------------------------------------ -+------------------+

## Estrutura de diretorios

    .hrns/
    +-- skills/
    |   +-- arquivo1.py
    |   +-- arquivo2.py
    +-- context/
    |   +-- contexto1.md
    +-- hooks/
        +-- hook1.py
        +-- hook2.py

## Componentes Textual sugeridos

### Border com titulo

    widget = Label("conteudo")
    widget.border_title = "conversacional"
    widget.styles.border = ("round", "cyan")

### TabbedContent com tres abas

    from textual.widgets import TabbedContent, TabPane

    with TabbedContent(*tabs, id="status-tabs"):
        with TabPane("skills", id="skills-pane"):
            yield ListView(...)
        with TabPane("context", id="context-pane"):
            yield ListView(...)
        with TabPane("hooks", id="hooks-pane"):
            yield ListView(...)

### Listagem de arquivos

    from pathlib import Path
    from textual.widgets import ListView, ListItem, Label

    def list_files(directory: str) -> list:
        path = Path(directory)
        if not path.exists():
            return ["nao existem arquivos em {directory}"]

        files = sorted([p.name for p in path.iterdir() if p.is_file()])
        if not files:
            return [f"nao existem arquivos em {directory}"]

        return files

## CSS sugerido

    /* Bordas nas janelas */
    .conversational-panel {
        border: round cyan;
        border-title-color: cyan;
        border-title-style: bold;
    }

    .status-panel {
        border: round green;
        border-title-color: green;
        border-title-style: bold;
    }

    .tasks-panel {
        border: round yellow;
        border-title-color: yellow;
        border-title-style: bold;
    }

    .work-panel {
        border: round magenta;
        border-title-color: magenta;
        border-title-style: bold;
    }

    /* Abas na janela Status */
    #status-tabs {
        height: 100%;
    }

## Criterios de aceitacao

- Todas as quatro janelas devem ter bordas visiveis
- Cada janela deve ter um titulo na borda superior
- A janela `Status` deve ter tres abas: skills, context, hooks
- Cada aba deve listar os arquivos do diretorio correspondente
- Se um diretorio estiver vazio, mostrar "nao existem arquivos em {dir}"
- Os arquivos devem estar ordenados alfabeticamente
- A interface deve ser renderizada corretamente com bordas e abas

## Exemplo de implementacao esperada

    from pathlib import Path
    from textual.app import App, ComposeResult
    from textual.widgets import (
        Header, Footer, Label, ListView, 
        ListItem, TabbedContent, TabPane
    )
    from textual.containers import Container


    class HrnsApp(App):
        CSS = """
        Screen {
            layout: grid;
            grid-size: 2;
            grid-columns: 70% 30%;
        }

        .panel {
            border: round;
            padding: 1;
        }

        .conversational-panel {
            grid-column: 1;
            grid-row: 1 / 3;
            border: round cyan;
            border-title-color: cyan;
            border-title-style: bold;
        }

        .status-panel {
            grid-column: 1;
            grid-row: 3;
            border: round green;
            border-title-color: green;
            border-title-style: bold;
        }

        .tasks-panel {
            grid-column: 2;
            grid-row: 1;
            border: round yellow;
            border-title-color: yellow;
            border-title-style: bold;
        }

        .work-panel {
            grid-column: 2;
            grid-row: 2;
            border: round magenta;
            border-title-color: magenta;
            border-title-style: bold;
        }
        """

        def compose(self) -> ComposeResult:
            yield Header()

            # Janela conversacional
            conv = Label("Historico da conversa")
            conv.border_title = "conversacional"
            conv.add_class("conversational-panel")
            yield conv

            # Janela Status com abas
            status_container = Container(
                TabbedContent(
                    TabPane("skills", self._create_file_list(".hrns/skills")),
                    TabPane("context", self._create_file_list(".hrns/context")),
                    TabPane("hooks", self._create_file_list(".hrns/hooks")),
                    id="status-tabs"
                ),
                id="status-container"
            )
            status_container.border_title = "status"
            status_container.add_class("status-panel")
            yield status_container

            # Janela tarefas
            tasks = Label("Tarefas")
            tasks.border_title = "tarefas"
            tasks.add_class("tasks-panel")
            yield tasks

            # Janela trabalho
            work = Label("Trabalho")
            work.border_title = "trabalho"
            work.add_class("work-panel")
            yield work

            yield Footer()

        def _create_file_list(self, directory: str) -> ComposeResult:
            """Cria uma ListView com os arquivos do diretorio."""
            path = Path(directory)

            if not path.exists():
                yield Label(f"nao existem arquivos em {directory}")
                return

            files = sorted([p for p in path.iterdir() if p.is_file()])

            if not files:
                yield Label(f"nao existem arquivos em {directory}")
                return

            for file in files:
                yield ListItem(Label(file.name))


    if __name__ == "__main__":
        HrnsApp().run()

## Revisao do documento

A revisao aplica as seguintes correcoes e melhorias:

- Garante bordas em todas as janelas com titulo e linha
- Garante tres abas na janela Status: skills, context, hooks
- Garante listagem de arquivos dos diretorios `.hrns/skills`, `.hrns/context`, `.hrns/hooks`
- Garante mensagem "nao existem arquivos em {dir}" quando diretorio vazio

## Metricas de sucesso

- Maior clareza visual ao identificar cada janela
- Acesso rapido aos arquivos de configuracao pelas abas
- Reducao de confusao entre areas da interface
- Melhoria na experiencia de uso do `hrns`

## Evolucoes futuras

Possiveis extensoes futuras:

- Clicar em arquivo para abrir/visualizar conteudo
- Adicionar botoes de acao nos arquivos (executar, editar, deletar)
- Filtro de busca na listagem de arquivos
- Atalhos de teclado para navegar entre abas e arquivos
- Badges ou indicadores de status nos arquivos
