"""Agrupamento por `obra` — o exemplar, não a entidade (ADR-0009).

O que estes cenários fixam é a diferença entre as duas somas do projeto: a duração da
obra soma as fatias, e o custo **não** soma — conta uma vez.
"""

from __future__ import annotations

import fabrica
from trilhas.catalogo.modelo import Status
from trilhas.catalogo.obras import (
    custo_das_obras,
    nome_da_obra,
    obra,
    obras,
    obras_pedidas,
    recorte_da_fatia,
)

LIVRO = "livro-de-teste"


def _catalogo_com_duas_fatias() -> object:
    return fabrica.catalogo(
        fabrica.etapa("etapa:x/um"),
        fabrica.etapa("etapa:x/dois"),
        fabrica.recurso(
            "rec:x/livro-parte-2",
            "etapa:x/dois",
            titulo="Livro de Teste (Autor) — parte 2: o resto",
            custo=90,
            duracao_min=180,
            obra=LIVRO,
        ),
        fabrica.recurso(
            "rec:x/livro-parte-1",
            "etapa:x/um",
            titulo="Livro de Teste (Autor) — parte 1: o começo",
            custo=90,
            duracao_min=120,
            obra=LIVRO,
        ),
        fabrica.recurso("rec:x/avulso", "etapa:x/um", custo=50, duracao_min=60),
    )


def test_agrupa_as_fatias_do_exemplar() -> None:
    achada = obra(_catalogo_com_duas_fatias(), LIVRO)
    assert achada is not None
    assert [f.id for f in achada.fatias] == ["rec:x/livro-parte-1", "rec:x/livro-parte-2"]


def test_duracao_soma_as_fatias() -> None:
    """Fatias são partes complementares de um exemplar: ler as duas é ler o livro."""
    achada = obra(_catalogo_com_duas_fatias(), LIVRO)
    assert achada is not None
    assert achada.duracao_total_min == 300


def test_custo_conta_o_exemplar_uma_vez() -> None:
    """ADR-0009: qualquer agregação monetária conta cada obra uma vez, não 90 + 90."""
    achada = obra(_catalogo_com_duas_fatias(), LIVRO)
    assert achada is not None
    assert achada.custo == 90


def test_custo_ignora_fatia_depreciada() -> None:
    """Preço de material retirado não é fato do exemplar de hoje (catalogo.md §5.12)."""
    catalogo = fabrica.catalogo(
        fabrica.etapa("etapa:x/um"),
        fabrica.recurso(
            "rec:x/velha",
            "etapa:x/um",
            custo=999,
            status=Status.DEPRECIADO,
            obra=LIVRO,
            titulo="Livro — fatia velha",
        ),
        fabrica.recurso(
            "rec:x/nova", "etapa:x/um", custo=120, obra=LIVRO, titulo="Livro — fatia nova"
        ),
    )
    achada = obra(catalogo, LIVRO)
    assert achada is not None
    assert achada.custo == 120
    assert achada.fatias_vivas == 1
    assert not achada.toda_depreciada


def test_obra_toda_depreciada_segue_enderecavel() -> None:
    """Nada é removido do catálogo (catalogo.md §6); a obra some do motor, não da URL."""
    catalogo = fabrica.catalogo(
        fabrica.etapa("etapa:x/um"),
        fabrica.recurso("rec:x/so", "etapa:x/um", custo=40, status=Status.DEPRECIADO, obra=LIVRO),
    )
    achada = obra(catalogo, LIVRO)
    assert achada is not None
    assert achada.toda_depreciada
    assert achada.custo == 40


def test_etapas_atendidas_sem_repetir() -> None:
    catalogo = fabrica.catalogo(
        fabrica.etapa("etapa:x/um"),
        fabrica.recurso("rec:x/a", "etapa:x/um", obra=LIVRO, titulo="Livro — a"),
        fabrica.recurso("rec:x/b", "etapa:x/um", obra=LIVRO, titulo="Livro — b"),
    )
    achada = obra(catalogo, LIVRO)
    assert achada is not None
    assert achada.etapas == ("etapa:x/um",)


def test_recurso_sem_obra_nao_aparece() -> None:
    """Recurso sem `obra` é obra de si mesmo para custo, mas não tem slug para endereçar."""
    todas = obras(_catalogo_com_duas_fatias())
    assert [o.slug for o in todas] == [LIVRO]


