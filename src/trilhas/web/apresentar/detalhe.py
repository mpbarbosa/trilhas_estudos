"""Visões de uma entidade: trilha, etapa e competência.

O que estas três telas têm de fazer bem é explicar **dependência**: por que uma etapa
vem depois, quem ensina o que ela exige, e o que ela destrava. O resto é cadastro.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from types import MappingProxyType

from ...catalogo import obras as dominio_obras
from ...catalogo.modelo import Catalogo, Competencia, Etapa, Nivel, Recurso, Status, Trilha
from ...motor.modelo import EstadoEtapa, Percurso, ProgressoEtapa
from ...motor.sugerir import possuidos_em
from ...percurso.projecao import Evidencia, Percorrido
from ...percurso.registrar import CONFIANCA_AUTOAVALIACAO, NIVEIS_DECLARAVEIS
from ..dados import Acervo
from ..escrever import Acao
from . import comum
from .comum import ROTULO_ORIGEM
from .disposicao import Disposicao, dispor


@dataclass(frozen=True, slots=True)
class Referencia:
    """Link para outra entidade, já com o rótulo pronto."""

    id: str
    titulo: str
    href: str
    nota: str = ""


@dataclass(frozen=True, slots=True)
class Exigencia:
    competencia_id: str
    titulo: str
    nivel: Nivel
    nivel_rotulo: str
    ensinada_por: tuple[Referencia, ...]
    """Etapas ativas que levam a competência ao nível exigido — como destravar."""


@dataclass(frozen=True, slots=True)
class Desenvolvimento:
    competencia_id: str
    titulo: str
    nivel: Nivel
    nivel_rotulo: str
    exigida_por: int


@dataclass(frozen=True, slots=True)
class LinhaRecurso:
    id: str
    titulo: str
    formato: str
    idioma: str
    custo: str
    custo_valor: float
    duracao: str
    duracao_min: int
    url: str
    status: Status
    disponivel: bool
    verificado_em: date | None
    dias_sem_verificar: int | None
    vencido: bool
    obra: str = ""
    """Slug do exemplar, quando o recurso é fatia de um (ADR-0009). Vazio quando não é."""
    em_uso: bool = False
    """Recurso declarado ao iniciar esta etapa — por onde o estudante de fato estudou."""
    percorrido_em: date | None = None
    """Data da última passagem pelo material, quando houve uma (ADR-0012).

    É fato **do recurso**, não da etapa: percorrer não conclui etapa nem emite
    evidência, e por isso não se confunde com `em_uso` nem com o estado da etapa. Sem
    passagem registrada, `None` — ausência de fato, não fato negativo."""


@dataclass(frozen=True, slots=True)
class GrupoDeRecursos:
    """Os recursos de uma etapa, no bloco que reúne os da trilha inteira.

    A seção da trilha vem agrupada **por etapa**, e não como lista plana, porque os
    recursos de uma etapa são rotas alternativas entre si enquanto os de etapas
    diferentes são complementares (`catalogo/obras.py`). Uma lista plana de 78 linhas
    — o que a trilha do emulador tem hoje — se leria como bibliografia a percorrer
    inteira, que é o oposto do que o modelo diz.

    Agrupar é trabalho de tela, mas é aqui e não no template: Jinja agrupando viraria
    a segunda implementação que a §3.3 proíbe, e a etapa sem recurso desapareceria do
    laço — justamente a que a página precisa denunciar (CAT-050).
    """

    etapa: Referencia
    onda: int
    opcional: bool
    emprestada: bool
    recursos: tuple[LinhaRecurso, ...]
    """Vazio quando a etapa não tem recurso algum — grupo que a tela mostra como falta."""


@dataclass(frozen=True, slots=True)
class LinhaLivro:
    """Um exemplar que a trilha pede — o que se tem em mãos, não o que se abre no link.

    Existe porque o livro é a unidade de **aquisição** e o recurso é a de estudo: um
    livro que atende cinco etapas aparece cinco vezes na lista de recursos e uma vez
    aqui, com o preço cobrado uma vez (ADR-0009). Quem monta a estante pergunta pelo
    exemplar; quem senta para estudar pergunta pelo recurso.
    """

    slug: str
    nome: str
    href: str
    custo: str
    custo_valor: float
    duracao: str
    """Soma das fatias **que esta trilha pede** — não do exemplar inteiro."""
    duracao_min: int
    qtd_fatias: int
    qtd_fatias_do_exemplar: int
    parcial: bool
    """A trilha usa parte do livro; o resto dele serve a outras etapas."""
    etapas: tuple[Referencia, ...]
    idiomas: str
    toda_depreciada: bool
    ja_tenho: bool = False
    """O exemplar está na estante do percurso (ADR-0015). Basta uma fatia declarada: a
    posse se propaga às irmãs pela mesma `possuidos_em` que o motor usa, porque duas
    implementações da propagação discordariam em silêncio."""


@dataclass(frozen=True, slots=True)
class LinhaEtapaDaTrilha:
    id: str
    titulo: str
    href: str
    onda: int
    opcional: bool
    emprestada: bool
    status: Status
    esforco: str
    esforco_min: int
    destrava: int
    qtd_recursos: int
    requisitos: int
    estado: EstadoEtapa = EstadoEtapa.NAO_INICIADA
    estado_rotulo: str = ""
    atualizado_em: date | None = None


@dataclass(frozen=True, slots=True)
class VisaoTrilha:
    trilha: Trilha
    area: str
    objetivo: tuple[Exigencia, ...]
    etapas: tuple[LinhaEtapaDaTrilha, ...]
    disposicao: Disposicao
    recursos_por_etapa: tuple[GrupoDeRecursos, ...]
    """Todo material que realiza alguma etapa da trilha, na ordem das ondas."""
    qtd_recursos: int
    livros: tuple[LinhaLivro, ...]
    """Os exemplares que a trilha pede, cada um uma vez. Vazio quando nenhum recurso
    dela declara `obra` — e aí a tela diz isso, em vez de afirmar que não há livro."""
    custo_dos_livros: str
    custo_dos_livros_valor: float
    custo_que_falta: str
    """O que falta comprar, descontada a estante. Só se mostra havendo percurso: sem
    estudante, "falta tudo" seria afirmação sobre quem não existe."""
    custo_que_falta_valor: float
    qtd_livros_que_tenho: int
    recursos_sem_exemplar: int
    """Recursos da trilha que não declaram `obra`. A seção de livros não os conhece, e
    calar esse número faria a estante parecer completa (docs/catalogo.md §2)."""
    esforco: str
    qtd_obrigatorias: int
    qtd_opcionais: int
    emprestadas: tuple[Referencia, ...]
    tem_percurso: bool = False
    """Houve percurso para consultar. Distingue "nenhuma etapa concluída" de "não se
    sabe": sem isso a tela afirmaria progresso zero a quem nunca declarou estudante."""
    qtd_concluidas: int = 0
    qtd_em_andamento: int = 0


