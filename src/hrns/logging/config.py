"""
config.py — Configuração centralizada de logging.

Inicializa handlers, formatters e nível global.
Previne duplicação de handlers em reexecuções no mesmo processo.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .formatter import StdFormatter

_CONFIGURED = False


def configure_logging(
    level: str = "INFO",
    log_to_console: bool = True,
    log_to_file: bool = False,
    log_dir: str = "./logs",
    file_name: str = "application.log",
    max_bytes: int = 5_000_000,
    backup_count: int = 5,
) -> None:
    """
    Configura o logging da aplicação.

    Args:
        level: Nível mínimo de severidade (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_to_console: Emite logs para stderr.
        log_to_file: Grava logs em arquivo com rotação por tamanho.
        log_dir: Diretório onde o arquivo de log será criado.
        file_name: Nome do arquivo de log.
        max_bytes: Tamanho máximo antes da rotação (default 5 MB).
        backup_count: Quantidade de arquivos antigos mantidos.
    """
    global _CONFIGURED

    if _CONFIGURED:
        return

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    formatter = StdFormatter()

    if log_to_console:
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        root.addHandler(console)

    if log_to_file:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=str(log_path / file_name),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    _CONFIGURED = True
