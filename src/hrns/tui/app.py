"""Main Textual application for the hrns TUI."""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Input

from .widgets import ConversationalPanel, StatusPanel, TasksPanel, WorkPanel
from ..chat import ChatService
from ..chat_history import ChatHistoryService


CSS = """
Screen {
    layout: horizontal;
}

#left-column {
    width: 7fr;
    height: 100%;
    layout: vertical;
}

#right-column {
    width: 3fr;
    height: 100%;
    layout: vertical;
}

ConversationalPanel {
    height: 7fr;
}

StatusPanel {
    height: 3fr;
}

TasksPanel {
    height: 1fr;
}

WorkPanel {
    height: 1fr;
}

StatusPanel Input {
    dock: bottom;
}
"""


class HrnsApp(App):
    """Main hrns Textual application with four-panel layout."""

    CSS = CSS

    BINDINGS = [
        ("ctrl+q", "quit", "Sair"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the four-panel layout."""
        with Horizontal():
            with Vertical(id="left-column"):
                yield ConversationalPanel()
                yield StatusPanel()
            with Vertical(id="right-column"):
                yield TasksPanel()
                yield WorkPanel()

    def on_mount(self) -> None:
        """Initialize services, load history, and focus the input field."""
        self.chat_service = ChatService()
        self.chat_history = ChatHistoryService()

        conversational = self.query_one(ConversationalPanel)
        history = self.chat_history.load_history("default")
        if history:
            conversational.populate(history)

        input_widget = self.query_one("#status-input", Input)
        input_widget.focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input: persist, echo, call LLM, persist response, display."""
        if event.input.id == "status-input" and event.value.strip():
            user_text = event.value
            conversational = self.query_one(ConversationalPanel)

            # Persist user message immediately (RF3).
            self.chat_history.save_message("default", "user", user_text)

            conversational.append_message(user_text, role="user")
            event.input.clear()

            response = await self.chat_service.send(user_text)

            # Only persist the assistant reply when we actually got one (RF4).
            if not response.startswith("[Erro]") and response != "(resposta vazia)":
                self.chat_history.save_message("default", "assistant", response)

            conversational.append_message(response)