@dataclass(frozen=True, slots=True)
class AcaoDeEtapa:
    """Um botão de registro de progresso, já decidido pela projeção.

    Quais ações a tela oferece sai **daqui**, não do template: é função do estado
    projetado do log, e decidi-la em Jinja seria a segunda implementação que a §3.3
    proíbe. `Acao` vem de `web/escrever.py` porque lá mora a única definição desse
    vocabulário — importar o enum não é fazer I/O, e duplicá-lo é que seria o risco.
    """

    acao: Acao
    rotulo: str
    pede_recurso: bool = False
    pede_motivo: bool = False


# O último fato sobre a etapa vence (projecao.progresso_de), então reiniciar uma etapa
# concluída ou abandonada é fato legítimo — e é a única saída de quem clicou errado,
# enquanto não houver fato de retratação (ADR-0008, Consequências).
ACOES_POR_ESTADO: Mapping[EstadoEtapa, tuple[AcaoDeEtapa, ...]] = {
    EstadoEtapa.NAO_INICIADA: (AcaoDeEtapa(Acao.INICIAR, "Iniciar", pede_recurso=True),),
    EstadoEtapa.EM_ANDAMENTO: (
        AcaoDeEtapa(Acao.CONCLUIR, "Concluir"),
        AcaoDeEtapa(Acao.ABANDONAR, "Abandonar", pede_motivo=True),
    ),
    EstadoEtapa.ABANDONADA: (AcaoDeEtapa(Acao.INICIAR, "Retomar", pede_recurso=True),),
    EstadoEtapa.CONCLUIDA: (AcaoDeEtapa(Acao.INICIAR, "Estudar de novo", pede_recurso=True),),
}


