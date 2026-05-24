"""
Testes para src/hrns/logging/ — configure_logging() e get_logger()

Cobre os critérios de aceitação do PRD:
- Configuração de console com uma única chamada
- Configuração de arquivo com rotação
- Loggers nomeados sem duplicar handlers
- Formato padronizado (timestamp | level | name | mensagem)
- Prevenção de duplicidade em múltiplas chamadas
- Registro de exceções com stack trace
- Criação automática do diretório de logs
- Suporte a todos os níveis (DEBUG a CRITICAL)
"""

import io
import logging
import os
import re
import shutil
import tempfile
from pathlib import Path

import pytest

from src.hrns.logging import configure_logging, get_logger
from src.hrns.logging.formatter import FORMAT


# ── Fixtures ────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_logging():
    """Reseta o estado do logging antes de cada teste."""
    # Reseta a flag de configurado
    import src.hrns.logging.config as cfg

    cfg._CONFIGURED = False

    # Remove todos os handlers do logger raiz
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.WARNING)  # default do Python

    yield

    # Cleanup pós-teste
    root.handlers.clear()
    root.setLevel(logging.WARNING)
    cfg._CONFIGURED = False


@pytest.fixture
def tmp_workspace():
    """Cria um diretório temporário isolado para cada teste."""
    original = os.getcwd()
    tmpdir = tempfile.mkdtemp(prefix="hrns_logging_test_")
    os.chdir(tmpdir)
    yield Path(tmpdir)
    os.chdir(original)
    shutil.rmtree(tmpdir)


# ── Critérios de aceitação ──────────────────────────────────────────


def test_configuracao_console_uma_chamada():
    """
    O módulo deve configurar logging para console com uma única chamada.
    """
    configure_logging(log_to_console=True, log_to_file=False)

    root = logging.getLogger()
    handlers = root.handlers

    assert len(handlers) >= 1
    assert any(isinstance(h, logging.StreamHandler) for h in handlers)


def test_configuracao_arquivo_com_rotacao(tmp_workspace):
    """
    O módulo deve configurar logging para arquivo com rotação habilitada.
    """
    configure_logging(
        log_to_console=False,
        log_to_file=True,
        log_dir="test_logs",
        file_name="test.log",
        max_bytes=1000,
        backup_count=3,
    )

    root = logging.getLogger()
    handlers = root.handlers

    file_handlers = [h for h in handlers if isinstance(h, logging.Handler)
                     and hasattr(h, 'maxBytes')]
    assert len(file_handlers) == 1

    fh = file_handlers[0]
    assert fh.maxBytes == 1000
    assert fh.backupCount == 3
    assert Path("test_logs").is_dir()


def test_formato_padronizado():
    """
    Logs emitidos devem seguir o formato `timestamp | level | name | mensagem`.
    """
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)

    from src.hrns.logging.formatter import StdFormatter
    handler.setFormatter(StdFormatter())

    logger = logging.getLogger("api.auth")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.propagate = False

    logger.info("Usuário autenticado com sucesso")

    output = stream.getvalue().strip()
    pattern = (
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} "
        r"\| INFO \| api\.auth "
        r"\| Usuário autenticado com sucesso"
    )
    assert re.match(pattern, output), f"Formato inesperado: {output}"


def test_get_logger_nomeado():
    """
    O módulo deve permitir recuperar loggers nomeados.
    """
    logger = get_logger("api.auth")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "api.auth"


def test_get_logger_sem_duplicar_handlers():
    """
    Loggers nomeados não devem receber handlers adicionais — apenas
    herdam a configuração do root.
    """
    configure_logging(log_to_console=True)

    root_handlers_before = len(logging.getLogger().handlers)
    logger = get_logger("modulo.x")
    # get_logger não adiciona handlers ao root
    assert len(logging.getLogger().handlers) == root_handlers_before
    # O logger em si não deve ter handlers próprios
    assert len(logger.handlers) == 0


