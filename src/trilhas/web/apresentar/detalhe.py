"""Visões de uma entidade: trilha, etapa e competência.

O que estas três telas têm de fazer bem é explicar **dependência**: por que uma etapa
vem depois, quem ensina o que ela exige, e o que ela destrava. O resto é cadastro.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date

from ...catalogo.modelo import Competencia, Etapa, Nivel, Recurso, Status, Trilha
from ...motor.modelo import EstadoEtapa, Percurso, ProgressoEtapa
from ..dados import Acervo
from . import comum
from .disposicao import Disposicao, dispor


@dataclass(frozen=True, slots=True)
class Referencia:
    """Link para outra entidade, já com o rótulo pronto."""

    id: str
    titulo: str
    href: str
    nota: str = ""


@dataclass(frozen=True, slots=True)
class Exigencia:
    competencia_id: str
    titulo: str
    nivel: Nivel
    nivel_rotulo: str
    ensinada_por: tuple[Referencia, ...]
    """Etapas ativas que levam a competência ao nível exigido — como destravar."""


@dataclass(frozen=True, slots=True)
class Desenvolvimento:
    competencia_id: str
    titulo: str
    nivel: Nivel
    nivel_rotulo: str
    exigida_por: int


@dataclass(frozen=True, slots=True)
class LinhaRecurso:
    id: str
    titulo: str
    formato: str
    idioma: str
    custo: str
    custo_valor: float
    duracao: str
    duracao_min: int
    url: str
    status: Status
    disponivel: bool
    verificado_em: date | None
    dias_sem_verificar: int | None
    vencido: bool
    em_uso: bool = False
    """Recurso declarado ao iniciar esta etapa — por onde o estudante de fato estudou."""


@dataclass(frozen=True, slots=True)
class LinhaEtapaDaTrilha:
    id: str
    titulo: str
    href: str
    onda: int
    opcional: bool
    emprestada: bool
    status: Status
    esforco: str
    esforco_min: int
    destrava: int
    qtd_recursos: int
    requisitos: int
    estado: EstadoEtapa = EstadoEtapa.NAO_INICIADA
    estado_rotulo: str = ""
    atualizado_em: date | None = None


@dataclass(frozen=True, slots=True)
class VisaoTrilha:
    trilha: Trilha
    area: str
    objetivo: tuple[Exigencia, ...]
    etapas: tuple[LinhaEtapaDaTrilha, ...]
    disposicao: Disposicao
    esforco: str
    qtd_obrigatorias: int
    qtd_opcionais: int
    emprestadas: tuple[Referencia, ...]
    tem_percurso: bool = False
    """Houve percurso para consultar. Distingue "nenhuma etapa concluída" de "não se
    sabe": sem isso a tela afirmaria progresso zero a quem nunca declarou estudante."""
    qtd_concluidas: int = 0
    qtd_em_andamento: int = 0


@dataclass(frozen=True, slots=True)
class VisaoEtapa:
    etapa: Etapa
    area: str
    trilha: Referencia | None
    onda: int
    esforco: str
    requisitos: tuple[Exigencia, ...]
    desenvolve: tuple[Desenvolvimento, ...]
    recursos: tuple[LinhaRecurso, ...]
    destravada_por: tuple[Referencia, ...]
    destrava: tuple[Referencia, ...]
    tambem_em: tuple[Referencia, ...]
    """Trilhas que referenciam esta etapa sem a definir (catalogo.md §1)."""
    alertas: tuple[str, ...]
    tem_percurso: bool = False
    estado: EstadoEtapa = EstadoEtapa.NAO_INICIADA
    estado_rotulo: str = ""
    atualizado_em: date | None = None


@dataclass(frozen=True, slots=True)
class VisaoCompetencia:
    competencia: Competencia
    area: str
    nivel_no_catalogo: Nivel
    nivel_no_catalogo_rotulo: str
    ensinada_por: tuple[tuple[Referencia, str], ...]
    exigida_por: tuple[tuple[Referencia, str], ...]
    objetivo_de: tuple[Referencia, ...]
    alertas: tuple[str, ...]


