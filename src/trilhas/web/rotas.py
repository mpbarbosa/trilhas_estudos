"""Uma função por rota. Nenhuma regra de domínio aqui.

A rota resolve parâmetro, chama uma projeção de `apresentar/` e devolve template. Se
aparecer comparação de nível ou varredura de `requires` neste arquivo, está no lugar
errado (docs/interface.md §3.3).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qsl, quote

from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Route

from ..motor import Opcoes, sugerir
from ..motor.modelo import Percurso, Resultado
from .apresentar import acervo as apresentar_acervo
from .apresentar import detalhe, diagnostico
from .apresentar import sugestao as apresentar_sugestao
from .escrever import Acao, registrar_na_etapa
from .percurso import nome_do_estudante, percurso_completo, percursos_em

if TYPE_CHECKING:
    from .app import Contexto


def _ctx(request: Request) -> Contexto:
    ctx: Contexto = request.app.state.ctx
    return ctx


def _arquivo_de_percurso(request: Request) -> Path | None:
    """O percurso a mostrar: o de `?estudante=`, ou o primeiro que houver.

    Mesma escolha em todas as telas — se a home mostra o percurso de alguém, a página
    da etapa tem de mostrar o progresso **dessa mesma pessoa**, ou as duas se
    contradizem sem dizer por quê.
    """
    arquivos = percursos_em(_ctx(request).fonte.percursos)
    escolhido = request.query_params.get("estudante", "").strip()
    return arquivos.get(escolhido) or (next(iter(arquivos.values()), None))


def _percurso(request: Request) -> Percurso | None:
    caminho = _arquivo_de_percurso(request)
    return percurso_completo(caminho) if caminho else None


def _responder(
    request: Request, modelo: str, contexto: dict[str, Any], *, status: int = 200
) -> Response:
    ctx = _ctx(request)
    acervo = ctx.fonte.acervo()
    base = {
        "cabecalho": acervo.cabecalho,
        "problemas_do_acervo": acervo.problemas,
        "caminho": request.url.path,
        "estudante_atual": request.query_params.get("estudante", "").strip(),
    }
    return ctx.templates.TemplateResponse(request, modelo, {**base, **contexto}, status_code=status)


async def agora(request: Request) -> Response:
    """Painel *Agora*: o que estudar neste instante, com os fatores à vista.

    `?tempo=` e `?quantidade=` entram na URL de propósito — uma sugestão tem de ser
    reproduzível, e estado só em sessão não se compartilha (ADR-0007).
    """
    ctx = _ctx(request)
    acervo = ctx.fonte.acervo()
    arquivos = percursos_em(ctx.fonte.percursos)
    caminho = _arquivo_de_percurso(request)

    percurso: Percurso | None = percurso_completo(caminho) if caminho else None
    tempo = _inteiro(request.query_params.get("tempo"))
    quantidade = _inteiro(request.query_params.get("quantidade")) or 3
    momento = datetime.combine(ctx.hoje(), datetime.min.time())

    if percurso is None:
        resultado = Resultado(sugestoes=())
    else:
        resultado = sugerir(
            acervo.catalogo,
            percurso,
            momento,
            Opcoes(quantidade=quantidade, tempo_disponivel_min=tempo),
            catalogo_versao=acervo.cabecalho.catalogo_versao,
        )

    visao = apresentar_sugestao.painel(
        resultado,
        acervo.catalogo,
        percurso,
        estudante_nome=nome_do_estudante(caminho) if caminho else "",
        estudantes=tuple(arquivos),
        tempo_disponivel_min=tempo,
        quantidade=quantidade,
        momento=momento,
        catalogo_versao=acervo.cabecalho.catalogo_versao,
        hoje=ctx.hoje(),
    )
    return _responder(request, "agora.html", {"v": visao, "titulo": "Agora"})


async def inicio(request: Request) -> Response:
    ctx = _ctx(request)
    visao = apresentar_acervo.inicio(ctx.fonte.acervo(), hoje=ctx.hoje())
    return _responder(request, "inicio.html", {"v": visao, "titulo": "Acervo"})


def _inteiro(bruto: str | None) -> int | None:
    try:
        valor = int(bruto or "")
    except ValueError:
        return None
    return valor if valor > 0 else None


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
    visao = detalhe.trilha(
        ctx.fonte.acervo(), request.path_params["ident"], percurso=_percurso(request)
    )
    if visao is None:
        return await nao_encontrado(request, None)
    return _responder(request, "trilha.html", {"v": visao, "titulo": visao.trilha.titulo})


async def etapa(request: Request) -> Response:
    if request.method == "POST":
        return await _registrar_na_etapa(request)
    ctx = _ctx(request)
    visao = detalhe.etapa(
        ctx.fonte.acervo(),
        request.path_params["ident"],
        hoje=ctx.hoje(),
        percurso=_percurso(request),
    )
    if visao is None:
        return await nao_encontrado(request, None)
    return _responder(request, "etapa.html", {"v": visao, "titulo": visao.etapa.titulo})


async def _registrar_na_etapa(request: Request) -> Response:
    """Grava um fato de percurso e redireciona para a própria etapa (interface.md §5.10).

    A resposta é **303**, não a página: um POST que respondesse HTML deixaria o F5 e o
    botão Voltar reenviando o formulário, e cada reenvio gravaria outro fato num log
    que não tem como desfazê-lo (ADR-0008). Com o redirect, recarregar é um GET.

    Nenhuma decisão de domínio aqui: a rota resolve parâmetro, delega a `escrever` e
    devolve resposta (§3.3).
    """
    if not _mesma_origem(request):
        return _recusado(
            request,
            "Registrar progresso só pela própria interface.",
            request.headers.get("origin", ""),
            status=403,
        )

    arquivo = _arquivo_de_percurso(request)
    percurso = percurso_completo(arquivo) if arquivo else None
    if arquivo is None or percurso is None:
        return _recusado(
            request,
            "Nenhum percurso para receber o fato — um fato precisa de estudante.",
            f"crie {_ctx(request).fonte.percursos.name}/<estudante>.yaml",
            status=409,
        )

    campos = await _campos(request)
    try:
        acao = Acao(campos.get("acao", ""))
    except ValueError:
        return _recusado(request, "Ação desconhecida.", campos.get("acao", ""))

    erro = registrar_na_etapa(
        arquivo.parent,
        percurso.estudante_id,
        _ctx(request).fonte.acervo().catalogo,
        acao,
        request.path_params["ident"],
        recurso=_texto(campos.get("recurso")),
        motivo=_texto(campos.get("motivo")),
    )
    if erro is not None:
        return _recusado(request, "Nada foi gravado.", erro)
    return RedirectResponse(_de_volta(request), status_code=303)


async def _campos(request: Request) -> dict[str, str]:
    """Lê o corpo de um formulário HTML, sem `request.form()`.

    `request.form()` do Starlette exige `python-multipart` instalado **mesmo para
    corpo `urlencoded`**, e nenhum formulário daqui envia arquivo: a dependência
    pagaria por uma capacidade que a interface não tem. Corpo de outro tipo vira
    dicionário vazio, e a ação sai como desconhecida.
    """
    tipo = request.headers.get("content-type", "").split(";")[0].strip()
    if tipo != "application/x-www-form-urlencoded":
        return {}
    bruto = (await request.body()).decode("utf-8", errors="replace")
    return dict(parse_qsl(bruto, keep_blank_values=True))


def _texto(bruto: str | None) -> str | None:
    """Campo de formulário vazio é ausência, não string vazia."""
    return bruto.strip() or None if bruto else None


def _de_volta(request: Request) -> str:
    """A própria etapa, preservando `?estudante=`: o POST não troca de pessoa."""
    estudante = request.query_params.get("estudante", "").strip()
    sufixo = f"?estudante={quote(estudante)}" if estudante else ""
    return f"{request.url.path}{sufixo}"


def _recusado(request: Request, mensagem: str, detalhe: str = "", *, status: int = 400) -> Response:
    return _responder(
        request,
        "erro.html",
        {"titulo": "Recusado", "mensagem": mensagem, "detalhe": detalhe},
        status=status,
    )


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


def _mesma_origem(request: Request) -> bool:
    """Recusa POST vindo de outra origem.

    Qualquer página aberta no navegador pode fazer POST para `localhost`, e desligar o
    servidor é efeito colateral — não basta não ser GET. O navegador manda `Origin` em
    POST; cliente sem navegador (teste, curl) não manda, e aí não há o que comparar.
    """
    origem = request.headers.get("origin")
    if origem is None:
        return True
    hospedeiro = request.headers.get("host", "")
    return origem in (f"http://{hospedeiro}", f"https://{hospedeiro}")


async def desligar(request: Request) -> Response:
    """Encerra o servidor a pedido da tela (docs/interface.md §5.9).

    O encerramento vai numa tarefa de fundo: a resposta chega inteira ao navegador e só
    então o processo recebe o sinal. Quem desliga é `ctx.desligar` — o teste injeta
    outro, e por isso esta rota pode ser exercitada sem matar o pytest.
    """
    if not _mesma_origem(request):
        return _recusado(
            request,
            "Desligar só pela própria interface.",
            request.headers.get("origin", ""),
            status=403,
        )
    resposta = _responder(request, "desligado.html", {"titulo": "Desligado"})
    resposta.background = BackgroundTask(_ctx(request).desligar)
    return resposta


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
    Route("/", agora),
    Route("/acervo", inicio),
    Route("/catalogo", lista),
    Route("/catalogo/diagnostico", diagnostico_do_catalogo),
    Route("/trilha/{ident:path}", trilha),
    Route("/etapa/{ident:path}", etapa, methods=["GET", "POST"]),
    Route("/competencia/{ident:path}", competencia),
    Route("/desligar", desligar, methods=["POST"]),
]
