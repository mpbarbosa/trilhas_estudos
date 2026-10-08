"""Construtores enxutos para montar catálogos em memória nos testes."""

from __future__ import annotations

from datetime import date

from trilhas.catalogo.modelo import (
    Alvo,
    Catalogo,
    Competencia,
    Ensino,
    Etapa,
    Formato,
    Nivel,
    Recurso,
    Requisito,
    Status,
    Trilha,
)

N = Nivel

# Data de referência dos testes; mantém §5.10 (recurso não verificado) quieta.
VERIFICADO_EM = date(2026, 10, 8)


def competencia(
    ident: str, *, rev: int = 1, status: Status = Status.ATIVO, **kw: object
) -> Competencia:
    return Competencia(
        id=ident,
        titulo=ident,
        rev=rev,
        status=status,
        verificacao="critério de verificação",
        **kw,  # type: ignore[arg-type]
    )


def etapa(
    ident: str,
    *,
    requires: list[tuple[str, Nivel]] | None = None,
    teaches: list[tuple[str, Nivel]] | None = None,
    rev: int = 1,
    status: Status = Status.ATIVO,
    trilha: str | None = None,
    esforco: int = 60,
    **kw: object,
) -> Etapa:
    return Etapa(
        id=ident,
        titulo=ident,
        rev=rev,
        status=status,
        esforco_estimado_min=esforco,
        trilha=trilha,
        requires=tuple(Requisito(c, n) for c, n in (requires or [])),
        teaches=tuple(Ensino(c, n) for c, n in (teaches or [])),
        **kw,  # type: ignore[arg-type]
    )


def recurso(
    ident: str,
    etapa_id: str,
    *,
    disponivel: bool = True,
    status: Status = Status.ATIVO,
    rev: int = 1,
    verificado_em: date | None = VERIFICADO_EM,
    **kw: object,
) -> Recurso:
    return Recurso(
        id=ident,
        titulo=ident,
        rev=rev,
        status=status,
        etapa=etapa_id,
        formato=Formato.TEXTO,
        idioma="pt-BR",
        custo=0.0,
        duracao_min=60,
        url="https://exemplo.invalid/x",
        disponivel=disponivel,
        verificado_em=verificado_em,
        **kw,  # type: ignore[arg-type]
    )


def trilha(
    ident: str,
    *,
    etapas: list[str] | None = None,
    referenciadas: list[str] | None = None,
    objetivo: list[tuple[str, Nivel]] | None = None,
    rev: int = 1,
    status: Status = Status.ATIVO,
    **kw: object,
) -> Trilha:
    return Trilha(
        id=ident,
        titulo=ident,
        rev=rev,
        status=status,
        objetivo_declarado=tuple(Alvo(c, n) for c, n in (objetivo or [])),
        etapas=tuple(etapas or []),
        etapas_referenciadas=tuple(referenciadas or []),
        **kw,  # type: ignore[arg-type]
    )


def catalogo(*entidades: object) -> Catalogo:
    cat = Catalogo()
    for ent in entidades:
        if isinstance(ent, Competencia):
            cat.competencias[ent.id] = ent
        elif isinstance(ent, Etapa):
            cat.etapas[ent.id] = ent
        elif isinstance(ent, Recurso):
            cat.recursos[ent.id] = ent
        elif isinstance(ent, Trilha):
            cat.trilhas[ent.id] = ent
        else:  # pragma: no cover
            raise TypeError(f"entidade desconhecida: {ent!r}")
    return cat


def minimo_valido() -> Catalogo:
    """Uma competência, uma etapa que a ensina, um recurso e uma trilha."""
    return catalogo(
        competencia("comp:x/base"),
        etapa("etapa:x/inicial", teaches=[("comp:x/base", N.INICIANTE)], trilha="trilha:x/t"),
        recurso("rec:x/inicial", "etapa:x/inicial"),
        trilha(
            "trilha:x/t",
            etapas=["etapa:x/inicial"],
            objetivo=[("comp:x/base", N.INICIANTE)],
        ),
    )
