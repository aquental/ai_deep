"""Tests for the hrns Textual TUI module."""

import pytest
from unittest.mock import patch, MagicMock

from src.hrns.tui.validate import validate_terminal_size, run_tui, MIN_TERMINAL_LINES
from src.hrns.tui.widgets import (
    ConversationalPanel,
    StatusPanel,
    TasksPanel,
    WorkPanel,
)
from src.hrns.tui.app import HrnsApp


# ---------------------------------------------------------------------------
# validate_terminal_size
# ---------------------------------------------------------------------------


class TestValidateTerminalSize:
    """Tests for terminal size validation."""

    def test_terminal_above_minimum_does_not_raise(self):
        """SystemExit not raised when terminal has enough lines."""
        fake_size = MagicMock()
        fake_size.lines = MIN_TERMINAL_LINES + 5
        with patch("src.hrns.tui.validate.get_terminal_size", return_value=fake_size):
            validate_terminal_size()  # should not raise

    def test_terminal_at_minimum_does_not_raise(self):
        """SystemExit not raised when terminal has exactly MIN_TERMINAL_LINES."""
        fake_size = MagicMock()
        fake_size.lines = MIN_TERMINAL_LINES
        with patch("src.hrns.tui.validate.get_terminal_size", return_value=fake_size):
            validate_terminal_size()  # should not raise

    def test_terminal_below_minimum_raises_system_exit(self):
        """SystemExit(1) raised when terminal has fewer lines than minimum."""
        fake_size = MagicMock()
        fake_size.lines = MIN_TERMINAL_LINES - 1
        with patch("src.hrns.tui.validate.get_terminal_size", return_value=fake_size):
            with pytest.raises(SystemExit) as exc_info:
                validate_terminal_size()
            assert exc_info.value.code == 1

    def test_error_message_is_printed(self, capsys):
        """Error message is printed to stdout when terminal is too small."""
        fake_size = MagicMock()
        fake_size.lines = 5
        with patch("src.hrns.tui.validate.get_terminal_size", return_value=fake_size):
            try:
                validate_terminal_size()
            except SystemExit:
                pass
        captured = capsys.readouterr()
        assert "Não é possível iniciar o hrns" in captured.out
        assert "20 linhas" in captured.out

    def test_min_lines_constant_is_20(self):
        """MIN_TERMINAL_LINES equals 20."""
        assert MIN_TERMINAL_LINES == 20


# ---------------------------------------------------------------------------
# Widget instantiation
# ---------------------------------------------------------------------------


class TestConversationalPanel:
    """Tests for the ConversationalPanel widget."""

    def test_instantiation(self):
        """ConversationalPanel can be instantiated."""
        panel = ConversationalPanel()
        assert panel is not None
        assert panel.BORDER_TITLE == "Conversacional"


class TestStatusPanel:
    """Tests for the StatusPanel widget."""

    def test_instantiation(self):
        """StatusPanel can be instantiated."""
        panel = StatusPanel()
        assert panel is not None
        assert panel.BORDER_TITLE == "Status"


class TestTasksPanel:
    """Tests for the TasksPanel widget."""

    def test_instantiation(self):
        """TasksPanel can be instantiated."""
        panel = TasksPanel()
        assert panel is not None
        assert panel.BORDER_TITLE == "Tarefas"


class TestWorkPanel:
    """Tests for the WorkPanel widget."""

    def test_instantiation(self):
        """WorkPanel can be instantiated."""
        panel = WorkPanel()
        assert panel is not None
        assert panel.BORDER_TITLE == "Trabalho"


# ---------------------------------------------------------------------------
# App composition
# ---------------------------------------------------------------------------


class TestHrnsApp:
    """Tests for the main HrnsApp."""

    def test_app_instantiation(self):
        """HrnsApp can be instantiated."""
        app = HrnsApp()
        assert app is not None

    def test_app_css_contains_layout_proportions(self):
        """App CSS defines the 70/30 horizontal layout."""
        app = HrnsApp()
        assert "7fr" in app.CSS
        assert "3fr" in app.CSS
        assert "ConversationalPanel" in app.CSS
        assert "StatusPanel" in app.CSS
        assert "TasksPanel" in app.CSS
        assert "WorkPanel" in app.CSS

    def test_app_has_bindings(self):
        """App has the quit binding."""
        app = HrnsApp()
        bindings = app.BINDINGS
        assert any(binding[0] == "ctrl+q" for binding in bindings)

    def test_app_css_is_defined(self):
        """App has CSS defined."""
        app = HrnsApp()
        assert app.CSS is not None
        assert "7fr" in app.CSS
        assert "3fr" in app.CSS


# ---------------------------------------------------------------------------
# run_tui integration
# ---------------------------------------------------------------------------


class TestRunTui:
    """Tests for the run_tui entry point."""

    def test_run_tui_validates_before_launch(self):
        """run_tui validates terminal size before launching the app."""
        fake_size = MagicMock()
        fake_size.lines = 5  # below minimum
        with patch("src.hrns.tui.validate.get_terminal_size", return_value=fake_size):
            with pytest.raises(SystemExit):
                run_tui()

    def test_run_tui_imports_app(self):
        """run_tui does not raise ImportError for HrnsApp."""
        fake_size = MagicMock()
        fake_size.lines = MIN_TERMINAL_LINES + 10
        with patch("src.hrns.tui.validate.get_terminal_size", return_value=fake_size):
            with patch("src.hrns.tui.app.HrnsApp.run"):
                run_tui()  # should not raise
