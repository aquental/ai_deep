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
from textual.widgets import Footer

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
    """Tests for the StatusPanel widget with tabbed file viewer."""

    def test_instantiation(self):
        """StatusPanel can be instantiated."""
        panel = StatusPanel()
        assert panel is not None
        assert panel.BORDER_TITLE == "Status"

    def test_dirs_has_three_entries(self):
        """StatusPanel.DIRS maps the three .hrns subdirectories."""
        assert len(StatusPanel.DIRS) == 3
        assert StatusPanel.DIRS["skills"] == ".hrns/skills"
        assert StatusPanel.DIRS["context"] == ".hrns/context"
        assert StatusPanel.DIRS["hooks"] == ".hrns/hooks"

    def test_dirs_keys_match_tab_ids(self):
        """DIRS keys match the tab identifiers used in compose."""
        assert set(StatusPanel.DIRS.keys()) == {"skills", "context", "hooks"}


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
        """App has the quit binding and all tab-switching shortcuts."""
        app = HrnsApp()
        bindings = app.BINDINGS
        keys = {b[0] for b in bindings}
        assert "ctrl+q" in keys
        # numeric shortcuts (RF8)
        assert "1" in keys
        assert "2" in keys
        assert "3" in keys
        # letter shortcuts (RF8)
        assert "s" in keys
        assert "c" in keys
        assert "h" in keys

    def test_action_switch_tab_exists(self):
        """action_switch_tab method is defined on HrnsApp."""
        app = HrnsApp()
        assert hasattr(app, "action_switch_tab")
        assert callable(app.action_switch_tab)

    def test_footer_imported_in_app(self):
        """Footer is imported and used in app.py."""
        import inspect
        source = inspect.getsource(HrnsApp.compose)
        assert "Footer" in source
        assert "yield Footer()" in source

    def test_footer_import_in_module(self):
        """Footer is among the app module imports."""
        import src.hrns.tui.app as app_module
        assert "Footer" in app_module.__dict__

    def test_app_css_is_defined(self):
        """App has CSS defined."""
        app = HrnsApp()
        assert app.CSS is not None
        assert "7fr" in app.CSS
        assert "3fr" in app.CSS

    # ------------------------------------------------------------------
    # Border CSS (RF1, RF2, RF3)
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("panel,color", [
        ("ConversationalPanel", "cyan"),
        ("StatusPanel", "green"),
        ("TasksPanel", "yellow"),
        ("WorkPanel", "magenta"),
    ])
    def test_panel_has_border_style(self, panel, color):
        """Each panel CSS block declares a round border with the correct color."""
        app = HrnsApp()
        assert f"border: round {color}" in app.CSS

    @pytest.mark.parametrize("panel,color", [
        ("ConversationalPanel", "cyan"),
        ("StatusPanel", "green"),
        ("TasksPanel", "yellow"),
        ("WorkPanel", "magenta"),
    ])
    def test_panel_has_border_title_color(self, panel, color):
        """Each panel CSS block sets border-title-color."""
        app = HrnsApp()
        assert f"border-title-color: {color}" in app.CSS

    @pytest.mark.parametrize("panel", [
        "ConversationalPanel",
        "StatusPanel",
        "TasksPanel",
        "WorkPanel",
    ])
    def test_panel_has_bold_border_title(self, panel):
        """Each panel uses bold border-title-style."""
        app = HrnsApp()
        assert "border-title-style: bold" in app.CSS

    def test_status_tabs_css_is_defined(self):
        """CSS defines #status-tabs with height: 1fr."""
        app = HrnsApp()
        assert "#status-tabs" in app.CSS
        assert "height: 1fr" in app.CSS

    def test_status_input_has_bottom_dock(self):
        """Input in StatusPanel is docked at bottom with fixed height."""
        app = HrnsApp()
        assert "dock: bottom" in app.CSS
        assert "height: 3" in app.CSS


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
