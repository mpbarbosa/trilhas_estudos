"""Escrita do percurso pela tela — a outra metade da borda de `web/percurso.py`.

`web/percurso.py` lê o percurso; este módulo grava nele. Os dois são borda de I/O no
mesmo nível de `cli.py`, e nenhum dos dois tem regra de domínio própria: quais eventos
cada ação produz é de `percurso.registrar`, a transação é de `Repositorio.anexar`, e a
conferência do recurso é a **mesma função** que `trilhas-percurso` chama. Interface que
recusasse o que a CLI aceita daria ao estudante dois sistemas com memórias diferentes
(docs/interface.md §3.3).

**Pré-requisito não satisfeito não impede concluir.** O log é de fatos, não de
permissões: quem leu o livro antes de o sistema saber disso concluiu a etapa, e o
sistema ter opinião contrária não desfaz a leitura. Quem filtra por fronteira
satisfeita é o motor, ao escolher o que *sugerir* (motor §2.2) — ali a regra protege
uma recomendação, aqui ela estaria negando um acontecimento. Recusar também poria em
`web/` uma comparação de `Nivel` que a §3.3 proíbe e que `registrar.concluir_etapa`
não faz.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from ..catalogo.modelo import Catalogo, Etapa, Nivel
from ..percurso import Evento, Repositorio, registrar


class Acao(StrEnum):
    """O que um POST de etapa pede. É o vocabulário do formulário, e o único."""

    INICIAR = "iniciar"
    CONCLUIR = "concluir"
    ABANDONAR = "abandonar"


class AcaoDaCompetencia(StrEnum):
    """O que um POST de competência pede (interface.md §5.12).

    Enum próprio, e não `Acao` alargada: as duas URLs recebem fatos de naturezas
    diferentes, e um vocabulário só deixaria `concluir` chegar à competência — a rota
    o aceitaria como ação conhecida para só então não achar o que fazer com ele. Cada
    URL recusa no mesmo lugar o que não é dela.
    """

    AUTOAVALIAR = "autoavaliar"
    RETRATAR = "retratar"


def registrar_na_etapa(
    diretorio: Path,
    estudante_id: str,
    catalogo: Catalogo,
    acao: Acao,
    etapa_id: str,
    *,
    recurso: str | None = None,
    motivo: str | None = None,
) -> str | None:
    """Grava os fatos de uma ação sobre uma etapa. Devolve o erro, ou `None`.

    Uma transação por chamada, e uma chamada por POST (docs/interface.md §9). Quem a
    abre é `Repositorio.anexar`: concluir são dois fatos — a conclusão e a evidência —
    e meia conclusão produziria progresso sem a evidência que o justifica.
    """
    etapa = catalogo.etapas.get(etapa_id)
    if etapa is None:
        return f"etapa desconhecida no catálogo: {etapa_id}"

    if acao is Acao.INICIAR and recurso:
        problema = registrar.conferir_recurso(recurso, catalogo, etapa)
        if problema is not None:
            return problema

    with Repositorio.em_diretorio(diretorio) as repo:
        repo.anexar(estudante_id, _eventos(acao, etapa, recurso=recurso, motivo=motivo))
    return None


def autoavaliar_competencia(
    diretorio: Path,
    estudante_id: str,
    catalogo: Catalogo,
    competencia_id: str,
    nivel_bruto: str | None,
) -> str | None:
    """Declara que se sabe algo, fora do sistema. Devolve o erro, ou `None` (§5.12).

    O mesmo caminho de `trilhas-percurso sei`: `registrar.conferir_autoavaliacao`
    decide o que vale — competência do catálogo, nível declarável —, e
    `registrar.registrar_autoavaliacao` grava, com a confiança menor que distingue
    "eu digo que sei" de "concluí a etapa" (`CONFIANCA_AUTOAVALIACAO`, motor §3.2).

    O nível chega como texto do formulário e é traduzido aqui, na borda, como o `seq`
    de `retratar_na_competencia`: converter o que veio do corpo HTTP é trabalho de
    quem recebe o corpo. Decidir *quais* níveis existem não é, e por isso a lista é
    de `registrar.NIVEIS_DECLARAVEIS`.

    Conferência fora da transação, ao contrário da retratação: o que se confere é o
    catálogo, que esta escrita não muda.
    """
    try:
        nivel = Nivel.de_texto(nivel_bruto or "")
    except ValueError:
        return f"nível desconhecido: {nivel_bruto!r} não é um nível da escala"

    problema = registrar.conferir_autoavaliacao(competencia_id, nivel, catalogo)
    if problema is not None:
        return problema

    with Repositorio.em_diretorio(diretorio) as repo:
        repo.anexar(estudante_id, registrar.registrar_autoavaliacao(competencia_id, nivel))
    return None


def retratar_na_competencia(
    diretorio: Path,
    estudante_id: str,
    seq_bruto: str | None,
    *,
    motivo: str | None = None,
) -> str | None:
    """Retrata a evidência de `seq`. Devolve o erro, ou `None` (ADR-0015).

    O alvo é o `seq`, não a competência da URL: a competência diz de qual tela o pedido
    saiu e para onde voltar, e repeti-la como alvo seria a redundância capaz de
    contradizer o fato que a [ADR-0014](../../../docs/adr/0014-retratacao-de-evidencia-por-seq.md)
    recusou dentro do próprio evento. A única regra é `registrar.conferir_retratacao` —
    a **mesma** que `trilhas-percurso retratar` chama, e por isso a tela recusa
    exatamente o que a CLI recusa (docs/interface.md §3.3).

    Conferência e escrita entram na mesma transação, como em `registrar_na_etapa`: o
    alvo "existe e não está retratado" é afirmação sobre o log, e conferi-la fora da
    transação que grava a deixaria valendo sobre um log que já mudou.
    """
    try:
        seq = int(seq_bruto or "")
    except ValueError:
        return f"seq inválido: {seq_bruto!r} não é um número de evento"

    with Repositorio.em_diretorio(diretorio) as repo:
        problema = registrar.conferir_retratacao(seq, repo.registros(estudante_id))
        if problema is not None:
            return problema
        repo.anexar(estudante_id, registrar.retratar_evidencia(seq, motivo=motivo))
    return None


def _eventos(acao: Acao, etapa: Etapa, *, recurso: str | None, motivo: str | None) -> list[Evento]:
    if acao is Acao.INICIAR:
        return registrar.iniciar_etapa(etapa, recurso=recurso or None)
    if acao is Acao.CONCLUIR:
        return registrar.concluir_etapa(etapa)
    return registrar.abandonar_etapa(etapa, motivo=motivo or None)
