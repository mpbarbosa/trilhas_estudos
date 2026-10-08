"""Uma asserção por validação de docs/catalogo.md §5."""

from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta

import pytest

from fabrica import N, catalogo, competencia, etapa, minimo_valido, recurso, trilha
from trilhas.catalogo.modelo import Status
from trilhas.catalogo.problemas import Codigo, Severidade
from trilhas.catalogo.snapshot import EstadoAnterior
from trilhas.catalogo.validar import validar

HOJE = date(2026, 10, 8)


def codigos(problemas: list) -> set[Codigo]:
    return {p.codigo for p in problemas}


def test_catalogo_minimo_nao_tem_problema() -> None:
    assert validar(minimo_valido(), hoje=HOJE) == []


# §5.1 ------------------------------------------------------------------------


@pytest.mark.parametrize(
    "ident",
    [
        "comp:SemMinuscula/x",
        "comp:sem-area",
        "comp:area/com_underscore",
        "comp:área/acento",
        "trilha:sem-area",
    ],
)
def test_id_fora_do_padrao(ident: str) -> None:
    cat = catalogo(competencia(ident)) if ident.startswith("comp") else catalogo(trilha(ident))
    assert Codigo.ID_INVALIDO in codigos(validar(cat, hoje=HOJE))


def test_prefixo_incompativel_com_a_colecao() -> None:
    cat = catalogo(competencia("etapa:x/y"))
    assert Codigo.ID_INVALIDO in codigos(validar(cat, hoje=HOJE))


def test_entidade_removida_em_relacao_ao_snapshot_anterior() -> None:
    anterior = EstadoAnterior(versao=3, ids=frozenset({"comp:x/sumida"}), revs={"comp:x/sumida": 1})
    problemas = validar(minimo_valido(), anterior, hoje=HOJE)
    assert Codigo.ID_INVALIDO in codigos(problemas)
    assert any("depreciadas, nunca removidas" in p.mensagem for p in problemas)


# §5.2 ------------------------------------------------------------------------


def test_requisito_para_competencia_inexistente() -> None:
    cat = catalogo(etapa("etapa:x/a", requires=[("comp:x/fantasma", N.INICIANTE)]))
    assert Codigo.REFERENCIA_QUEBRADA in codigos(validar(cat, hoje=HOJE))


def test_substituido_por_inexistente() -> None:
    cat = minimo_valido()
    cat.competencias["comp:x/base"] = replace(
        cat.competencias["comp:x/base"],
        status=Status.DEPRECIADO,
        depreciado_em=HOJE,
        substituido_por="comp:x/inexistente",
    )
    assert Codigo.REFERENCIA_QUEBRADA in codigos(validar(cat, hoje=HOJE))


# §5.3 ------------------------------------------------------------------------


def test_dependencia_circular_real_e_detectada() -> None:
    """A exige o que só B ensina e B exige o que só A ensina: nenhuma destrava."""
    cat = catalogo(
        competencia("comp:x/a"),
        competencia("comp:x/b"),
        etapa(
            "etapa:x/a",
            requires=[("comp:x/b", N.INICIANTE)],
            teaches=[("comp:x/a", N.INICIANTE)],
            trilha="trilha:x/t",
        ),
        etapa(
            "etapa:x/b",
            requires=[("comp:x/a", N.INICIANTE)],
            teaches=[("comp:x/b", N.INICIANTE)],
            trilha="trilha:x/t",
        ),
        recurso("rec:x/a", "etapa:x/a"),
        recurso("rec:x/b", "etapa:x/b"),
        trilha("trilha:x/t", etapas=["etapa:x/a", "etapa:x/b"]),
    )
    problemas = validar(cat, hoje=HOJE)
    assert Codigo.ETAPA_INALCANCAVEL in codigos(problemas)
    assert {p.entidade for p in problemas if p.codigo is Codigo.ETAPA_INALCANCAVEL} == {
        "etapa:x/a",
        "etapa:x/b",
    }


