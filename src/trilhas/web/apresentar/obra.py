"""Visão de uma obra: o exemplar, suas fatias e a exportação em Markdown.

A tela da obra responde uma pergunta que nenhuma outra responde: *"este livro, que eu
tenho na mão, serve a quê no catálogo — e quanto dele falta?"*. Etapa compara recursos
dentro de uma etapa; aqui o eixo é o exemplar, que atravessa etapas e trilhas.

Nada de domínio aqui (docs/interface.md §3.3): o agrupamento, a soma de duração e o
custo contado uma vez vêm de `catalogo.obras`, e este módulo só formata e escreve o
Markdown.
"""

from __future__ import annotations

from dataclasses import dataclass

from ...catalogo import obras as dominio
from ...catalogo.modelo import Catalogo, Status
from ...catalogo.obras import Obra
from ...catalogo.snapshot import Cabecalho
from ..dados import Acervo
from . import comum


@dataclass(frozen=True, slots=True)
class LinhaFatia:
    """Uma fatia do exemplar, com a etapa que ela atende."""

    id: str
    recorte: str
    """O que esta fatia recorta. Vazio quando a fatia é o exemplar inteiro."""
    titulo: str
    formato: str
    duracao: str
    duracao_min: int
    url: str
    status: Status
    disponivel: bool
    etapa_id: str
    etapa_titulo: str
    etapa_href: str
    etapa_ativa: bool


@dataclass(frozen=True, slots=True)
class VisaoObra:
    slug: str
    nome: str
    fatias: tuple[LinhaFatia, ...]
    duracao_total: str
    duracao_total_min: int
    custo: str
    custo_valor: float
    idiomas: tuple[str, ...]
    formatos: tuple[str, ...]
    qtd_etapas: int
    fatias_vivas: int
    toda_depreciada: bool
    exportar_href: str
    nome_do_arquivo: str
    catalogo_versao: int
    snapshot: str
    gerado_em: str


@dataclass(frozen=True, slots=True)
class LinhaObra:
    """Um exemplar na lista: o bastante para escolher qual abrir."""

    slug: str
    nome: str
    href: str
    qtd_fatias: int
    duracao: str
    duracao_min: int
    custo: str
    custo_valor: float
    qtd_etapas: int
    idiomas: str
    toda_depreciada: bool


@dataclass(frozen=True, slots=True)
class VisaoIndice:
    obras: tuple[LinhaObra, ...]
    qtd: int
    custo_total: str
    custo_total_valor: float
    duracao_total: str
    gratuitas: int


def indice(acervo: Acervo) -> VisaoIndice:
    """Todos os exemplares fatiados, em ordem de nome.

    O total de custo conta cada exemplar uma vez — é a regra do ADR-0009 aplicada à
    coleção, e a soma vem do domínio (`catalogo.obras.custo_das_obras`), não daqui.
    """
    reunidas = dominio.obras(acervo.catalogo)
    linhas = tuple(
        sorted(
            (
                LinhaObra(
                    slug=uma.slug,
                    nome=uma.nome,
                    href=f"/obra/{uma.slug}",
                    qtd_fatias=len(uma.fatias),
                    duracao=comum.duracao(uma.duracao_total_min),
                    duracao_min=uma.duracao_total_min,
                    custo=comum.dinheiro(uma.custo),
                    custo_valor=uma.custo,
                    qtd_etapas=len(uma.etapas),
                    idiomas=", ".join(uma.idiomas),
                    toda_depreciada=uma.toda_depreciada,
                )
                for uma in reunidas
            ),
            key=lambda linha: linha.nome.casefold(),
        )
    )
    return VisaoIndice(
        obras=linhas,
        qtd=len(linhas),
        custo_total=comum.dinheiro(dominio.custo_das_obras(reunidas)),
        custo_total_valor=dominio.custo_das_obras(reunidas),
        duracao_total=comum.duracao(sum(uma.duracao_total_min for uma in reunidas)),
        gratuitas=sum(1 for linha in linhas if linha.custo_valor <= 0),
    )