@dataclass(frozen=True, slots=True)
class VisaoEtapa:
    etapa: Etapa
    area: str
    trilha: Referencia | None
    onda: int
    esforco: str
    requisitos: tuple[Exigencia, ...]
    desenvolve: tuple[Desenvolvimento, ...]
    recursos: tuple[LinhaRecurso, ...]
    destravada_por: tuple[Referencia, ...]
    destrava: tuple[Referencia, ...]
    tambem_em: tuple[Referencia, ...]
    """Trilhas que referenciam esta etapa sem a definir (catalogo.md §1)."""
    alertas: tuple[str, ...]
    tem_percurso: bool = False
    estado: EstadoEtapa = EstadoEtapa.NAO_INICIADA
    estado_rotulo: str = ""
    atualizado_em: date | None = None
    acoes: tuple[AcaoDeEtapa, ...] = ()
    """Vazio sem percurso carregado: um fato precisa de estudante a quem atribuí-lo,
    e oferecer o botão faria o clique criar o estudante (docs/interface.md §5.10)."""


NIVEIS_PARA_DECLARAR: tuple[tuple[str, str], ...] = tuple(
    (str(n), comum.nivel(n)) for n in NIVEIS_DECLARAVEIS
)
"""Cada nível declarável como `(valor do formulário, rótulo)`.

O valor é o que `Nivel.de_texto` lê de volta no POST; o rótulo é o que a pessoa vê, e
difere dele onde há acento (`intermediario` / `intermediário`). Quais níveis entram é
decisão do domínio — aqui só se escreve como eles aparecem."""


@dataclass(frozen=True, slots=True)
class LinhaEvidencia:
    """Uma evidência na linha do tempo, com o `seq` à vista (docs/interface.md §5.11).

    O `seq` é dado de tela, não detalhe de armazenamento: é o alvo de `retratar`, e sem
    ele na página a retratação não tem como ser pedida de lugar nenhum
    ([ADR-0014](../../../../docs/adr/0014-retratacao-de-evidencia-por-seq.md)).
    """

    seq: int
    nivel: Nivel
    nivel_rotulo: str
    origem_rotulo: str
    confianca: float
    em: date
    etapa: Referencia | None
    """A etapa cuja conclusão a emitiu. `None` em autoavaliação — que é exatamente por
    que a tela da etapa não serviria de casa para a retratação."""
    etapa_rev: int | None
    retratada: bool
    retratada_em: date | None
    motivo_da_retratacao: str


