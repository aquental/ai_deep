# PRD - Atalhos de teclado para alternar abas no hrns

## Visao geral

Este documento define os requisitos de produto para adicionar atalhos de teclado na interface TUI do projeto `hrns` usando Textual, permitindo alternar rapidamente entre as abas skills, context e hooks na janela Status.

O PRD valida que as abas usam a funcao `list_files` do PRD de listagem de arquivos para exibir os arquivos dos diretorios `.hrns/skills`, `.hrns/context` e `.hrns/hooks`.

## Objetivo

Implementar atalhos de teclado que:

- Permatam alternar entre as tres abas da janela Status usando teclas numericas (1, 2, 3) e/ou letras (s, c, h)
- Usem a funcao `list_files` do PRD de listagem de arquivos para popolar as abas
- Mostrem os atalhos disponiveis no Footer da interface
- Sejam consistentes com a arquitetura de bindings do Textual

## Problema

Sem atalhos de teclado, o usuario precisa usar o mouse ou navegar clicando nas abas, o que e mais lento e menos eficiente em uma interface de terminal. Atalhos de teclado melhoram a produtividade e a experiencia de uso, especialmente para usuarios que preferem manter as mao no teclado [cite:68].

## Escopo

O sistema deve adicionar BINDINGS para alternar entre abas no Textual.

Inclui:

- Adicao de BINDINGS no app principal do hrns
- Metodo `action_switch_tab` para mudar a aba ativa
- Uso da funcao `list_files` para listar arquivos nas abas
- Exibicao dos atalhos no Footer
- Validacao de que as abas listam arquivos corretamente

Nao inclui:

- Criacao de novas abas dinamicamente
- Remocao de abas existentes
- Acao ao pressionar teclas Alips de alternar abas
- Modificacao na estrutura dos Bindings do Textual

## Usuarios-alvo

- Desenvolvedores operando o hrns no terminal
- Usuarios tecnicos que usam atalhos de teclado frequentemente
- Qualquer pessoa que precise navegar rapidamente entre abas

## Requisitos funcionais

### RF1. Adicionar BINDINGS no App

O app deve definir BINDINGS com os atalhos de teclado:

```python
BINDINGS = [
    ("1", "switch_tab('skills')", "Skills (1)"),
    ("2", "switch_tab('context')", "Context (2)"),
    ("3", "switch_tab('hooks')", "Hooks (3)"),
    # Ou usar letras:
    ("s", "switch_tab('skills')", "Skills"),
    ("c", "switch_tab('context')", "Context"),
    ("h", "switch_tab('hooks')", "Hooks"),
]
```

### RF2. Implementar action_switch_tab

O app deve implementar o metodo `action_switch_tab(tab_id: str)` que muda a aba ativa do TabbedContent [cite:68].

### RF3. Usar list_files para listar arquivos

Cada aba deve usar a funcao `list_files(directory: str)` do PRD de listagem de arquivos para obter a lista de arquivos do diretorio correspondente [cite:68].

### RF4. Validar lista de arquivos na aba skills

A aba skills deve listar arquivos de `.hrns/skills` usando `list_files(".hrns/skills")`.

### RF5. Validar lista de arquivos na aba context

A aba context deve listar arquivos de `.hrns/context` usando `list_files(".hrns/context")`.

### RF6. Validar lista de arquivos na aba hooks

A aba hooks deve listar arquivos de `.hrns/hooks` usando `list_files(".hrns/hooks")`.

### RF7. Mostrar atalhos no Footer

O Footer deve ser exibido na interface mostrando os atalhos de teclado disponiveis [cite:68].

### RF8. Alternar entre abas numericase letras

O sistema deve permitir alternar tanto usando numeros (1, 2, 3) quanto letras (s, c, h) para flexibilidade [cite:68].

## Requisitos nao funcionais

### RNF1. simplicidade

A implementacao deve ser simples e direta, sem complicacao desnecessaria.

### RNF2. Consistencia

Os atalhos devem ser consistentes com a nomenclatura das abas (skills, context, hooks).

### RNF3. Descoberta facil

Os atalhos devem ser visiveis no Footer para que o usuario descubra facilmente.

### RNF4. Performance

A alternancia entre abas deve ser instantanea, sem atraso perceptivel.

## Funcao list_files do PRD de listagem

A funcao `list_files` do PRD de listagem de arquivos (2026-05-24) deve ser usada:

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

## Exemplo de uso nas abas

