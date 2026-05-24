"""
discovery.py — Descoberta de arquivos em diretórios de configuração.

Função genérica para listar arquivos de um diretório, reutilizável
para .hrns/skills, .hrns/hooks e .hrns/contexts.
"""

from pathlib import Path


def list_files(directory: str) -> list[str]:
    """
    Lista todos os arquivos regulares em `directory`, ordenados.

    Args:
        directory: Caminho do diretório a ser inspecionado.

    Returns:
        Lista ordenada de caminhos (str) dos arquivos encontrados.

    Raises:
        FileNotFoundError: Se o diretório não existir.
        NotADirectoryError: Se o caminho não for um diretório.
    """
    path = Path(directory)

    if not path.exists():
        raise FileNotFoundError(f"Diretório não encontrado: {directory}")

    if not path.is_dir():
        raise NotADirectoryError(f"Caminho não é um diretório: {directory}")

    files = [str(item) for item in path.iterdir() if item.is_file()]
    return sorted(files)
