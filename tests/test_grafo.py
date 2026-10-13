"""Fecho progressivo e arestas derivadas — as duas armadilhas de docs/interface.md §4."""

from __future__ import annotations

from fabrica import N, catalogo, competencia, etapa
from trilhas.catalogo.grafo import arestas_derivadas, fecho_progressivo
from trilhas.catalogo.modelo import Nivel, Status


def _cadeia():
    """a → b → c, cada etapa exigindo o que a anterior ensina."""
    return catalogo(
        competencia("comp:x/um"),
        competencia("comp:x/dois"),
        etapa("etapa:x/a", teaches=[("comp:x/um", N.INICIANTE)]),
        etapa(
            "etapa:x/b",
            requires=[("comp:x/um", N.INICIANTE)],
            teaches=[("comp:x/dois", N.INICIANTE)],
        ),
        etapa("etapa:x/c", requires=[("comp:x/dois", N.INICIANTE)]),
    )


def test_onda_e_a_profundidade_de_pre_requisito() -> None:
    fecho = fecho_progressivo(_cadeia().etapas.values())
    assert fecho.onda == {"etapa:x/a": 1, "etapa:x/b": 2, "etapa:x/c": 3}
    assert fecho.ondas == 3
    assert fecho.liberadas == {"etapa:x/a", "etapa:x/b", "etapa:x/c"}


def test_etapa_presa_nao_entra_no_fecho() -> None:
    cat = catalogo(
        competencia("comp:x/um"),
        etapa("etapa:x/presa", requires=[("comp:x/um", N.AVANCADO)]),
        etapa("etapa:x/livre", teaches=[("comp:x/um", N.INICIANTE)]),
    )
    fecho = fecho_progressivo(cat.etapas.values())
    assert "etapa:x/presa" not in fecho.liberadas
    assert fecho.nivel("comp:x/um") is Nivel.INICIANTE
    assert fecho.nivel("comp:x/inexistente") is Nivel.DESCONHECE


def test_onda_nao_depende_da_ordem_de_iteracao() -> None:
    """Determinismo: o layout da interface depende disto (ADR-0007)."""
    etapas = list(_cadeia().etapas.values())
    direta = fecho_progressivo(etapas)
    inversa = fecho_progressivo(reversed(etapas))
    assert direta.onda == inversa.onda


def test_etapa_sem_requisito_entra_na_primeira_onda() -> None:
    fecho = fecho_progressivo(_cadeia().etapas.values())
    assert fecho.onda["etapa:x/a"] == 1


def test_aresta_derivada_carrega_a_competencia_mediadora() -> None:
    """Aresta nua esconde a única informação acionável (docs/CONTEXT.md §3.2)."""
    arestas = arestas_derivadas(_cadeia().etapas.values())
    assert [(a.origem, a.destino, a.competencias) for a in arestas] == [
        ("etapa:x/a", "etapa:x/b", ("comp:x/um",)),
        ("etapa:x/b", "etapa:x/c", ("comp:x/dois",)),
    ]


def test_aresta_so_existe_se_o_nivel_ensinado_alcanca_o_exigido() -> None:
    cat = catalogo(
        competencia("comp:x/um"),
        etapa("etapa:x/pouco", teaches=[("comp:x/um", N.INICIANTE)]),
        etapa("etapa:x/muito", teaches=[("comp:x/um", N.AVANCADO)]),
        etapa("etapa:x/exige", requires=[("comp:x/um", N.AVANCADO)]),
    )
    origens = {a.origem for a in arestas_derivadas(cat.etapas.values())}
    assert origens == {"etapa:x/muito"}


def test_grafo_derivado_pode_ter_ciclo_sem_catalogo_invalido() -> None:
    """Duas etapas ordenadas, uma competência em dois níveis: arestas nos dois sentidos.

    É a armadilha que tirou `graphlib` do projeto (ADR-0006, Nota de correção). O
    fecho continua ordenando as duas corretamente.
    """
    cat = catalogo(
        competencia("comp:x/um"),
        etapa("etapa:x/basico", teaches=[("comp:x/um", N.INICIANTE)]),
        etapa(
            "etapa:x/avancado",
            requires=[("comp:x/um", N.INICIANTE)],
            teaches=[("comp:x/um", N.AVANCADO)],
        ),
        etapa(
            "etapa:x/reforco",
            requires=[("comp:x/um", N.AVANCADO)],
            teaches=[("comp:x/um", N.INICIANTE)],
        ),
    )
    pares = {(a.origem, a.destino) for a in arestas_derivadas(cat.etapas.values())}
    assert ("etapa:x/avancado", "etapa:x/reforco") in pares
    assert ("etapa:x/reforco", "etapa:x/avancado") in pares  # contramão: ciclo aparente

    fecho = fecho_progressivo(cat.etapas.values())
    assert fecho.onda == {
        "etapa:x/basico": 1,
        "etapa:x/avancado": 2,
        "etapa:x/reforco": 3,
    }


def test_etapa_depreciada_pode_ser_excluida_pelo_chamador() -> None:
    cat = catalogo(
        competencia("comp:x/um"),
        etapa("etapa:x/velha", status=Status.DEPRECIADO, teaches=[("comp:x/um", N.INICIANTE)]),
        etapa("etapa:x/nova", requires=[("comp:x/um", N.INICIANTE)]),
    )
    assert fecho_progressivo(cat.etapas_ativas()).liberadas == frozenset()
    assert fecho_progressivo(cat.etapas.values()).ondas == 2
