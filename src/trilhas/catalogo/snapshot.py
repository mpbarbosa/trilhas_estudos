"""Snapshot compilado — a fronteira entre autoria e consumo (ADR-0004)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

VERSAO_SNAPSHOT = 1


@dataclass(frozen=True, slots=True)
class EstadoAnterior:
    """O mínimo do snapshot anterior de que a validação precisa.

    Mantém `validar` independente do formato do arquivo de snapshot.
    """

    versao: int
    ids: frozenset[str]
    revs: Mapping[str, int]

    @classmethod
    def vazio(cls) -> EstadoAnterior:
        return cls(versao=0, ids=frozenset(), revs={})


@dataclass(frozen=True, slots=True)
class Cabecalho:
    """Identificação do snapshot lido — o que a auditoria precisa citar.

    `catalogo_versao` é o que toda `Sugestao` persiste para ser reproduzível
    (docs/catalogo.md §5), e `hash` é o que diz se o catálogo em memória envelheceu.
    """

    versao_snapshot: int
    catalogo_versao: int
    gerado_em: str
    hash: str

    @classmethod
    def de(cls, dados: Mapping[str, Any]) -> Cabecalho:
        return cls(
            versao_snapshot=int(dados.get("versao_snapshot", 0)),
            catalogo_versao=int(dados.get("catalogo_versao", 0)),
            gerado_em=str(dados.get("gerado_em", "")),
            hash=str(dados.get("hash", "")),
        )