def test_competencia_ensinada_em_dois_niveis_nao_e_ciclo() -> None:
    """Regressão: escada de níveis não é dependência circular.

    `a` exige iniciante e entrega intermediario; `b` exige intermediario e entrega
    avancado. Ordenação topológica sobre "quem ensina o que o outro exige" acusaria
    ciclo — o fecho progressivo não.
    """
    cat = catalogo(
        competencia("comp:x/escada"),
        etapa("etapa:x/base", teaches=[("comp:x/escada", N.INICIANTE)], trilha="trilha:x/t"),
        etapa(
            "etapa:x/a",
            requires=[("comp:x/escada", N.INICIANTE)],
            teaches=[("comp:x/escada", N.INTERMEDIARIO)],
            trilha="trilha:x/t",
        ),
        etapa(
            "etapa:x/b",
            requires=[("comp:x/escada", N.INTERMEDIARIO)],
            teaches=[("comp:x/escada", N.AVANCADO)],
            trilha="trilha:x/t",
        ),
        recurso("rec:x/base", "etapa:x/base"),
        recurso("rec:x/a", "etapa:x/a"),
        recurso("rec:x/b", "etapa:x/b"),
        trilha(
            "trilha:x/t",
            etapas=["etapa:x/base", "etapa:x/a", "etapa:x/b"],
            objetivo=[("comp:x/escada", N.AVANCADO)],
        ),
    )
    assert validar(cat, hoje=HOJE) == []


# §5.4 ------------------------------------------------------------------------


def test_beco_sem_saida_quando_nenhuma_etapa_atinge_o_nivel() -> None:
    cat = catalogo(
        competencia("comp:x/base"),
        etapa("etapa:x/so-iniciante", teaches=[("comp:x/base", N.INICIANTE)], trilha="trilha:x/t"),
        etapa(
            "etapa:x/exige-avancado",
            requires=[("comp:x/base", N.AVANCADO)],
            trilha="trilha:x/t",
        ),
        recurso("rec:x/1", "etapa:x/so-iniciante"),
        recurso("rec:x/2", "etapa:x/exige-avancado"),
        trilha("trilha:x/t", etapas=["etapa:x/so-iniciante", "etapa:x/exige-avancado"]),
    )
    problemas = validar(cat, hoje=HOJE)
    assert Codigo.BECO_SEM_SAIDA in codigos(problemas)
    # §5.3 não duplica o que §5.4 já explicou com precisão
    assert Codigo.ETAPA_INALCANCAVEL not in codigos(problemas)


# §5.5 ------------------------------------------------------------------------


def test_etapa_ativa_sem_recurso_disponivel() -> None:
    cat = minimo_valido()
    cat.recursos["rec:x/inicial"] = replace(cat.recursos["rec:x/inicial"], disponivel=False)
    assert Codigo.SEM_RECURSO in codigos(validar(cat, hoje=HOJE))


# §5.6 ------------------------------------------------------------------------


def test_objetivo_inalcancavel_com_as_proprias_etapas() -> None:
    """A trilha declara objetivo que nenhuma de suas etapas desenvolve."""
    cat = minimo_valido()
    cat.etapas["etapa:x/inicial"] = replace(cat.etapas["etapa:x/inicial"], teaches=())
    assert Codigo.OBJETIVO_INALCANCAVEL in codigos(validar(cat, hoje=HOJE))


def test_trilha_de_continuacao_precisa_referenciar_os_pre_requisitos() -> None:
    """Consequência de §5.6: trilha não promete objetivo que suas etapas não entregam."""
    cat = catalogo(
        competencia("comp:x/base"),
        competencia("comp:x/avancada"),
        etapa("etapa:x/base", teaches=[("comp:x/base", N.INICIANTE)]),
        etapa(
            "etapa:x/seq",
            requires=[("comp:x/base", N.INICIANTE)],
            teaches=[("comp:x/avancada", N.INICIANTE)],
            trilha="trilha:x/continuacao",
        ),
        recurso("rec:x/base", "etapa:x/base"),
        recurso("rec:x/seq", "etapa:x/seq"),
        trilha(
            "trilha:x/continuacao",
            etapas=["etapa:x/seq"],
            objetivo=[("comp:x/avancada", N.INICIANTE)],
        ),
    )
    assert Codigo.OBJETIVO_INALCANCAVEL in codigos(validar(cat, hoje=HOJE))

    # com a etapa de pré-requisito referenciada, passa
    cat.trilhas["trilha:x/continuacao"] = replace(
        cat.trilhas["trilha:x/continuacao"], etapas_referenciadas=("etapa:x/base",)
    )
    assert Codigo.OBJETIVO_INALCANCAVEL not in codigos(validar(cat, hoje=HOJE))


