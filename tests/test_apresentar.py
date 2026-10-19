"""Projeções de tela — testadas sem servidor, que é o motivo de `apresentar/` ser puro."""

from __future__ import annotations

from datetime import date, datetime

import pytest

from fabrica import N, catalogo, competencia, etapa, minimo_valido, recurso, trilha
from trilhas.catalogo.grafo import arestas_derivadas, fecho_progressivo
from trilhas.catalogo.modelo import Catalogo, Formato, Nivel, Status
from trilhas.catalogo.snapshot import Cabecalho
from trilhas.motor import Matricula, Percurso, sugerir
from trilhas.web.apresentar import acervo as apresentar_acervo
from trilhas.web.apresentar import comum, detalhe
from trilhas.web.apresentar import sugestao as apresentar_sugestao
from trilhas.web.apresentar.disposicao import dispor
from trilhas.web.dados import Acervo

HOJE = date(2026, 10, 12)


def _acervo(cat: Catalogo) -> Acervo:
    ativas = cat.etapas_ativas()
    return Acervo(
        cabecalho=Cabecalho(1, 5, "2026-10-08T00:00:00+00:00", "sha256:abc123def456"),
        catalogo=cat,
        fecho=fecho_progressivo(ativas),
        arestas=arestas_derivadas(ativas),
    )


# --- rótulos -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("minutos", "esperado"),
    [(0, "—"), (45, "45 min"), (60, "1 h"), (90, "1 h 30 min"), (900, "15 h")],
)
def test_duracao_em_linguagem_de_gente(minutos: int, esperado: str) -> None:
    assert comum.duracao(minutos) == esperado


@pytest.mark.parametrize(
    ("custo", "esperado"), [(0, "grátis"), (90.0, "R$ 90"), (90.5, "R$ 90,50")]
)
def test_dinheiro(custo: float, esperado: str) -> None:
    assert comum.dinheiro(custo) == esperado


def test_nivel_e_mostrado_acentuado_mas_o_token_do_dominio_nao_muda() -> None:
    """A tela escreve pt-BR; o id continua ASCII (docs/catalogo.md §3)."""
    assert comum.nivel(Nivel.INTERMEDIARIO) == "intermediário"
    assert str(Nivel.INTERMEDIARIO) == "intermediario"


def test_vencido_usa_o_mesmo_limite_da_validacao() -> None:
    assert comum.vencido(date(2026, 1, 1), HOJE) is True
    assert comum.vencido(date(2026, 10, 1), HOJE) is False
    assert comum.vencido(None, HOJE) is True


def test_titulo_de_referencia_quebrada_cai_no_id() -> None:
    """Referência quebrada é erro de catálogo, não motivo para a tela cair."""
    assert comum.titulo_de(Catalogo(), "comp:x/fantasma") == "comp:x/fantasma"


# --- abertura e explorador -----------------------------------------------------


def test_inicio_conta_o_acervo() -> None:
    visao = apresentar_acervo.inicio(_acervo(minimo_valido()), hoje=HOJE)
    assert [(c.rotulo, c.quantidade) for c in visao.totais] == [
        ("trilhas", 1),
        ("etapas", 1),
        ("competências", 1),
        ("recursos", 1),
    ]
    assert visao.hash_curto == "abc123def456"
    assert visao.ondas == 1
    assert visao.sem_snapshot is False


def test_inicio_sem_catalogo_avisa_em_vez_de_mostrar_zeros() -> None:
    assert apresentar_acervo.inicio(Acervo.vazio(), hoje=HOJE).sem_snapshot is True


def test_busca_ignora_acento_e_caixa() -> None:
    cat = catalogo(
        competencia("comp:x/base"),
        etapa("etapa:x/inicial", teaches=[("comp:x/base", N.INICIANTE)]),
        recurso("rec:x/inicial", "etapa:x/inicial", titulo="Inferência estatística"),
    )
    achadas = apresentar_acervo.listar(_acervo(cat), apresentar_acervo.Filtro(q="INFERENCIA"))
    assert [linha.id for linha in achadas.linhas] == ["rec:x/inicial"]


def test_filtro_por_tipo_e_area() -> None:
    visao = apresentar_acervo.listar(
        _acervo(minimo_valido()), apresentar_acervo.Filtro(tipo="etapa", area="x")
    )
    assert len(visao.linhas) == 1
    assert visao.total == 4  # o filtro informa o universo, não só o recorte


# --- trilha --------------------------------------------------------------------


def test_trilha_desconhecida_devolve_none() -> None:
    assert detalhe.trilha(_acervo(minimo_valido()), "trilha:x/nao-existe") is None