@dataclass(frozen=True, slots=True)
class VisaoCompetencia:
    competencia: Competencia
    area: str
    nivel_no_catalogo: Nivel
    nivel_no_catalogo_rotulo: str
    ensinada_por: tuple[tuple[Referencia, str], ...]
    exigida_por: tuple[tuple[Referencia, str], ...]
    objetivo_de: tuple[Referencia, ...]
    alertas: tuple[str, ...]
    tem_percurso: bool = False
    """Houve percurso para consultar — distingue "nenhuma evidência" de "não se sabe"."""
    nivel_no_percurso: Nivel | None = None
    """O nível vigente, da projeção que o motor consome. `None` sem percurso ou sem
    evidência que sustente a competência (CONTEXT §4)."""
    nivel_no_percurso_rotulo: str = ""
    ultima_evidencia_em: date | None = None
    evidencias: tuple[LinhaEvidencia, ...] = ()
    """Todas as evidências, retratadas incluídas: é o histórico, não o nível vigente."""
    pode_retratar: bool = False
    """Só com percurso carregado: retratar é escrita, e um fato precisa de estudante a
    quem atribuí-lo (docs/interface.md §5.10.6)."""
    niveis_declaraveis: tuple[tuple[str, str], ...] = ()
    """`(valor, rótulo)` de cada nível que a autoavaliação pode declarar (§5.12).

    Sai de `registrar.NIVEIS_DECLARAVEIS`, a mesma lista de onde a CLI tira o `choices`
    de `sei` — `desconhece` fica de fora nas duas. Montá-la aqui a partir de `Nivel`
    seria a segunda implementação que a §3.3 proíbe, e a tela passaria a oferecer o que
    a CLI recusa."""
    confianca_da_autoavaliacao: float = CONFIANCA_AUTOAVALIACAO
    """Com que peso o que se declara entra no log. Vem da constante do domínio e não de
    um número escrito no template: a tela diz o preço antes do clique, e um literal em
    Jinja passaria a mentir no dia em que a constante mudasse."""


def trilha(
    acervo: Acervo,
    trilha_id: str,
    *,
    hoje: date,
    percurso: Percurso | None = None,
    percorridos: tuple[Percorrido, ...] = (),
) -> VisaoTrilha | None:
    """A trilha: objetivo, grafo, etapas por onda e os recursos de todas elas.

    `hoje` entra porque a lista de recursos carrega `verificado_em` e o aviso CAT-100,
    que são relativos a uma data — a mesma razão pela qual `etapa()` já o pedia.
    """
    cat = acervo.catalogo
    alvo = cat.trilhas.get(trilha_id)
    if alvo is None:
        return None

    progresso = _progresso_por_etapa(percurso)
    etapas = [cat.etapas[e] for e in alvo.todas_as_etapas if e in cat.etapas]
    proprias = set(alvo.etapas)
    disposicao = dispor(
        etapas,
        acervo.fecho,
        acervo.arestas,
        catalogo=cat,
        proprias=proprias,
        estados={ident: p.estado for ident, p in progresso.items()},
    )
    destrava = {n.etapa_id: n.destrava for n in disposicao.nos}

    ordenadas = sorted(etapas, key=lambda e: (acervo.fecho.onda.get(e.id, 0), e.titulo))
    passagens = _percorridos_por_recurso(percorridos)
    por_etapa = {
        e.id: _recursos_da_etapa(cat, e.id, hoje=hoje, progresso=progresso, percorridos=passagens)
        for e in ordenadas
    }

    pedidas = dominio_obras.obras_pedidas(cat, (e.id for e in ordenadas))
    possuidos = possuidos_em(cat, percurso.estante if percurso else frozenset())
    tenho = {
        pedida.obra.slug
        for pedida in pedidas
        if any(fatia.id in possuidos for fatia in pedida.obra.fatias)
    }
    livros = tuple(
        sorted(
            (_livro(pedida, cat, ja_tenho=pedida.obra.slug in tenho) for pedida in pedidas),
            key=lambda linha: linha.nome.casefold(),
        )
    )
    custo = dominio_obras.custo_das_obras(pedida.obra for pedida in pedidas)
    falta = dominio_obras.custo_das_obras(
        pedida.obra for pedida in pedidas if pedida.obra.slug not in tenho
    )

    linhas = tuple(
        LinhaEtapaDaTrilha(
            id=e.id,
            titulo=e.titulo,
            href=f"/etapa/{e.id}",
            onda=acervo.fecho.onda.get(e.id, 0),
            opcional=e.opcional,
            emprestada=e.id not in proprias,
            status=e.status,
            esforco=comum.duracao(e.esforco_estimado_min),
            esforco_min=e.esforco_estimado_min,
            destrava=destrava.get(e.id, 0),
            qtd_recursos=len(por_etapa[e.id]),
            requisitos=len(e.requires),
            estado=_estado(progresso, e.id),
            estado_rotulo=comum.estado_de_etapa(_estado(progresso, e.id)),
            atualizado_em=progresso[e.id].atualizado_em if e.id in progresso else None,
        )
        for e in ordenadas
    )

    return VisaoTrilha(
        trilha=alvo,
        area=comum.area_do_id(alvo.id),
        objetivo=tuple(_exigencia(acervo, a.competencia, a.nivel) for a in alvo.objetivo_declarado),
        etapas=linhas,
        disposicao=disposicao,
        livros=livros,
        custo_dos_livros=comum.dinheiro(custo),
        custo_dos_livros_valor=custo,
        custo_que_falta=comum.dinheiro(falta),
        custo_que_falta_valor=falta,
        qtd_livros_que_tenho=len(tenho),
        recursos_sem_exemplar=sum(
            1 for linhas_ in por_etapa.values() for r in linhas_ if not r.obra
        ),
        recursos_por_etapa=tuple(
            GrupoDeRecursos(
                etapa=Referencia(e.id, e.titulo, f"/etapa/{e.id}"),
                onda=acervo.fecho.onda.get(e.id, 0),
                opcional=e.opcional,
                emprestada=e.id not in proprias,
                recursos=por_etapa[e.id],
            )
            for e in ordenadas
        ),
        qtd_recursos=sum(len(r) for r in por_etapa.values()),
        esforco=comum.duracao(sum(e.esforco_estimado_min for e in etapas)),
        qtd_obrigatorias=sum(1 for e in etapas if not e.opcional),
        qtd_opcionais=sum(1 for e in etapas if e.opcional),
        emprestadas=tuple(
            Referencia(
                id=e,
                titulo=comum.titulo_de(cat, e),
                href=f"/etapa/{e}",
                nota=comum.titulo_de(cat, cat.etapas[e].trilha or "") if e in cat.etapas else "",
            )
            for e in alvo.etapas_referenciadas
        ),
        tem_percurso=percurso is not None,
        qtd_concluidas=sum(1 for e in etapas if _estado(progresso, e.id) is EstadoEtapa.CONCLUIDA),
        qtd_em_andamento=sum(
            1 for e in etapas if _estado(progresso, e.id) is EstadoEtapa.EM_ANDAMENTO
        ),
    )


