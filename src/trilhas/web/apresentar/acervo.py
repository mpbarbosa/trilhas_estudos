"""Visão do acervo: a abertura e o explorador de catálogo.

A abertura é provisória. Quando o motor existir, `/` passa a ser o painel *Agora*
(docs/interface.md §5.2) e o acervo vira `/catalogo`; é por isso que as duas visões
já moram no mesmo módulo e a abertura não acumula função de painel.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from ...catalogo.modelo import Catalogo, Status, Trilha
from ..dados import Acervo
from . import comum


@dataclass(frozen=True, slots=True)
class Alvo:
    competencia_id: str
    titulo: str
    nivel: str


@dataclass(frozen=True, slots=True)
class ResumoTrilha:
    id: str
    titulo: str
    area: str
    status: Status
    objetivo: tuple[Alvo, ...]
    qtd_proprias: int
    qtd_emprestadas: int
    qtd_obrigatorias: int
    qtd_opcionais: int
    esforco_min: int
    esforco: str
    ondas: tuple[int, int]
    """Primeira e última onda ocupada pela trilha — sua profundidade no grafo."""


@dataclass(frozen=True, slots=True)
class Contagem:
    rotulo: str
    quantidade: int


@dataclass(frozen=True, slots=True)
class VisaoInicio:
    catalogo_versao: int
    gerado_em: str
    hash_curto: str
    trilhas: tuple[ResumoTrilha, ...]
    totais: tuple[Contagem, ...]
    esforco_total: str
    ondas: int
    arestas: int
    arestas_sem_avanco: int
    """Arestas cujo destino não avança de onda — desenhadas por cima (disposicao._caminho).

    Não é o mesmo que ciclo no grafo derivado: medida simples, para a tela.
    """
    formatos: tuple[Contagem, ...]
    idiomas: tuple[Contagem, ...]
    gratuitos: int
    recursos_vencidos: int
    sem_snapshot: bool


def inicio(acervo: Acervo, *, hoje: date) -> VisaoInicio:
    cat = acervo.catalogo
    etapas = list(cat.etapas.values())
    recursos = list(cat.recursos.values())
    esforco = sum(e.esforco_estimado_min for e in etapas)

    return VisaoInicio(
        catalogo_versao=acervo.cabecalho.catalogo_versao,
        gerado_em=acervo.cabecalho.gerado_em,
        hash_curto=acervo.cabecalho.hash[7:19] if acervo.cabecalho.hash else "",
        trilhas=tuple(
            _resumo(t, acervo) for t in sorted(cat.trilhas.values(), key=lambda t: t.titulo)
        ),
        totais=(
            Contagem("trilhas", len(cat.trilhas)),
            Contagem("etapas", len(cat.etapas)),
            Contagem("competências", len(cat.competencias)),
            Contagem("recursos", len(cat.recursos)),
        ),
        esforco_total=comum.duracao(esforco),
        ondas=acervo.fecho.ondas,
        arestas=len(acervo.arestas),
        arestas_sem_avanco=sum(
            1
            for a in acervo.arestas
            if acervo.fecho.onda.get(a.destino, 0) <= acervo.fecho.onda.get(a.origem, 0)
        ),
        formatos=_contar(comum.formato(r.formato) for r in recursos),
        idiomas=_contar(r.idioma for r in recursos),
        gratuitos=sum(1 for r in recursos if r.custo <= 0),
        recursos_vencidos=sum(1 for r in recursos if comum.vencido(r.verificado_em, hoje)),
        sem_snapshot=not cat.ids(),
    )


def _resumo(trilha: Trilha, acervo: Acervo) -> ResumoTrilha:
    cat = acervo.catalogo
    etapas = [cat.etapas[e] for e in trilha.todas_as_etapas if e in cat.etapas]
    ondas = sorted(acervo.fecho.onda.get(e.id, 0) for e in etapas)
    return ResumoTrilha(
        id=trilha.id,
        titulo=trilha.titulo,
        area=comum.area_do_id(trilha.id),
        status=trilha.status,
        objetivo=tuple(
            Alvo(a.competencia, comum.titulo_de(cat, a.competencia), comum.nivel(a.nivel))
            for a in trilha.objetivo_declarado
        ),
        qtd_proprias=len(trilha.etapas),
        qtd_emprestadas=len(trilha.etapas_referenciadas),
        qtd_obrigatorias=sum(1 for e in etapas if not e.opcional),
        qtd_opcionais=sum(1 for e in etapas if e.opcional),
        esforco_min=sum(e.esforco_estimado_min for e in etapas),
        esforco=comum.duracao(sum(e.esforco_estimado_min for e in etapas)),
        ondas=(ondas[0], ondas[-1]) if ondas else (0, 0),
    )


def _contar(valores: Iterable[str]) -> tuple[Contagem, ...]:
    contagem: dict[str, int] = {}
    for chave in valores:
        contagem[chave] = contagem.get(chave, 0) + 1
    return tuple(
        Contagem(k, v) for k, v in sorted(contagem.items(), key=lambda kv: (-kv[1], kv[0]))
    )


# --- explorador ----------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Linha:
    tipo: str
    tipo_rotulo: str
    id: str
    titulo: str
    area: str
    status: Status
    detalhe: str
    href: str


@dataclass(frozen=True, slots=True)
class Filtro:
    q: str = ""
    tipo: str = ""
    area: str = ""
    status: str = ""

    @property
    def ativo(self) -> bool:
        return bool(self.q or self.tipo or self.area or self.status)


@dataclass(frozen=True, slots=True)
class VisaoLista:
    linhas: tuple[Linha, ...]
    filtro: Filtro
    total: int
    """Total antes do filtro — para dizer `23 de 210`."""
    areas: tuple[str, ...]
    tipos: tuple[Contagem, ...]
    status: tuple[str, ...]


def listar(acervo: Acervo, filtro: Filtro) -> VisaoLista:
    """Filtra as quatro coleções numa lista só.

    Busca sem acento e sem caixa, sobre id e título: quem procura `competencia` não
    deve ficar sem resposta por não ter digitado o acento.
    """
    todas = _linhas(acervo.catalogo)
    termo = _normalizar(filtro.q)
    filtradas = tuple(
        linha
        for linha in todas
        if (not termo or termo in _normalizar(f"{linha.id} {linha.titulo} {linha.detalhe}"))
        and (not filtro.tipo or linha.tipo == filtro.tipo)
        and (not filtro.area or linha.area == filtro.area)
        and (not filtro.status or linha.status.value == filtro.status)
    )
    return VisaoLista(
        linhas=filtradas,
        filtro=filtro,
        total=len(todas),
        areas=tuple(sorted({linha.area for linha in todas if linha.area})),
        tipos=tuple(
            Contagem(comum.ROTULO_TIPO_PLURAL[t], sum(1 for linha in todas if linha.tipo == t))
            for t in ("trilha", "etapa", "comp", "rec")
        ),
        status=tuple(s.value for s in Status),
    )


def _linhas(cat: Catalogo) -> tuple[Linha, ...]:
    linhas: list[Linha] = []
    for trilha in cat.trilhas.values():
        etapas = [cat.etapas[e] for e in trilha.todas_as_etapas if e in cat.etapas]
        linhas.append(
            Linha(
                tipo="trilha",
                tipo_rotulo=comum.ROTULO_TIPO["trilha"],
                id=trilha.id,
                titulo=trilha.titulo,
                area=comum.area_do_id(trilha.id),
                status=trilha.status,
                detalhe=f"{len(etapas)} etapas · "
                f"{comum.duracao(sum(e.esforco_estimado_min for e in etapas))}",
                href=f"/trilha/{trilha.id}",
            )
        )
    for etapa in cat.etapas.values():
        linhas.append(
            Linha(
                tipo="etapa",
                tipo_rotulo=comum.ROTULO_TIPO["etapa"],
                id=etapa.id,
                titulo=etapa.titulo,
                area=comum.area_do_id(etapa.id),
                status=etapa.status,
                detalhe=comum.duracao(etapa.esforco_estimado_min)
                + (" · opcional" if etapa.opcional else ""),
                href=f"/etapa/{etapa.id}",
            )
        )
    for competencia in cat.competencias.values():
        linhas.append(
            Linha(
                tipo="comp",
                tipo_rotulo=comum.ROTULO_TIPO["comp"],
                id=competencia.id,
                titulo=competencia.titulo,
                area=comum.area_do_id(competencia.id),
                status=competencia.status,
                detalhe=competencia.descricao.strip().splitlines()[0]
                if competencia.descricao.strip()
                else competencia.verificacao[:90],
                href=f"/competencia/{competencia.id}",
            )
        )
    for recurso in cat.recursos.values():
        linhas.append(
            Linha(
                tipo="rec",
                tipo_rotulo=comum.ROTULO_TIPO["rec"],
                id=recurso.id,
                titulo=recurso.titulo,
                area=comum.area_do_id(recurso.id),
                status=recurso.status,
                detalhe=f"{comum.formato(recurso.formato)} · {recurso.idioma} · "
                f"{comum.dinheiro(recurso.custo)} · {comum.duracao(recurso.duracao_min)}",
                href=f"/etapa/{recurso.etapa}#{recurso.id}",
            )
        )
    return tuple(sorted(linhas, key=lambda linha: (linha.tipo, linha.titulo, linha.id)))


def _normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(c for c in sem_acento if not unicodedata.combining(c))
