"""Tasks panel — reserved for task display."""

from textual.widgets import Static


class TasksPanel(Static):
    """Panel reserved for task visualization in the top-right area."""

    BORDER_TITLE = "Tarefas"

    def on_mount(self) -> None:
        """Called when the widget is mounted."""
        self.update("Nenhuma tarefa ativa.")
