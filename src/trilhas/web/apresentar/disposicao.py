"""Layout do grafo: coordenadas a partir das ondas do fecho progressivo.

Função pura e determinística — mesmo catálogo, mesmas coordenadas (teste de ouro em
tests/test_disposicao.py). O servidor desenha o SVG com isso, e as mesmas coordenadas
servem a um renderizador de terceiros se a interação crescer (ADR-0007).

Por que onda e não ordenação topológica: docs/interface.md §4 e a *Nota de correção*
de ADR-0006. Neste catálogo o grafo derivado tem 95 arestas e 13 arestas de retorno —
layout hierárquico desenharia um emaranhado falso. A onda é a profundidade de
pré-requisito, e é a única ordenação honesta.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

from ...catalogo.grafo import ArestaDerivada, Fecho
from ...catalogo.modelo import Catalogo, Etapa, Status
from ...motor.modelo import EstadoEtapa
from . import comum

LARGURA_NO = 200
ALTURA_NO = 58
FOLGA_X = 88
FOLGA_Y = 22
MARGEM = 28
ALTURA_FAIXA = 26
"""Faixa de cabeçalho onde vai o rótulo da onda."""


@dataclass(frozen=True, slots=True)
class No:
    etapa_id: str
    titulo: str
    linhas: tuple[str, ...]
    onda: int
    coluna: int
    x: int
    y: int
    opcional: bool
    status: Status
    emprestada: bool
    entrada: bool
    """Sem `requires`: ponto de entrada do grafo."""
    esforco_min: int
    esforco: str
    destrava: int
    estado: EstadoEtapa = EstadoEtapa.NAO_INICIADA
    """Progresso do estudante nesta etapa. `NAO_INICIADA` também é o que se vê sem
    percurso nenhum — o grafo do catálogo não deixa de ser desenhável por isso."""

    @property
    def largura(self) -> int:
        return LARGURA_NO

    @property
    def altura(self) -> int:
        return ALTURA_NO


@dataclass(frozen=True, slots=True)
class Aresta:
    origem: str
    destino: str
    competencias: tuple[str, ...]
    rotulo: str
    """As competências que justificam a aresta — a informação que uma aresta nua esconde."""
    caminho: str
    retorno: bool


@dataclass(frozen=True, slots=True)
class Faixa:
    onda: int
    coluna: int
    x: int
    rotulo: str
    quantidade: int


@dataclass(frozen=True, slots=True)
class Disposicao:
    nos: tuple[No, ...]
    arestas: tuple[Aresta, ...]
    faixas: tuple[Faixa, ...]
    largura: int
    altura: int

    @property
    def vazia(self) -> bool:
        return not self.nos

    def no(self, etapa_id: str) -> No | None:
        return next((n for n in self.nos if n.etapa_id == etapa_id), None)


def dispor(
    etapas: Sequence[Etapa],
    fecho: Fecho,
    arestas: Iterable[ArestaDerivada],
    *,
    catalogo: Catalogo,
    proprias: Iterable[str] = (),
    estados: Mapping[str, EstadoEtapa] | None = None,
) -> Disposicao:
    """Dispõe as `etapas` em colunas de onda, com as arestas entre elas.

    `fecho` e `arestas` são do catálogo **inteiro**: uma etapa emprestada de outra
    trilha conserva a profundidade real de pré-requisito, em vez de parecer inicial
    só porque esta trilha a introduz tarde.
    """
    por_etapa = estados or {}
    do_escopo = {e.id for e in etapas}
    proprias_ids = set(proprias) or do_escopo
    arestas_do_escopo = [a for a in arestas if a.origem in do_escopo and a.destino in do_escopo]
    destrava = _contar_destravadas(arestas_do_escopo)

    ondas = sorted({fecho.onda.get(e.id, 0) for e in etapas})
    coluna_da_onda = {onda: i for i, onda in enumerate(ondas)}

    por_coluna: dict[int, list[Etapa]] = {}
    for etapa in etapas:
        coluna = coluna_da_onda[fecho.onda.get(etapa.id, 0)]
        por_coluna.setdefault(coluna, []).append(etapa)

    nos: list[No] = []
    for coluna, etapas_da_coluna in sorted(por_coluna.items()):
        ordenadas = sorted(
            etapas_da_coluna,
            key=lambda e: (e.id not in proprias_ids, e.titulo, e.id),
        )
        for linha, etapa in enumerate(ordenadas):
            nos.append(
                No(
                    etapa_id=etapa.id,
                    titulo=etapa.titulo,
                    linhas=comum.quebrar(etapa.titulo),
                    onda=fecho.onda.get(etapa.id, 0),
                    coluna=coluna,
                    x=MARGEM + coluna * (LARGURA_NO + FOLGA_X),
                    y=MARGEM + ALTURA_FAIXA + linha * (ALTURA_NO + FOLGA_Y),
                    opcional=etapa.opcional,
                    status=etapa.status,
                    emprestada=etapa.id not in proprias_ids,
                    entrada=not etapa.requires,
                    esforco_min=etapa.esforco_estimado_min,
                    esforco=comum.duracao(etapa.esforco_estimado_min),
                    destrava=destrava.get(etapa.id, 0),
                    estado=por_etapa.get(etapa.id, EstadoEtapa.NAO_INICIADA),
                )
            )

    indice = {n.etapa_id: n for n in nos}
    desenhadas = tuple(
        _aresta(indice[a.origem], indice[a.destino], a, catalogo)
        for a in arestas_do_escopo
        if a.origem in indice and a.destino in indice
    )

    faixas = tuple(
        Faixa(
            onda=onda,
            coluna=coluna_da_onda[onda],
            x=MARGEM + coluna_da_onda[onda] * (LARGURA_NO + FOLGA_X),
            rotulo=f"onda {onda}",
            quantidade=len(por_coluna.get(coluna_da_onda[onda], [])),
        )
        for onda in ondas
    )

    linhas_max = max((len(v) for v in por_coluna.values()), default=0)
    return Disposicao(
        nos=tuple(nos),
        arestas=desenhadas,
        faixas=faixas,
        largura=2 * MARGEM + max(1, len(ondas)) * LARGURA_NO + max(0, len(ondas) - 1) * FOLGA_X,
        altura=2 * MARGEM
        + ALTURA_FAIXA
        + max(1, linhas_max) * ALTURA_NO
        + max(0, linhas_max - 1) * FOLGA_Y,
    )


def _contar_destravadas(arestas: Iterable[ArestaDerivada]) -> dict[str, int]:
    contagem: dict[str, int] = {}
    for aresta in arestas:
        contagem[aresta.origem] = contagem.get(aresta.origem, 0) + 1
    return contagem


def _aresta(origem: No, destino: No, bruta: ArestaDerivada, catalogo: Catalogo) -> Aresta:
    titulos = tuple(comum.titulo_de(catalogo, c) for c in bruta.competencias)
    return Aresta(
        origem=origem.etapa_id,
        destino=destino.etapa_id,
        competencias=bruta.competencias,
        rotulo=", ".join(titulos),
        caminho=_caminho(origem, destino),
        retorno=destino.coluna <= origem.coluna,
    )


def _caminho(origem: No, destino: No) -> str:
    """Bézier da direita da origem à esquerda do destino.

    Aresta de retorno (destino em coluna anterior ou igual) sai por cima e volta por
    cima: cruzar o corpo dos nós na horizontal a tornaria ilegível, e ela precisa
    parecer diferente — é contramão, não erro (docs/interface.md §4).
    """
    if destino.coluna > origem.coluna:
        x1 = origem.x + LARGURA_NO
        y1 = origem.y + ALTURA_NO // 2
        x2 = destino.x
        y2 = destino.y + ALTURA_NO // 2
        dx = max(32, (x2 - x1) // 2)
        return f"M {x1} {y1} C {x1 + dx} {y1}, {x2 - dx} {y2}, {x2} {y2}"

    x1 = origem.x + LARGURA_NO // 2
    y1 = origem.y
    x2 = destino.x + LARGURA_NO // 2
    y2 = destino.y
    alto = min(y1, y2) - 36 - 8 * abs(origem.coluna - destino.coluna)
    return f"M {x1} {y1} C {x1} {alto}, {x2} {alto}, {x2} {y2}"
