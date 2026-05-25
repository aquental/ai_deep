"""Status panel — file viewer tabs (skills/context/hooks) + chat input."""

from pathlib import Path

import frontmatter
from textual.containers import Vertical
from textual.widgets import (
    Input,
    Label,
    ListItem,
    ListView,
    TabbedContent,
    TabPane,
)

from ...discovery import list_files


class StatusPanel(Vertical):
    """Bottom-left panel with three tabs (skills, context, hooks) listing
    files from ``.hrns/`` and a docked chat input."""

    BORDER_TITLE = "Status"

    DIRS: dict[str, str] = {
        "skills": ".hrns/skills",
        "context": ".hrns/context",
        "hooks": ".hrns/hooks",
    }

    def compose(self):
        """Compose the tabbed file viewer and the chat input."""
        with TabbedContent(id="status-tabs"):
            for tab_id in self.DIRS:
                with TabPane(tab_id, id=tab_id):
                    yield ListView(id=f"{tab_id}-list")
        yield Input(placeholder="Digite aqui...", id="status-input")

    def on_mount(self) -> None:
        """Populate each tab with files from the corresponding directory."""
        for tab_id, dir_path in self.DIRS.items():
            self._populate_tab(tab_id, dir_path)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _populate_tab(self, tab_id: str, dir_path: str) -> None:
        """Fill *tab_id*'s ListView with file names (or an empty-directory
        message).  The skills tab reads YAML frontmatter for display names."""
        list_view = self.query_one(f"#{tab_id}-list", ListView)
        list_view.clear()

        try:
            files = list_files(dir_path)
        except FileNotFoundError:
            list_view.append(
                ListItem(Label(f"nao existem arquivos em {dir_path}"))
            )
            return

        if not files:
            list_view.append(
                ListItem(Label(f"nao existem arquivos em {dir_path}"))
            )
            return

        for fname in files:
            if tab_id == "skills":
                display = self._get_skill_display_name(fname)
            else:
                display = Path(fname).name
            list_view.append(ListItem(Label(display)))

    # ------------------------------------------------------------------
    # frontmatter (skills tab)
    # ------------------------------------------------------------------

    @staticmethod
    def _get_skill_display_name(file_path: str) -> str:
        """Return a human-readable label for a skill file.

        When the file contains YAML frontmatter with a ``nome`` field the
        result is ``"filename - nome"``.  Otherwise only the file name is
        returned.  Any read / parse error is silently swallowed — the bare
        file name is used as a fallback.
        """
        fname = Path(file_path).name
        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                content = fh.read()
        except Exception:
            return fname

        try:
            metadata, _ = frontmatter.parse(content)
        except Exception:
            return fname

        # Accept both Portuguese ("nome") and English ("name") keys (RF2 / RF5).
        if isinstance(metadata, dict):
            nome = metadata.get("nome") or metadata.get("name")
            if nome:
                return f"{fname} - {nome}"
        return fname