def etapa(
    acervo: Acervo,
    etapa_id: str,
    *,
    hoje: date,
    percurso: Percurso | None = None,
    percorridos: tuple[Percorrido, ...] = (),
) -> VisaoEtapa | None:
    cat = acervo.catalogo
    alvo = cat.etapas.get(etapa_id)
    if alvo is None:
        return None

    progresso = _progresso_por_etapa(percurso)
    aqui = progresso.get(etapa_id)
    recursos = _recursos_da_etapa(
        cat,
        etapa_id,
        hoje=hoje,
        progresso=progresso,
        percorridos=_percorridos_por_recurso(percorridos),
    )
    exigida = _quantas_exigem(acervo)

    return VisaoEtapa(
        etapa=alvo,
        area=comum.area_do_id(alvo.id),
        trilha=(
            Referencia(alvo.trilha, comum.titulo_de(cat, alvo.trilha), f"/trilha/{alvo.trilha}")
            if alvo.trilha
            else None
        ),
        onda=acervo.fecho.onda.get(alvo.id, 0),
        esforco=comum.duracao(alvo.esforco_estimado_min),
        requisitos=tuple(_exigencia(acervo, r.competencia, r.nivel_minimo) for r in alvo.requires),
        desenvolve=tuple(
            Desenvolvimento(
                competencia_id=t.competencia,
                titulo=comum.titulo_de(cat, t.competencia),
                nivel=t.nivel_resultante,
                nivel_rotulo=comum.nivel(t.nivel_resultante),
                exigida_por=exigida.get(t.competencia, 0),
            )
            for t in alvo.teaches
        ),
        recursos=recursos,
        destravada_por=tuple(
            Referencia(
                a.origem,
                comum.titulo_de(cat, a.origem),
                f"/etapa/{a.origem}",
                nota=", ".join(comum.titulo_de(cat, c) for c in a.competencias),
            )
            for a in acervo.arestas
            if a.destino == etapa_id
        ),
        destrava=tuple(
            Referencia(
                a.destino,
                comum.titulo_de(cat, a.destino),
                f"/etapa/{a.destino}",
                nota=", ".join(comum.titulo_de(cat, c) for c in a.competencias),
            )
            for a in acervo.arestas
            if a.origem == etapa_id
        ),
        tambem_em=tuple(
            Referencia(t.id, t.titulo, f"/trilha/{t.id}")
            for t in cat.trilhas.values()
            if etapa_id in t.etapas_referenciadas
        ),
        alertas=_alertas_da_etapa(alvo, recursos),
        tem_percurso=percurso is not None,
        estado=_estado(progresso, etapa_id),
        estado_rotulo=comum.estado_de_etapa(_estado(progresso, etapa_id)),
        atualizado_em=aqui.atualizado_em if aqui else None,
        acoes=ACOES_POR_ESTADO[_estado(progresso, etapa_id)] if percurso is not None else (),
    )


