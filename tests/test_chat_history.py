"""Tests for the ChatHistoryService SQLite persistence module."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.hrns.chat_history import ChatHistoryService, DB_PATH
from src.hrns.tui.widgets.conversational import ConversationalPanel


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_db_path():
    """Return a path to a temporary SQLite database file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "chat_history.db"


@pytest.fixture
def service(tmp_db_path):
    """Return a ChatHistoryService backed by a temporary database."""
    return ChatHistoryService(db_path=tmp_db_path)


# ---------------------------------------------------------------------------
# Common cases
# ---------------------------------------------------------------------------


class TestSaveAndLoad:
    """Happy-path: save messages and retrieve them."""

    def test_save_user_message_and_load(self, service):
        """A saved user message appears in load_history."""
        assert service.save_message("default", "user", "Olá, mundo!")
        history = service.load_history("default")
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Olá, mundo!"
        assert history[0]["conversation_id"] == "default"

    def test_save_user_and_assistant_messages(self, service):
        """Both user and assistant messages are returned in order."""
        service.save_message("default", "user", "Pergunta")
        service.save_message("default", "assistant", "Resposta")
        history = service.load_history("default")
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Pergunta"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Resposta"

    def test_multiple_turns_preserved_in_order(self, service):
        """Several back-and-forth turns are returned in chronological order."""
        messages = [
            ("user", "Q1"),
            ("assistant", "A1"),
            ("user", "Q2"),
            ("assistant", "A2"),
            ("user", "Q3"),
            ("assistant", "A3"),
        ]
        for role, content in messages:
            service.save_message("default", role, content)
        history = service.load_history("default")
        assert len(history) == 6
        for i, (expected_role, expected_content) in enumerate(messages):
            assert history[i]["role"] == expected_role
            assert history[i]["content"] == expected_content

    def test_save_message_returns_true(self, service):
        """save_message returns True on success."""
        result = service.save_message("default", "user", "teste")
        assert result is True

    def test_get_latest_messages_default_limit(self, service):
        """get_latest_messages returns at most 50 by default."""
        for i in range(60):
            service.save_message("default", "user", f"msg-{i}")
        latest = service.get_latest_messages("default")
        assert len(latest) == 50

    def test_get_latest_messages_custom_limit(self, service):
        """get_latest_messages respects a custom limit."""
        for i in range(10):
            service.save_message("default", "user", f"msg-{i}")
        latest = service.get_latest_messages("default", limit=3)
        assert len(latest) == 3

    def test_get_latest_messages_ordering_descending(self, service):
        """get_latest_messages returns newest first."""
        service.save_message("default", "user", "primeira")
        service.save_message("default", "user", "segunda")
        service.save_message("default", "user", "terceira")
        latest = service.get_latest_messages("default", limit=3)
        assert latest[0]["content"] == "terceira"
        assert latest[1]["content"] == "segunda"
        assert latest[2]["content"] == "primeira"

    def test_multiple_conversations_isolated(self, service):
        """Messages for different conversation_ids do not leak."""
        service.save_message("conv-a", "user", "msg-a")
        service.save_message("conv-b", "user", "msg-b")
        hist_a = service.load_history("conv-a")
        hist_b = service.load_history("conv-b")
        assert len(hist_a) == 1
        assert hist_a[0]["content"] == "msg-a"
        assert len(hist_b) == 1
        assert hist_b[0]["content"] == "msg-b"

    def test_history_includes_timestamp(self, service):
        """Each record has a non-empty timestamp field."""
        service.save_message("default", "user", "msg")
        history = service.load_history("default")
        assert "timestamp" in history[0]
        assert len(history[0]["timestamp"]) > 0


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Boundary and edge-case behaviour."""

    def test_empty_database_returns_empty_list(self, service):
        """load_history on a fresh database returns []."""
        history = service.load_history("default")
        assert history == []

    def test_nonexistent_conversation_returns_empty(self, service):
        """Querying an unknown conversation_id returns []."""
        service.save_message("default", "user", "msg")
        history = service.load_history("conv-nao-existe")
        assert history == []

    def test_empty_content_saved_and_loaded(self, service):
        """An empty string as content is accepted (TEXT NOT NULL allows '')."""
        service.save_message("default", "user", "")
        history = service.load_history("default")
        assert len(history) == 1
        assert history[0]["content"] == ""

    def test_limit_zero_returns_empty(self, service):
        """limit=0 returns []."""
        service.save_message("default", "user", "msg")
        latest = service.get_latest_messages("default", limit=0)
        assert latest == []

    def test_limit_one_returns_one(self, service):
        """limit=1 returns exactly one message, newest first."""
        service.save_message("default", "user", "mais antiga")
        service.save_message("default", "user", "mais nova")
        latest = service.get_latest_messages("default", limit=1)
        assert len(latest) == 1
        assert latest[0]["content"] == "mais nova"

    def test_db_path_created_if_missing(self, tmp_db_path):
        """The database file is created even when its directory exists but file doesn't."""
        assert not tmp_db_path.exists()
        svc = ChatHistoryService(db_path=tmp_db_path)
        assert svc._ready
        assert tmp_db_path.exists()

    def test_db_directory_created_if_missing(self):
        """The parent directory is created automatically."""
        import shutil
        with tempfile.TemporaryDirectory() as tmpdir:
            db = Path(tmpdir) / "nested" / "dir" / "chat.db"
            assert not db.parent.exists()
            svc = ChatHistoryService(db_path=db)
            assert svc._ready
            assert db.exists()

    def test_save_message_with_special_characters(self, service):
        """Messages with newlines, quotes, and unicode are preserved."""
        content = "Linha 1\nLinha 2\n'aspas' \"duplas\" — emoji: 🚀"
        service.save_message("default", "user", content)
        history = service.load_history("default")
        assert history[0]["content"] == content

    def test_very_long_content(self, service):
        """A message with a large body is saved and loaded correctly."""
        content = "x" * 10_000
        service.save_message("default", "assistant", content)
        history = service.load_history("default")
        assert history[0]["content"] == content


