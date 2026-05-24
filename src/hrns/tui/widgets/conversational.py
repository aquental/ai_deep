"""Conversational panel — displays conversation output."""

from textual.widgets import RichLog


class ConversationalPanel(RichLog):
    """Panel that displays the conversation output in the top-left area."""

    BORDER_TITLE = "Conversacional"

    def on_mount(self) -> None:
        """Called when the widget is mounted. Write a welcome message."""
        self.write("hrns — Harness para API do DeepSeek")
        self.write("Digite sua mensagem no painel Status abaixo.")
