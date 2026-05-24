"""
structure.py — Criação idempotente da estrutura de diretórios .hrns/

Cria os subdiretórios skills, context e hooks dentro do diretório base padrão.
"""

from pathlib import Path

BASE = ".hrns"
REQUIRED_DIRS = ["skills", "context", "hooks"]


def create_structure(base_path: str = BASE) -> dict:
    """
    Garante a existência da árvore de diretórios sob `base_path`.

    Cria o diretório base e os subdiretórios skills, context, hooks.
    Seguro para reexecução: diretórios já existentes são preservados.

    Returns:
        dict com chaves:
            - base_path (str): caminho base utilizado
            - created (list[str]): diretórios criados nesta chamada
            - existing (list[str]): diretórios que já existiam
            - success (bool): True se a operação concluiu sem erros
    """
    base = Path(base_path)
    base.mkdir(parents=True, exist_ok=True)

    created = []
    existing = []

    for name in REQUIRED_DIRS:
        path = base / name
        if path.exists():
            existing.append(name)
        else:
            path.mkdir(parents=True, exist_ok=True)
            created.append(name)

    return {
        "base_path": str(base),
        "created": created,
        "existing": existing,
        "success": True,
    }
