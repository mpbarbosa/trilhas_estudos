"""Deriva os eventos de cada ação do estudante (ADR-0008). Domínio puro.

O catálogo é consultado **aqui**, na escrita, uma vez. Concluir uma etapa grava a
evidência do que ela ensinava naquele momento, com a `rev` da etapa; a projeção nunca
reconsulta `teaches`. É o que faz "fato datado não retroage" valer por construção
(catalogo.md §4) em vez de depender de alguém não recalcular.
"""

from __future__ import annotations

from trilhas.catalogo.modelo import Etapa, Nivel
from trilhas.motor.modelo import Reacao, Sugestao

from .eventos import (
    EtapaAbandonada,
    EtapaConcluida,
    EtapaIniciada,
    Evento,
    EvidenciaRegistrada,
    FeedbackDado,
    Origem,
    SugestaoEmitida,
)

# Concluir uma etapa é observável; dizer que se sabe algo, não. A diferença pesa no
# fator `prontidao` (motor §3.2), que desconta confiança baixa.
CONFIANCA_CONCLUSAO = 1.0
CONFIANCA_AUTOAVALIACAO = 0.6


def iniciar_etapa(etapa: Etapa, *, recurso: str | None = None) -> list[Evento]:
    return [EtapaIniciada(etapa=etapa.id, etapa_rev=etapa.rev, recurso=recurso)]


def concluir_etapa(etapa: Etapa, *, confianca: float = CONFIANCA_CONCLUSAO) -> list[Evento]:
    """Conclusão mais a evidência de cada competência que a etapa ensinava.

    Etapa sem `teaches` gera só a conclusão: há progresso, não há competência nova.
    """
    eventos: list[Evento] = [EtapaConcluida(etapa=etapa.id, etapa_rev=etapa.rev)]
    eventos += [
        EvidenciaRegistrada(
            competencia=ensino.competencia,
            nivel=ensino.nivel_resultante,
            origem=Origem.CONCLUSAO_DE_ETAPA,
            confianca=confianca,
            etapa=etapa.id,
            etapa_rev=etapa.rev,
        )
        for ensino in etapa.teaches
    ]
    return eventos


def abandonar_etapa(etapa: Etapa, *, motivo: str | None = None) -> list[Evento]:
    """Abandono não retira evidência: o que já foi aprendido continua aprendido."""
    return [EtapaAbandonada(etapa=etapa.id, etapa_rev=etapa.rev, motivo=motivo)]


def registrar_autoavaliacao(
    competencia: str, nivel: Nivel, *, confianca: float = CONFIANCA_AUTOAVALIACAO
) -> list[Evento]:
    """Competência adquirida fora do sistema (motor §4), com confiança menor."""
    return [
        EvidenciaRegistrada(
            competencia=competencia,
            nivel=nivel,
            origem=Origem.AUTOAVALIACAO,
            confianca=confianca,
        )
    ]


def dar_feedback(etapa_id: str, reacao: Reacao, *, motivo: str | None = None) -> list[Evento]:
    return [FeedbackDado(etapa=etapa_id, reacao=reacao, motivo=motivo)]


def emitir_sugestao(sugestao: Sugestao) -> list[Evento]:
    """Grava a sugestão como fato, com os fatores que a produziram (ADR-0003)."""
    return [
        SugestaoEmitida(
            etapa=sugestao.etapa_id,
            recurso=sugestao.recurso_sugerido_id,
            score=sugestao.score,
            tipo=sugestao.tipo,
            catalogo_versao=sugestao.catalogo_versao,
            fatores=tuple((f.nome, f.contribuicao) for f in sugestao.fatores),
        )
    ]
