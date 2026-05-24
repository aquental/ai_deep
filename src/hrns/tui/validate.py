"""Terminal size validation for the hrns Textual TUI."""

from shutil import get_terminal_size

MIN_TERMINAL_LINES = 20


def validate_terminal_size() -> None:
    """Check if the terminal meets the minimum height requirement.

    Raises SystemExit(1) with a user-friendly message if the terminal
    has fewer than MIN_TERMINAL_LINES lines.
    """
    size = get_terminal_size()
    if size.lines < MIN_TERMINAL_LINES:
        print(
            "Não é possível iniciar o hrns: "
            "o terminal precisa ter pelo menos 20 linhas."
        )
        raise SystemExit(1)


def run_tui() -> None:
    """Entry point for the hrns Textual TUI.

    Validates terminal size and then launches the Textual application.
    """
    validate_terminal_size()
    from .app import HrnsApp
    app = HrnsApp()
    app.run()