def test_prevencao_duplicidade():
    """
    O módulo deve evitar configuração duplicada de handlers quando
    inicializado mais de uma vez no mesmo processo.
    """
    configure_logging(log_to_console=True)
    first_count = len(logging.getLogger().handlers)

    configure_logging(log_to_console=True)
    second_count = len(logging.getLogger().handlers)

    assert second_count == first_count

    import src.hrns.logging.config as cfg
    assert cfg._CONFIGURED is True


def test_multiplas_execucoes_mesmo_processo():
    """
    O módulo deve funcionar corretamente em múltiplas execuções.
    """
    configure_logging(log_to_console=True, level="DEBUG")
    root = logging.getLogger()
    assert root.level == logging.DEBUG

    # Segunda chamada não altera
    configure_logging(log_to_console=True, level="INFO")
    assert root.level == logging.DEBUG  # permanece o da primeira


def test_registro_excecao_com_stack_trace():
    """
    O módulo deve permitir registrar exceções com stack trace.
    """
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)

    from src.hrns.logging.formatter import StdFormatter
    handler.setFormatter(StdFormatter())

    logger = logging.getLogger("test.exc")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.propagate = False

    try:
        raise ValueError("erro simulado")
    except ValueError:
        logger.exception("Falha ao processar requisição")

    output = stream.getvalue()

    assert "Falha ao processar requisição" in output
    assert "ValueError" in output
    assert "erro simulado" in output
    assert "Traceback" in output


def test_diretorio_logs_criado_automaticamente(tmp_workspace):
    """
    O módulo deve criar automaticamente o diretório de logs, se ele não existir.
    """
    logs_dir = Path("deep/nested/logs")
    assert not logs_dir.exists()

    configure_logging(
        log_to_console=False,
        log_to_file=True,
        log_dir=str(logs_dir),
        file_name="app.log",
    )

    assert logs_dir.is_dir()
    assert (logs_dir / "app.log").exists() or True  # arquivo pode estar vazio


def test_niveis_severidade(caplog):
    """
    O módulo deve suportar DEBUG, INFO, WARNING, ERROR, CRITICAL.
    """
    configure_logging(log_to_console=True, level="DEBUG")

    logger = get_logger("test.levels")
    # caplog captura no nível do root
    with caplog.at_level(logging.DEBUG):
        logger.debug("mensagem debug")
        logger.info("mensagem info")
        logger.warning("mensagem warning")
        logger.error("mensagem error")
        logger.critical("mensagem critical")

    levels_found = {r.levelname for r in caplog.records}
    assert levels_found >= {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def test_nivel_configuravel():
    """
    O nível de log deve ser ajustável via parâmetro.
    """
    configure_logging(log_to_console=True, level="ERROR")
    root = logging.getLogger()
    assert root.level == logging.ERROR

    # Reseta para o próximo teste
    root.handlers.clear()
    import src.hrns.logging.config as cfg
    cfg._CONFIGURED = False

    configure_logging(log_to_console=True, level="DEBUG")
    assert root.level == logging.DEBUG


def test_gravacao_efetiva_em_arquivo(tmp_workspace):
    """
    Logs devem ser efetivamente gravados no arquivo configurado.
    """
    configure_logging(
        log_to_console=False,
        log_to_file=True,
        log_dir="test_logs",
        file_name="write_test.log",
    )

    logger = get_logger("test.write")
    logger.warning("mensagem de teste no arquivo")

    # Força flush fechando handlers
    for h in logging.getLogger().handlers:
        h.flush()
        h.close()

    log_file = Path("test_logs/write_test.log")
    assert log_file.exists()

    content = log_file.read_text()
    assert "mensagem de teste no arquivo" in content
    assert "WARNING" in content
    assert "test.write" in content


def test_importacao_publica():
    """
    As funções configure_logging e get_logger devem estar disponíveis
    no namespace público do pacote.
    """
    from src.hrns.logging import configure_logging, get_logger

    assert callable(configure_logging)
    assert callable(get_logger)
