"""Painel *Agora* — a tela que justifica o projeto (docs/interface.md §5.2).

Duas regras mandam aqui:

1. **Nenhuma sugestão sem fatores à vista** (§6.2). O score é a soma visível das
   contribuições; se os fatores não cabem, o cartão não cabe.
2. **Candidato eliminado tem motivo** (motor §2.2). "Por que isto não apareceu" é
   resposta, não depuração — e é o que distingue este sistema.

A ordem dos cartões é a do motor. A interface não reordena, não filtra e não desempata:
isso é domínio, e duplicá-lo aqui faria a tela discordar do score que ela mostra (§3.3).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime

from ...catalogo.modelo import Catalogo, Recurso
from ...motor.modelo import (
    Eliminacao,
    Motivo,
    MotivoVazio,
    Percurso,
    Resultado,
    Sugestao,
    Tipo,
)
from . import comum

ROTULO_TIPO = {
    Tipo.RETOMADA: "retomada",
    Tipo.PROXIMA_ETAPA: "próximo passo",
    Tipo.REVISAO: "revisão",
    Tipo.EXPLORACAO: "exploração",
}

# Escrito como escape porque o sinal literal cai no RUF001 (caractere ambíguo).
VEZES = "\u00d7"

ROTULO_FATOR = {
    "relevancia": "relevância",
    "prontidao": "prontidão",
    "momentum": "momentum",
    "encaixe_de_esforco": "encaixe de esforço",
    "desbloqueio": "desbloqueio",
    "urgencia_de_revisao": "urgência de revisão",
}

ROTULO_MOTIVO = {
    Motivo.CONCLUIDA: "já concluída",
    Motivo.JA_DOMINADA: "competências já dominadas",
    Motivo.REQUISITO_NAO_SATISFEITO: "pré-requisito não satisfeito",
    Motivo.REJEITADA_RECENTEMENTE: "rejeitada recentemente",
    Motivo.SEM_RECURSO_VIAVEL: "nenhum recurso passa nas suas restrições",
    Motivo.NAO_CABE_NO_TEMPO: "não cabe no tempo informado",
}

TEXTO_MOTIVO_VAZIO = {
    MotivoVazio.PERFIL_INSUFICIENTE: (
        "Nada a sugerir ainda",
        "Sem objetivo declarado nem matrícula não há para onde apontar, e inventar "
        "sugestão seria pior que não sugerir.",
    ),
    MotivoVazio.SEM_CAMINHO_NO_CATALOGO: (
        "O catálogo não chega ao seu objetivo",
        "Isto é lacuna de catálogo, não falha sua: nenhuma etapa ativa leva às "
        "competências abaixo no nível pedido.",
    ),
    MotivoVazio.RESTRICOES_BLOQUEIAM: (
        "Suas restrições eliminaram tudo",
        "Todos os candidatos foram filtrados antes de serem pontuados.",
    ),
    MotivoVazio.NADA_SUGERIVEL: (
        "Nada sugerível agora",
        "Não sobrou candidato depois dos filtros — veja abaixo o que foi eliminado.",
    ),
}


@dataclass(frozen=True, slots=True)
class Trecho:
    """Pedaço da explicação, com ou sem ênfase.

    O motor escreve `*assim*` o nome de uma entidade. Quebrar isso em trechos no
    servidor evita marcar HTML como seguro no template: o escape do Jinja continua
    valendo para o texto todo.
    """

    texto: str
    enfase: bool = False


@dataclass(frozen=True, slots=True)
class Barra:
    nome: str
    rotulo: str
    peso: float
    valor: float
    contribuicao: float
    largura_trilho: float
    """Percentual da linha que este fator pode ocupar — proporcional ao peso."""
    largura_preenchida: float
    """Percentual efetivamente ocupado — proporcional à contribuição."""
    conta: str


@dataclass(frozen=True, slots=True)
class RecursoSugerido:
    id: str
    titulo: str
    formato: str
    idioma: str
    custo: str
    duracao: str
    url: str


@dataclass(frozen=True, slots=True)
class Cartao:
    posicao: int
    etapa_id: str
    titulo: str
    href: str
    tipo: str
    tipo_chave: str
    score: float
    score_pct: float
    explicacao: str
    trechos: tuple[Trecho, ...]
    barras: tuple[Barra, ...]
    recurso: RecursoSugerido | None
    trilha_id: str
    trilha_titulo: str
    esforco: str


@dataclass(frozen=True, slots=True)
class GrupoEliminado:
    motivo: str
    motivo_chave: str
    por_restricao: bool
    quantidade: int
    etapas: tuple[tuple[str, str, str], ...]
    """`(etapa_id, título, detalhe)` — o detalhe é o do motor, não inventado aqui."""


@dataclass(frozen=True, slots=True)
class VisaoPainel:
    estudante_id: str
    estudante_nome: str
    estudantes: tuple[str, ...]
    cartoes: tuple[Cartao, ...]
    motivo_vazio: str
    titulo_vazio: str
    texto_vazio: str
    detalhe_vazio: str
    lacunas: tuple[tuple[str, str, str], ...]
    eliminados: tuple[GrupoEliminado, ...]
    total_eliminados: int
    bloqueio_principal: GrupoEliminado | None
    """O filtro que eliminou mais candidatos — a restrição a afrouxar primeiro (§5.2)."""
    tempo_disponivel_min: int | None
    quantidade: int
    gerada_em: str
    catalogo_versao: int
    sem_percurso: bool
    matriculas: int
    competencias_dominadas: int

    @property
    def vazio(self) -> bool:
        return not self.cartoes


def painel(
    resultado: Resultado,
    catalogo: Catalogo,
    percurso: Percurso | None,
    *,
    estudante_nome: str = "",
    estudantes: tuple[str, ...] = (),
    tempo_disponivel_min: int | None = None,
    quantidade: int = 3,
    momento: datetime | None = None,
    catalogo_versao: int = 0,
    hoje: date | None = None,
) -> VisaoPainel:
    titulo, texto = (
        TEXTO_MOTIVO_VAZIO.get(resultado.motivo_vazio, ("", ""))
        if (resultado.motivo_vazio is not None)
        else ("", "")
    )

    grupos = _agrupar(resultado.eliminadas, catalogo)
    por_restricao = [g for g in grupos if g.por_restricao]

    return VisaoPainel(
        estudante_id=percurso.estudante_id if percurso else "",
        estudante_nome=estudante_nome,
        estudantes=estudantes,
        cartoes=tuple(
            _cartao(posicao, sugestao, catalogo)
            for posicao, sugestao in enumerate(resultado.sugestoes, start=1)
        ),
        motivo_vazio=resultado.motivo_vazio.value if resultado.motivo_vazio else "",
        titulo_vazio=titulo,
        texto_vazio=texto,
        detalhe_vazio=resultado.detalhe,
        lacunas=tuple(
            (alvo.competencia, comum.titulo_de(catalogo, alvo.competencia), comum.nivel(alvo.nivel))
            for alvo in resultado.lacunas
        ),
        eliminados=grupos,
        total_eliminados=len(resultado.eliminadas),
        bloqueio_principal=por_restricao[0] if por_restricao else None,
        tempo_disponivel_min=tempo_disponivel_min,
        quantidade=quantidade,
        gerada_em=momento.date().isoformat() if momento else "",
        catalogo_versao=catalogo_versao,
        sem_percurso=percurso is None,
        matriculas=len(percurso.matriculas) if percurso else 0,
        competencias_dominadas=len(percurso.competencias) if percurso else 0,
    )


def _cartao(posicao: int, sugestao: Sugestao, catalogo: Catalogo) -> Cartao:
    etapa = catalogo.etapas.get(sugestao.etapa_id)
    trilha_id = etapa.trilha or "" if etapa else ""
    return Cartao(
        posicao=posicao,
        etapa_id=sugestao.etapa_id,
        titulo=comum.titulo_de(catalogo, sugestao.etapa_id),
        href=f"/etapa/{sugestao.etapa_id}",
        tipo=ROTULO_TIPO[sugestao.tipo],
        tipo_chave=sugestao.tipo.value,
        score=sugestao.score,
        score_pct=round(sugestao.score * 100),
        explicacao=sugestao.explicacao,
        trechos=_trechos(sugestao.explicacao),
        barras=tuple(_barra(f.nome, f.peso, f.valor, f.contribuicao) for f in sugestao.fatores),
        recurso=_recurso(catalogo.recursos.get(sugestao.recurso_sugerido_id)),
        trilha_id=trilha_id,
        trilha_titulo=comum.titulo_de(catalogo, trilha_id) if trilha_id else "",
        esforco=comum.duracao(etapa.esforco_estimado_min) if etapa else "",
    )


_ENFASE = re.compile(r"\*([^*]+)\*")


def _trechos(explicacao: str) -> tuple[Trecho, ...]:
    partes: list[Trecho] = []
    posicao = 0
    for achado in _ENFASE.finditer(explicacao):
        if achado.start() > posicao:
            partes.append(Trecho(explicacao[posicao : achado.start()]))
        partes.append(Trecho(achado.group(1), enfase=True))
        posicao = achado.end()
    if posicao < len(explicacao):
        partes.append(Trecho(explicacao[posicao:]))
    return tuple(partes)


def _barra(nome: str, peso: float, valor: float, contribuicao: float) -> Barra:
    return Barra(
        nome=nome,
        rotulo=ROTULO_FATOR.get(nome, nome),
        peso=peso,
        valor=valor,
        contribuicao=contribuicao,
        largura_trilho=round(peso * 100, 2),
        largura_preenchida=round(contribuicao * 100, 2),
        conta=f"{_numero(peso)} {VEZES} {_numero(valor)} = {_numero(contribuicao)}",
    )


def _numero(valor: float) -> str:
    return f"{valor:.2f}".replace(".", ",")


def _recurso(recurso: Recurso | None) -> RecursoSugerido | None:
    if recurso is None:
        return None
    return RecursoSugerido(
        id=recurso.id,
        titulo=recurso.titulo,
        formato=comum.formato(recurso.formato),
        idioma=recurso.idioma,
        custo=comum.dinheiro(recurso.custo),
        duracao=comum.duracao(recurso.duracao_min),
        url=recurso.url,
    )


def _agrupar(eliminadas: tuple[Eliminacao, ...], catalogo: Catalogo) -> tuple[GrupoEliminado, ...]:
    """Agrupa por motivo, do mais frequente ao menos — o que mais bloqueia primeiro."""
    por_motivo: dict[Motivo, list[Eliminacao]] = {}
    for eliminacao in eliminadas:
        por_motivo.setdefault(eliminacao.motivo, []).append(eliminacao)

    grupos = [
        GrupoEliminado(
            motivo=ROTULO_MOTIVO.get(motivo, motivo.value),
            motivo_chave=motivo.value,
            por_restricao=motivo.por_restricao,
            quantidade=len(lista),
            etapas=tuple(
                (e.etapa_id, comum.titulo_de(catalogo, e.etapa_id), e.detalhe)
                for e in sorted(lista, key=lambda e: e.etapa_id)
            ),
        )
        for motivo, lista in por_motivo.items()
    ]
    return tuple(sorted(grupos, key=lambda g: (-g.quantidade, g.motivo_chave)))
