"""Problemas de catálogo: erros bloqueiam o snapshot, avisos não.

Os códigos correspondem às validações de docs/catalogo.md §5.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Severidade(StrEnum):
    ERRO = "erro"
    AVISO = "aviso"


class Codigo(StrEnum):
    # Erros de forma (antes das validações numeradas)
    YAML_INVALIDO = "CAT-000"
    SCHEMA_INVALIDO = "CAT-001"
    # Validações de catalogo.md §5
    ID_INVALIDO = "CAT-010"  # §5.1 formato / duplicado / reaproveitado
    REFERENCIA_QUEBRADA = "CAT-020"  # §5.2
    ETAPA_INALCANCAVEL = "CAT-030"  # §5.3
    BECO_SEM_SAIDA = "CAT-040"  # §5.4
    SEM_RECURSO = "CAT-050"  # §5.5
    OBJETIVO_INALCANCAVEL = "CAT-060"  # §5.6
    NIVEL_REBAIXA = "CAT-070"  # §5.7
    DEPRECIACAO_INCOERENTE = "CAT-080"  # §5.8
    REV_DECRESCEU = "CAT-090"  # §5.9
    RECURSO_NAO_VERIFICADO = "CAT-100"  # §5.10 — aviso
    ETAPA_ORFA = "CAT-110"  # §5.11 — aviso


@dataclass(frozen=True, slots=True)
class Problema:
    codigo: Codigo
    severidade: Severidade
    mensagem: str
    entidade: str | None = None
    arquivo: str | None = None
    linha: int | None = None

    def __str__(self) -> str:
        local = self.arquivo or ""
        if local and self.linha:
            local = f"{local}:{self.linha}"
        alvo = self.entidade or local or "-"
        prefixo = f"{self.codigo.value} {self.severidade.value}"
        sufixo = f"  ({local})" if local and self.entidade else ""
        return f"{prefixo}  {alvo}: {self.mensagem}{sufixo}"


def erro(codigo: Codigo, mensagem: str, **kw: object) -> Problema:
    return Problema(codigo, Severidade.ERRO, mensagem, **kw)  # type: ignore[arg-type]


def aviso(codigo: Codigo, mensagem: str, **kw: object) -> Problema:
    return Problema(codigo, Severidade.AVISO, mensagem, **kw)  # type: ignore[arg-type]


def tem_erro(problemas: list[Problema]) -> bool:
    return any(p.severidade is Severidade.ERRO for p in problemas)