def pagina(acervo: Acervo, slug: str) -> VisaoObra | None:
    """Monta a visão da obra, ou `None` quando o slug não existe no catálogo."""
    encontrada = dominio.obra(acervo.catalogo, slug)
    return None if encontrada is None else _visao(encontrada, acervo)


def _visao(obra: Obra, acervo: Acervo) -> VisaoObra:
    catalogo = acervo.catalogo
    linhas = tuple(
        LinhaFatia(
            id=fatia.id,
            recorte=dominio.recorte_da_fatia(fatia),
            titulo=fatia.titulo,
            formato=comum.formato(fatia.formato),
            duracao=comum.duracao(fatia.duracao_min),
            duracao_min=fatia.duracao_min,
            url=fatia.url,
            status=fatia.status,
            disponivel=fatia.disponivel,
            etapa_id=fatia.etapa,
            etapa_titulo=comum.titulo_de(catalogo, fatia.etapa),
            etapa_href=f"/etapa/{fatia.etapa}",
            etapa_ativa=_etapa_ativa(catalogo, fatia.etapa),
        )
        for fatia in obra.fatias
    )
    cabecalho: Cabecalho = acervo.cabecalho
    return VisaoObra(
        slug=obra.slug,
        nome=obra.nome,
        fatias=linhas,
        duracao_total=comum.duracao(obra.duracao_total_min),
        duracao_total_min=obra.duracao_total_min,
        custo=comum.dinheiro(obra.custo),
        custo_valor=obra.custo,
        idiomas=obra.idiomas,
        formatos=tuple(dict.fromkeys(comum.formato(f.formato) for f in obra.fatias)),
        qtd_etapas=len(obra.etapas),
        fatias_vivas=obra.fatias_vivas,
        toda_depreciada=obra.toda_depreciada,
        exportar_href=f"/obra/{obra.slug}/exportar",
        nome_do_arquivo=f"obra-{obra.slug}.md",
        catalogo_versao=cabecalho.catalogo_versao,
        snapshot=cabecalho.hash[7:19],
        gerado_em=cabecalho.gerado_em[:10],
    )


def _etapa_ativa(catalogo: Catalogo, ident: str) -> bool:
    """Fatia pendurada em etapa depreciada não é erro de catálogo, mas a tela o diz."""
    etapa = catalogo.etapas.get(ident)
    return etapa is not None and etapa.status is Status.ATIVO


def markdown(v: VisaoObra) -> str:
    """O arquivo que a tela entrega. Markdown porque é o que cola em doc e em issue.

    Leva `catalogo_versao` e o hash do snapshot no pé pelo mesmo motivo que a sugestão
    os persiste (docs/catalogo.md §5): um export sem a versão que o produziu não se
    confere depois.
    """
    linhas = [
        f"# {v.nome}",
        "",
        f"- **obra** — `{v.slug}`",
        f"- **fatias** — {len(v.fatias)}"
        + ("" if v.fatias_vivas == len(v.fatias) else f" ({v.fatias_vivas} não depreciada(s))"),
        f"- **duração somada** — {v.duracao_total}",
        f"- **custo do exemplar** — {v.custo}, contado uma vez (ADR-0009)",
        f"- **idiomas** — {', '.join(v.idiomas)}",
        f"- **formatos** — {', '.join(v.formatos)}",
        f"- **etapas atendidas** — {v.qtd_etapas}",
    ]
    if v.toda_depreciada:
        linhas.append("- **situação** — todas as fatias depreciadas; segue no catálogo (§6)")
    linhas += ["", "## Fatias", "", "| recorte | duração | etapa |", "|---|---|---|"]
    for fatia in v.fatias:
        recorte = fatia.recorte or fatia.titulo
        marca = "" if fatia.status is Status.ATIVO else f" _({fatia.status.value})_"
        linhas.append(
            f"| {recorte}{marca} | {fatia.duracao} | {fatia.etapa_titulo} (`{fatia.etapa_id}`) |"
        )
    linhas += [
        "",
        "---",
        "",
        f"Exportado de trilhas de estudo · catálogo v{v.catalogo_versao} · "
        f"snapshot {v.snapshot} · gerado em {v.gerado_em}",
        "",
    ]
    return "\n".join(linhas)
