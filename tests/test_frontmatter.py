"""Tests for frontmatter reading in the StatusPanel skills tab."""

import tempfile
from pathlib import Path

import pytest

from src.hrns.tui.widgets.status import StatusPanel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_skill(dir_path: Path, name: str, content: str) -> Path:
    """Write *content* to *name* inside *dir_path* and return the full path."""
    file_path = dir_path / name
    file_path.write_text(content, encoding="utf-8")
    return file_path


# ---------------------------------------------------------------------------
# Common cases
# ---------------------------------------------------------------------------


class TestSkillDisplayName:
    """Happy-path: files with valid frontmatter ``nome`` field."""

    def test_file_with_nome_shows_display_name(self, tmp_path):
        """A file with a ``nome`` field returns ``filename - nome``."""
        content = """---
nome: Carregar Contexto
description: Carrega o contexto do projeto
trigger: on_load
---
# Conteúdo da skill
"""
        path = _write_skill(tmp_path, "carregar_contexto.py", content)
        result = StatusPanel._get_skill_display_name(str(path))
        assert result == "carregar_contexto.py - Carregar Contexto"

    def test_file_with_nome_and_unicode(self, tmp_path):
        """Unicode in ``nome`` is preserved."""
        content = """---
nome: Ação Rápida 🚀
---
"""
        path = _write_skill(tmp_path, "acao.py", content)
        result = StatusPanel._get_skill_display_name(str(path))
        assert result == "acao.py - Ação Rápida 🚀"

    def test_file_with_english_name_key(self, tmp_path):
        """The English ``name`` key is accepted as an alias for ``nome``."""
        content = """---
name: Load Context
description: Loads project context
trigger: on_load
---
"""
        path = _write_skill(tmp_path, "load_context.py", content)
        result = StatusPanel._get_skill_display_name(str(path))
        assert result == "load_context.py - Load Context"

    def test_multiple_skills_with_different_names(self, tmp_path):
        """Multiple files each get their own display name."""
        content_a = '---\nnome: Skill A\n---\n'
        content_b = '---\nnome: Skill B\n---\n'
        path_a = _write_skill(tmp_path, "a.py", content_a)
        path_b = _write_skill(tmp_path, "b.py", content_b)
        assert StatusPanel._get_skill_display_name(str(path_a)) == "a.py - Skill A"
        assert StatusPanel._get_skill_display_name(str(path_b)) == "b.py - Skill B"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestSkillDisplayNameEdgeCases:
    """Boundary and edge-case behaviour."""

    def test_file_without_frontmatter_shows_filename_only(self, tmp_path):
        """A plain text file returns only the file name."""
        path = _write_skill(tmp_path, "plain.py", "print('hello')")
        result = StatusPanel._get_skill_display_name(str(path))
        assert result == "plain.py"

    def test_file_with_frontmatter_but_no_nome_field(self, tmp_path):
        """Frontmatter without ``nome`` falls back to file name."""
        content = """---
description: apenas descrição
trigger: manual
---
"""
        path = _write_skill(tmp_path, "skill.py", content)
        result = StatusPanel._get_skill_display_name(str(path))
        assert result == "skill.py"

    def test_file_with_empty_frontmatter(self, tmp_path):
        """Empty frontmatter ``---\\n---`` falls back to file name."""
        content = "---\n---\n# corpo\n"
        path = _write_skill(tmp_path, "empty_frontmatter.md", content)
        result = StatusPanel._get_skill_display_name(str(path))
        assert result == "empty_frontmatter.md"

    def test_file_with_invalid_yaml_frontmatter(self, tmp_path):
        """Malformed YAML frontmatter is tolerated — returns file name."""
        content = "---\n[invalid: yaml: [\n---\n"
        path = _write_skill(tmp_path, "bad.yaml", content)
        result = StatusPanel._get_skill_display_name(str(path))
        assert result == "bad.yaml"

    def test_empty_file(self, tmp_path):
        """An empty file returns the file name."""
        path = _write_skill(tmp_path, "empty.py", "")
        result = StatusPanel._get_skill_display_name(str(path))
        assert result == "empty.py"

    def test_markdown_file_with_frontmatter(self, tmp_path):
        """Markdown files with frontmatter are supported."""
        content = """---
nome: Guia de Uso
---
# Guia

Conteúdo em markdown.
"""
        path = _write_skill(tmp_path, "guia.md", content)
        result = StatusPanel._get_skill_display_name(str(path))
        assert result == "guia.md - Guia de Uso"

    def test_file_with_only_nome_surrounded_by_whitespace(self, tmp_path):
        """``nome`` value with surrounding spaces is used as-is."""
        content = "---\nnome:   Espaçado   \n---\n"
        path = _write_skill(tmp_path, "spaced.py", content)
        result = StatusPanel._get_skill_display_name(str(path))
        # YAML strips leading/trailing whitespace from unquoted scalars.
        assert result == "spaced.py - Espaçado"

    def test_file_name_with_special_characters(self, tmp_path):
        """File names with dots, hyphens, underscores are preserved."""
        content = '---\nnome: Teste\n---\n'
        path = _write_skill(tmp_path, "my-skill.v2.py", content)
        result = StatusPanel._get_skill_display_name(str(path))
        assert result == "my-skill.v2.py - Teste"


# ---------------------------------------------------------------------------
# Error / failure cases
# ---------------------------------------------------------------------------


class TestSkillDisplayNameErrors:
    """Graceful handling when the file system misbehaves."""

    def test_nonexistent_file_returns_filename(self):
        """A path that does not exist returns just the file name."""
        result = StatusPanel._get_skill_display_name("/tmp/nao_existe_xyz.py")
        assert result == "nao_existe_xyz.py"

    def test_path_is_directory_returns_name(self, tmp_path):
        """Passing a directory returns the directory name."""
        result = StatusPanel._get_skill_display_name(str(tmp_path))
        assert result == tmp_path.name

    def test_file_with_binary_content(self, tmp_path):
        """A binary file should not crash — returns file name."""
        path = tmp_path / "binary.bin"
        path.write_bytes(b"\x00\x01\x02\xff\xfe")
        result = StatusPanel._get_skill_display_name(str(path))
        assert result == "binary.bin"
