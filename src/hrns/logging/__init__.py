"""
hrns.logging — Módulo de logging robusto.

Configuração centralizada, formato padronizado, saída em console
e arquivo com rotação.
"""

from .config import configure_logging
from .logger import get_logger

__all__ = ["configure_logging", "get_logger"]
