"""Main Textual application for the hrns TUI."""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Input

from .widgets import ConversationalPanel, StatusPanel, TasksPanel, WorkPanel


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
        """Focus the input field on startup."""
        input_widget = self.query_one("#status-input", Input)
        input_widget.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input submission: write to conversational panel."""
        if event.input.id == "status-input" and event.value.strip():
            conversational = self.query_one(ConversationalPanel)
            conversational.write(f"> {event.value}")
            event.input.clear()