def test_slug_desconhecido_nao_existe() -> None:
    assert obra(_catalogo_com_duas_fatias(), "nao-existe") is None


def test_nome_vem_da_menor_cabeca_de_titulo() -> None:
    """Uma fatia traz edição e autoria, outra só o título: o nome é o que todas contêm."""
    fatias = (
        fabrica.recurso(
            "rec:x/a", "etapa:x/um", titulo="Calculus (Morris Kline), 2ª ed. — derivada"
        ),
        fabrica.recurso("rec:x/b", "etapa:x/um", titulo="Calculus (Morris Kline) — integral"),
    )
    assert nome_da_obra(fatias) == "Calculus (Morris Kline)"


def test_nome_de_fatia_sem_recorte_e_o_titulo_inteiro() -> None:
    fatias = (fabrica.recurso("rec:x/a", "etapa:x/um", titulo="Livro Inteiro"),)
    assert nome_da_obra(fatias) == "Livro Inteiro"
    assert recorte_da_fatia(fatias[0]) == ""


def test_recorte_e_o_que_vem_depois_do_travessao() -> None:
    fatia = fabrica.recurso("rec:x/a", "etapa:x/um", titulo="Livro — caps. 1 a 3: começo")
    assert recorte_da_fatia(fatia) == "caps. 1 a 3: começo"


def test_obra_do_catalogo_real(catalogo_real: object) -> None:
    """A regra tem de valer no catálogo autorado, não só no de teste."""
    from pathlib import Path

    from trilhas.catalogo.carregar import carregar

    catalogo, problemas = carregar(Path(str(catalogo_real)))
    assert not [p for p in problemas if p.severidade == "erro"]
    todas = obras(catalogo)
    assert len(todas) >= 20
    for uma in todas:
        # O nome é sempre cabeça de título escrita por quem autorou, nunca string montada.
        cabecas = {f.titulo.split(" — ")[0].strip() for f in uma.fatias}
        assert uma.nome in cabecas
        assert uma.duracao_total_min >= max(f.duracao_min for f in uma.fatias)
        # Obra sem fatia viva nasceria retirada — ADR-0020 proíbe marcar recurso
        # depreciado, e sem esta linha a falha vem como StopIteration abaixo.
        assert uma.fatias_vivas, f"obra sem fatia viva: {uma.slug}"
        assert uma.custo == next(f.custo for f in uma.fatias if f.status is not Status.DEPRECIADO)


def test_custo_das_obras_conta_cada_exemplar_uma_vez() -> None:
    """A agregação que o ADR-0009 sempre previu: dois livros, não quatro fatias."""
    catalogo = fabrica.catalogo(
        fabrica.etapa("etapa:x/um"),
        fabrica.recurso("rec:x/a1", "etapa:x/um", custo=90, obra="livro-a", titulo="A — 1"),
        fabrica.recurso("rec:x/a2", "etapa:x/um", custo=90, obra="livro-a", titulo="A — 2"),
        fabrica.recurso("rec:x/b1", "etapa:x/um", custo=120, obra="livro-b", titulo="B — 1"),
        fabrica.recurso("rec:x/b2", "etapa:x/um", custo=120, obra="livro-b", titulo="B — 2"),
    )
    assert custo_das_obras(obras(catalogo)) == 210


def test_custo_das_obras_ignora_recurso_sem_obra() -> None:
    """A soma responde quanto custam os exemplares fatiados, não o catálogo inteiro."""
    catalogo = fabrica.catalogo(
        fabrica.etapa("etapa:x/um"),
        fabrica.recurso("rec:x/a1", "etapa:x/um", custo=90, obra="livro-a", titulo="A — 1"),
        fabrica.recurso("rec:x/avulso", "etapa:x/um", custo=500),
    )
    assert custo_das_obras(obras(catalogo)) == 90


def test_custo_das_obras_sem_obra_alguma_e_zero() -> None:
    catalogo = fabrica.catalogo(
        fabrica.etapa("etapa:x/um"), fabrica.recurso("rec:x/avulso", "etapa:x/um", custo=500)
    )
    assert custo_das_obras(obras(catalogo)) == 0


