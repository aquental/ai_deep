"""Status panel — contains the user input field."""

from textual.widgets import Static, Input


class StatusPanel(Static):
    """Panel that hosts the user input field in the bottom-left area."""

    BORDER_TITLE = "Status"

    def compose(self):
        """Compose the input field."""
        yield Input(placeholder="Digite aqui...", id="status-input")
