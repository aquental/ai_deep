"""Chat service — async wrapper around DeepSeek API with conversation history."""

import os
import logging

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv(override=False)

logger = logging.getLogger("hrns.chat")


class ChatService:
    """Orchestrates chat interactions with the DeepSeek LLM.

    Maintains an in-memory conversation history and provides an async
    ``send`` method that appends user/assistant messages on success.
    """

    def __init__(self) -> None:
        self.api_key: str | None = os.environ.get("DEEPSEEK_API_KEY")
        self.base_url: str = os.environ.get(
            "DEEPSEEK_BASE_URL", "https://api.deepseek.com"
        )
        self.model: str = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
        self._history: list[dict[str, str]] = []
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        """Lazily initialise and return the AsyncOpenAI client."""
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self.api_key, base_url=self.base_url
            )
        return self._client

    @property
    def history(self) -> list[dict[str, str]]:
        """Return a shallow copy of the current conversation history."""
        return list(self._history)

    async def send(self, user_message: str) -> str:
        """Send a user message to the LLM and return the response text.

        On success the user message and assistant reply are appended to the
        internal history.  On failure the history is left unchanged and an
        error string is returned.
        """
        if not self.api_key:
            logger.error("DEEPSEEK_API_KEY não configurada.")
            return "[Erro] DEEPSEEK_API_KEY não configurada."

        # Build provisional message list so history is untouched on failure.
        messages = self._history + [{"role": "user", "content": user_message}]

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
            )
        except Exception as exc:
            logger.error("Falha na chamada ao LLM: %s", exc)
            return f"[Erro] Falha ao contatar o LLM: {exc}"

        content: str | None = response.choices[0].message.content
        if not content:
            logger.warning("LLM retornou resposta vazia.")
            return "(resposta vazia)"

        # Persist the exchange in history.
        self._history = messages + [{"role": "assistant", "content": content}]
        return content
