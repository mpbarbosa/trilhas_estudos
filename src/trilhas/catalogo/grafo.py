"""O grafo de pré-requisitos: fecho progressivo e arestas derivadas.

Função pura, sem I/O. Mora no catálogo porque é propriedade do catálogo, não de quem
o consome: a validação §5.3/§5.6 usa o fecho, o motor usará as arestas (fator
`desbloqueio`) e a interface usa os dois para dispor o grafo.

Duas armadilhas estão resolvidas aqui, e não devem ser reabertas fora:

1. **Ordenação topológica não serve.** Uma competência ensinada em mais de um nível
   por etapas distintas gera arestas nos dois sentidos entre etapas perfeitamente
   ordenadas — ver a *Nota de correção* de docs/adr/0006-stack-python.md. O que
   ordena é o fecho progressivo a partir de perfil vazio.
2. **Pré-requisito nunca é etapa→etapa** (docs/CONTEXT.md §3.2). A aresta derivada
   existe por conveniência de quem desenha ou pontua, e por isso carrega sempre as
   competências que a produziram: sem elas, a aresta esconde a única informação
   acionável.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from .modelo import Etapa, Nivel


@dataclass(frozen=True, slots=True)
class Fecho:
    """Resultado do fecho progressivo a partir de um perfil (vazio, por padrão)."""

    perfil: Mapping[str, Nivel]
    onda: Mapping[str, int]
    """Onda em que cada etapa liberada destravou, começando em 1.

    É a profundidade de pré-requisito da etapa, e a única ordenação honesta do grafo.
    Etapa presa não aparece aqui.
    """

    @property
    def liberadas(self) -> frozenset[str]:
        return frozenset(self.onda)

    def nivel(self, competencia: str) -> Nivel:
        return self.perfil.get(competencia, Nivel.DESCONHECE)

    @property
    def ondas(self) -> int:
        return max(self.onda.values(), default=0)


@dataclass(frozen=True, slots=True)
class ArestaDerivada:
    """`origem` destrava `destino` por ensinar o que `destino` exige."""

    origem: str
    destino: str
    competencias: tuple[str, ...] = field(default=())


def fecho_progressivo(etapas: Iterable[Etapa], inicial: Mapping[str, Nivel] | None = None) -> Fecho:
    """Aplica, em rodadas, toda etapa cujos `requires` já estão satisfeitos.

    Cada rodada é uma onda: todas as etapas liberadas pelo perfil da rodada anterior
    entram juntas, e só depois o perfil avança. Sem isso a onda dependeria da ordem
    de iteração, e o layout da interface deixaria de ser determinístico.

    `inicial` é o perfil de partida: vazio na validação, que ordena o catálogo em si,
    e o perfil do estudante no motor de sugestão, que mede o que ele ainda alcança.
    """
    perfil: dict[str, Nivel] = dict(inicial or {})
    onda: dict[str, int] = {}
    pendentes = sorted(etapas, key=lambda e: e.id)
    rodada = 0

    while pendentes:
        rodada += 1
        liberadas = [e for e in pendentes if _satisfeita(e, perfil)]
        if not liberadas:
            break
        for etapa in liberadas:
            onda[etapa.id] = rodada
        for etapa in liberadas:
            for ens in etapa.teaches:
                if ens.nivel_resultante > perfil.get(ens.competencia, Nivel.DESCONHECE):
                    perfil[ens.competencia] = ens.nivel_resultante
        liberadas_ids = {e.id for e in liberadas}
        pendentes = [e for e in pendentes if e.id not in liberadas_ids]

    return Fecho(perfil=perfil, onda=onda)


def arestas_derivadas(etapas: Iterable[Etapa]) -> tuple[ArestaDerivada, ...]:
    """Arestas etapa→etapa implicadas por `teaches`/`requires`, com a mediadora.

    Uma aresta por par, agrupando as competências que a justificam. O resultado
    **não** é acíclico, e não deve ser tratado como se fosse (ver o cabeçalho).
    """
    lista = sorted(etapas, key=lambda e: e.id)
    ensina: dict[str, list[tuple[str, Nivel]]] = {}
    for etapa in lista:
        for ens in etapa.teaches:
            ensina.setdefault(ens.competencia, []).append((etapa.id, ens.nivel_resultante))

    pares: dict[tuple[str, str], list[str]] = {}
    for destino in lista:
        for req in destino.requires:
            for origem, nivel in ensina.get(req.competencia, ()):
                if origem == destino.id or nivel < req.nivel_minimo:
                    continue
                competencias = pares.setdefault((origem, destino.id), [])
                if req.competencia not in competencias:
                    competencias.append(req.competencia)

    return tuple(
        ArestaDerivada(origem, destino, tuple(sorted(competencias)))
        for (origem, destino), competencias in sorted(pares.items())
    )


def _satisfeita(etapa: Etapa, perfil: Mapping[str, Nivel]) -> bool:
    return all(
        perfil.get(r.competencia, Nivel.DESCONHECE) >= r.nivel_minimo for r in etapa.requires
    )
