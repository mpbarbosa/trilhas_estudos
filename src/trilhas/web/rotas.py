"""Uma função por rota. Nenhuma regra de domínio aqui.

A rota resolve parâmetro, chama uma projeção de `apresentar/` e devolve template. Se
aparecer comparação de nível ou varredura de `requires` neste arquivo, está no lugar
errado (docs/interface.md §3.3).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from .apresentar import acervo as apresentar_acervo
from .apresentar import detalhe, diagnostico

if TYPE_CHECKING:
    from .app import Contexto


def _ctx(request: Request) -> Contexto:
    ctx: Contexto = request.app.state.ctx
    return ctx


def _responder(
    request: Request, modelo: str, contexto: dict[str, Any], *, status: int = 200
) -> Response:
    ctx = _ctx(request)
    acervo = ctx.fonte.acervo()
    base = {
        "cabecalho": acervo.cabecalho,
        "problemas_do_acervo": acervo.problemas,
        "caminho": request.url.path,
    }
    return ctx.templates.TemplateResponse(request, modelo, {**base, **contexto}, status_code=status)


async def inicio(request: Request) -> Response:
    ctx = _ctx(request)
    visao = apresentar_acervo.inicio(ctx.fonte.acervo(), hoje=ctx.hoje())
    return _responder(request, "inicio.html", {"v": visao, "titulo": "Acervo"})


async def lista(request: Request) -> Response:
    ctx = _ctx(request)
    filtro = apresentar_acervo.Filtro(
        q=request.query_params.get("q", "").strip(),
        tipo=request.query_params.get("tipo", "").strip(),
        area=request.query_params.get("area", "").strip(),
        status=request.query_params.get("status", "").strip(),
    )
    visao = apresentar_acervo.listar(ctx.fonte.acervo(), filtro)
    return _responder(request, "lista.html", {"v": visao, "titulo": "Catálogo"})


async def trilha(request: Request) -> Response:
    ctx = _ctx(request)
    visao = detalhe.trilha(ctx.fonte.acervo(), request.path_params["ident"])
    if visao is None:
        return await nao_encontrado(request, None)
    return _responder(request, "trilha.html", {"v": visao, "titulo": visao.trilha.titulo})


async def etapa(request: Request) -> Response:
    ctx = _ctx(request)
    visao = detalhe.etapa(ctx.fonte.acervo(), request.path_params["ident"], hoje=ctx.hoje())
    if visao is None:
        return await nao_encontrado(request, None)
    return _responder(request, "etapa.html", {"v": visao, "titulo": visao.etapa.titulo})


async def competencia(request: Request) -> Response:
    ctx = _ctx(request)
    visao = detalhe.competencia(ctx.fonte.acervo(), request.path_params["ident"])
    if visao is None:
        return await nao_encontrado(request, None)
    return _responder(request, "competencia.html", {"v": visao, "titulo": visao.competencia.titulo})


async def diagnostico_do_catalogo(request: Request) -> Response:
    ctx = _ctx(request)
    acervo = ctx.fonte.acervo()
    visao = diagnostico.diagnostico(
        ctx.fonte.diagnosticar(),
        catalogo_versao=acervo.cabecalho.catalogo_versao,
        gerado_em=acervo.cabecalho.gerado_em,
        hash_completo=acervo.cabecalho.hash,
    )
    return _responder(request, "diagnostico.html", {"v": visao, "titulo": "Diagnóstico"})


async def nao_encontrado(request: Request, exc: Exception | None = None) -> Response:
    return _responder(
        request,
        "erro.html",
        {
            "titulo": "Não encontrado",
            "mensagem": "Nenhuma entidade de catálogo com este id.",
            "detalhe": request.url.path,
        },
        status=404,
    )


async def falhou(request: Request, exc: Exception) -> Response:
    return _responder(
        request,
        "erro.html",
        {
            "titulo": "Erro",
            "mensagem": "A interface falhou ao montar esta tela.",
            "detalhe": str(exc),
        },
        status=500,
    )


ROTAS = [
    Route("/", inicio),
    Route("/catalogo", lista),
    Route("/catalogo/diagnostico", diagnostico_do_catalogo),
    Route("/trilha/{ident:path}", trilha),
    Route("/etapa/{ident:path}", etapa),
    Route("/competencia/{ident:path}", competencia),
]
