"""Compila o catálogo validado em `catalogo.lock.json` (ADR-0004).

`catalogo_versao` é monotônica e só avança quando o conteúdo muda — comparado pelo
hash do catálogo normalizado, não pelo arquivo gerado (que carrega `gerado_em`).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import UTC, date, datetime
from typing import Any

from .modelo import Catalogo
from .snapshot import EstadoAnterior

VERSAO_SNAPSHOT = 1


def compilar(catalogo: Catalogo, anterior: EstadoAnterior | None = None) -> dict[str, Any]:
    """Monta o snapshot. Pressupõe catálogo já validado sem erros."""
    anterior = anterior or EstadoAnterior.vazio()
    corpo = {
        "competencias": [_serializar(c) for c in _ordenado(catalogo.competencias)],
        "etapas": [_serializar(e) for e in _ordenado(catalogo.etapas)],
        "trilhas": [_serializar(t) for t in _ordenado(catalogo.trilhas)],
        "recursos": [_serializar(r) for r in _ordenado(catalogo.recursos)],
    }
    digest = _hash(corpo)
    return {
        "versao_snapshot": VERSAO_SNAPSHOT,
        "catalogo_versao": anterior.versao + 1,
        "gerado_em": datetime.now(UTC).isoformat(timespec="seconds"),
        "hash": f"sha256:{digest}",
        **corpo,
    }


def estado_anterior(snapshot: dict[str, Any] | None) -> EstadoAnterior:
    """Extrai de um snapshot lido em disco o que a validação precisa."""
    if not snapshot:
        return EstadoAnterior.vazio()
    revs: dict[str, int] = {}
    for colecao in ("competencias", "etapas", "trilhas", "recursos"):
        for item in snapshot.get(colecao, []):
            revs[item["id"]] = int(item["rev"])
    return EstadoAnterior(
        versao=int(snapshot.get("catalogo_versao", 0)),
        ids=frozenset(revs),
        revs=revs,
    )


def mudou(snapshot_novo: dict[str, Any], snapshot_antigo: dict[str, Any] | None) -> bool:
    """True se o conteúdo difere — ignora `gerado_em` e `catalogo_versao`."""
    if not snapshot_antigo:
        return True
    return bool(snapshot_novo["hash"] != snapshot_antigo.get("hash"))


def _ordenado(indice: dict[str, Any]) -> list[Any]:
    return [indice[k] for k in sorted(indice)]


def _hash(corpo: dict[str, Any]) -> str:
    canonico = json.dumps(corpo, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonico.encode("utf-8")).hexdigest()


def _serializar(entidade: Any) -> dict[str, Any]:
    return {chave: _valor(v) for chave, v in asdict(entidade).items() if v != () and v is not None}


def _valor(valor: Any) -> Any:
    if isinstance(valor, date):
        return valor.isoformat()
    if isinstance(valor, tuple | list):
        return [_valor(v) for v in valor]
    if isinstance(valor, dict):
        return {k: _valor(v) for k, v in valor.items()}
    if hasattr(valor, "name") and hasattr(valor, "value"):  # Nivel / Status / Formato
        return str(valor)
    return valor