```python
def _create_file_list(self, directory: str) -> ComposeResult:
    """Cria uma ListView com os arquivos do diretorio usando list_files."""
    try:
        files = list_files(directory)
        if not files:
            yield Label(f"nao existem arquivos em {directory}")
            return

        for file_path in files:
            yield ListItem(Label(Path(file_path).name))

    except (FileNotFoundError, NotADirectoryError) as e:
        yield Label(f"nao existem arquivos em {directory}")
```

## Layout dos BINDINGS

Pode-se escolher entre:

| Opcao | BINDINGS |
|---|---|
| Numeros | ("1", "switch_tab('skills')", "Skills (1)") |
| Letra | ("s", "switch_tab('skills')", "Skills") |
| Mix | Ambos (1, 2, 3 e s, c, h) |

Recomenda-se usar numeros para simplicidade ou letras para mnemonicidade.

## Criterios de aceitacao

- Os atalhos 1, 2, 3 (ou s, c, h) devem alternar entre as abas skills, context e hooks
- O metodo `action_switch_tab` deve mudar o atributo `active` do TabbedContent
- Cada aba deve usar a funcao `list_files` para listar arquivos
- A aba skills deve listar arquivos de `.hrns/skills`
- A aba context deve listar arquivos de `.hrns/context`
- A aba hooks deve listar arquivos de `.hrns/hooks`
- O Footer deve mostrar os atalhos disponiveis
- A alternancia entre abas deve ser instantanea

## Exemplo de implementacao completa

```python
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Label, ListView, 
    ListItem, TabbedContent, TabPane
)
from textual.containers import Container


def list_files(directory: str) -> list[str]:
    """Lista todos os arquivos de um diretorio, ordenados alfabeticamente."""
    path = Path(directory)

    if not path.exists():
        raise FileNotFoundError(f"Diretorio nao encontrado: {directory}")

    if not path.is_dir():
        raise NotADirectoryError(f"Caminho nao e um diretorio: {directory}")

    files = [str(item) for item in path.iterdir() if item.is_file()]
    return sorted(files)


class HrnsApp(App):
    BINDINGS = [
        ("1", "switch_tab('skills')", "Skills (1)"),
        ("2", "switch_tab('context')", "Context (2)"),
        ("3", "switch_tab('hooks')", "Hooks (3)"),
    ]

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-columns: 70% 30%;
    }

    .status-panel {
        border: round green;
        border-title-color: green;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()

        # Janela Status com abas
        status_container = Container(
            TabbedContent(
                TabPane("skills", self._create_file_list(".hrns/skills"), id="skills"),
                TabPane("context", self._create_file_list(".hrns/context"), id="context"),
                TabPane("hooks", self._create_file_list(".hrns/hooks"), id="hooks"),
                id="status-tabs",
                initial="skills"
            ),
            id="status-container"
        )
        status_container.border_title = "status"
        status_container.add_class("status-panel")
        yield status_container
        
        yield Footer()
    
    def action_switch_tab(self, tab_id: str) -> None:
        """Muda para a aba especificada."""
        tabbed = self.query_one("#status-tabs", TabbedContent)
        tabbed.active = tab_id
    
    def _create_file_list(self, directory: str) -> ComposeResult:
        """Cria uma ListView com os arquivos do diretorio usando list_files."""
        try:
            files = list_files(directory)
            if not files:
                yield Label(f"nao existem arquivos em {directory}")
                return
            
            for file_path in files:
                yield ListItem(Label(Path(file_path).name))
        
        except (FileNotFoundError, NotADirectoryError):
            yield Label(f"nao existem arquivos em {directory}")


if __name__ == "__main__":
    HrnsApp().run()
```

## Revisao do documento

A revisao aplica as seguintes correcoes e melhorias:

- Garante BINDINGS com atalhos numericos (1, 2, 3) ou letras (s, c, h)
- Garante metodo `action_switch_tab` para alternar abas
- Garante uso da funcao `list_files` do PRD de listagem de arquivos
- Garante que as abas listam arquivos de `.hrns/skills`, `.hrns/context`, `.hrns/hooks`

## Metricas de sucesso

- Reducao do tempo de navegacao entre abas
- Maior uso de atalhos de teclado em vez do mouse
- Melhoria na experiencia de uso do hrns
- Usuarios conseguem alternar abas sem olhar para o Footer

## Evolucoes futuras

Possiveis extensoes futuras:

- Atalhos para navegar entre itens dentro de cada aba
- Atalhos para executar acao nos arquivos listados
-不平衡 de atalhos por contexto (eltas em diferentes abas)
- Memo de atalhos customizados pelo usuario
- Help screen mostrando todos os atalhos disponiveis
