from __future__ import annotations

from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture
def fixture_catalogo() -> Path:
    """Catálogo-exemplo válido: 2 trilhas, 6 competências, caminhos paralelos."""
    return RAIZ / "tests" / "fixtures" / "catalogo_exemplo"


@pytest.fixture
def catalogo_real() -> Path:
    """O catálogo autorado do projeto."""
    return RAIZ / "catalogo"