def competencia(
    acervo: Acervo,
    competencia_id: str,
    *,
    percurso: Percurso | None = None,
    evidencias: tuple[Evidencia, ...] = (),
) -> VisaoCompetencia | None:
    """A competência, e — havendo percurso — o que no log sustenta o nível dela.

    `percurso` dá o nível vigente, que é a projeção que o motor consome; `evidencias`
    dá os fatos que o produziram, com o `seq` de cada um. São duas leituras do mesmo
    log de propósito (ADR-0016): o nível é o que o motor filtra, o `seq` é o que a
    retratação endereça, e nenhum dos dois serve para o papel do outro.
    """
    cat = acervo.catalogo
    alvo = cat.competencias.get(competencia_id)
    if alvo is None:
        return None

    ensinada = tuple(
        (
            Referencia(e.id, e.titulo, f"/etapa/{e.id}"),
            comum.nivel(max(t.nivel_resultante for t in e.teaches if t.competencia == alvo.id)),
        )
        for e in sorted(cat.ensina(alvo.id, somente_ativas=False), key=lambda e: e.titulo)
    )
    exigida = tuple(
        (
            Referencia(e.id, e.titulo, f"/etapa/{e.id}"),
            comum.nivel(max(r.nivel_minimo for r in e.requires if r.competencia == alvo.id)),
        )
        for e in sorted(cat.etapas.values(), key=lambda e: e.titulo)
        if any(r.competencia == alvo.id for r in e.requires)
    )

    alertas: list[str] = []
    if not ensinada:
        alertas.append("nenhuma etapa desenvolve esta competência")
    if alvo.status is Status.DEPRECIADO and alvo.substituido_por:
        alertas.append(f"depreciada — substituída por {alvo.substituido_por}")

    dominada = next(
        (c for c in (percurso.competencias if percurso else ()) if c.competencia == alvo.id), None
    )
    minhas = tuple(_evidencia(e, cat) for e in evidencias if e.competencia == alvo.id)

    return VisaoCompetencia(
        competencia=alvo,
        area=comum.area_do_id(alvo.id),
        nivel_no_catalogo=acervo.fecho.nivel(alvo.id),
        nivel_no_catalogo_rotulo=comum.nivel(acervo.fecho.nivel(alvo.id)),
        ensinada_por=ensinada,
        exigida_por=exigida,
        objetivo_de=tuple(
            Referencia(t.id, t.titulo, f"/trilha/{t.id}", nota=comum.nivel(a.nivel))
            for t in sorted(cat.trilhas.values(), key=lambda t: t.titulo)
            for a in t.objetivo_declarado
            if a.competencia == alvo.id
        ),
        alertas=tuple(alertas),
        tem_percurso=percurso is not None,
        nivel_no_percurso=dominada.nivel if dominada else None,
        nivel_no_percurso_rotulo=comum.nivel(dominada.nivel) if dominada else "",
        ultima_evidencia_em=dominada.ultima_evidencia_em if dominada else None,
        evidencias=minhas,
        pode_retratar=percurso is not None,
        niveis_declaraveis=NIVEIS_PARA_DECLARAR,
    )


