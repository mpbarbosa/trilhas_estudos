"""Deriva os eventos de cada ação do estudante (ADR-0008). Domínio puro.

O catálogo é consultado **aqui**, na escrita, uma vez. Concluir uma etapa grava a
evidência do que ela ensinava naquele momento, com a `rev` da etapa; a projeção nunca
reconsulta `teaches`. É o que faz "fato datado não retroage" valer por construção
(catalogo.md §4) em vez de depender de alguém não recalcular.
"""

from __future__ import annotations

from trilhas.catalogo.modelo import Catalogo, Etapa, Nivel, Recurso
from trilhas.motor.modelo import Reacao, Sugestao

from .eventos import (
    EtapaAbandonada,
    EtapaConcluida,
    EtapaIniciada,
    Evento,
    EvidenciaRegistrada,
    FeedbackDado,
    Origem,
    RecursoPercorrido,
    SugestaoEmitida,
)

# Concluir uma etapa é observável; dizer que se sabe algo, não. A diferença pesa no
# fator `prontidao` (motor §3.2), que desconta confiança baixa.
CONFIANCA_CONCLUSAO = 1.0
CONFIANCA_AUTOAVALIACAO = 0.6


def conferir_recurso(recurso_id: str, catalogo: Catalogo, etapa: Etapa) -> str | None:
    """Confere o recurso declarado ao iniciar uma etapa. Devolve o erro, ou `None`.

    Exige **pertencer à etapa**, não só existir: um recurso pertence a uma etapa só, e
    um livro que atende sete etapas é sete recursos (catalogo.md §2, ADR-0009), então
    "estudo esta etapa por aquele material" sempre tem um id próprio desta etapa — a
    conferência mais forte não fecha porta nenhuma e pega a troca de fatia.

    `status` e `disponivel` ficam de fora de propósito: estudar por recurso depreciado
    ou que saiu do ar é fato legítimo de quem já tem o material em mãos, e fato datado
    não se recusa pelo catálogo de hoje (catalogo.md §4).

    Mora aqui, e não na CLI, porque a tela também inicia etapa (interface.md §5.10):
    duas cópias desta regra divergiriam, e a interface recusaria o que a CLI aceita.
    """
    recurso = catalogo.recursos.get(recurso_id)
    if recurso is None:
        return f"recurso desconhecido no catálogo: {recurso_id}"
    if recurso.etapa != etapa.id:
        return f"recurso de outra etapa: {recurso_id} é de {recurso.etapa}, não de {etapa.id}"
    return None


def conferir_recurso_avulso(recurso_id: str, catalogo: Catalogo) -> str | None:
    """Confere o recurso que se percorreu. Devolve o erro, ou `None` (ADR-0012).

    Mais fraca que `conferir_recurso` de propósito: percorrer material não é sobre uma
    etapa, então não há com que comparar o `etapa` do recurso — existir no catálogo é
    tudo que se pode exigir.

    `status` e `disponivel` ficam de fora pelo mesmo motivo de lá: percorrer material
    depreciado ou fora do ar é fato legítimo de quem o tem em mãos, e fato datado não se
    recusa pelo catálogo de hoje (catalogo.md §4).
    """
    if recurso_id not in catalogo.recursos:
        return f"recurso desconhecido no catálogo: {recurso_id}"
    return None


def percorrer_recurso(recurso: Recurso) -> list[Evento]:
    """Material percorrido de ponta a ponta. **Sem evidência de competência** (ADR-0012).

    O verbo é `percorrer`, não `concluir`: CONTEXT §1 reserva "concluível" à etapa, e
    `concluir_etapa` emite evidência. Um `concluir_recurso` que não emitisse faria o
    mesmo verbo significar duas forças de fato — a confusão que a ADR existe para evitar.
    """
    return [RecursoPercorrido(recurso=recurso.id, recurso_rev=recurso.rev)]


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
