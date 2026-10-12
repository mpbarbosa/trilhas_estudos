"""Pipeline do motor de sugestão (motor-de-sugestao.md §2).

    candidatos  ->  filtros duros  ->  fatores  ->  diversificação  ->  top-N

Função pura: recebe catálogo, percurso e o instante; não lê relógio nem disco. A
mesma entrada produz sempre a mesma saída (§5, cenário 6).
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from trilhas.catalogo.modelo import Alvo, Catalogo, Etapa, Nivel, Recurso
from trilhas.catalogo.validar import fecho

from .explicar import explicar
from .modelo import (
    CompetenciaDominada,
    Config,
    Eliminacao,
    EstadoEtapa,
    Fator,
    Motivo,
    MotivoVazio,
    Opcoes,
    Percurso,
    ProgressoEtapa,
    Reacao,
    Resultado,
    Sugestao,
    Tipo,
)

_D = Nivel.DESCONHECE


def sugerir(
    catalogo: Catalogo,
    percurso: Percurso,
    momento: datetime,
    opcoes: Opcoes | None = None,
    config: Config | None = None,
    *,
    catalogo_versao: int | None = None,
) -> Resultado:
    opcoes = opcoes or Opcoes()
    config = config or Config()
    ctx = _Contexto.montar(catalogo, percurso, momento.date(), opcoes, config)

    # §4: sem objetivo nem trilha não há para onde apontar; não inventar sugestão.
    if percurso.objetivo is None and not percurso.matriculas:
        return Resultado(
            sugestoes=(),
            motivo_vazio=MotivoVazio.PERFIL_INSUFICIENTE,
            detalhe="declare um objetivo ou matricule-se numa trilha",
        )

    lacunas = ctx.lacunas()
    if (
        percurso.objetivo is not None
        and ctx.alvos_pendentes
        and set(lacunas) == set(ctx.alvos_pendentes)
    ):
        faltam = ", ".join(f"{a.competencia} ({a.nivel})" for a in lacunas)
        return Resultado(
            sugestoes=(),
            motivo_vazio=MotivoVazio.SEM_CAMINHO_NO_CATALOGO,
            detalhe=f"nenhum caminho do catálogo alcança: {faltam}",
            lacunas=lacunas,
        )

    vivos, eliminadas = _filtrar(ctx, _gerar_candidatos(ctx))
    avaliados = _pontuar(ctx, vivos)
    escolhidos = _diversificar(ctx, avaliados, opcoes.quantidade)

    sugestoes = tuple(
        Sugestao(
            etapa_id=a.etapa.id,
            recurso_sugerido_id=a.recurso.id,
            score=a.score,
            fatores=a.fatores,
            explicacao=explicar(ctx, a.etapa, a.tipo, a.fatores, a.recurso, a.desbloqueia),
            tipo=a.tipo,
            gerada_em=momento,
            catalogo_versao=catalogo_versao,
        )
        for a in escolhidos
    )
    if sugestoes:
        return Resultado(sugestoes=sugestoes, eliminadas=eliminadas, lacunas=lacunas)

    por_restricao = Counter(e.detalhe for e in eliminadas if e.motivo.por_restricao)
    if por_restricao:
        # Restrições são o último filtro: quem caiu nelas passou por todos os outros.
        pior, _ = max(por_restricao.items(), key=lambda kv: (kv[1], kv[0]))
        return Resultado(
            sugestoes=(),
            eliminadas=eliminadas,
            motivo_vazio=MotivoVazio.RESTRICOES_BLOQUEIAM,
            detalhe=pior,
            lacunas=lacunas,
        )
    return Resultado(
        sugestoes=(),
        eliminadas=eliminadas,
        motivo_vazio=MotivoVazio.NADA_SUGERIVEL,
        detalhe="nenhuma etapa passa os filtros",
        lacunas=lacunas,
    )


# --- Contexto ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _Contexto:
    """Tudo o que os passos do pipeline consultam, calculado uma vez."""

    catalogo: Catalogo
    percurso: Percurso
    hoje: date
    opcoes: Opcoes
    config: Config
    perfil: dict[str, CompetenciaDominada]
    niveis: dict[str, Nivel]
    estado: dict[str, ProgressoEtapa]
    trilhas_da_etapa: dict[str, tuple[str, ...]]  # só trilhas matriculadas
    trilhas_recentes: frozenset[str]
    trilhas_desalinhadas: frozenset[str]
    alvos: tuple[Alvo, ...]
    alvos_pendentes: tuple[Alvo, ...]
    requerentes: dict[str, tuple[Etapa, ...]]  # competência -> etapas que a exigem

    @classmethod
    def montar(
        cls,
        catalogo: Catalogo,
        percurso: Percurso,
        hoje: date,
        opcoes: Opcoes,
        config: Config,
    ) -> _Contexto:
        perfil = {c.competencia: c for c in percurso.competencias}
        niveis = {c: d.nivel for c, d in perfil.items()}

        estado: dict[str, ProgressoEtapa] = {}
        for p in sorted(percurso.progresso, key=lambda p: (p.atualizado_em, p.estado)):
            estado[p.etapa] = p

        matriculadas = sorted(
            {m.trilha for m in percurso.matriculas if m.trilha in catalogo.trilhas}
        )
        trilhas_da_etapa: dict[str, list[str]] = {}
        for tid in matriculadas:
            for eid in catalogo.trilhas[tid].todas_as_etapas:
                trilhas_da_etapa.setdefault(eid, []).append(tid)

        if percurso.objetivo is not None:
            alvos = percurso.objetivo.alvos
        else:
            # §3.1: sem objetivo, a relevância cai para as trilhas matriculadas.
            alvos = tuple(
                a for tid in matriculadas for a in catalogo.trilhas[tid].objetivo_declarado
            )
        alvos = tuple(sorted(set(alvos), key=lambda a: (a.competencia, a.nivel)))
        pendentes = tuple(a for a in alvos if niveis.get(a.competencia, _D) < a.nivel)

        requerentes: dict[str, list[Etapa]] = {}
        for etapa in _ativas(catalogo):
            for req in etapa.requires:
                requerentes.setdefault(req.competencia, []).append(etapa)

        return cls(
            catalogo=catalogo,
            percurso=percurso,
            hoje=hoje,
            opcoes=opcoes,
            config=config,
            perfil=perfil,
            niveis=niveis,
            estado=estado,
            trilhas_da_etapa={e: tuple(ts) for e, ts in trilhas_da_etapa.items()},
            trilhas_recentes=_trilhas_recentes(estado, trilhas_da_etapa),
            trilhas_desalinhadas=_trilhas_desalinhadas(percurso, hoje, config, trilhas_da_etapa),
            alvos=alvos,
            alvos_pendentes=pendentes,
            requerentes={c: tuple(es) for c, es in requerentes.items()},
        )

    def estado_de(self, etapa_id: str) -> EstadoEtapa:
        p = self.estado.get(etapa_id)
        return p.estado if p else EstadoEtapa.NAO_INICIADA

    def urgencia(self, competencia: str) -> float:
        """§3.6: zero até a meia-vida do nível; cresce linearmente até 1 em mais uma."""
        dominada = self.perfil.get(competencia)
        if dominada is None or dominada.nivel is _D:
            return 0.0
        meia_vida = self.config.meia_vida_dias.get(dominada.nivel)
        if not meia_vida:
            return 0.0
        dias = (self.hoje - dominada.ultima_evidencia_em).days
        return min(1.0, max(0.0, (dias - meia_vida) / meia_vida))

    def lacunas(self) -> tuple[Alvo, ...]:
        alcancado, _ = fecho(_ativas(self.catalogo), self.niveis)
        return tuple(a for a in self.alvos_pendentes if alcancado.get(a.competencia, _D) < a.nivel)

    def distancias(self, etapa: Etapa) -> dict[str, int]:
        """Etapas até cada competência-alvo pendente, seguindo `teaches` -> `requires`.

        A distância ignora níveis: mede proximidade no grafo, não suficiência. O
        conjunto de visitadas garante término mesmo com ciclo no catálogo.
        """
        pendentes = {a.competencia for a in self.alvos_pendentes}
        achadas: dict[str, int] = {}
        visitadas = {etapa.id}
        fila: deque[tuple[Etapa, int]] = deque([(etapa, 0)])
        while fila and len(achadas) < len(pendentes):
            atual, d = fila.popleft()
            for ens in atual.teaches:
                if ens.competencia in pendentes:
                    achadas.setdefault(ens.competencia, d)
                for seguinte in self.requerentes.get(ens.competencia, ()):
                    if seguinte.id not in visitadas:
                        visitadas.add(seguinte.id)
                        fila.append((seguinte, d + 1))
        return achadas

    def requisitos_faltando(self, etapa: Etapa) -> list[str]:
        return [
            f"{r.competencia} ({r.nivel_minimo})"
            for r in etapa.requires
            if self.niveis.get(r.competencia, _D) < r.nivel_minimo
        ]


def _ativas(catalogo: Catalogo) -> list[Etapa]:
    return [catalogo.etapas[e] for e in sorted(catalogo.etapas) if catalogo.etapas[e].status.ativo]


def _trilhas_recentes(
    estado: dict[str, ProgressoEtapa], trilhas_da_etapa: dict[str, list[str]]
) -> frozenset[str]:
    """Trilhas com o evento de progresso mais recente; empates contam todas."""
    datas = [p.atualizado_em for e, p in estado.items() if e in trilhas_da_etapa]
    if not datas:
        return frozenset()
    ultima = max(datas)
    return frozenset(
        t
        for e, p in estado.items()
        if p.atualizado_em == ultima
        for t in trilhas_da_etapa.get(e, ())
    )


def _trilhas_desalinhadas(
    percurso: Percurso, hoje: date, config: Config, trilhas_da_etapa: dict[str, list[str]]
) -> frozenset[str]:
    """§4: rejeições repetidas na mesma trilha sinalizam objetivo desalinhado."""
    desde = hoje - timedelta(days=config.janela_de_desalinhamento_dias)
    contagem: Counter[str] = Counter()
    for f in percurso.feedback:
        if f.reacao is Reacao.REJEITADA and f.em >= desde:
            contagem.update(trilhas_da_etapa.get(f.etapa, ()))
    return frozenset(t for t, n in contagem.items() if n >= config.rejeicoes_para_desalinhar)


# --- §2.1 Candidatos -----------------------------------------------------------


def _gerar_candidatos(ctx: _Contexto) -> dict[str, list[Tipo]]:
    """Cada etapa com todos os tipos sob os quais ela entra; a filtragem escolhe."""
    candidatos: dict[str, list[Tipo]] = {}

    def incluir(etapa: Etapa, tipo: Tipo) -> None:
        tipos = candidatos.setdefault(etapa.id, [])
        if tipo not in tipos:
            tipos.append(tipo)

    ativas = _ativas(ctx.catalogo)
    for etapa in ativas:
        if etapa.id in ctx.trilhas_da_etapa:
            em_andamento = ctx.estado_de(etapa.id) is EstadoEtapa.EM_ANDAMENTO
            incluir(etapa, Tipo.RETOMADA if em_andamento else Tipo.PROXIMA_ETAPA)

        # Revisão: a etapa revisita, no nível que o estudante já tem, algo que decaiu.
        if any(
            ctx.urgencia(t.competencia) > 0
            and t.nivel_resultante <= ctx.niveis.get(t.competencia, _D)
            for t in etapa.teaches
        ):
            incluir(etapa, Tipo.REVISAO)

        if etapa.id not in ctx.trilhas_da_etapa and ctx.distancias(etapa):
            incluir(etapa, Tipo.EXPLORACAO)

    for tipos in candidatos.values():
        tipos.sort(key=lambda t: t.prioridade)
    return candidatos


# --- §2.2 Filtros duros --------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _Vivo:
    etapa: Etapa
    tipo: Tipo
    recurso: Recurso


def _filtrar(
    ctx: _Contexto, candidatos: dict[str, list[Tipo]]
) -> tuple[list[_Vivo], tuple[Eliminacao, ...]]:
    vivos: list[_Vivo] = []
    eliminadas: list[Eliminacao] = []
    for eid in sorted(candidatos):
        etapa = ctx.catalogo.etapas[eid]
        # Se todos os tipos caem, vale o motivo do último: é o que foi mais longe.
        ultima: Eliminacao | None = None
        for tipo in candidatos[eid]:
            resultado = _aplicar_filtros(ctx, etapa, tipo)
            if isinstance(resultado, Eliminacao):
                ultima = resultado
                continue
            vivos.append(_Vivo(etapa, tipo, resultado))
            break
        else:
            assert ultima is not None
            eliminadas.append(ultima)
    return vivos, tuple(eliminadas)


def _aplicar_filtros(ctx: _Contexto, etapa: Etapa, tipo: Tipo) -> Recurso | Eliminacao:
    """Devolve o recurso sugerido, ou o primeiro filtro que eliminou a etapa."""

    def fora(motivo: Motivo, detalhe: str = "") -> Eliminacao:
        return Eliminacao(etapa.id, tipo, motivo, detalhe)

    if tipo is not Tipo.REVISAO:
        if ctx.estado_de(etapa.id) is EstadoEtapa.CONCLUIDA:
            return fora(Motivo.CONCLUIDA)
        # Competência adquirida fora da trilha pula as etapas que só a ensinam (§5, 2).
        if etapa.teaches and all(
            ctx.niveis.get(t.competencia, _D) >= t.nivel_resultante for t in etapa.teaches
        ):
            return fora(Motivo.JA_DOMINADA)
        faltando = ctx.requisitos_faltando(etapa)
        if faltando:
            return fora(Motivo.REQUISITO_NAO_SATISFEITO, ", ".join(faltando))

    rejeicao = _rejeicao_vigente(ctx, etapa.id)
    if rejeicao is not None:
        return fora(Motivo.REJEITADA_RECENTEMENTE, rejeicao.isoformat())

    viaveis, culpada = _recursos_viaveis(ctx, etapa)
    if not viaveis:
        return fora(Motivo.SEM_RECURSO_VIAVEL, culpada)

    tempo = ctx.opcoes.tempo_disponivel_min
    if tempo is not None:
        viaveis = [r for r in viaveis if r.duracao_min <= tempo]
        if not viaveis:
            return fora(Motivo.NAO_CABE_NO_TEMPO, "tempo")

    return min(viaveis, key=lambda r: (-_encaixe(ctx, r.duracao_min), r.custo, r.duracao_min, r.id))


def _rejeicao_vigente(ctx: _Contexto, etapa_id: str) -> date | None:
    limite = ctx.hoje - timedelta(days=ctx.config.dias_de_rejeicao)
    objetivo = ctx.percurso.objetivo
    rejeicoes = [
        f.em
        for f in ctx.percurso.feedback
        if f.etapa == etapa_id
        and f.reacao is Reacao.REJEITADA
        and f.em > limite
        # Mudança de objetivo depois da rejeição devolve a etapa antes do prazo.
        and not (objetivo is not None and objetivo.declarado_em > f.em)
    ]
    return max(rejeicoes) if rejeicoes else None


def _recursos_viaveis(ctx: _Contexto, etapa: Etapa) -> tuple[list[Recurso], str]:
    """Recursos que passam as restrições e a restrição que mais eliminou."""
    r = ctx.percurso.restricoes
    viaveis: list[Recurso] = []
    culpas: Counter[str] = Counter()
    for rec in sorted(ctx.catalogo.recursos_da_etapa(etapa.id), key=lambda x: x.id):
        if not rec.status.ativo or not rec.disponivel:
            culpas["indisponivel"] += 1
        elif r.idiomas and rec.idioma not in r.idiomas:
            culpas["idioma"] += 1
        elif r.custo_maximo is not None and rec.custo > r.custo_maximo:
            culpas["custo"] += 1
        elif r.formatos_aceitos and rec.formato not in r.formatos_aceitos:
            culpas["formato"] += 1
        else:
            viaveis.append(rec)
    culpada = max(culpas.items(), key=lambda kv: (kv[1], kv[0]))[0] if culpas else "sem_recurso"
    return viaveis, culpada


# --- §2.3 / §3 Fatores ---------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _Avaliado:
    etapa: Etapa
    tipo: Tipo
    recurso: Recurso
    fatores: tuple[Fator, ...]
    score: float
    desbloqueia: int


def _pontuar(ctx: _Contexto, vivos: list[_Vivo]) -> list[_Avaliado]:
    desbloqueios = {v.etapa.id: _desbloqueio_bruto(ctx, v.etapa) for v in vivos}
    maximo = max(desbloqueios.values(), default=0)
    pesos = ctx.config.pesos.como_dict()

    avaliados: list[_Avaliado] = []
    for v in vivos:
        valores = {
            "relevancia": _relevancia(ctx, v.etapa),
            "prontidao": _prontidao(ctx, v.etapa),
            "momentum": _momentum(ctx, v.etapa, v.tipo),
            "encaixe_de_esforco": _encaixe(ctx, v.recurso.duracao_min),
            "desbloqueio": desbloqueios[v.etapa.id] / maximo if maximo else 0.0,
            "urgencia_de_revisao": max(
                (ctx.urgencia(t.competencia) for t in v.etapa.teaches), default=0.0
            ),
        }
        fatores = tuple(
            Fator(nome, pesos[nome], valor, pesos[nome] * valor) for nome, valor in valores.items()
        )
        avaliados.append(
            _Avaliado(
                etapa=v.etapa,
                tipo=v.tipo,
                recurso=v.recurso,
                fatores=fatores,
                score=sum(f.contribuicao for f in fatores),
                desbloqueia=desbloqueios[v.etapa.id],
            )
        )
    return avaliados


def _relevancia(ctx: _Contexto, etapa: Etapa) -> float:
    """§3.1: média, sobre os alvos pendentes, de 1 / (1 + distância)."""
    if not ctx.alvos_pendentes:
        return 0.0
    distancias = ctx.distancias(etapa)
    competencias = {a.competencia for a in ctx.alvos_pendentes}
    return sum(1 / (1 + distancias[c]) for c in competencias if c in distancias) / len(competencias)


# §3.2: valor por margem (nível do perfil - nível exigido). Pico em um grau acima.
_PRONTIDAO_POR_MARGEM = {0: 0.6, 1: 1.0, 2: 0.7, 3: 0.5}
_PRONTIDAO_SEM_REQUISITO = 0.8


def _prontidao(ctx: _Contexto, etapa: Etapa) -> float:
    if not etapa.requires:
        return _PRONTIDAO_SEM_REQUISITO
    valores = []
    for req in etapa.requires:
        margem = ctx.niveis.get(req.competencia, _D) - req.nivel_minimo
        base = _PRONTIDAO_POR_MARGEM.get(margem, 0.0)
        dominada = ctx.perfil.get(req.competencia)
        confianca = dominada.confianca if dominada else 1.0
        valores.append(base * (0.5 + 0.5 * confianca))
    return sum(valores) / len(valores)


def _momentum(ctx: _Contexto, etapa: Etapa, tipo: Tipo) -> float:
    """§3.3, com os ajustes de §4 para etapa abandonada e rejeições repetidas."""
    if tipo is Tipo.RETOMADA:
        return 1.0
    if tipo is Tipo.EXPLORACAO:
        return 0.3 if ctx.trilhas_desalinhadas else 0.0
    if ctx.estado_de(etapa.id) is EstadoEtapa.ABANDONADA:
        return 0.0
    trilhas = ctx.trilhas_da_etapa.get(etapa.id, ())
    if not trilhas:
        return 0.0
    valor = 0.7 if ctx.trilhas_recentes.intersection(trilhas) else 0.3
    if ctx.trilhas_desalinhadas.intersection(trilhas):
        valor /= 2
    return valor


def _encaixe(ctx: _Contexto, duracao: int) -> float:
    """§3.4: 1,0 se o recurso ocupa de 50% a 100% da sessão de referência."""
    referencia = ctx.opcoes.tempo_disponivel_min
    semana = ctx.percurso.restricoes.minutos_por_semana
    if referencia is None and semana:
        referencia = semana // max(1, ctx.config.sessoes_por_semana)
    if not referencia or duracao <= 0:
        return 0.5
    razao = duracao / referencia
    if razao < 0.5:
        return razao / 0.5
    if razao > 1:
        return 1 / razao
    return 1.0


def _desbloqueio_bruto(ctx: _Contexto, etapa: Etapa) -> int:
    """§3.5: etapas hoje bloqueadas que concluir esta libera."""
    depois = dict(ctx.niveis)
    for ens in etapa.teaches:
        depois[ens.competencia] = max(depois.get(ens.competencia, _D), ens.nivel_resultante)
    vistas: set[str] = set()
    for ens in etapa.teaches:
        for outra in ctx.requerentes.get(ens.competencia, ()):
            if outra.id == etapa.id or outra.id in vistas:
                continue
            if ctx.requisitos_faltando(outra) and all(
                depois.get(r.competencia, _D) >= r.nivel_minimo for r in outra.requires
            ):
                vistas.add(outra.id)
    return len(vistas)


# --- §2.4 Diversificação e desempate --------------------------------------------

_MAXIMO_POR_TRILHA = 2


def _diversificar(ctx: _Contexto, avaliados: list[_Avaliado], quantidade: int) -> list[_Avaliado]:
    ordenados = sorted(
        avaliados,
        key=lambda a: (
            -round(a.score, 9),
            a.tipo.prioridade,
            a.etapa.esforco_estimado_min,
            -a.desbloqueia,
            a.etapa.id,
        ),
    )
    decaidas = sum(
        1 for a in ctx.alvos if ctx.urgencia(a.competencia) >= ctx.config.decaimento_alto
    )
    limite_revisao = quantidade if decaidas >= 3 else 1

    escolhidos: list[_Avaliado] = []
    revisoes = 0
    por_trilha: Counter[str] = Counter()
    for a in ordenados:
        if len(escolhidos) == quantidade:
            break
        if a.tipo is Tipo.REVISAO and revisoes >= limite_revisao:
            continue
        trilhas = _trilhas_de(ctx, a.etapa)
        if any(por_trilha[t] >= _MAXIMO_POR_TRILHA for t in trilhas):
            continue
        escolhidos.append(a)
        revisoes += a.tipo is Tipo.REVISAO
        por_trilha.update(trilhas)
    return escolhidos


def _trilhas_de(ctx: _Contexto, etapa: Etapa) -> tuple[str, ...]:
    if etapa.id in ctx.trilhas_da_etapa:
        return ctx.trilhas_da_etapa[etapa.id]
    return (etapa.trilha,) if etapa.trilha else ()
