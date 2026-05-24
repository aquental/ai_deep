"""Chat history persistence — SQLite-backed storage for conversation messages."""

import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger("hrns.chat_history")

DB_PATH = Path(".hrns") / "chat_history.db"


class ChatHistoryService:
    """Persists and retrieves chat messages using a local SQLite database.

    The database file is created automatically under ``.hrns/chat_history.db``.
    Errors are logged and surfaced as return values — the service never raises
    on its own, so the TUI can degrade gracefully.
    """

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self._ready = False
        try:
            self._init_db()
            self._ready = True
        except Exception as exc:
            logger.error("Falha ao inicializar banco de dados de histórico: %s", exc)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _init_db(self) -> None:
        """Create the database file, required directories, and the messages table."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT    NOT NULL DEFAULT 'default',
                    role            TEXT    NOT NULL CHECK(role IN ('user', 'assistant')),
                    content         TEXT    NOT NULL,
                    timestamp       TEXT    NOT NULL,
                    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_conversation_id "
                "ON messages(conversation_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)"
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _now_iso() -> str:
        """Return the current UTC time as an ISO-8601 string."""
        return datetime.now(timezone.utc).isoformat()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_message(
        self, conversation_id: str, role: str, content: str
    ) -> bool:
        """Persist a single chat message.

        Returns ``True`` on success, ``False`` when the database is not ready
        or an error occurs (errors are logged).
        """
        if not self._ready:
            logger.warning(
                "Tentativa de salvar mensagem com banco de dados não inicializado."
            )
            return False

        try:
            conn = sqlite3.connect(str(self.db_path))
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO messages "
                    "(conversation_id, role, content, timestamp) "
                    "VALUES (?, ?, ?, ?)",
                    (conversation_id, role, content, self._now_iso()),
                )
                conn.commit()
                return True
            finally:
                conn.close()
        except Exception as exc:
            logger.error("Falha ao salvar mensagem: %s", exc)
            return False

    def load_history(self, conversation_id: str = "default") -> List[Dict]:
        """Load all messages for *conversation_id*, ordered by timestamp ascending.

        Returns an empty list when the database is not ready, the conversation
        has no messages, or an error occurs.
        """
        if not self._ready:
            logger.warning(
                "Tentativa de carregar histórico com banco de dados não inicializado."
            )
            return []

        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM messages "
                    "WHERE conversation_id = ? "
                    "ORDER BY timestamp ASC",
                    (conversation_id,),
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            finally:
                conn.close()
        except Exception as exc:
            logger.error("Falha ao carregar histórico: %s", exc)
            return []

    def get_latest_messages(
        self, conversation_id: str = "default", limit: int = 50
    ) -> List[Dict]:
        """Return the *limit* most recent messages for *conversation_id*.

        Messages are ordered by timestamp descending (newest first).
        """
        if not self._ready:
            logger.warning(
                "Tentativa de obter mensagens recentes com banco de dados "
                "não inicializado."
            )
            return []

        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM messages "
                    "WHERE conversation_id = ? "
                    "ORDER BY timestamp DESC "
                    "LIMIT ?",
                    (conversation_id, limit),
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            finally:
                conn.close()
        except Exception as exc:
            logger.error("Falha ao obter mensagens recentes: %s", exc)
            return []
