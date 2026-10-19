"""Os 7 cenários de docs/motor-de-sugestao.md §5, mais os casos de borda de §4.

Os cenários rodam sobre o catálogo-fixture (`tests/fixtures/catalogo_exemplo/`):

    fundamentos:  modelagem-basica ─┐
                  sql-select ───────┼─> sql-join
                  logica-booleana ──┘
                  sql-select ─> sql-group-by
    analise:      sql-join ─> etl-basico
                  sql-group-by ─> graficos ─> dashboards
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from fabrica import N, catalogo, competencia, etapa, recurso, trilha
from trilhas.catalogo.carregar import carregar
from trilhas.catalogo.modelo import Alvo, Catalogo, Formato
from trilhas.catalogo.problemas import Codigo
from trilhas.catalogo.validar import validar
from trilhas.motor import (
    CompetenciaDominada,
    EstadoEtapa,
    Feedback,
    Matricula,
    Motivo,
    MotivoVazio,
    Objetivo,
    Opcoes,
    Percurso,
    ProgressoEtapa,
    Reacao,
    Restricoes,
    Resultado,
    Tipo,
    sugerir,
)

AGORA = datetime(2026, 10, 12, 9, 0)
HOJE = AGORA.date()

FUNDAMENTOS = "trilha:dados/fundamentos"
ANALISE = "trilha:dados/analise"
SELECT = "etapa:dados/sql-select"
MODELAGEM = "etapa:dados/modelagem-basica"
JOIN = "etapa:dados/sql-join"
GROUP_BY = "etapa:dados/sql-group-by"
LOGICA = "etapa:programacao/logica-booleana"
CONSULTAS = "comp:dados/sql-consultas"
AGREGACAO = "comp:dados/sql-agregacao"
VISUALIZACAO = "comp:dados/visualizacao"


@pytest.fixture
def cat(fixture_catalogo: Path) -> Catalogo:
    carregado, problemas = carregar(fixture_catalogo)
    assert not problemas
    return carregado


def dias_atras(n: int) -> date:
    return HOJE - timedelta(days=n)


def dominada(comp: str, nivel: N, *, ha_dias: int = 10) -> CompetenciaDominada:
    return CompetenciaDominada(comp, nivel, dias_atras(ha_dias))


def objetivo(*alvos: tuple[str, N], ha_dias: int = 60) -> Objetivo:
    return Objetivo(tuple(Alvo(c, n) for c, n in alvos), dias_atras(ha_dias))


def matricula(trilha_id: str) -> Matricula:
    return Matricula(trilha_id, dias_atras(60))


def ids(resultado: Resultado) -> list[str]:
    return [s.etapa_id for s in resultado.sugestoes]


def motivo_de(resultado: Resultado, etapa_id: str) -> Motivo:
    return next(e.motivo for e in resultado.eliminadas if e.etapa_id == etapa_id)


# --- §5, cenário 1 -------------------------------------------------------------


def test_perfil_vazio_com_objetivo_sugere_primeira_etapa_do_caminho(cat: Catalogo) -> None:
    percurso = Percurso("est:x", objetivo=objetivo((VISUALIZACAO, N.INTERMEDIARIO)))
    resultado = sugerir(cat, percurso, AGORA)

    assert ids(resultado)[0] == SELECT
    assert resultado.sugestoes[0].tipo is Tipo.EXPLORACAO
    # Só etapas sem pré-requisito são sugeríveis com perfil vazio.
    assert all(not cat.etapas[e].requires for e in ids(resultado))
    assert motivo_de(resultado, "etapa:analise/graficos") is Motivo.REQUISITO_NAO_SATISFEITO


# --- §5, cenário 2 -------------------------------------------------------------


def test_competencia_de_fora_pula_etapas_iniciais(cat: Catalogo) -> None:
    percurso = Percurso(
        "est:x",
        competencias=(dominada(CONSULTAS, N.INTERMEDIARIO),),
        matriculas=(matricula(FUNDAMENTOS),),
    )
    resultado = sugerir(cat, percurso, AGORA)

    assert GROUP_BY in ids(resultado)
    assert SELECT not in ids(resultado)
    assert motivo_de(resultado, SELECT) is Motivo.JA_DOMINADA


# --- §5, cenário 3 -------------------------------------------------------------


def _percurso_com_select_concluida(ha_dias: int) -> Percurso:
    return Percurso(
        "est:x",
        competencias=(dominada(CONSULTAS, N.INICIANTE, ha_dias=ha_dias),),
        matriculas=(matricula(FUNDAMENTOS),),
        progresso=(ProgressoEtapa(SELECT, EstadoEtapa.CONCLUIDA, dias_atras(ha_dias)),),
    )


def test_evidencia_antiga_poe_revisao_no_top3(cat: Catalogo) -> None:
    resultado = sugerir(cat, _percurso_com_select_concluida(ha_dias=200), AGORA)

    revisao = next(s for s in resultado.sugestoes if s.etapa_id == SELECT)
    assert revisao.tipo is Tipo.REVISAO
    assert "200 dias" in revisao.explicacao


def test_evidencia_recente_nao_gera_revisao(cat: Catalogo) -> None:
    resultado = sugerir(cat, _percurso_com_select_concluida(ha_dias=20), AGORA)

    assert SELECT not in ids(resultado)
    assert all(s.tipo is not Tipo.REVISAO for s in resultado.sugestoes)
    assert motivo_de(resultado, SELECT) is Motivo.CONCLUIDA


# --- §5, cenário 4 -------------------------------------------------------------


def test_tempo_curto_filtra_etapa_longa_em_vez_de_despontuar(cat: Catalogo) -> None:
    percurso = Percurso("est:x", matriculas=(matricula(FUNDAMENTOS),))

    resultado = sugerir(cat, percurso, AGORA, Opcoes(tempo_disponivel_min=30))
    assert ids(resultado) == [SELECT]
    # O recurso sugerido é o que cabe: os exercícios de 25 min, não o vídeo de 45.
    assert resultado.sugestoes[0].recurso_sugerido_id == "rec:dados/sql-select-exercicios"
    assert motivo_de(resultado, MODELAGEM) is Motivo.NAO_CABE_NO_TEMPO
    assert motivo_de(resultado, LOGICA) is Motivo.NAO_CABE_NO_TEMPO


def test_tempo_de_15_min_nao_cabe_nada_e_diz_por_que(cat: Catalogo) -> None:
    percurso = Percurso("est:x", matriculas=(matricula(FUNDAMENTOS),))
    resultado = sugerir(cat, percurso, AGORA, Opcoes(tempo_disponivel_min=15))

    assert resultado.sugestoes == ()
    assert resultado.motivo_vazio is MotivoVazio.RESTRICOES_BLOQUEIAM
    assert resultado.detalhe == "tempo"


# --- §5, cenário 5 -------------------------------------------------------------


def _rejeitou_select(ha_dias: int, objetivo_ha_dias: int | None = None) -> Percurso:
    return Percurso(
        "est:x",
        objetivo=(
            objetivo((CONSULTAS, N.INICIANTE), ha_dias=objetivo_ha_dias)
            if objetivo_ha_dias is not None
            else None
        ),
        matriculas=(matricula(FUNDAMENTOS),),
        feedback=(Feedback(SELECT, Reacao.REJEITADA, dias_atras(ha_dias)),),
    )


def test_rejeicao_tira_a_etapa_por_30_dias(cat: Catalogo) -> None:
    resultado = sugerir(cat, _rejeitou_select(ha_dias=10), AGORA)
    assert SELECT not in ids(resultado)
    assert motivo_de(resultado, SELECT) is Motivo.REJEITADA_RECENTEMENTE

    depois = sugerir(cat, _rejeitou_select(ha_dias=31), AGORA)
    assert SELECT in ids(depois)


def test_mudanca_de_objetivo_devolve_etapa_rejeitada(cat: Catalogo) -> None:
    resultado = sugerir(cat, _rejeitou_select(ha_dias=10, objetivo_ha_dias=2), AGORA)
    assert SELECT in ids(resultado)


# --- §5, cenário 6 -------------------------------------------------------------


def test_mesma_entrada_mesma_saida(cat: Catalogo) -> None:
    percurso = Percurso(
        "est:x",
        competencias=(dominada(CONSULTAS, N.INICIANTE, ha_dias=200),),
        matriculas=(matricula(FUNDAMENTOS), matricula(ANALISE)),
    )
    # Ordem de inserção dos índices invertida: a saída não pode depender dela.
    invertido = Catalogo(
        competencias=dict(reversed(cat.competencias.items())),
        etapas=dict(reversed(cat.etapas.items())),
        recursos=dict(reversed(cat.recursos.items())),
        trilhas=dict(reversed(cat.trilhas.items())),
    )
    primeira = sugerir(cat, percurso, AGORA)
    assert primeira.sugestoes
    assert sugerir(cat, percurso, AGORA) == primeira
    assert sugerir(invertido, percurso, AGORA) == primeira


# --- §5, cenário 7 -------------------------------------------------------------


def _catalogo_com_ciclo() -> Catalogo:
    return catalogo(
        competencia("comp:x/a"),
        competencia("comp:x/b"),
        etapa(
            "etapa:x/a", requires=[("comp:x/b", N.INICIANTE)], teaches=[("comp:x/a", N.INICIANTE)]
        ),
        etapa(
            "etapa:x/b", requires=[("comp:x/a", N.INICIANTE)], teaches=[("comp:x/b", N.INICIANTE)]
        ),
        recurso("rec:x/a", "etapa:x/a"),
        recurso("rec:x/b", "etapa:x/b"),
        trilha(
            "trilha:x/t", etapas=["etapa:x/a", "etapa:x/b"], objetivo=[("comp:x/a", N.INICIANTE)]
        ),
    )


def test_ciclo_no_catalogo_e_erro_de_validacao() -> None:
    problemas = validar(_catalogo_com_ciclo(), hoje=HOJE)
    assert Codigo.ETAPA_INALCANCAVEL in {p.codigo for p in problemas}


def test_ciclo_no_catalogo_nao_trava_o_motor() -> None:
    percurso = Percurso("est:x", objetivo=objetivo(("comp:x/a", N.INICIANTE)))
    resultado = sugerir(_catalogo_com_ciclo(), percurso, AGORA)
    assert resultado.motivo_vazio is MotivoVazio.SEM_CAMINHO_NO_CATALOGO


# --- §4 Casos de borda ---------------------------------------------------------


def test_estudante_sem_objetivo_nem_trilha_nao_recebe_sugestao(cat: Catalogo) -> None:
    resultado = sugerir(cat, Percurso("est:x"), AGORA)
    assert resultado.sugestoes == ()
    assert resultado.motivo_vazio is MotivoVazio.PERFIL_INSUFICIENTE


def test_objetivo_sem_caminho_lista_lacunas(cat: Catalogo) -> None:
    percurso = Percurso("est:x", objetivo=objetivo((VISUALIZACAO, N.AVANCADO)))
    resultado = sugerir(cat, percurso, AGORA)
    assert resultado.motivo_vazio is MotivoVazio.SEM_CAMINHO_NO_CATALOGO
    assert resultado.lacunas == (Alvo(VISUALIZACAO, N.AVANCADO),)


def test_restricao_de_idioma_bloqueia_e_e_nomeada(cat: Catalogo) -> None:
    percurso = Percurso(
        "est:x",
        restricoes=Restricoes(idiomas=frozenset({"en-US"})),
        matriculas=(matricula(FUNDAMENTOS),),
    )
    resultado = sugerir(cat, percurso, AGORA)
    assert resultado.motivo_vazio is MotivoVazio.RESTRICOES_BLOQUEIAM
    assert resultado.detalhe == "idioma"


def test_restricao_de_formato_escolhe_recurso_aceito(cat: Catalogo) -> None:
    percurso = Percurso(
        "est:x",
        restricoes=Restricoes(formatos_aceitos=frozenset({Formato.VIDEO})),
        matriculas=(matricula(FUNDAMENTOS),),
    )
    resultado = sugerir(cat, percurso, AGORA)
    assert ids(resultado) == [SELECT]
    assert resultado.sugestoes[0].recurso_sugerido_id == "rec:dados/sql-select-video"


def _duas_fatias_do_mesmo_livro(obra: str | None = "livro-x") -> Catalogo:
    """Duas etapas, cada uma com uma fatia de 90 do mesmo exemplar (ADR-0009)."""
    return catalogo(
        competencia("comp:x/a"),
        competencia("comp:x/b"),
        etapa("etapa:x/a", teaches=[("comp:x/a", N.INICIANTE)], trilha="trilha:x/t"),
        etapa("etapa:x/b", teaches=[("comp:x/b", N.INICIANTE)], trilha="trilha:x/t"),
        recurso("rec:x/a", "etapa:x/a", custo=90, obra=obra),
        recurso("rec:x/b", "etapa:x/b", custo=90, obra=obra),
        trilha(
            "trilha:x/t",
            etapas=["etapa:x/a", "etapa:x/b"],
            objetivo=[("comp:x/a", N.INICIANTE)],
        ),
    )


def _com_teto(teto: float | None, cat: Catalogo | None = None) -> Resultado:
    percurso = Percurso(
        "est:x",
        matriculas=(matricula("trilha:x/t"),),
        restricoes=Restricoes(custo_maximo=teto),
    )
    return sugerir(cat or _duas_fatias_do_mesmo_livro(), percurso, AGORA)


def test_teto_abaixo_do_custo_do_recurso_elimina_a_etapa_por_custo() -> None:
    resultado = _com_teto(89)
    assert ids(resultado) == []
    assert motivo_de(resultado, "etapa:x/a") is Motivo.SEM_RECURSO_VIAVEL
    assert all(e.detalhe == "custo" for e in resultado.eliminadas)
    assert resultado.motivo_vazio is MotivoVazio.RESTRICOES_BLOQUEIAM
    assert resultado.detalhe == "custo"


def test_teto_igual_ao_custo_do_recurso_nao_elimina() -> None:
    """O corte é `custo > custo_maximo`: no limite o recurso ainda passa."""
    resultado = _com_teto(90)
    assert ids(resultado) == ["etapa:x/a", "etapa:x/b"]
    assert resultado.eliminadas == ()


def test_filtro_de_custo_e_por_recurso_nao_por_caminho() -> None:
    """Teto de 90 passa, embora o caminho reúna duas fatias de 90 (soma 180).

    `obra` não muda isso: o filtro compara uma fatia por vez, e nenhuma soma de
    `custo` existe no motor (ADR-0009).
    """
    sem_obra = _duas_fatias_do_mesmo_livro(obra=None)
    assert ids(_com_teto(90, sem_obra)) == ids(_com_teto(90)) == ["etapa:x/a", "etapa:x/b"]
    assert ids(_com_teto(179)) == ["etapa:x/a", "etapa:x/b"]


# --- §5, cenário 8: estante (ADR-0013) ----------------------------------------


def _livro_contra_gratuito() -> Catalogo:
    """Uma etapa com duas opções: a fatia paga de 30 min e o site grátis de 120 min.

    Sem `minutos_por_semana` nem `tempo_disponivel_min`, `_encaixe` devolve 0,5 para
    os dois (§3.4): o empate é universal e o custo é o primeiro critério efetivo.
    """
    return catalogo(
        competencia("comp:x/a"),
        etapa("etapa:x/a", teaches=[("comp:x/a", N.INICIANTE)], trilha="trilha:x/t"),
        recurso("rec:x/livro", "etapa:x/a", custo=30, duracao_min=30, obra="livro-x"),
        recurso("rec:x/site", "etapa:x/a", custo=0, duracao_min=120),
        trilha("trilha:x/t", etapas=["etapa:x/a"], objetivo=[("comp:x/a", N.INICIANTE)]),
    )


def _com_estante(
    estante: frozenset[str], teto: float | None = None, cat: Catalogo | None = None
) -> Resultado:
    percurso = Percurso(
        "est:x",
        matriculas=(matricula("trilha:x/t"),),
        restricoes=Restricoes(custo_maximo=teto),
        estante=estante,
    )
    return sugerir(cat or _livro_contra_gratuito(), percurso, AGORA)


def test_sem_estante_o_gratuito_mais_longo_vence_o_livro() -> None:
    """A linha de base do cenário 8: é o custo que escolhe, não a duração."""
    resultado = _com_estante(frozenset())
    assert resultado.sugestoes[0].recurso_sugerido_id == "rec:x/site"


def test_recurso_na_estante_vence_alternativa_gratuita_mais_longa() -> None:
    resultado = _com_estante(frozenset({"rec:x/livro"}))
    assert resultado.sugestoes[0].recurso_sugerido_id == "rec:x/livro"


def test_recurso_na_estante_perde_para_gratuito_mais_curto() -> None:
    """Posse empata o custo em zero; o desempate seguinte é `duracao_min`."""
    cat = catalogo(
        competencia("comp:x/a"),
        etapa("etapa:x/a", teaches=[("comp:x/a", N.INICIANTE)], trilha="trilha:x/t"),
        recurso("rec:x/livro", "etapa:x/a", custo=30, duracao_min=120, obra="livro-x"),
        recurso("rec:x/site", "etapa:x/a", custo=0, duracao_min=30),
        trilha("trilha:x/t", etapas=["etapa:x/a"], objetivo=[("comp:x/a", N.INICIANTE)]),
    )
    resultado = _com_estante(frozenset({"rec:x/livro"}), cat=cat)
    assert resultado.sugestoes[0].recurso_sugerido_id == "rec:x/site"


def test_recurso_na_estante_passa_teto_abaixo_do_custo_de_catalogo() -> None:
    """Com teto 0 a fatia de 30 é eliminada; declarada na estante, ela passa.

    É o caso que ADR-0009 recusou enquanto o zero era incondicional, e que a posse
    torna verdadeiro: ler o exemplar não gasta orçamento nenhum.
    """
    so_o_livro = catalogo(
        competencia("comp:x/a"),
        etapa("etapa:x/a", teaches=[("comp:x/a", N.INICIANTE)], trilha="trilha:x/t"),
        recurso("rec:x/livro", "etapa:x/a", custo=30, obra="livro-x"),
        trilha("trilha:x/t", etapas=["etapa:x/a"], objetivo=[("comp:x/a", N.INICIANTE)]),
    )
    sem = _com_estante(frozenset(), teto=0, cat=so_o_livro)
    assert ids(sem) == []
    assert motivo_de(sem, "etapa:x/a") is Motivo.SEM_RECURSO_VIAVEL
    assert sem.detalhe == "custo"

    com = _com_estante(frozenset({"rec:x/livro"}), teto=0, cat=so_o_livro)
    assert ids(com) == ["etapa:x/a"]
    assert com.sugestoes[0].recurso_sugerido_id == "rec:x/livro"


def test_posse_de_uma_fatia_se_propaga_as_irmas_pela_obra() -> None:
    """Declarar `rec:x/a` basta: `rec:x/b` é do mesmo exemplar (ADR-0009)."""
    cat = _duas_fatias_do_mesmo_livro()
    percurso = Percurso(
        "est:x",
        matriculas=(matricula("trilha:x/t"),),
        restricoes=Restricoes(custo_maximo=0),
        estante=frozenset({"rec:x/a"}),
    )
    assert ids(sugerir(cat, percurso, AGORA)) == ["etapa:x/a", "etapa:x/b"]


def test_sem_obra_a_posse_nao_se_propaga() -> None:
    """Fatias sem `obra` são exemplares distintos: cada uma se declara sozinha."""
    cat = _duas_fatias_do_mesmo_livro(obra=None)
    percurso = Percurso(
        "est:x",
        matriculas=(matricula("trilha:x/t"),),
        restricoes=Restricoes(custo_maximo=0),
        estante=frozenset({"rec:x/a"}),
    )
    assert ids(sugerir(cat, percurso, AGORA)) == ["etapa:x/a"]


def test_id_fora_do_catalogo_na_estante_nao_quebra_nem_propaga() -> None:
    percurso = Percurso(
        "est:x",
        matriculas=(matricula("trilha:x/t"),),
        estante=frozenset({"rec:x/nao-existe"}),
    )
    resultado = sugerir(_livro_contra_gratuito(), percurso, AGORA)
    assert resultado.sugestoes[0].recurso_sugerido_id == "rec:x/site"


def test_estante_nao_muda_a_explicacao_nem_os_fatores() -> None:
    """A escolha do recurso não pontua etapa: §2.5 segue intacta (ADR-0013)."""
    sem = _com_estante(frozenset()).sugestoes[0]
    com = _com_estante(frozenset({"rec:x/livro"})).sugestoes[0]
    assert com.recurso_sugerido_id != sem.recurso_sugerido_id
    assert [f.nome for f in com.fatores] == [f.nome for f in sem.fatores]
    assert "estante" not in com.explicacao and "já seu" not in com.explicacao


def test_estante_nao_muda_o_custo_do_catalogo() -> None:
    cat = _livro_contra_gratuito()
    _com_estante(frozenset({"rec:x/livro"}), cat=cat)
    assert cat.recursos["rec:x/livro"].custo == 30


def test_etapa_em_andamento_entra_como_retomada(cat: Catalogo) -> None:
    percurso = Percurso(
        "est:x",
        matriculas=(matricula(FUNDAMENTOS),),
        progresso=(ProgressoEtapa(MODELAGEM, EstadoEtapa.EM_ANDAMENTO, dias_atras(1)),),
    )
    retomada = next(s for s in sugerir(cat, percurso, AGORA).sugestoes if s.etapa_id == MODELAGEM)
    assert retomada.tipo is Tipo.RETOMADA
    assert "já começou" in retomada.explicacao


def test_no_maximo_duas_sugestoes_por_trilha(cat: Catalogo) -> None:
    percurso = Percurso("est:x", matriculas=(matricula(FUNDAMENTOS),))
    resultado = sugerir(cat, percurso, AGORA, Opcoes(quantidade=5))
    # Há três etapas sugeríveis em `fundamentos`; só duas entram.
    assert len(resultado.sugestoes) == 2


def test_rejeicoes_repetidas_rebaixam_a_trilha(cat: Catalogo) -> None:
    base = Percurso("est:x", matriculas=(matricula(FUNDAMENTOS),))
    rejeitou = Percurso(
        "est:x",
        matriculas=base.matriculas,
        feedback=tuple(
            Feedback(e, Reacao.REJEITADA, dias_atras(40 - i))  # fora dos 30 dias de bloqueio
            for i, e in enumerate([JOIN, GROUP_BY, "etapa:analise/graficos"])
        ),
    )
    antes = {s.etapa_id: s for s in sugerir(cat, base, AGORA).sugestoes}
    depois = {s.etapa_id: s for s in sugerir(cat, rejeitou, AGORA).sugestoes}
    # As rejeições têm mais de 14 dias: nada muda.
    assert antes.keys() == depois.keys()

    recente = Percurso(
        "est:x",
        matriculas=base.matriculas,
        feedback=tuple(
            Feedback(e, Reacao.REJEITADA, dias_atras(5)) for e in [JOIN, GROUP_BY, MODELAGEM]
        ),
    )
    momentum = {
        s.etapa_id: next(f.valor for f in s.fatores if f.nome == "momentum")
        for s in sugerir(cat, recente, AGORA).sugestoes
    }
    assert momentum == {SELECT: 0.15, LOGICA: 0.15}


def test_score_e_soma_das_contribuicoes(cat: Catalogo) -> None:
    percurso = Percurso("est:x", objetivo=objetivo((AGREGACAO, N.INICIANTE)))
    for s in sugerir(cat, percurso, AGORA).sugestoes:
        assert s.score == pytest.approx(sum(f.contribuicao for f in s.fatores))
        assert sum(f.peso for f in s.fatores) == pytest.approx(1.0)
        assert 0 <= s.score <= 1


def test_catalogo_real_produz_sugestoes(catalogo_real: Path) -> None:
    cat, problemas = carregar(catalogo_real)
    assert not problemas
    percurso = Percurso("est:x", matriculas=tuple(matricula(t) for t in sorted(cat.trilhas)))
    resultado = sugerir(cat, percurso, AGORA)
    assert len(resultado.sugestoes) == 3
    assert all(s.explicacao for s in resultado.sugestoes)