# --- apoio ---------------------------------------------------------------------


def _exigencia(acervo: Acervo, competencia_id: str, nivel: Nivel) -> Exigencia:
    cat = acervo.catalogo
    return Exigencia(
        competencia_id=competencia_id,
        titulo=comum.titulo_de(cat, competencia_id),
        nivel=nivel,
        nivel_rotulo=comum.nivel(nivel),
        ensinada_por=tuple(
            Referencia(e.id, e.titulo, f"/etapa/{e.id}")
            for e in sorted(cat.ensina(competencia_id), key=lambda e: e.titulo)
            if any(
                t.competencia == competencia_id and t.nivel_resultante >= nivel for t in e.teaches
            )
        ),
    )


def _evidencia(evidencia: Evidencia, catalogo: Catalogo) -> LinhaEvidencia:
    """Formata uma evidência do log. A ordem é a do log — é linha do tempo, não ranking."""
    return LinhaEvidencia(
        seq=evidencia.seq,
        nivel=evidencia.nivel,
        nivel_rotulo=comum.nivel(evidencia.nivel),
        origem_rotulo=ROTULO_ORIGEM[evidencia.origem],
        confianca=evidencia.confianca,
        em=evidencia.em,
        etapa=(
            Referencia(
                evidencia.etapa,
                comum.titulo_de(catalogo, evidencia.etapa),
                f"/etapa/{evidencia.etapa}",
            )
            if evidencia.etapa
            else None
        ),
        etapa_rev=evidencia.etapa_rev,
        retratada=evidencia.retratada,
        retratada_em=evidencia.retratada_em,
        motivo_da_retratacao=evidencia.motivo_da_retratacao or "",
    )


def _livro(
    pedida: dominio_obras.ObraPedida, catalogo: Catalogo, *, ja_tenho: bool = False
) -> LinhaLivro:
    """Formata um exemplar pedido. As duas somas vêm do domínio, nenhuma é feita aqui.

    O custo é o do exemplar inteiro mesmo quando a trilha usa parte dele — compra-se o
    livro, não o capítulo —, e a duração é só a das fatias pedidas. Inverter qualquer
    uma das duas daria um número que soa razoável e está errado (§3.3).
    """
    return LinhaLivro(
        slug=pedida.obra.slug,
        nome=pedida.obra.nome,
        href=f"/obra/{pedida.obra.slug}",
        custo=comum.dinheiro(pedida.obra.custo),
        custo_valor=pedida.obra.custo,
        duracao=comum.duracao(pedida.duracao_min),
        duracao_min=pedida.duracao_min,
        qtd_fatias=len(pedida.fatias),
        qtd_fatias_do_exemplar=len(pedida.obra.fatias),
        parcial=pedida.parcial,
        etapas=tuple(
            Referencia(e, comum.titulo_de(catalogo, e), f"/etapa/{e}") for e in pedida.etapas
        ),
        idiomas=", ".join(pedida.obra.idiomas),
        toda_depreciada=pedida.obra.toda_depreciada,
        ja_tenho=ja_tenho,
    )


