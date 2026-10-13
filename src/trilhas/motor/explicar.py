"""Explicação gerada a partir dos fatores (motor-de-sugestao.md §2.5).

Usa dois fatores com contribuição positiva: o que define o tipo, quando há um
(`retomada` -> momentum, `revisao` -> urgência), e os de maior contribuição.
Nunca menciona fator que não esteja em `fatores`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from trilhas.catalogo.modelo import Etapa, Recurso

from .modelo import Fator, Tipo

if TYPE_CHECKING:
    from .sugerir import _Contexto

_FATOR_DO_TIPO = {Tipo.RETOMADA: "momentum", Tipo.REVISAO: "urgencia_de_revisao"}

_ROTULO = {
    Tipo.RETOMADA: "Retome",
    Tipo.PROXIMA_ETAPA: "Próximo passo",
    Tipo.REVISAO: "Revisão",
    Tipo.EXPLORACAO: "Fora das suas trilhas",
}


def explicar(
    ctx: _Contexto,
    etapa: Etapa,
    tipo: Tipo,
    fatores: tuple[Fator, ...],
    recurso: Recurso,
    desbloqueia: int,
) -> str:
    ordem = {f.nome: i for i, f in enumerate(fatores)}
    proprio = _FATOR_DO_TIPO.get(tipo)
    principais = sorted(
        (f for f in fatores if f.contribuicao > 0),
        key=lambda f: (f.nome != proprio, -f.contribuicao, ordem[f.nome]),
    )[:2]
    frases = [_frase(ctx, etapa, tipo, f.nome, recurso, desbloqueia) for f in principais]
    corpo = " e ".join(frases) if frases else "passa todos os filtros, sem fator de destaque"
    return f"{_ROTULO[tipo]}: *{etapa.titulo}* — {corpo}."


def _frase(
    ctx: _Contexto, etapa: Etapa, tipo: Tipo, nome: str, recurso: Recurso, desbloqueia: int
) -> str:
    if nome == "relevancia":
        distancias = ctx.distancias(etapa)
        alvo = min(distancias, key=lambda c: (distancias[c], c))
        de_quem = "do seu objetivo" if ctx.percurso.objetivo else "do objetivo das suas trilhas"
        verbo = "desenvolve" if distancias[alvo] == 0 else "aproxima você de"
        return f"{verbo} *{_competencia(ctx, alvo)}*, {de_quem}"
    if nome == "prontidao":
        if not etapa.requires:
            return "não exige pré-requisito"
        base = ", ".join(f"*{_competencia(ctx, r.competencia)}*" for r in etapa.requires)
        return f"você já tem a base que ela pede ({base})"
    if nome == "momentum":
        if tipo is Tipo.RETOMADA:
            return "você já começou esta etapa"
        if tipo is Tipo.EXPLORACAO:
            return "abre caminho fora das trilhas que vêm sendo rejeitadas"
        trilhas = ctx.trilhas_da_etapa.get(etapa.id, ())
        recentes = sorted(ctx.trilhas_recentes.intersection(trilhas)) or sorted(trilhas)
        return f"continua *{_trilha(ctx, recentes[0])}*"
    if nome == "encaixe_de_esforco":
        return f"o recurso sugerido leva {recurso.duracao_min} min"
    if nome == "desbloqueio":
        plural = "etapa adiante" if desbloqueia == 1 else "etapas adiante"
        return f"destrava {desbloqueia} {plural}"
    if nome == "urgencia_de_revisao":
        decaida = max(
            (t.competencia for t in etapa.teaches if t.competencia in ctx.perfil),
            key=lambda c: (ctx.urgencia(c), c),
        )
        dias = (ctx.hoje - ctx.perfil[decaida].ultima_evidencia_em).days
        return f"sua última evidência de *{_competencia(ctx, decaida)}* é de {dias} dias atrás"
    raise ValueError(f"fator sem frase: {nome}")


def _competencia(ctx: _Contexto, ident: str) -> str:
    comp = ctx.catalogo.competencias.get(ident)
    return comp.titulo if comp else ident


def _trilha(ctx: _Contexto, ident: str) -> str:
    trilha = ctx.catalogo.trilhas.get(ident)
    return trilha.titulo if trilha else ident
