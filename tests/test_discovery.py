"""
Testes para src/hrns/discovery.py — list_files()

Cobre os critérios de aceitação do PRD:
- Listagem correta dos diretórios skills, hooks, contexts
- Filtragem de subdiretórios (apenas arquivos)
- Lista vazia para diretórios sem arquivos
- Erro claro para diretórios inexistentes
- Erro claro para caminhos que não são diretórios
- Ordenação determinística
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

from src.hrns.discovery import list_files
from src.hrns import list_files as list_files_public


@pytest.fixture
def tmp_workspace():
    """Cria um diretório temporário isolado para cada teste."""
    original = os.getcwd()
    tmpdir = tempfile.mkdtemp(prefix="hrns_discovery_test_")
    os.chdir(tmpdir)
    yield Path(tmpdir)
    os.chdir(original)
    shutil.rmtree(tmpdir)


@pytest.fixture
def hrns_dirs(tmp_workspace):
    """Cria a estrutura .hrns/ com arquivos de exemplo em cada subdiretório."""
    base = Path(".hrns")
    for sub in ["skills", "hooks", "contexts"]:
        (base / sub).mkdir(parents=True)

    # skills: 2 arquivos
    (base / "skills" / "load_context.py").write_text("")
    (base / "skills" / "register_tools.py").write_text("")

    # hooks: 1 arquivo
    (base / "hooks" / "pre_commit.py").write_text("")

    # contexts: 3 arquivos
    (base / "contexts" / "auth.py").write_text("")
    (base / "contexts" / "db.py").write_text("")
    (base / "contexts" / "cache.py").write_text("")

    return base


# ── Critérios de aceitação ──────────────────────────────────────────


def test_lista_skills(hrns_dirs):
    """A função deve listar corretamente todos os arquivos de .hrns/skills."""
    files = list_files(".hrns/skills")
    names = [Path(f).name for f in files]

    assert len(files) == 2
    assert names == ["load_context.py", "register_tools.py"]


def test_lista_hooks(hrns_dirs):
    """A função deve listar corretamente todos os arquivos de .hrns/hooks."""
    files = list_files(".hrns/hooks")
    names = [Path(f).name for f in files]

    assert len(files) == 1
    assert names == ["pre_commit.py"]


def test_lista_contexts(hrns_dirs):
    """A função deve listar corretamente todos os arquivos de .hrns/contexts."""
    files = list_files(".hrns/contexts")
    names = [Path(f).name for f in files]

    assert len(files) == 3
    assert names == ["auth.py", "cache.py", "db.py"]


def test_nao_retorna_subdiretorios(hrns_dirs):
    """A função não deve retornar subdiretórios, apenas arquivos."""
    # Adiciona um subdiretório dentro de skills
    (Path(".hrns/skills/sub_plugin")).mkdir()

    files = list_files(".hrns/skills")
    names = [Path(f).name for f in files]

    assert "sub_plugin" not in names
    assert len(files) == 2  # apenas os 2 arquivos originais


def test_diretorio_vazio_retorna_lista_vazia(tmp_workspace):
    """Para diretórios válidos sem arquivos, retorna lista vazia."""
    Path("empty_dir").mkdir()

    result = list_files("empty_dir")
    assert result == []


def test_diretorio_inexistente_lanca_erro(tmp_workspace):
    """Deve lançar FileNotFoundError para diretórios inexistentes."""
    with pytest.raises(FileNotFoundError, match="não encontrado"):
        list_files("diretorio_que_nao_existe")


def test_caminho_nao_e_diretorio_lanca_erro(tmp_workspace):
    """Deve lançar NotADirectoryError se o caminho for um arquivo."""
    Path("arquivo.txt").write_text("conteúdo")

    with pytest.raises(NotADirectoryError, match="não é um diretório"):
        list_files("arquivo.txt")


def test_ordenacao_deterministica(tmp_workspace):
    """O retorno deve ser ordenado de forma consistente entre execuções."""
    d = Path("mixed")
    d.mkdir()

    # Cria arquivos em ordem não-alfabética
    (d / "zebra.txt").write_text("")
    (d / "alpha.txt").write_text("")
    (d / "gamma.txt").write_text("")
    (d / "beta.txt").write_text("")

    first = list_files("mixed")
    second = list_files("mixed")

    assert first == second
    assert first == sorted(first)
    names = [Path(f).name for f in first]
    assert names == ["alpha.txt", "beta.txt", "gamma.txt", "zebra.txt"]


def test_diretorio_vazio_sem_subdiretorios(tmp_workspace):
    """Diretório com apenas subdiretórios deve retornar lista vazia."""
    d = Path("only_dirs")
    d.mkdir()
    (d / "sub_a").mkdir()
    (d / "sub_b").mkdir()

    result = list_files("only_dirs")
    assert result == []


def test_retorno_str_ordenado(tmp_workspace):
    """O retorno deve ser uma lista de strings ordenadas."""
    d = Path("files")
    d.mkdir()
    (d / "b.txt").write_text("")
    (d / "a.txt").write_text("")

    result = list_files("files")

    assert isinstance(result, list)
    assert all(isinstance(f, str) for f in result)
    assert result == sorted(result)


def test_importacao_publica():
    """list_files deve estar disponível no namespace público do pacote."""
    assert callable(list_files_public)
