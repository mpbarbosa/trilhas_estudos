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

from ..catalogo.modelo import Catalogo, Etapa
from ..percurso import Evento, Repositorio, registrar


class Acao(StrEnum):
    """O que um POST de etapa pede. É o vocabulário do formulário, e o único."""

    INICIAR = "iniciar"
    CONCLUIR = "concluir"
    ABANDONAR = "abandonar"


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


def _eventos(acao: Acao, etapa: Etapa, *, recurso: str | None, motivo: str | None) -> list[Evento]:
    if acao is Acao.INICIAR:
        return registrar.iniciar_etapa(etapa, recurso=recurso or None)
    if acao is Acao.CONCLUIR:
        return registrar.concluir_etapa(etapa)
    return registrar.abandonar_etapa(etapa, motivo=motivo or None)
