"""Snapshot compilado — a fronteira entre autoria e consumo (ADR-0004)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


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
