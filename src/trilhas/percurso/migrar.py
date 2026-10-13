"""Converte um `percurso/*.yaml` em fatos datados (ADR-0008). Domínio puro.

A ADR tirou `competencias_dominadas`, `progresso` e `feedback` do YAML e os tornou
projeção do log. Sem esta conversão, adotá-la apagaria em silêncio o progresso já
registrado — o YAML de hoje declara etapas em andamento desde 2026-10-08.

Cada fato conserva **a data que o YAML declarava**, não a data da migração: é a
diferença entre importar história e inventá-la. Daí `list[tuple[Evento, datetime]]`
em vez de um lote com um instante só.

Uma etapa já concluída **não** gera evidência aqui. `concluir_etapa` gera, porque lá o
catálogo é consultado no momento da ação; sintetizar evidência retroativa a partir do
`teaches` de hoje seria exatamente o que "fato datado não retroage" proíbe. A
competência de quem concluiu etapa antes desta ADR vem de `competencias_dominadas`.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, date, datetime
from typing import Any

from trilhas.catalogo.modelo import Nivel
from trilhas.motor.modelo import Reacao

from .eventos import (
    EtapaAbandonada,
    EtapaConcluida,
    EtapaIniciada,
    Evento,
    EvidenciaRegistrada,
    FeedbackDado,
    Origem,
)

Datado = tuple[Evento, datetime]


def eventos_do_yaml(dados: Mapping[str, Any]) -> list[Datado]:
    """Todos os fatos que o YAML declarava, em ordem cronológica."""
    fatos: list[Datado] = []
    fatos += _competencias(_mapa(dados.get("perfil")))
    fatos += _progresso(dados.get("progresso"))
    fatos += _feedback(dados.get("feedback"))
    return sorted(fatos, key=lambda par: par[1])


def _competencias(perfil: Mapping[str, Any]) -> list[Datado]:
    fatos: list[Datado] = []
    for item in _lista(perfil.get("competencias_dominadas")):
        competencia = item.get("competencia")
        nivel = _nivel(item.get("nivel"))
        quando = _data(item.get("ultima_evidencia_em"))
        if not competencia or nivel is None or quando is None:
            continue
        fatos.append(
            (
                EvidenciaRegistrada(
                    competencia=str(competencia),
                    nivel=nivel,
                    origem=Origem.AUTOAVALIACAO,
                    confianca=float(item.get("confianca", 1.0)),
                ),
                _instante(quando),
            )
        )
    return fatos


def _progresso(bruto: Any) -> list[Datado]:
    fatos: list[Datado] = []
    for item in _lista(bruto):
        etapa = item.get("etapa")
        if not etapa:
            continue
        rev = int(item.get("rev", 1))
        estado = str(item.get("estado", "nao_iniciada"))
        concluida = _data(item.get("concluida_em"))
        abandonada = _data(item.get("abandonada_em"))
        iniciada = _data(item.get("iniciada_em"))

        if estado == "concluida" and (concluida or iniciada):
            quando = concluida or iniciada
            evento: Evento = EtapaConcluida(etapa=str(etapa), etapa_rev=rev)
        elif estado == "abandonada" and (abandonada or iniciada):
            quando = abandonada or iniciada
            evento = EtapaAbandonada(etapa=str(etapa), etapa_rev=rev)
        elif estado == "em_andamento" and iniciada:
            quando = iniciada
            evento = EtapaIniciada(
                etapa=str(etapa), etapa_rev=rev, recurso=item.get("recurso_em_uso")
            )
        else:
            continue
        assert quando is not None
        fatos.append((evento, _instante(quando)))
    return fatos


def _feedback(bruto: Any) -> list[Datado]:
    fatos: list[Datado] = []
    for item in _lista(bruto):
        etapa = item.get("etapa")
        quando = _data(item.get("em") or item.get("data"))
        try:
            reacao = Reacao(str(item.get("reacao", "")))
        except ValueError:
            continue
        if not etapa or quando is None:
            continue
        fatos.append((FeedbackDado(etapa=str(etapa), reacao=reacao), _instante(quando)))
    return fatos


def _instante(dia: date) -> datetime:
    return datetime(dia.year, dia.month, dia.day, tzinfo=UTC)


def _mapa(valor: Any) -> Mapping[str, Any]:
    return valor if isinstance(valor, Mapping) else {}


def _lista(valor: Any) -> list[Mapping[str, Any]]:
    if not isinstance(valor, list):
        return []
    return [item for item in valor if isinstance(item, Mapping)]


def _data(valor: Any) -> date | None:
    if isinstance(valor, date):
        return valor
    try:
        return date.fromisoformat(str(valor))
    except (TypeError, ValueError):
        return None


def _nivel(valor: Any) -> Nivel | None:
    try:
        return Nivel.de_texto(str(valor))
    except ValueError:
        return None