# --- obras pedidas por um recorte de etapas (a trilha) --------------------------


def _catalogo_de_duas_trilhas() -> object:
    """Um livro atravessa as duas trilhas; outro só serve à segunda."""
    return fabrica.catalogo(
        fabrica.etapa("etapa:x/um", trilha="trilha:x/a"),
        fabrica.etapa("etapa:x/dois", trilha="trilha:x/a"),
        fabrica.etapa("etapa:x/tres", trilha="trilha:x/b"),
        fabrica.recurso(
            "rec:x/atravessa-1",
            "etapa:x/um",
            custo=90,
            duracao_min=120,
            obra="atravessa",
            titulo="Atravessa (Autor) — parte 1",
        ),
        fabrica.recurso(
            "rec:x/atravessa-2",
            "etapa:x/dois",
            custo=90,
            duracao_min=60,
            obra="atravessa",
            titulo="Atravessa (Autor) — parte 2",
        ),
        fabrica.recurso(
            "rec:x/atravessa-3",
            "etapa:x/tres",
            custo=90,
            duracao_min=200,
            obra="atravessa",
            titulo="Atravessa (Autor) — parte 3",
        ),
        fabrica.recurso(
            "rec:x/so-la",
            "etapa:x/tres",
            custo=40,
            obra="so-la",
            titulo="Só lá (Autor)",
        ),
        fabrica.recurso("rec:x/avulso", "etapa:x/um", custo=500),
    )


def test_obra_que_atende_varias_etapas_do_recorte_aparece_uma_vez() -> None:
    """É o que transforma "os recursos da trilha" em "os livros da trilha"."""
    pedidas = obras_pedidas(_catalogo_de_duas_trilhas(), ["etapa:x/um", "etapa:x/dois"])
    assert [p.obra.slug for p in pedidas] == ["atravessa"]
    (uma,) = pedidas
    assert [f.id for f in uma.fatias] == ["rec:x/atravessa-1", "rec:x/atravessa-2"]
    assert uma.etapas == ("etapa:x/um", "etapa:x/dois")


def test_duracao_pedida_soma_so_as_fatias_do_recorte() -> None:
    """ "Quanto deste livro esta trilha me pede" — 120 + 60, não as três partes."""
    (uma,) = obras_pedidas(_catalogo_de_duas_trilhas(), ["etapa:x/um", "etapa:x/dois"])
    assert uma.duracao_min == 180
    assert uma.obra.duracao_total_min == 380  # o exemplar inteiro segue inteiro
    assert uma.parcial


def test_custo_pedido_e_o_do_exemplar_inteiro() -> None:
    """Compra-se o livro, não o capítulo: usar uma fatia de três custa o mesmo."""
    (uma,) = obras_pedidas(_catalogo_de_duas_trilhas(), ["etapa:x/um"])
    assert uma.fatias == tuple(f for f in uma.fatias if f.id == "rec:x/atravessa-1")
    assert uma.obra.custo == 90
    assert (
        custo_das_obras(
            [
                p.obra
                for p in obras_pedidas(_catalogo_de_duas_trilhas(), ["etapa:x/um", "etapa:x/tres"])
            ]
        )
        == 130
    )


def test_recorte_que_usa_o_exemplar_todo_nao_e_parcial() -> None:
    pedidas = obras_pedidas(
        _catalogo_de_duas_trilhas(), ["etapa:x/um", "etapa:x/dois", "etapa:x/tres"]
    )
    atravessa = next(p for p in pedidas if p.obra.slug == "atravessa")
    assert not atravessa.parcial
    assert atravessa.duracao_min == atravessa.obra.duracao_total_min


def test_recurso_sem_obra_nao_entra_no_pedido() -> None:
    """Sem slug não há como endereçá-lo, e inventar um criaria id que o catálogo não tem."""
    pedidas = obras_pedidas(_catalogo_de_duas_trilhas(), ["etapa:x/um"])
    assert [f.id for p in pedidas for f in p.fatias] == ["rec:x/atravessa-1"]


def test_recorte_sem_obra_alguma_vem_vazio() -> None:
    assert obras_pedidas(_catalogo_de_duas_trilhas(), ["etapa:x/nao-existe"]) == ()
