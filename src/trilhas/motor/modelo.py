"""Entrada e saída do motor de sugestão (motor-de-sugestao.md §1).

O percurso chega aqui já em memória: carregá-lo e persisti-lo é o passo 4 da ordem
de construção (docs/README.md) e não entra no motor.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from types import MappingProxyType

from trilhas.catalogo.modelo import Alvo, Formato, Nivel

# --- Percurso (entrada) --------------------------------------------------------


class EstadoEtapa(StrEnum):
    NAO_INICIADA = "nao_iniciada"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
    ABANDONADA = "abandonada"


class Reacao(StrEnum):
    ACEITA = "aceita"
    POSTERGADA = "postergada"
    REJEITADA = "rejeitada"


@dataclass(frozen=True, slots=True)
class CompetenciaDominada:
    """Competência do perfil, já resumida a partir das evidências (CONTEXT.md §2)."""

    competencia: str
    nivel: Nivel
    ultima_evidencia_em: date
    confianca: float = 1.0


@dataclass(frozen=True, slots=True)
class Restricoes:
    """Limites duros do estudante. Coleção vazia ou `None` significa sem limite."""

    minutos_por_semana: int | None = None
    idiomas: frozenset[str] = frozenset()
    custo_maximo: float | None = None
    formatos_aceitos: frozenset[Formato] = frozenset()


@dataclass(frozen=True, slots=True)
class Objetivo:
    alvos: tuple[Alvo, ...]
    declarado_em: date


@dataclass(frozen=True, slots=True)
class Matricula:
    """Matrícula ativa numa trilha."""

    trilha: str
    iniciada_em: date


@dataclass(frozen=True, slots=True)
class ProgressoEtapa:
    etapa: str
    estado: EstadoEtapa
    atualizado_em: date  # data do último evento: início, conclusão ou abandono
    recurso_em_uso: str | None = None
    """Recurso declarado ao iniciar a etapa, quando houve um. Opcional de propósito:
    iniciar sem dizer por onde se estuda é legítimo, e concluir não repete o recurso."""


@dataclass(frozen=True, slots=True)
class Feedback:
    etapa: str
    reacao: Reacao
    em: date


@dataclass(frozen=True, slots=True)
class Percurso:
    estudante_id: str
    competencias: tuple[CompetenciaDominada, ...] = ()
    restricoes: Restricoes = field(default_factory=Restricoes)
    objetivo: Objetivo | None = None
    matriculas: tuple[Matricula, ...] = ()
    progresso: tuple[ProgressoEtapa, ...] = ()
    feedback: tuple[Feedback, ...] = ()
    estante: frozenset[str] = frozenset()
    """Ids de recurso cujo exemplar o estudante já adquiriu (ADR-0013).

    Uma fatia basta: o motor propaga a posse às irmãs pela `obra` do catálogo de hoje
    (ADR-0009), e `estante` não guarda o agrupamento. Posse é estado declarado, não
    fato datado — por isso aqui e não no log (ADR-0012)."""


@dataclass(frozen=True, slots=True)
class Opcoes:
    quantidade: int = 3
    tempo_disponivel_min: int | None = None


# --- Configuração --------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Pesos:
    """Pesos dos fatores (§2.3). Ponto de partida declarado, não medido (ADR-0003)."""

    relevancia: float = 0.30
    prontidao: float = 0.20
    momentum: float = 0.15
    encaixe_de_esforco: float = 0.15
    desbloqueio: float = 0.10
    urgencia_de_revisao: float = 0.10

    def __post_init__(self) -> None:
        valores = self.como_dict().values()
        if any(v < 0 for v in valores) or abs(sum(valores) - 1.0) > 1e-9:
            raise ValueError("pesos devem ser não negativos e somar 1")

    def como_dict(self) -> dict[str, float]:
        return {
            "relevancia": self.relevancia,
            "prontidao": self.prontidao,
            "momentum": self.momentum,
            "encaixe_de_esforco": self.encaixe_de_esforco,
            "desbloqueio": self.desbloqueio,
            "urgencia_de_revisao": self.urgencia_de_revisao,
        }


_MEIA_VIDA_PADRAO = MappingProxyType(
    {Nivel.INICIANTE: 60, Nivel.INTERMEDIARIO: 120, Nivel.AVANCADO: 240}
)


@dataclass(frozen=True, slots=True)
class Config:
    """Parâmetros do motor. Todos são palpites declarados, calibráveis com uso."""

    pesos: Pesos = field(default_factory=Pesos)
    dias_de_rejeicao: int = 30
    # §3.6: dias sem evidência a partir dos quais a competência começa a decair.
    meia_vida_dias: Mapping[Nivel, int] = _MEIA_VIDA_PADRAO
    # §2.4: decaimento a partir do qual uma competência-alvo conta como "alto".
    decaimento_alto: float = 0.5
    # §3.4: sem `tempo_disponivel_min`, a sessão de referência é a semana dividida
    # por este número.
    sessoes_por_semana: int = 3
    # §4, rejeições repetidas na mesma trilha.
    rejeicoes_para_desalinhar: int = 3
    janela_de_desalinhamento_dias: int = 14


# --- Saída ---------------------------------------------------------------------


class Tipo(StrEnum):
    RETOMADA = "retomada"
    PROXIMA_ETAPA = "proxima_etapa"
    REVISAO = "revisao"
    EXPLORACAO = "exploracao"

    @property
    def prioridade(self) -> int:
        """Ordem de desempate (§2.4): menor vence."""
        return list(Tipo).index(self)


class Motivo(StrEnum):
    """Por que um candidato foi eliminado pelos filtros duros (§2.2)."""

    CONCLUIDA = "concluida"
    JA_DOMINADA = "ja_dominada"
    REQUISITO_NAO_SATISFEITO = "requisito_nao_satisfeito"
    REJEITADA_RECENTEMENTE = "rejeitada_recentemente"
    SEM_RECURSO_VIAVEL = "sem_recurso_viavel"
    NAO_CABE_NO_TEMPO = "nao_cabe_no_tempo"

    @property
    def por_restricao(self) -> bool:
        return self in (Motivo.SEM_RECURSO_VIAVEL, Motivo.NAO_CABE_NO_TEMPO)


class MotivoVazio(StrEnum):
    """Por que a lista de sugestões saiu vazia (§4)."""

    PERFIL_INSUFICIENTE = "perfil_insuficiente"
    SEM_CAMINHO_NO_CATALOGO = "sem_caminho_no_catalogo"
    RESTRICOES_BLOQUEIAM = "restricoes_bloqueiam"
    NADA_SUGERIVEL = "nada_sugerivel"


@dataclass(frozen=True, slots=True)
class Fator:
    nome: str
    peso: float
    valor: float
    contribuicao: float


@dataclass(frozen=True, slots=True)
class Sugestao:
    etapa_id: str
    recurso_sugerido_id: str
    score: float
    fatores: tuple[Fator, ...]
    explicacao: str
    tipo: Tipo
    gerada_em: datetime
    catalogo_versao: int | None = None


@dataclass(frozen=True, slots=True)
class Eliminacao:
    etapa_id: str
    tipo: Tipo
    motivo: Motivo
    detalhe: str = ""


@dataclass(frozen=True, slots=True)
class Resultado:
    sugestoes: tuple[Sugestao, ...]
    eliminadas: tuple[Eliminacao, ...] = ()
    motivo_vazio: MotivoVazio | None = None
    detalhe: str = ""
    # Competências-alvo que nenhum caminho do catálogo alcança (lacuna de catálogo).
    lacunas: tuple[Alvo, ...] = ()
