from __future__ import annotations

from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent

# As rotas só existem com o extra `web` (ADR-0007); o domínio é testável sem ele.
# `uv run pytest` continua verde numa instalação sem a camada de entrega.
collect_ignore = []
try:
    import starlette  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    collect_ignore.append("test_web.py")


@pytest.fixture
def fixture_catalogo() -> Path:
    """Catálogo-exemplo válido: 2 trilhas, 6 competências, caminhos paralelos."""
    return RAIZ / "tests" / "fixtures" / "catalogo_exemplo"


@pytest.fixture
def catalogo_real() -> Path:
    """O catálogo autorado do projeto."""
    return RAIZ / "catalogo"
