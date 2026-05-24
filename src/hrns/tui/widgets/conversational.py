"""Conversational panel — displays conversation output."""

from typing import List, Dict

from textual.widgets import RichLog


class ConversationalPanel(RichLog):
    """Panel that displays the conversation output in the top-left area."""

    BORDER_TITLE = "Conversacional"

    def on_mount(self) -> None:
        """Called when the widget is mounted. Write a welcome message."""
        self.write("hrns — Harness para API do DeepSeek")
        self.write("Digite sua mensagem no painel Status abaixo.")

    def append_message(self, text: str, role: str = "assistant") -> None:
        """Append a message to the panel, preserving existing history.

        Args:
            text: The message content.
            role: ``"user"`` (prefixed with ``>``) or ``"assistant"``.
        """
        if role == "user":
            self.write(f"> {text}")
        else:
            self.write(text)

    def populate(self, history: List[Dict]) -> None:
        """Fill the panel with previously persisted messages.

        Each dict in *history* should contain ``role`` and ``content`` keys.
        Unlike ``append_message``, this does **not** write a leading banner.
        """
        for entry in history:
            self.append_message(
                text=entry["content"],
                role=entry.get("role", "assistant"),
            )