def test_etapas_da_trilha_saem_ordenadas_por_onda() -> None:
    cat = catalogo(
        competencia("comp:x/um"),
        etapa("etapa:x/b", requires=[("comp:x/um", N.INICIANTE)], trilha="trilha:x/t"),
        etapa("etapa:x/a", teaches=[("comp:x/um", N.INICIANTE)], trilha="trilha:x/t"),
        recurso("rec:x/a", "etapa:x/a"),
        recurso("rec:x/b", "etapa:x/b"),
        trilha("trilha:x/t", etapas=["etapa:x/b", "etapa:x/a"]),
    )
    visao = detalhe.trilha(_acervo(cat), "trilha:x/t")
    assert visao is not None
    assert [e.id for e in visao.etapas] == ["etapa:x/a", "etapa:x/b"]
    assert [e.onda for e in visao.etapas] == [1, 2]
    assert visao.etapas[0].destrava == 1


def test_etapa_referenciada_aparece_como_emprestada() -> None:
    cat = catalogo(
        competencia("comp:x/um"),
        etapa("etapa:x/dona", teaches=[("comp:x/um", N.INICIANTE)], trilha="trilha:x/dona"),
        etapa("etapa:x/propria", requires=[("comp:x/um", N.INICIANTE)], trilha="trilha:x/t"),
        trilha("trilha:x/dona", etapas=["etapa:x/dona"]),
        trilha("trilha:x/t", etapas=["etapa:x/propria"], referenciadas=["etapa:x/dona"]),
    )
    visao = detalhe.trilha(_acervo(cat), "trilha:x/t")
    assert visao is not None
    emprestadas = {e.id: e.emprestada for e in visao.etapas}
    assert emprestadas == {"etapa:x/dona": True, "etapa:x/propria": False}
    assert [r.id for r in visao.emprestadas] == ["etapa:x/dona"]


# --- etapa ---------------------------------------------------------------------


def test_requisito_diz_quem_ensina_o_que_falta() -> None:
    """O travamento tem de ser explicado, não só sinalizado (docs/interface.md §5.3)."""
    cat = catalogo(
        competencia("comp:x/um", titulo="Competência um"),
        etapa("etapa:x/professora", teaches=[("comp:x/um", N.INTERMEDIARIO)]),
        etapa("etapa:x/travada", requires=[("comp:x/um", N.INTERMEDIARIO)]),
    )
    visao = detalhe.etapa(_acervo(cat), "etapa:x/travada", hoje=HOJE)
    assert visao is not None
    (exigencia,) = visao.requisitos
    assert exigencia.nivel_rotulo == "intermediário"
    assert [r.id for r in exigencia.ensinada_por] == ["etapa:x/professora"]


def test_etapa_sem_recurso_disponivel_alerta_com_o_codigo_da_validacao() -> None:
    cat = catalogo(
        competencia("comp:x/base"),
        etapa("etapa:x/so", teaches=[("comp:x/base", N.INICIANTE)]),
        recurso("rec:x/so", "etapa:x/so", disponivel=False),
    )
    visao = detalhe.etapa(_acervo(cat), "etapa:x/so", hoje=HOJE)
    assert visao is not None
    assert any("CAT-050" in alerta for alerta in visao.alertas)


def test_recurso_vencido_e_sinalizado_a_quem_estuda() -> None:
    cat = catalogo(
        competencia("comp:x/base"),
        etapa("etapa:x/so", teaches=[("comp:x/base", N.INICIANTE)]),
        recurso("rec:x/velho", "etapa:x/so", verificado_em=date(2025, 1, 1)),
    )
    visao = detalhe.etapa(_acervo(cat), "etapa:x/so", hoje=HOJE)
    assert visao is not None
    assert visao.recursos[0].vencido is True
    assert any("CAT-100" in alerta for alerta in visao.alertas)


def test_recursos_vem_ordenados_por_custo_e_duracao() -> None:
    cat = catalogo(
        competencia("comp:x/base"),
        etapa("etapa:x/so", teaches=[("comp:x/base", N.INICIANTE)]),
        recurso("rec:x/pago", "etapa:x/so", custo=90.0, titulo="pago"),
        recurso("rec:x/gratis", "etapa:x/so", custo=0.0, titulo="grátis"),
        recurso("rec:x/fora", "etapa:x/so", custo=0.0, disponivel=False, titulo="fora"),
    )
    visao = detalhe.etapa(_acervo(cat), "etapa:x/so", hoje=HOJE)
    assert visao is not None
    assert [r.id for r in visao.recursos] == ["rec:x/gratis", "rec:x/pago", "rec:x/fora"]


# --- competência ---------------------------------------------------------------


def test_competencia_mostra_o_nivel_que_o_catalogo_alcanca() -> None:
    cat = catalogo(
        competencia("comp:x/um"),
        etapa("etapa:x/a", teaches=[("comp:x/um", N.AVANCADO)]),
    )
    visao = detalhe.competencia(_acervo(cat), "comp:x/um")
    assert visao is not None
    assert visao.nivel_no_catalogo is Nivel.AVANCADO
    assert visao.nivel_no_catalogo_rotulo == "avançado"