def trilha(
    acervo: Acervo, trilha_id: str, *, percurso: Percurso | None = None
) -> VisaoTrilha | None:
    cat = acervo.catalogo
    alvo = cat.trilhas.get(trilha_id)
    if alvo is None:
        return None

    progresso = _progresso_por_etapa(percurso)
    etapas = [cat.etapas[e] for e in alvo.todas_as_etapas if e in cat.etapas]
    proprias = set(alvo.etapas)
    disposicao = dispor(
        etapas,
        acervo.fecho,
        acervo.arestas,
        catalogo=cat,
        proprias=proprias,
        estados={ident: p.estado for ident, p in progresso.items()},
    )
    destrava = {n.etapa_id: n.destrava for n in disposicao.nos}

    linhas = tuple(
        LinhaEtapaDaTrilha(
            id=e.id,
            titulo=e.titulo,
            href=f"/etapa/{e.id}",
            onda=acervo.fecho.onda.get(e.id, 0),
            opcional=e.opcional,
            emprestada=e.id not in proprias,
            status=e.status,
            esforco=comum.duracao(e.esforco_estimado_min),
            esforco_min=e.esforco_estimado_min,
            destrava=destrava.get(e.id, 0),
            qtd_recursos=len(cat.recursos_da_etapa(e.id)),
            requisitos=len(e.requires),
            estado=_estado(progresso, e.id),
            estado_rotulo=comum.estado_de_etapa(_estado(progresso, e.id)),
            atualizado_em=progresso[e.id].atualizado_em if e.id in progresso else None,
        )
        for e in sorted(etapas, key=lambda e: (acervo.fecho.onda.get(e.id, 0), e.titulo))
    )

    return VisaoTrilha(
        trilha=alvo,
        area=comum.area_do_id(alvo.id),
        objetivo=tuple(_exigencia(acervo, a.competencia, a.nivel) for a in alvo.objetivo_declarado),
        etapas=linhas,
        disposicao=disposicao,
        esforco=comum.duracao(sum(e.esforco_estimado_min for e in etapas)),
        qtd_obrigatorias=sum(1 for e in etapas if not e.opcional),
        qtd_opcionais=sum(1 for e in etapas if e.opcional),
        emprestadas=tuple(
            Referencia(
                id=e,
                titulo=comum.titulo_de(cat, e),
                href=f"/etapa/{e}",
                nota=comum.titulo_de(cat, cat.etapas[e].trilha or "") if e in cat.etapas else "",
            )
            for e in alvo.etapas_referenciadas
        ),
        tem_percurso=percurso is not None,
        qtd_concluidas=sum(1 for e in etapas if _estado(progresso, e.id) is EstadoEtapa.CONCLUIDA),
        qtd_em_andamento=sum(
            1 for e in etapas if _estado(progresso, e.id) is EstadoEtapa.EM_ANDAMENTO
        ),
    )


def etapa(
    acervo: Acervo, etapa_id: str, *, hoje: date, percurso: Percurso | None = None
) -> VisaoEtapa | None:
    cat = acervo.catalogo
    alvo = cat.etapas.get(etapa_id)
    if alvo is None:
        return None

    progresso = _progresso_por_etapa(percurso)
    aqui = progresso.get(etapa_id)
    recursos = tuple(
        _recurso(r, hoje=hoje, em_uso=aqui is not None and aqui.recurso_em_uso == r.id)
        for r in sorted(
            cat.recursos_da_etapa(etapa_id),
            key=lambda r: (not r.disponivel, r.custo, r.duracao_min, r.titulo),
        )
    )
    exigida = _quantas_exigem(acervo)

    return VisaoEtapa(
        etapa=alvo,
        area=comum.area_do_id(alvo.id),
        trilha=(
            Referencia(alvo.trilha, comum.titulo_de(cat, alvo.trilha), f"/trilha/{alvo.trilha}")
            if alvo.trilha
            else None
        ),
        onda=acervo.fecho.onda.get(alvo.id, 0),
        esforco=comum.duracao(alvo.esforco_estimado_min),
        requisitos=tuple(_exigencia(acervo, r.competencia, r.nivel_minimo) for r in alvo.requires),
        desenvolve=tuple(
            Desenvolvimento(
                competencia_id=t.competencia,
                titulo=comum.titulo_de(cat, t.competencia),
                nivel=t.nivel_resultante,
                nivel_rotulo=comum.nivel(t.nivel_resultante),
                exigida_por=exigida.get(t.competencia, 0),
            )
            for t in alvo.teaches
        ),
        recursos=recursos,
        destravada_por=tuple(
            Referencia(
                a.origem,
                comum.titulo_de(cat, a.origem),
                f"/etapa/{a.origem}",
                nota=", ".join(comum.titulo_de(cat, c) for c in a.competencias),
            )
            for a in acervo.arestas
            if a.destino == etapa_id
        ),
        destrava=tuple(
            Referencia(
                a.destino,
                comum.titulo_de(cat, a.destino),
                f"/etapa/{a.destino}",
                nota=", ".join(comum.titulo_de(cat, c) for c in a.competencias),
            )
            for a in acervo.arestas
            if a.origem == etapa_id
        ),
        tambem_em=tuple(
            Referencia(t.id, t.titulo, f"/trilha/{t.id}")
            for t in cat.trilhas.values()
            if etapa_id in t.etapas_referenciadas
        ),
        alertas=_alertas_da_etapa(alvo, recursos),
        tem_percurso=percurso is not None,
        estado=_estado(progresso, etapa_id),
        estado_rotulo=comum.estado_de_etapa(_estado(progresso, etapa_id)),
        atualizado_em=aqui.atualizado_em if aqui else None,
    )


