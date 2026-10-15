"""Leitura do acervo — a borda de I/O da interface.

A entrada é o **snapshot** `catalogo.lock.json`, nunca o YAML de autoria (ADR-0004).
A exceção é o diagnóstico (docs/interface.md §5.6), que precisa justamente comparar
autoria e snapshot para dizer o que a CLI diria.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..catalogo.carregar import carregar, do_snapshot
from ..catalogo.compilar import compilar, estado_anterior, mudou
from ..catalogo.grafo import ArestaDerivada, Fecho, arestas_derivadas, fecho_progressivo
from ..catalogo.modelo import Catalogo
from ..catalogo.problemas import Codigo, Problema, erro
from ..catalogo.snapshot import Cabecalho
from ..catalogo.validar import validar

NOME_DO_LOCK = "catalogo.lock.json"
NOME_DA_AUTORIA = "catalogo"
NOME_DO_PERCURSO = "percurso"


@dataclass(frozen=True, slots=True)
class Acervo:
    """O catálogo em memória, com o grafo já resolvido.

    `fecho` e `arestas` são calculados uma vez por snapshot: são função do catálogo,
    e recalculá-los por requisição seria desperdício sem ganho.
    """

    cabecalho: Cabecalho
    catalogo: Catalogo
    fecho: Fecho
    arestas: tuple[ArestaDerivada, ...]
    problemas: tuple[Problema, ...] = ()

    @classmethod
    def de_dados(cls, dados: dict[str, Any]) -> Acervo:
        catalogo, problemas = do_snapshot(dados)
        ativas = catalogo.etapas_ativas()
        return cls(
            cabecalho=Cabecalho.de(dados),
            catalogo=catalogo,
            fecho=fecho_progressivo(ativas),
            arestas=arestas_derivadas(ativas),
            problemas=tuple(problemas),
        )

    @classmethod
    def vazio(cls) -> Acervo:
        return cls(
            cabecalho=Cabecalho(0, 0, "", ""),
            catalogo=Catalogo(),
            fecho=Fecho(perfil={}, onda={}),
            arestas=(),
        )


@dataclass(frozen=True, slots=True)
class Diagnostico:
    """O que a CLI diria sobre o catálogo, para quem não roda a CLI."""

    problemas: tuple[Problema, ...]
    fonte: str
    lock_desatualizado: bool | None
    """`None` quando não foi possível conferir (sem diretório de autoria)."""


class Fonte:
    """Lê o snapshot e o relê quando o arquivo muda.

    Recarregar por `mtime` em vez de manter o processo preso ao primeiro estado é o
    que permite rodar `trilhas compilar` com a interface aberta.
    """

    def __init__(self, lock: Path) -> None:
        self.lock = lock
        self._mtime: float | None = None
        self._acervo = Acervo.vazio()

    @property
    def autoria(self) -> Path:
        return self.lock.parent / NOME_DA_AUTORIA

    @property
    def percursos(self) -> Path:
        """Diretório de percurso, ao lado do snapshot. Leitura apenas (web/percurso.py)."""
        return self.lock.parent / NOME_DO_PERCURSO

    def acervo(self) -> Acervo:
        mtime = self.lock.stat().st_mtime if self.lock.is_file() else None
        if mtime != self._mtime or self._mtime is None:
            self._acervo = self._ler()
            self._mtime = mtime
        return self._acervo

    def _ler(self) -> Acervo:
        dados = _ler_json(self.lock)
        if dados is None:
            vazio = Acervo.vazio()
            return Acervo(
                cabecalho=vazio.cabecalho,
                catalogo=vazio.catalogo,
                fecho=vazio.fecho,
                arestas=(),
                problemas=(
                    erro(
                        Codigo.YAML_INVALIDO,
                        "snapshot não encontrado ou ilegível — rode `trilhas compilar`",
                        arquivo=str(self.lock),
                    ),
                ),
            )
        return Acervo.de_dados(dados)

    def diagnosticar(self) -> Diagnostico:
        """Roda as 12 validações sobre a autoria, e confere se o lock está em dia.

        Sem diretório de autoria (pacote instalado sem as fontes), cai para validar o
        próprio snapshot — menos útil, mas honesto sobre o que conferiu.
        """
        anterior_bruto = _ler_json(self.lock)
        anterior = estado_anterior(anterior_bruto)

        if self.autoria.is_dir():
            catalogo, problemas = carregar(self.autoria)
            problemas += validar(catalogo, anterior)
            desatualizado: bool | None = None
            if not any(p.severidade == "erro" for p in problemas):
                desatualizado = mudou(compilar(catalogo, anterior), anterior_bruto)
            return Diagnostico(tuple(problemas), f"{self.autoria.name}/", desatualizado)

        acervo = self.acervo()
        problemas = list(acervo.problemas) + validar(acervo.catalogo, anterior)
        return Diagnostico(tuple(problemas), NOME_DO_LOCK, None)


def _ler_json(caminho: Path) -> dict[str, Any] | None:
    if not caminho.is_file():
        return None
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return dados if isinstance(dados, dict) else None
