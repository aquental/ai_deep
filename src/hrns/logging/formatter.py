"""
formatter.py — Formatador padronizado para logs.

Formato: 2026-05-24 16:48:00 | INFO | api.auth | mensagem
"""

import logging

FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class StdFormatter(logging.Formatter):
    """Formatador com timestamp, nível, logger e mensagem separados por pipe."""

    def __init__(self):
        super().__init__(fmt=FORMAT, datefmt=DATE_FORMAT)
