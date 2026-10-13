"""Montagem do aplicativo (ADR-0007).

Toda a configuração mora aqui: caminho do snapshot, templates, estáticos e rotas. As
rotas estão em `rotas.py` e recebem o `Contexto` por `request.app.state`, de modo que
nada precise de variável global — é o que torna o app testável com um catálogo-fixture.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from . import rotas
from .dados import NOME_DO_LOCK, Fonte

AQUI = Path(__file__).parent


@dataclass(slots=True)
class Contexto:
    """O que as rotas precisam, injetado em vez de importado."""

    fonte: Fonte
    templates: Jinja2Templates
    hoje: Callable[[], date] = field(default=date.today)


def criar_app(
    *,
    lock: Path | None = None,
    hoje: Callable[[], date] | None = None,
) -> Starlette:
    caminho = lock or Path.cwd() / NOME_DO_LOCK
    templates = Jinja2Templates(directory=str(AQUI / "modelos"))
    templates.env.trim_blocks = True
    templates.env.lstrip_blocks = True

    app = Starlette(
        routes=[
            *rotas.ROTAS,
            Mount("/estatico", StaticFiles(directory=str(AQUI / "estatico")), name="estatico"),
        ],
        exception_handlers={404: rotas.nao_encontrado, 500: rotas.falhou},
    )
    app.state.ctx = Contexto(
        fonte=Fonte(caminho),
        templates=templates,
        hoje=hoje or date.today,
    )
    return app