def test_competencia_sem_professor_alerta() -> None:
    visao = detalhe.competencia(_acervo(catalogo(competencia("comp:x/orfa"))), "comp:x/orfa")
    assert visao is not None
    assert visao.alertas == ("nenhuma etapa desenvolve esta competência",)


# --- disposição ----------------------------------------------------------------


def test_disposicao_e_deterministica() -> None:
    """Teste de ouro exigido pela ADR-0007: mesmo catálogo, mesmas coordenadas."""
    acervo = _acervo(minimo_valido())
    etapas = list(acervo.catalogo.etapas.values())
    uma = dispor(etapas, acervo.fecho, acervo.arestas, catalogo=acervo.catalogo)
    outra = dispor(etapas, acervo.fecho, acervo.arestas, catalogo=acervo.catalogo)
    assert uma == outra
    assert uma.nos[0].x == 28
    assert uma.nos[0].y == 54
    assert uma.largura == 256
    assert not uma.vazia


def test_aresta_sem_avanco_de_onda_e_marcada_para_desenhar_por_cima() -> None:
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
    acervo = _acervo(cat)
    disposicao = dispor(list(cat.etapas.values()), acervo.fecho, acervo.arestas, catalogo=cat)
    retorno = [(a.origem, a.destino) for a in disposicao.arestas if a.retorno]
    assert ("etapa:x/reforco", "etapa:x/avancado") in retorno


def test_disposicao_de_catalogo_vazio_nao_quebra() -> None:
    acervo = Acervo.vazio()
    disposicao = dispor([], acervo.fecho, (), catalogo=acervo.catalogo)
    assert disposicao.vazia
    assert disposicao.largura > 0 and disposicao.altura > 0


def test_titulo_do_no_vem_quebrado_para_o_svg() -> None:
    linhas = comum.quebrar("Análise exploratória — interrogar um conjunto desconhecido")
    assert len(linhas) == 2
    assert linhas[-1].endswith("…")


def test_formato_tem_rotulo_para_todo_valor_do_dominio() -> None:
    assert {comum.formato(f) for f in Formato} == {"vídeo", "texto", "exercício", "projeto"}


def test_status_tem_rotulo_para_todo_valor_do_dominio() -> None:
    assert set(comum.ROTULO_STATUS) == set(Status)


# --- painel Agora --------------------------------------------------------------


def test_enfase_da_explicacao_vira_trecho_em_vez_de_html_cru() -> None:
    """O motor escreve `*assim*`; marcar HTML como seguro no template seria pior."""
    from trilhas.web.apresentar.sugestao import _trechos

    trechos = _trechos("Retome: *SQL básico* — você já começou.")
    assert [(t.texto, t.enfase) for t in trechos] == [
        ("Retome: ", False),
        ("SQL básico", True),
        (" — você já começou.", False),
    ]


def test_explicacao_sem_enfase_vira_um_trecho_so() -> None:
    from trilhas.web.apresentar.sugestao import _trechos

    assert [t.texto for t in _trechos("sem ênfase")] == ["sem ênfase"]


# --- estante no cartão (ADR-0015) ----------------------------------------------


def _cat_com_livro() -> Catalogo:
    return catalogo(
        competencia("comp:x/a"),
        etapa("etapa:x/a", teaches=[("comp:x/a", N.INICIANTE)], trilha="trilha:x/t"),
        recurso("rec:x/livro", "etapa:x/a", custo=350, duracao_min=30, obra="livro-x"),
        recurso("rec:x/site", "etapa:x/a", custo=0, duracao_min=120),
        trilha("trilha:x/t", etapas=["etapa:x/a"], objetivo=[("comp:x/a", N.INICIANTE)]),
    )


def _painel_do_livro(estante: frozenset[str]):  # type: ignore[no-untyped-def]
    cat = _cat_com_livro()
    percurso = Percurso(
        "est:x",
        matriculas=(Matricula("trilha:x/t", date(2026, 10, 1)),),
        estante=estante,
    )
    momento = datetime(2026, 10, 12, 9, 0)
    return apresentar_sugestao.painel(sugerir(cat, percurso, momento), cat, percurso)


def test_recurso_da_estante_mostra_o_preco_de_catalogo_e_que_ja_e_seu() -> None:
    """Zerar o custo na tela chamaria de "grátis" um livro de R$ 350 (ADR-0015)."""
    visao = _painel_do_livro(frozenset({"rec:x/livro"}))
    sugerido = visao.cartoes[0].recurso
    assert sugerido is not None
    assert sugerido.id == "rec:x/livro"
    assert sugerido.custo == "R$ 350"
    assert sugerido.na_estante


def test_recurso_fora_da_estante_nao_e_marcado() -> None:
    visao = _painel_do_livro(frozenset())
    sugerido = visao.cartoes[0].recurso
    assert sugerido is not None
    assert sugerido.id == "rec:x/site"
    assert not sugerido.na_estante
