"""Modelo imutável do catálogo.

Os nomes seguem o glossário de docs/CONTEXT.md — a linguagem do domínio é pt-BR,
inclusive no código.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from enum import IntEnum, StrEnum
from typing import Protocol, Self

_AREA_SLUG = r"[a-z0-9][a-z0-9-]*/[a-z0-9][a-z0-9-]*"

# Uniforme nos quatro tipos: `<tipo>:<area>/<slug>` (catalogo.md §3).
ID_PADROES = {
    prefixo: re.compile(rf"^{prefixo}:{_AREA_SLUG}$")
    for prefixo in ("comp", "etapa", "rec", "trilha")
}

FORMA_DO_ID = {prefixo: f"{prefixo}:<area>/<slug>" for prefixo in ID_PADROES}

VERSAO_SCHEMA_SUPORTADA = 1


class Nivel(IntEnum):
    """Escala ordinal de domínio de uma competência (CONTEXT.md §1)."""

    DESCONHECE = 0
    INICIANTE = 1
    INTERMEDIARIO = 2
    AVANCADO = 3

    @classmethod
    def de_texto(cls, texto: str) -> Self:
        try:
            return cls[texto.upper()]
        except KeyError:
            raise ValueError(f"nível desconhecido: {texto!r}") from None

    def __str__(self) -> str:
        return self.name.lower()


class Status(StrEnum):
    """Ciclo de vida de uma entidade de catálogo (catalogo.md §6)."""

    RASCUNHO = "rascunho"
    ATIVO = "ativo"
    DEPRECIADO = "depreciado"

    @property
    def ativo(self) -> bool:
        return self is Status.ATIVO


class Formato(StrEnum):
    VIDEO = "video"
    TEXTO = "texto"
    EXERCICIO = "exercicio"
    PROJETO = "projeto"


@dataclass(frozen=True, slots=True)
class Requisito:
    """Competência exigida por uma etapa, em nível mínimo."""

    competencia: str
    nivel_minimo: Nivel


@dataclass(frozen=True, slots=True)
class Ensino:
    """Competência desenvolvida por uma etapa, no nível resultante."""

    competencia: str
    nivel_resultante: Nivel


@dataclass(frozen=True, slots=True)
class Alvo:
    """Competência-alvo de um objetivo declarado."""

    competencia: str
    nivel: Nivel


@dataclass(frozen=True, slots=True)
class Competencia:
    id: str
    titulo: str
    rev: int
    status: Status
    verificacao: str
    descricao: str = ""
    substituido_por: str | None = None
    depreciado_em: date | None = None


@dataclass(frozen=True, slots=True)
class Etapa:
    id: str
    titulo: str
    rev: int
    status: Status
    esforco_estimado_min: int
    trilha: str | None = None
    opcional: bool = False
    requires: tuple[Requisito, ...] = ()
    teaches: tuple[Ensino, ...] = ()
    substituido_por: str | None = None
    depreciado_em: date | None = None


@dataclass(frozen=True, slots=True)
class Recurso:
    id: str
    titulo: str
    rev: int
    status: Status
    etapa: str
    formato: Formato
    idioma: str
    custo: float
    duracao_min: int
    url: str
    disponivel: bool
    verificado_em: date | None = None
    substituido_por: str | None = None
    depreciado_em: date | None = None


@dataclass(frozen=True, slots=True)
class Trilha:
    id: str
    titulo: str
    rev: int
    status: Status
    objetivo_declarado: tuple[Alvo, ...] = ()
    etapas: tuple[str, ...] = ()
    etapas_referenciadas: tuple[str, ...] = ()
    substituido_por: str | None = None
    depreciado_em: date | None = None

    @property
    def todas_as_etapas(self) -> tuple[str, ...]:
        return self.etapas + self.etapas_referenciadas


class EntidadeCatalogo(Protocol):
    """O que toda entidade de catálogo tem em comum (catalogo.md §3 e §6).

    Declarado como propriedades somente-leitura para casar com dataclasses congeladas.
    """

    @property
    def id(self) -> str: ...

    @property
    def titulo(self) -> str: ...

    @property
    def rev(self) -> int: ...

    @property
    def status(self) -> Status: ...

    @property
    def substituido_por(self) -> str | None: ...

    @property
    def depreciado_em(self) -> date | None: ...


@dataclass(frozen=True, slots=True)
class Catalogo:
    """Catálogo resolvido, indexado por id. Produto de `carregar`."""

    competencias: dict[str, Competencia] = field(default_factory=dict)
    etapas: dict[str, Etapa] = field(default_factory=dict)
    recursos: dict[str, Recurso] = field(default_factory=dict)
    trilhas: dict[str, Trilha] = field(default_factory=dict)

    def recursos_da_etapa(self, etapa_id: str) -> list[Recurso]:
        return [r for r in self.recursos.values() if r.etapa == etapa_id]

    def etapas_ativas(self) -> list[Etapa]:
        return [e for e in self.etapas.values() if e.status.ativo]

    def ensina(self, competencia_id: str, *, somente_ativas: bool = True) -> list[Etapa]:
        """Etapas que desenvolvem a competência."""
        return [
            e
            for e in self.etapas.values()
            if (e.status.ativo or not somente_ativas)
            and any(t.competencia == competencia_id for t in e.teaches)
        ]

    def ids(self) -> set[str]:
        return {*self.competencias, *self.etapas, *self.recursos, *self.trilhas}

    def por_id(self) -> dict[str, EntidadeCatalogo]:
        """Todas as entidades indexadas por id, qualquer que seja o tipo."""
        return {**self.competencias, **self.etapas, **self.recursos, **self.trilhas}

    def revs(self) -> dict[str, int]:
        return {ident: ent.rev for ident, ent in self.por_id().items()}