def _recursos_da_etapa(
    catalogo: Catalogo,
    etapa_id: str,
    *,
    hoje: date,
    progresso: Mapping[str, ProgressoEtapa],
    percorridos: Mapping[str, date] = MappingProxyType({}),
) -> tuple[LinhaRecurso, ...]:
    """Os recursos de uma etapa, na ordem em que se escolhe entre eles.

    Disponível primeiro, depois o mais barato e o mais curto: são alternativas, e a
    ordem é a da decisão do estudante (docs/interface.md §5.4). Serve às duas telas que
    listam recurso — a da etapa e a da trilha —, porque ordenar nos dois lugares daria
    duas ordens para a mesma lista.
    """
    aqui = progresso.get(etapa_id)
    return tuple(
        _recurso(
            r,
            hoje=hoje,
            em_uso=aqui is not None and aqui.recurso_em_uso == r.id,
            percorrido_em=percorridos.get(r.id),
        )
        for r in sorted(
            catalogo.recursos_da_etapa(etapa_id),
            key=lambda r: (not r.disponivel, r.custo, r.duracao_min, r.titulo),
        )
    )


def _recurso(
    recurso: Recurso, *, hoje: date, em_uso: bool = False, percorrido_em: date | None = None
) -> LinhaRecurso:
    dias = comum.dias_desde(recurso.verificado_em, hoje)
    return LinhaRecurso(
        id=recurso.id,
        titulo=recurso.titulo,
        formato=comum.formato(recurso.formato),
        idioma=recurso.idioma,
        custo=comum.dinheiro(recurso.custo),
        custo_valor=recurso.custo,
        duracao=comum.duracao(recurso.duracao_min),
        duracao_min=recurso.duracao_min,
        url=recurso.url,
        status=recurso.status,
        disponivel=recurso.disponivel,
        verificado_em=recurso.verificado_em,
        dias_sem_verificar=dias,
        vencido=comum.vencido(recurso.verificado_em, hoje),
        obra=recurso.obra or "",
        em_uso=em_uso,
        percorrido_em=percorrido_em,
    )


def _percorridos_por_recurso(percorridos: tuple[Percorrido, ...]) -> dict[str, date]:
    """Data da passagem por recurso. Sem log, dicionário vazio — como `_progresso_por_etapa`.

    `percorridos_de` já devolve um fato por recurso, o último; aqui só se guarda a data,
    que é tudo que a linha de recurso mostra. A `rev` de então fica no log, onde ela
    responde à pergunta de auditoria que a tabela de recursos não faz.
    """
    return {p.recurso: p.percorrido_em for p in percorridos}


def _progresso_por_etapa(percurso: Percurso | None) -> dict[str, ProgressoEtapa]:
    """Progresso indexado por etapa. Sem percurso, dicionário vazio — não um erro.

    As três telas de detalhe existiam antes de o percurso chegar até elas e continuam
    válidas sem ele: o catálogo é navegável por quem ainda não declarou estudante.
    """
    if percurso is None:
        return {}
    return {p.etapa: p for p in percurso.progresso}


def _estado(progresso: Mapping[str, ProgressoEtapa], etapa_id: str) -> EstadoEtapa:
    """Etapa ausente do progresso é não iniciada — ausência de fato, não fato negativo."""
    aqui = progresso.get(etapa_id)
    return aqui.estado if aqui else EstadoEtapa.NAO_INICIADA


def _quantas_exigem(acervo: Acervo) -> dict[str, int]:
    contagem: dict[str, int] = {}
    for etapa_ in acervo.catalogo.etapas.values():
        for req in etapa_.requires:
            contagem[req.competencia] = contagem.get(req.competencia, 0) + 1
    return contagem


def _alertas_da_etapa(alvo: Etapa, recursos: tuple[LinhaRecurso, ...]) -> tuple[str, ...]:
    alertas: list[str] = []
    disponiveis = [r for r in recursos if r.disponivel and r.status is Status.ATIVO]
    if not disponiveis:
        alertas.append("nenhum recurso ativo e disponível — a etapa não é estudável (CAT-050)")
    if vencidos := [r for r in recursos if r.vencido]:
        alertas.append(
            f"{len(vencidos)} recurso(s) sem verificação há mais de "
            f"{comum.DIAS_ATE_REVERIFICAR} dias (CAT-100)"
        )
    if alvo.status is Status.DEPRECIADO and alvo.substituido_por:
        alertas.append(f"depreciada — substituída por {alvo.substituido_por}")
    return tuple(alertas)
