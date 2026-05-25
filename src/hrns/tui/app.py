"""Main Textual application for the hrns TUI."""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Footer, Input, TabbedContent

from .widgets import ConversationalPanel, StatusPanel, TasksPanel, WorkPanel
from ..chat import ChatService
from ..chat_history import ChatHistoryService
from ..logging import configure_logging


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
    border: round cyan;
    border-title-color: cyan;
    border-title-style: bold;
}

StatusPanel {
    height: 3fr;
    border: round green;
    border-title-color: green;
    border-title-style: bold;
}

TasksPanel {
    height: 1fr;
    border: round yellow;
    border-title-color: yellow;
    border-title-style: bold;
}

WorkPanel {
    height: 1fr;
    border: round magenta;
    border-title-color: magenta;
    border-title-style: bold;
}

#status-tabs {
    height: 1fr;
}

StatusPanel Input {
    dock: bottom;
    height: 3;
}
"""


class HrnsApp(App):
    """Main hrns Textual application with four-panel layout."""

    CSS = CSS

    BINDINGS = [
        ("ctrl+q", "quit", "Sair"),
        ("1", "switch_tab('skills')", "Skills (1)"),
        ("2", "switch_tab('context')", "Context (2)"),
        ("3", "switch_tab('hooks')", "Hooks (3)"),
        ("s", "switch_tab('skills')", "Skills"),
        ("c", "switch_tab('context')", "Context"),
        ("h", "switch_tab('hooks')", "Hooks"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the four-panel layout."""
        yield Footer()
        with Horizontal():
            with Vertical(id="left-column"):
                yield ConversationalPanel()
                yield StatusPanel()
            with Vertical(id="right-column"):
                yield TasksPanel()
                yield WorkPanel()

    def on_mount(self) -> None:
        """Initialize services, load history, and focus the input field."""
        # Configure logging so errors are captured on stderr.
        configure_logging(level="INFO", log_to_console=True)

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
        if event.input.id != "status-input" or not event.value.strip():
            return

        user_text = event.value
        conversational = self.query_one(ConversationalPanel)
        input_widget = event.input

        # Persist user message immediately (RF3).
        self.chat_history.save_message("default", "user", user_text)

        conversational.append_message(user_text, role="user")
        input_widget.clear()

        # Block concurrent sends and show loading indicator.
        input_widget.disabled = True
        conversational.write("⏳ Aguardando resposta do LLM...")

        try:
            response = await self.chat_service.send(user_text)

            # Only persist the assistant reply when we actually got one (RF4).
            if not response.startswith("[Erro]") and response != "(resposta vazia)":
                self.chat_history.save_message("default", "assistant", response)

            conversational.append_message(response)
        finally:
            # Re-enable input regardless of outcome.
            input_widget.disabled = False
            input_widget.focus()

    # ------------------------------------------------------------------
    # Tab navigation (RF1, RF2, RF8)
    # ------------------------------------------------------------------

    def action_switch_tab(self, tab_id: str) -> None:
        """Switch the active tab in the StatusPanel."""
        tabbed = self.query_one("#status-tabs", TabbedContent)
        tabbed.active = tab_id
