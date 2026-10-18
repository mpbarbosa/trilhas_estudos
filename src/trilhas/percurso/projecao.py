"""Projeta o log de eventos no `Percurso` que o motor consome (ADR-0008). Puro.

`competencias_dominadas` é **derivada**: não existe caminho que produza competência
dominada sem evidência que a origine ([CONTEXT §4](../../../docs/CONTEXT.md)). O campo
homônimo do YAML é ignorado de propósito — ver `importar_competencias_declaradas`
em `registrar` para migrar um percurso que ainda o declare.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import replace

from trilhas.motor.modelo import (
    CompetenciaDominada,
    EstadoEtapa,
    Feedback,
    Percurso,
    ProgressoEtapa,
)

from .eventos import (
    EtapaAbandonada,
    EtapaConcluida,
    EtapaIniciada,
    EvidenciaRegistrada,
    FeedbackDado,
    Registro,
)


def competencias_de(registros: Iterable[Registro]) -> tuple[CompetenciaDominada, ...]:
    """Nível é o máximo evidenciado; a data é da evidência mais recente nesse nível.

    Usar a evidência mais recente *do nível vigente* — e não a mais recente de
    qualquer nível — é o que faz `urgencia_de_revisao` (motor §3.6) medir o
    decaimento do que a pessoa sabe hoje, não de um nível que ela já superou.
    """
    melhor: dict[str, CompetenciaDominada] = {}
    for registro in _ordenados(registros):
        evento = registro.evento
        if not isinstance(evento, EvidenciaRegistrada):
            continue
        atual = melhor.get(evento.competencia)
        if atual is not None and evento.nivel < atual.nivel:
            continue
        if (
            atual is not None
            and evento.nivel == atual.nivel
            and registro.dia < atual.ultima_evidencia_em
        ):
            continue
        melhor[evento.competencia] = CompetenciaDominada(
            competencia=evento.competencia,
            nivel=evento.nivel,
            ultima_evidencia_em=registro.dia,
            confianca=evento.confianca,
        )
    return tuple(melhor[chave] for chave in sorted(melhor))


def progresso_de(registros: Iterable[Registro]) -> tuple[ProgressoEtapa, ...]:
    """O último fato sobre cada etapa vence, pela ordem do log.

    `recurso_em_uso` é a exceção a "o último vence": só `EtapaIniciada` o carrega, e
    concluir não o repete. Esquecê-lo na conclusão faria a etapa concluída perder por
    qual recurso foi estudada — que é justamente o que se quer saber depois.
    """
    estado: dict[str, ProgressoEtapa] = {}
    for registro in _ordenados(registros):
        evento = registro.evento
        # isinstance em vez de tabela por `type`: só estes três têm `etapa: str`, e é
        # o que deixa o verificador conferir o acesso.
        if isinstance(evento, EtapaIniciada):
            situacao = EstadoEtapa.EM_ANDAMENTO
        elif isinstance(evento, EtapaConcluida):
            situacao = EstadoEtapa.CONCLUIDA
        elif isinstance(evento, EtapaAbandonada):
            situacao = EstadoEtapa.ABANDONADA
        else:
            continue
        anterior = estado.get(evento.etapa)
        recurso = evento.recurso if isinstance(evento, EtapaIniciada) else None
        estado[evento.etapa] = ProgressoEtapa(
            etapa=evento.etapa,
            estado=situacao,
            atualizado_em=registro.dia,
            recurso_em_uso=recurso or (anterior.recurso_em_uso if anterior else None),
        )
    return tuple(estado[chave] for chave in sorted(estado))


def feedback_de(registros: Iterable[Registro]) -> tuple[Feedback, ...]:
    """Todo feedback é mantido: o motor conta rejeições numa janela (motor §4)."""
    return tuple(
        Feedback(etapa=r.evento.etapa, reacao=r.evento.reacao, em=r.dia)
        for r in _ordenados(registros)
        if isinstance(r.evento, FeedbackDado)
    )


def montar_percurso(base: Percurso, registros: Iterable[Registro]) -> Percurso:
    """Combina o estado declarado (YAML) com os fatos do log.

    Do `base` vêm identidade, restrições, objetivo e matrículas — o que o estudante
    declara. Do log vêm competências, progresso e feedback — o que aconteceu.
    """
    guardados = list(registros)
    return replace(
        base,
        competencias=competencias_de(guardados),
        progresso=progresso_de(guardados),
        feedback=feedback_de(guardados),
    )


def _ordenados(registros: Iterable[Registro]) -> Sequence[Registro]:
    return sorted(registros, key=lambda r: (r.seq, r.em))
