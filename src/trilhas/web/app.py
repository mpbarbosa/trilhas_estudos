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
from starlette.responses import Response
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.types import Scope

from . import rotas
from .dados import NOME_DO_LOCK, Fonte
from .encerrar import encerrar_processo

AQUI = Path(__file__).parent


class EstaticosRevalidados(StaticFiles):
    """Estáticos que o navegador é obrigado a conferir antes de reusar.

    Sem `Cache-Control` o navegador cacheia por heurística, e quem mexe no CSS
    recarrega a página, vê a folha antiga e conclui que a mudança não funcionou —
    perde-se mais tempo nisso do que o cache economiza em servidor local. `no-cache`
    não proíbe guardar: obriga a perguntar, e a pergunta volta 304 enquanto o arquivo
    não muda.
    """

    async def get_response(self, path: str, scope: Scope) -> Response:
        resposta = await super().get_response(path, scope)
        resposta.headers.setdefault("cache-control", "no-cache")
        return resposta


@dataclass(slots=True)
class Contexto:
    """O que as rotas precisam, injetado em vez de importado."""

    fonte: Fonte
    templates: Jinja2Templates
    hoje: Callable[[], date] = field(default=date.today)
    desligar: Callable[[], None] = field(default=encerrar_processo)


def criar_app(
    *,
    lock: Path | None = None,
    hoje: Callable[[], date] | None = None,
    desligar: Callable[[], None] | None = None,
) -> Starlette:
    caminho = lock or Path.cwd() / NOME_DO_LOCK
    templates = Jinja2Templates(directory=str(AQUI / "modelos"))
    templates.env.trim_blocks = True
    templates.env.lstrip_blocks = True

    app = Starlette(
        routes=[
            *rotas.ROTAS,
            Mount(
                "/estatico",
                EstaticosRevalidados(directory=str(AQUI / "estatico")),
                name="estatico",
            ),
        ],
        exception_handlers={404: rotas.nao_encontrado, 500: rotas.falhou},
    )
    app.state.ctx = Contexto(
        fonte=Fonte(caminho),
        templates=templates,
        hoje=hoje or date.today,
        desligar=desligar or encerrar_processo,
    )
    return app
