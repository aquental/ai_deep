"""Work panel — reserved for work/logs display."""

from textual.widgets import Static


class WorkPanel(Static):
    """Panel reserved for work context and logs in the bottom-right area."""

    BORDER_TITLE = "Trabalho"

    def on_mount(self) -> None:
        """Called when the widget is mounted."""
        self.update("Aguardando execução...")