def competencia(acervo: Acervo, competencia_id: str) -> VisaoCompetencia | None:
    cat = acervo.catalogo
    alvo = cat.competencias.get(competencia_id)
    if alvo is None:
        return None

    ensinada = tuple(
        (
            Referencia(e.id, e.titulo, f"/etapa/{e.id}"),
            comum.nivel(max(t.nivel_resultante for t in e.teaches if t.competencia == alvo.id)),
        )
        for e in sorted(cat.ensina(alvo.id, somente_ativas=False), key=lambda e: e.titulo)
    )
    exigida = tuple(
        (
            Referencia(e.id, e.titulo, f"/etapa/{e.id}"),
            comum.nivel(max(r.nivel_minimo for r in e.requires if r.competencia == alvo.id)),
        )
        for e in sorted(cat.etapas.values(), key=lambda e: e.titulo)
        if any(r.competencia == alvo.id for r in e.requires)
    )

    alertas: list[str] = []
    if not ensinada:
        alertas.append("nenhuma etapa desenvolve esta competência")
    if alvo.status is Status.DEPRECIADO and alvo.substituido_por:
        alertas.append(f"depreciada — substituída por {alvo.substituido_por}")

    return VisaoCompetencia(
        competencia=alvo,
        area=comum.area_do_id(alvo.id),
        nivel_no_catalogo=acervo.fecho.nivel(alvo.id),
        nivel_no_catalogo_rotulo=comum.nivel(acervo.fecho.nivel(alvo.id)),
        ensinada_por=ensinada,
        exigida_por=exigida,
        objetivo_de=tuple(
            Referencia(t.id, t.titulo, f"/trilha/{t.id}", nota=comum.nivel(a.nivel))
            for t in sorted(cat.trilhas.values(), key=lambda t: t.titulo)
            for a in t.objetivo_declarado
            if a.competencia == alvo.id
        ),
        alertas=tuple(alertas),
    )


# --- apoio ---------------------------------------------------------------------


def _exigencia(acervo: Acervo, competencia_id: str, nivel: Nivel) -> Exigencia:
    cat = acervo.catalogo
    return Exigencia(
        competencia_id=competencia_id,
        titulo=comum.titulo_de(cat, competencia_id),
        nivel=nivel,
        nivel_rotulo=comum.nivel(nivel),
        ensinada_por=tuple(
            Referencia(e.id, e.titulo, f"/etapa/{e.id}")
            for e in sorted(cat.ensina(competencia_id), key=lambda e: e.titulo)
            if any(
                t.competencia == competencia_id and t.nivel_resultante >= nivel for t in e.teaches
            )
        ),
    )


def _recurso(recurso: Recurso, *, hoje: date, em_uso: bool = False) -> LinhaRecurso:
    dias = comum.dias_desde(recurso.verificado_em, hoje)
    return LinhaRecurso(
        id=recurso.id,
        titulo=recurso.titulo,
        formato=comum.formato(recurso.formato),
        idioma=recurso.idioma,
        custo=comum.dinheiro(recurso.custo),
        custo_valor=recurso.custo,
        duracao=comum.duracao(recurso.duracao_min),
        duracao_min=recurso.duracao_min,
        url=recurso.url,
        status=recurso.status,
        disponivel=recurso.disponivel,
        verificado_em=recurso.verificado_em,
        dias_sem_verificar=dias,
        vencido=comum.vencido(recurso.verificado_em, hoje),
        em_uso=em_uso,
    )


def _progresso_por_etapa(percurso: Percurso | None) -> dict[str, ProgressoEtapa]:
    """Progresso indexado por etapa. Sem percurso, dicionário vazio — não um erro.

    As três telas de detalhe existiam antes de o percurso chegar até elas e continuam
    válidas sem ele: o catálogo é navegável por quem ainda não declarou estudante.
    """
    if percurso is None:
        return {}
    return {p.etapa: p for p in percurso.progresso}


def _estado(progresso: Mapping[str, ProgressoEtapa], etapa_id: str) -> EstadoEtapa:
    """Etapa ausente do progresso é não iniciada — ausência de fato, não fato negativo."""
    aqui = progresso.get(etapa_id)
    return aqui.estado if aqui else EstadoEtapa.NAO_INICIADA


def _quantas_exigem(acervo: Acervo) -> dict[str, int]:
    contagem: dict[str, int] = {}
    for etapa_ in acervo.catalogo.etapas.values():
        for req in etapa_.requires:
            contagem[req.competencia] = contagem.get(req.competencia, 0) + 1
    return contagem


def _alertas_da_etapa(alvo: Etapa, recursos: tuple[LinhaRecurso, ...]) -> tuple[str, ...]:
    alertas: list[str] = []
    disponiveis = [r for r in recursos if r.disponivel and r.status is Status.ATIVO]
    if not disponiveis:
        alertas.append("nenhum recurso ativo e disponível — a etapa não é estudável (CAT-050)")
    if vencidos := [r for r in recursos if r.vencido]:
        alertas.append(
            f"{len(vencidos)} recurso(s) sem verificação há mais de "
            f"{comum.DIAS_ATE_REVERIFICAR} dias (CAT-100)"
        )
    if alvo.status is Status.DEPRECIADO and alvo.substituido_por:
        alertas.append(f"depreciada — substituída por {alvo.substituido_por}")
    return tuple(alertas)
