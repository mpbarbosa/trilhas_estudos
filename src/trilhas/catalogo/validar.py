"""As 11 validações de docs/catalogo.md §5.

Função pura: recebe catálogo em memória e o estado do snapshot anterior, devolve
problemas. Sem I/O.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date, timedelta

from .modelo import FORMA_DO_ID, ID_PADROES, Catalogo, Etapa, Nivel, Status
from .problemas import Codigo, Problema, aviso, erro
from .snapshot import EstadoAnterior

DIAS_ATE_REVERIFICAR = 180

_PREFIXO_ESPERADO = {
    "competencias": "comp",
    "etapas": "etapa",
    "recursos": "rec",
    "trilhas": "trilha",
}


def validar(
    catalogo: Catalogo,
    anterior: EstadoAnterior | None = None,
    *,
    hoje: date | None = None,
) -> list[Problema]:
    anterior = anterior or EstadoAnterior.vazio()
    hoje = hoje or date.today()

    problemas: list[Problema] = []
    problemas += _v1_ids(catalogo, anterior)
    problemas += _v2_referencias(catalogo)
    problemas += _v3_ordenavel(catalogo)
    problemas += _v4_beco_sem_saida(catalogo)
    problemas += _v5_recursos(catalogo)
    problemas += _v6_objetivo_alcancavel(catalogo)
    problemas += _v7_nivel_nao_rebaixa(catalogo)
    problemas += _v8_depreciacao(catalogo)
    problemas += _v9_rev_nao_decresce(catalogo, anterior)
    problemas += _v10_recursos_verificados(catalogo, hoje)
    problemas += _v11_etapas_orfas(catalogo)
    return problemas


# --- §5.1 ----------------------------------------------------------------------


def _v1_ids(catalogo: Catalogo, anterior: EstadoAnterior) -> list[Problema]:
    problemas: list[Problema] = []
    for colecao, prefixo in _PREFIXO_ESPERADO.items():
        for ident in getattr(catalogo, colecao):
            if not ident.startswith(f"{prefixo}:"):
                problemas.append(
                    erro(
                        Codigo.ID_INVALIDO,
                        f"id em `{colecao}` deve ter prefixo `{prefixo}:`",
                        entidade=ident,
                    )
                )
            elif not ID_PADROES[prefixo].match(ident):
                problemas.append(
                    erro(
                        Codigo.ID_INVALIDO,
                        f"id fora do padrão `{FORMA_DO_ID[prefixo]}` em minúsculas",
                        entidade=ident,
                    )
                )

    for sumido in sorted(anterior.ids - catalogo.ids()):
        problemas.append(
            erro(
                Codigo.ID_INVALIDO,
                "presente no snapshot anterior e ausente agora; entidades são "
                "depreciadas, nunca removidas (catalogo.md §6)",
                entidade=sumido,
            )
        )
    return problemas


# --- §5.2 ----------------------------------------------------------------------


def _v2_referencias(catalogo: Catalogo) -> list[Problema]:
    problemas: list[Problema] = []

    def conferir(origem: str, alvo: str, campo: str, universo: Iterable[str]) -> None:
        if alvo not in universo:
            problemas.append(
                erro(
                    Codigo.REFERENCIA_QUEBRADA,
                    f"`{campo}` aponta para {alvo!r}, que não existe no catálogo",
                    entidade=origem,
                )
            )

    for etapa in catalogo.etapas.values():
        for req in etapa.requires:
            conferir(etapa.id, req.competencia, "requires", catalogo.competencias)
        for ens in etapa.teaches:
            conferir(etapa.id, ens.competencia, "teaches", catalogo.competencias)

    for recurso in catalogo.recursos.values():
        conferir(recurso.id, recurso.etapa, "etapa", catalogo.etapas)

    for trilha in catalogo.trilhas.values():
        for etapa_id in trilha.etapas_referenciadas:
            conferir(trilha.id, etapa_id, "etapas_referenciadas", catalogo.etapas)
        for alvo in trilha.objetivo_declarado:
            conferir(trilha.id, alvo.competencia, "objetivo_declarado", catalogo.competencias)

    todos = catalogo.ids()
    for entidade in catalogo.por_id().values():
        if entidade.substituido_por is not None:
            conferir(entidade.id, entidade.substituido_por, "substituido_por", todos)

    return problemas


# --- §5.3 ----------------------------------------------------------------------


def _tem_professor(catalogo: Catalogo, competencia: str, nivel_minimo: Nivel) -> bool:
    """Existe etapa ativa que desenvolve a competência no nível pedido?"""
    return any(
        t.competencia == competencia and t.nivel_resultante >= nivel_minimo
        for etapa in catalogo.ensina(competencia)
        for t in etapa.teaches
    )


def _v3_ordenavel(catalogo: Catalogo) -> list[Problema]:
    """Toda etapa ativa precisa ser alcançável a partir de perfil vazio.

    Não se verifica por ordenação topológica: uma competência ensinada em mais de um
    nível produz arestas espúrias nos dois sentidos, e um ciclo nesse grafo não
    significa catálogo inordenável. O que importa é o fecho progressivo — se uma
    etapa nunca é liberada, ela está presa, seja por dependência circular real,
    seja por nível inalcançável.

    Etapas presas por falta de qualquer professor são reportadas por §5.4, mais
    preciso; aqui só entram as que têm professor e ainda assim não destravam.
    """
    ativas = catalogo.etapas_ativas()
    perfil, liberadas = _fecho(ativas)

    problemas: list[Problema] = []
    for etapa in ativas:
        if etapa.id in liberadas:
            continue
        pendentes = [
            req
            for req in etapa.requires
            if perfil.get(req.competencia, Nivel.DESCONHECE) < req.nivel_minimo
            and _tem_professor(catalogo, req.competencia, req.nivel_minimo)
        ]
        if not pendentes:
            continue
        faltando = ", ".join(f"{r.competencia} ({r.nivel_minimo})" for r in pendentes)
        problemas.append(
            erro(
                Codigo.ETAPA_INALCANCAVEL,
                "não é alcançável a partir de perfil vazio, embora exista etapa ativa "
                f"que desenvolva o que ela exige — dependência circular em: {faltando}",
                entidade=etapa.id,
            )
        )
    return problemas


# --- §5.4 ----------------------------------------------------------------------


def _v4_beco_sem_saida(catalogo: Catalogo) -> list[Problema]:
    problemas: list[Problema] = []
    for etapa in catalogo.etapas_ativas():
        for req in etapa.requires:
            if req.competencia not in catalogo.competencias:
                continue  # já reportado em §5.2
            if not _tem_professor(catalogo, req.competencia, req.nivel_minimo):
                problemas.append(
                    erro(
                        Codigo.BECO_SEM_SAIDA,
                        f"exige {req.competencia} em nível {req.nivel_minimo}, "
                        "e nenhuma etapa ativa desenvolve essa competência nesse nível",
                        entidade=etapa.id,
                    )
                )
    return problemas


# --- §5.5 ----------------------------------------------------------------------


def _v5_recursos(catalogo: Catalogo) -> list[Problema]:
    problemas: list[Problema] = []
    for etapa in catalogo.etapas_ativas():
        viaveis = [
            r for r in catalogo.recursos_da_etapa(etapa.id) if r.status.ativo and r.disponivel
        ]
        if not viaveis:
            problemas.append(
                erro(
                    Codigo.SEM_RECURSO,
                    "etapa ativa sem nenhum recurso ativo e disponível",
                    entidade=etapa.id,
                )
            )
    return problemas


# --- §5.6 ----------------------------------------------------------------------


def _fecho(etapas: Iterable[Etapa]) -> tuple[dict[str, Nivel], set[str]]:
    """Fecho progressivo a partir de perfil vazio.

    Devolve o perfil alcançado e os ids das etapas que chegaram a ser liberadas.
    Avança por ponto fixo: aplica toda etapa cujos `requires` já estão satisfeitos.
    """
    perfil: dict[str, Nivel] = {}
    liberadas: set[str] = set()
    pendentes = list(etapas)
    avancou = True
    while avancou:
        avancou = False
        restantes = []
        for etapa in pendentes:
            satisfeita = all(
                perfil.get(r.competencia, Nivel.DESCONHECE) >= r.nivel_minimo
                for r in etapa.requires
            )
            if not satisfeita:
                restantes.append(etapa)
                continue
            liberadas.add(etapa.id)
            for ens in etapa.teaches:
                atual = perfil.get(ens.competencia, Nivel.DESCONHECE)
                if ens.nivel_resultante > atual:
                    perfil[ens.competencia] = ens.nivel_resultante
            avancou = True
        pendentes = restantes
    return perfil, liberadas


def _v6_objetivo_alcancavel(catalogo: Catalogo) -> list[Problema]:
    problemas: list[Problema] = []
    for trilha in catalogo.trilhas.values():
        if not trilha.status.ativo or not trilha.objetivo_declarado:
            continue
        proprias = [
            catalogo.etapas[e]
            for e in trilha.todas_as_etapas
            if e in catalogo.etapas and catalogo.etapas[e].status.ativo
        ]
        perfil, _ = _fecho(proprias)
        faltam = [
            f"{alvo.competencia} ({alvo.nivel})"
            for alvo in trilha.objetivo_declarado
            if perfil.get(alvo.competencia, Nivel.DESCONHECE) < alvo.nivel
        ]
        if faltam:
            problemas.append(
                erro(
                    Codigo.OBJETIVO_INALCANCAVEL,
                    "objetivo não é alcançável a partir de perfil vazio com as etapas "
                    f"ativas da própria trilha; falta: {', '.join(faltam)}",
                    entidade=trilha.id,
                )
            )
    return problemas


# --- §5.7 ----------------------------------------------------------------------


def _v7_nivel_nao_rebaixa(catalogo: Catalogo) -> list[Problema]:
    problemas: list[Problema] = []
    for etapa in catalogo.etapas.values():
        minimos = {r.competencia: r.nivel_minimo for r in etapa.requires}
        for ens in etapa.teaches:
            minimo = minimos.get(ens.competencia)
            if minimo is not None and ens.nivel_resultante < minimo:
                problemas.append(
                    erro(
                        Codigo.NIVEL_REBAIXA,
                        f"ensina {ens.competencia} em {ens.nivel_resultante}, "
                        f"abaixo do nível {minimo} que a própria etapa exige",
                        entidade=etapa.id,
                    )
                )
    return problemas


# --- §5.8 ----------------------------------------------------------------------


def _v8_depreciacao(catalogo: Catalogo) -> list[Problema]:
    problemas: list[Problema] = []
    por_id = catalogo.por_id()

    for entidade in por_id.values():
        if entidade.status is Status.DEPRECIADO and entidade.depreciado_em is None:
            problemas.append(
                erro(
                    Codigo.DEPRECIACAO_INCOERENTE,
                    "entidade depreciada sem `depreciado_em`",
                    entidade=entidade.id,
                )
            )

    def apontar(origem: str, alvo: str, campo: str) -> None:
        destino = por_id.get(alvo)
        if destino is None or destino.status is not Status.DEPRECIADO:
            return
        if destino.substituido_por is None:
            problemas.append(
                erro(
                    Codigo.DEPRECIACAO_INCOERENTE,
                    f"`{campo}` aponta para {alvo!r}, depreciada e sem `substituido_por`",
                    entidade=origem,
                )
            )

    for etapa in catalogo.etapas_ativas():
        for req in etapa.requires:
            apontar(etapa.id, req.competencia, "requires")
        for ens in etapa.teaches:
            apontar(etapa.id, ens.competencia, "teaches")

    for recurso in catalogo.recursos.values():
        if recurso.status.ativo:
            apontar(recurso.id, recurso.etapa, "etapa")

    for trilha in catalogo.trilhas.values():
        if not trilha.status.ativo:
            continue
        for etapa_id in trilha.etapas_referenciadas:
            apontar(trilha.id, etapa_id, "etapas_referenciadas")
        for alvo in trilha.objetivo_declarado:
            destino = catalogo.competencias.get(alvo.competencia)
            if destino is not None and destino.status is Status.DEPRECIADO:
                problemas.append(
                    erro(
                        Codigo.DEPRECIACAO_INCOERENTE,
                        f"objetivo_declarado cita competência depreciada {alvo.competencia!r}; "
                        "migração é explícita",
                        entidade=trilha.id,
                    )
                )
    return problemas


# --- §5.9 ----------------------------------------------------------------------


def _v9_rev_nao_decresce(catalogo: Catalogo, anterior: EstadoAnterior) -> list[Problema]:
    problemas: list[Problema] = []
    atuais = catalogo.revs()
    for ident, rev_anterior in anterior.revs.items():
        rev_atual = atuais.get(ident)
        if rev_atual is not None and rev_atual < rev_anterior:
            problemas.append(
                erro(
                    Codigo.REV_DECRESCEU,
                    f"rev caiu de {rev_anterior} para {rev_atual}",
                    entidade=ident,
                )
            )
    return problemas


# --- §5.10 e §5.11 -------------------------------------------------------------


def _v10_recursos_verificados(catalogo: Catalogo, hoje: date) -> list[Problema]:
    limite = hoje - timedelta(days=DIAS_ATE_REVERIFICAR)
    problemas: list[Problema] = []
    for recurso in catalogo.recursos.values():
        if not recurso.status.ativo:
            continue
        if recurso.verificado_em is None:
            problemas.append(
                aviso(
                    Codigo.RECURSO_NAO_VERIFICADO,
                    "recurso ativo sem `verificado_em`",
                    entidade=recurso.id,
                )
            )
        elif recurso.verificado_em < limite:
            dias = (hoje - recurso.verificado_em).days
            problemas.append(
                aviso(
                    Codigo.RECURSO_NAO_VERIFICADO,
                    f"não verificado há {dias} dias (limite: {DIAS_ATE_REVERIFICAR})",
                    entidade=recurso.id,
                )
            )
    return problemas


def _v11_etapas_orfas(catalogo: Catalogo) -> list[Problema]:
    alcancadas: set[str] = set()
    for trilha in catalogo.trilhas.values():
        if trilha.status.ativo:
            alcancadas |= set(trilha.todas_as_etapas)

    return [
        aviso(
            Codigo.ETAPA_ORFA,
            "etapa ativa fora de qualquer trilha ativa; só alcançável por exploração",
            entidade=etapa.id,
        )
        for etapa in catalogo.etapas_ativas()
        if etapa.id not in alcancadas
    ]