# §5.7 ------------------------------------------------------------------------


def test_etapa_nao_pode_ensinar_abaixo_do_que_exige() -> None:
    cat = catalogo(
        competencia("comp:x/base"),
        etapa(
            "etapa:x/rebaixa",
            requires=[("comp:x/base", N.INTERMEDIARIO)],
            teaches=[("comp:x/base", N.INICIANTE)],
        ),
    )
    assert Codigo.NIVEL_REBAIXA in codigos(validar(cat, hoje=HOJE))


# §5.8 ------------------------------------------------------------------------


def test_depreciada_sem_data() -> None:
    cat = minimo_valido()
    cat.competencias["comp:x/base"] = replace(
        cat.competencias["comp:x/base"], status=Status.DEPRECIADO
    )
    assert Codigo.DEPRECIACAO_INCOERENTE in codigos(validar(cat, hoje=HOJE))


def test_etapa_ativa_aponta_para_competencia_depreciada_sem_substituto() -> None:
    cat = catalogo(
        competencia("comp:x/velha", status=Status.DEPRECIADO, depreciado_em=HOJE),
        competencia("comp:x/base"),
        etapa(
            "etapa:x/a",
            requires=[("comp:x/velha", N.INICIANTE)],
            teaches=[("comp:x/base", N.INICIANTE)],
        ),
    )
    assert Codigo.DEPRECIACAO_INCOERENTE in codigos(validar(cat, hoje=HOJE))


def test_objetivo_citando_competencia_depreciada() -> None:
    cat = minimo_valido()
    cat.competencias["comp:x/base"] = replace(
        cat.competencias["comp:x/base"],
        status=Status.DEPRECIADO,
        depreciado_em=HOJE,
        substituido_por="comp:x/base",
    )
    problemas = validar(cat, hoje=HOJE)
    assert Codigo.DEPRECIACAO_INCOERENTE in codigos(problemas)
    assert any("objetivo_declarado cita competência depreciada" in p.mensagem for p in problemas)


# §5.9 ------------------------------------------------------------------------


def test_rev_nao_pode_decrescer() -> None:
    anterior = EstadoAnterior(
        versao=2,
        ids=frozenset(minimo_valido().ids()),
        revs={"comp:x/base": 5},
    )
    problemas = validar(minimo_valido(), anterior, hoje=HOJE)
    assert Codigo.REV_DECRESCEU in codigos(problemas)


# §5.10 e §5.11 ---------------------------------------------------------------


def test_recurso_nao_verificado_e_aviso_nao_erro() -> None:
    cat = minimo_valido()
    cat.recursos["rec:x/inicial"] = replace(
        cat.recursos["rec:x/inicial"], verificado_em=HOJE - timedelta(days=200)
    )
    problemas = validar(cat, hoje=HOJE)
    assert Codigo.RECURSO_NAO_VERIFICADO in codigos(problemas)
    assert all(p.severidade is Severidade.AVISO for p in problemas)


def test_recurso_verificado_no_limite_nao_avisa() -> None:
    cat = minimo_valido()
    cat.recursos["rec:x/inicial"] = replace(
        cat.recursos["rec:x/inicial"], verificado_em=HOJE - timedelta(days=179)
    )
    assert validar(cat, hoje=HOJE) == []


def test_etapa_orfa_e_aviso() -> None:
    cat = minimo_valido()
    cat.etapas["etapa:x/solta"] = etapa(
        "etapa:x/solta", teaches=[("comp:x/base", N.INICIANTE)]
    )
    cat.recursos["rec:x/solta"] = recurso("rec:x/solta", "etapa:x/solta")
    problemas = validar(cat, hoje=HOJE)
    assert Codigo.ETAPA_ORFA in codigos(problemas)
    assert all(p.severidade is Severidade.AVISO for p in problemas)
