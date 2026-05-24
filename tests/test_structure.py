"""
Testes para src/hrns/structure.py — create_structure()

Cobre os critérios de aceitação do PRD:
- Criação limpa da estrutura
- Idempotência (reexecução segura)
- Cenário de existência parcial
- Customização do base_path
- Preservação de conteúdo pré-existente
- Formato do retorno
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

from src.hrns.structure import BASE, REQUIRED_DIRS, create_structure


@pytest.fixture
def tmp_workspace():
    """Cria um diretório temporário isolado para cada teste."""
    original = os.getcwd()
    tmpdir = tempfile.mkdtemp(prefix="hrns_test_")
    os.chdir(tmpdir)
    yield Path(tmpdir)
    os.chdir(original)
    shutil.rmtree(tmpdir)


# ── Critérios de aceitação ──────────────────────────────────────────


def test_cria_estrutura_completa_do_zero(tmp_workspace):
    """
    Ao executar em um diretório sem .hrns, a pasta base e os 3
    subdiretórios devem ser criados com sucesso.
    """
    result = create_structure()

    assert result["success"] is True
    assert result["base_path"] == ".hrns"
    assert sorted(result["created"]) == sorted(REQUIRED_DIRS)
    assert result["existing"] == []

    # Verifica no disco
    base = Path(".hrns")
    assert base.is_dir()
    for name in REQUIRED_DIRS:
        assert (base / name).is_dir()


def test_idempotencia(tmp_workspace):
    """
    Executar novamente no mesmo local não deve falhar e não deve
    recriar diretórios já existentes.
    """
    # Primeira execução
    create_structure()

    # Segunda execução
    result = create_structure()

    assert result["success"] is True
    assert result["created"] == []
    assert sorted(result["existing"]) == sorted(REQUIRED_DIRS)

    # Estrutura permanece intacta
    base = Path(".hrns")
    assert base.is_dir()
    for name in REQUIRED_DIRS:
        assert (base / name).is_dir()


def test_existencia_parcial(tmp_workspace):
    """
    Se alguns diretórios já existirem e outros não, o módulo cria
    apenas os ausentes e reporta corretamente.
    """
    base = Path(".hrns")
    base.mkdir()
    (base / "skills").mkdir()  # já existe

    # context e hooks não existem
    result = create_structure()

    assert result["success"] is True
    assert "skills" not in result["created"]
    assert "skills" in result["existing"]
    assert "context" in result["created"]
    assert "hooks" in result["created"]


def test_retorno_estruturado(tmp_workspace):
    """
    O retorno deve conter as chaves esperadas com tipos corretos.
    """
    result = create_structure()

    assert isinstance(result, dict)
    assert "base_path" in result
    assert "created" in result
    assert "existing" in result
    assert "success" in result

    assert isinstance(result["base_path"], str)
    assert isinstance(result["created"], list)
    assert isinstance(result["existing"], list)
    assert isinstance(result["success"], bool)


def test_base_path_customizado(tmp_workspace):
    """
    A função deve aceitar um base_path diferente do padrão.
    """
    custom = ".custom_hrns"
    result = create_structure(base_path=custom)

    assert result["success"] is True
    assert result["base_path"] == custom
    assert Path(custom).is_dir()

    for name in REQUIRED_DIRS:
        assert (Path(custom) / name).is_dir()


def test_preserva_conteudo_preexistente(tmp_workspace):
    """
    Diretórios que já existem não devem ser alterados; conteúdo
    interno deve ser preservado após reexecução.
    """
    base = Path(".hrns")
    base.mkdir()
    (base / "hooks").mkdir()

    # Cria um arquivo dentro de hooks
    marker = base / "hooks" / "keep.me"
    marker.write_text("conteúdo original")

    result = create_structure()

    assert result["success"] is True
    assert marker.exists()
    assert marker.read_text() == "conteúdo original"


def test_nao_cria_fora_do_base_path(tmp_workspace):
    """
    O módulo não deve criar diretórios fora do caminho base informado.
    """
    create_structure()

    # Lista tudo que foi criado no workspace
    all_items = set(os.listdir(tmp_workspace))
    # Só .hrns deve existir na raiz, e possivelmente __pycache__ ou .pytest_cache
    allowed_extras = {"__pycache__", ".pytest_cache"}
    unexpected = all_items - {".hrns", *allowed_extras}

    assert unexpected == set(), f"Diretórios inesperados na raiz: {unexpected}"
