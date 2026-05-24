"""
logger.py — Fábrica de loggers nomeados.

Cada módulo da aplicação obtém um logger com identidade própria.
"""

import logging


def get_logger(name: str) -> logging.Logger:
    """
    Retorna um logger nomeado.

    O logger herda a configuração global definida por configure_logging().
    Nenhum handler é adicionado aqui — isso evita duplicidade.
    """
    return logging.getLogger(name)
