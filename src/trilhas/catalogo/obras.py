"""Obras: as fatias de um exemplar, reunidas (ADR-0009).

`obra` agrupa as fatias de um mesmo exemplar e **não** é entidade de catálogo — não
nomeia entidade, não tem `rev`, `status` nem depreciação (docs/catalogo.md §2). O que
ela fixa é como somar: qualquer agregação monetária conta cada obra **uma vez**, pelo
`custo` de uma de suas fatias. Este módulo é o primeiro consumidor dessa regra — até
ele, o campo era inerte, como a própria §2 registrava.

Núcleo puro: nada de I/O aqui, e a interface só formata o que sai daqui
(docs/interface.md §3.3).

Duas somas convivem no projeto e não se confundem:

- **duração da obra** soma as fatias, porque fatias são partes complementares de um
  mesmo exemplar — ler as oito do Date é ler o livro uma vez;
- **esforço da etapa** é a leitura mais longa que a cobre, porque os recursos de uma
  etapa são rotas alternativas. Somar lá contaria o mesmo conteúdo quatro vezes.

Recurso sem `obra` é obra de si mesmo para efeito de custo (§2), mas não aparece aqui:
não há slug para endereçá-lo, e inventar um criaria identificador que o catálogo não
tem.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .modelo import Catalogo, Recurso, Status

SEPARADOR_DE_RECORTE = " — "
"""O que divide o nome do livro do recorte, na convenção de título do catálogo."""


@dataclass(frozen=True, slots=True)
class Obra:
    """Um exemplar e as fatias que o catálogo recortou dele."""

    slug: str
    nome: str
    fatias: tuple[Recurso, ...]
    """Ordenadas por id — ordem estável, porque `obra` não declara sequência de leitura."""

    @property
    def duracao_total_min(self) -> int:
        """Soma das fatias: são partes de um exemplar, não rotas alternativas."""
        return sum(f.duracao_min for f in self.fatias)

    @property
    def custo(self) -> float:
        """O preço do exemplar, contado uma vez (ADR-0009).

        Vem de uma fatia **não depreciada**: a validação 12 garante que essas
        concordam, e fatia depreciada pode carregar preço de material retirado, que
        não é fato do exemplar de hoje (docs/catalogo.md §5.12).
        """
        viva = next((f for f in self.fatias if f.status is not Status.DEPRECIADO), None)
        return (viva or self.fatias[0]).custo

    @property
    def etapas(self) -> tuple[str, ...]:
        """Etapas que a obra atende, sem repetir. Uma fatia serve uma etapa (§2)."""
        vistas: dict[str, None] = {}
        for fatia in self.fatias:
            vistas.setdefault(fatia.etapa, None)
        return tuple(vistas)

    @property
    def idiomas(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(f.idioma for f in self.fatias))

    @property
    def formatos(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(f.formato.value for f in self.fatias))

    @property
    def fatias_vivas(self) -> int:
        return sum(1 for f in self.fatias if f.status is not Status.DEPRECIADO)

    @property
    def toda_depreciada(self) -> bool:
        """Exemplar que saiu de circulação no catálogo — segue endereçável, não removido (§6)."""
        return self.fatias_vivas == 0


def nome_da_obra(fatias: tuple[Recurso, ...]) -> str:
    """O nome do livro, deduzido dos títulos das fatias.

    A convenção de título do catálogo é `<livro> — <recorte>`, e o pedaço antes do
    travessão é o nome. Quando as fatias discordam dele — uma traz a edição e a
    autoria, outra só o título —, vale o **menor**: é o que todas as versões têm em
    comum, e é título real escrito por quem autorou, não string montada aqui. Empate
    de tamanho se resolve em ordem alfabética, para a saída não depender da ordem de
    iteração.

    Sem fatia alguma não há nome — quem chama garante que a obra existe.
    """
    cabecas = {f.titulo.split(SEPARADOR_DE_RECORTE)[0].strip() for f in fatias}
    return min(cabecas, key=lambda c: (len(c), c))


def recorte_da_fatia(fatia: Recurso) -> str:
    """O que esta fatia recorta do exemplar: o título depois do travessão.

    Vazio quando a fatia é o exemplar inteiro, e aí a tela mostra o título cru.
    """
    partes = fatia.titulo.split(SEPARADOR_DE_RECORTE, 1)
    return partes[1].strip() if len(partes) == 2 else ""


def obras(catalogo: Catalogo) -> tuple[Obra, ...]:
    """Toda obra declarada no catálogo, em ordem de slug."""
    por_slug: dict[str, list[Recurso]] = {}
    for recurso in catalogo.recursos.values():
        if recurso.obra:
            por_slug.setdefault(recurso.obra, []).append(recurso)
    return tuple(_montar(slug, por_slug[slug]) for slug in sorted(por_slug))


def custo_das_obras(reunidas: Iterable[Obra]) -> float:
    """Soma o preço de cada exemplar **uma vez** (ADR-0009).

    É a agregação monetária que o catálogo sempre previu e nunca tinha: somar `custo`
    recurso a recurso cobraria o Date oito vezes, uma por fatia. Fica aqui, e não na
    tela, porque somar dinheiro é regra de domínio (docs/interface.md §3.3).

    Recurso sem `obra` não entra: ele é obra de si mesmo (docs/catalogo.md §2), mas
    não é fatia de exemplar algum, e esta soma responde "quanto custam os exemplares
    fatiados", não "quanto custa o catálogo".
    """
    return sum(uma.custo for uma in reunidas)


def obra(catalogo: Catalogo, slug: str) -> Obra | None:
    """A obra de `slug`, ou `None` — slug desconhecido é 404, não erro."""
    fatias = [r for r in catalogo.recursos.values() if r.obra == slug]
    return _montar(slug, fatias) if fatias else None


def _montar(slug: str, fatias: list[Recurso]) -> Obra:
    ordenadas = tuple(sorted(fatias, key=lambda r: r.id))
    return Obra(slug=slug, nome=nome_da_obra(ordenadas), fatias=ordenadas)