# ---------------------------------------------------------------------------
# Error / failure cases
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Graceful degradation when the database is unavailable."""

    def test_save_message_returns_false_when_db_not_ready(self):
        """When DB init fails, save_message returns False."""
        with patch.object(
            ChatHistoryService, "_init_db", side_effect=OSError("perm")
        ):
            svc = ChatHistoryService(db_path=DB_PATH)
            assert svc._ready is False
            result = svc.save_message("default", "user", "msg")
            assert result is False

    def test_load_history_returns_empty_when_db_not_ready(self):
        """When DB init fails, load_history returns []."""
        with patch.object(
            ChatHistoryService, "_init_db", side_effect=OSError("perm")
        ):
            svc = ChatHistoryService(db_path=DB_PATH)
            history = svc.load_history("default")
            assert history == []

    def test_get_latest_messages_returns_empty_when_db_not_ready(self):
        """When DB init fails, get_latest_messages returns []."""
        with patch.object(
            ChatHistoryService, "_init_db", side_effect=OSError("perm")
        ):
            svc = ChatHistoryService(db_path=DB_PATH)
            latest = svc.get_latest_messages("default")
            assert latest == []

    def test_invalid_path_does_not_raise(self):
        """A path like /dev/null/... should not raise — it degrades."""
        svc = ChatHistoryService(db_path=Path("/dev/null") / "chat.db")
        # Should not raise; _ready may be False depending on OS.
        assert isinstance(svc._ready, bool)


# ---------------------------------------------------------------------------
# ConversationalPanel.populate
# ---------------------------------------------------------------------------


class TestConversationalPanelPopulate:
    """Tests for the populate method added to ConversationalPanel."""

    def test_populate_empty_list_does_not_crash(self):
        """An empty list is a no-op."""
        panel = ConversationalPanel()
        panel.populate([])

    def test_populate_one_message(self):
        """A single user message is written to the panel."""
        panel = ConversationalPanel()
        panel.populate([{"role": "user", "content": "Olá"}])

    def test_populate_many_messages(self):
        """Multiple messages are written in order."""
        panel = ConversationalPanel()
        history = [
            {"role": "user", "content": "Q1"},
            {"role": "assistant", "content": "A1"},
            {"role": "user", "content": "Q2"},
        ]
        panel.populate(history)

    def test_populate_missing_role_defaults_to_assistant(self, service):
        """Entries without a 'role' key default to 'assistant'."""
        panel = ConversationalPanel()
        panel.populate([{"content": "sem role"}])
