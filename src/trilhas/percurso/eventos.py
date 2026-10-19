"""Os fatos datados do percurso (ADR-0008).

Cada evento é imutável e carrega o instante em que aconteceu. Nenhum deles é
calculado a partir do catálogo na leitura: o que o catálogo dizia no momento da
escrita fica gravado aqui, e é isso que faz "fato datado não retroage" valer por
construção (catalogo.md §4).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from typing import Any, Self

from trilhas.catalogo.modelo import Nivel
from trilhas.motor.modelo import Reacao, Tipo


class Origem(StrEnum):
    """De onde veio uma evidência. Pesa na confiança (CONTEXT.md §1)."""

    CONCLUSAO_DE_ETAPA = "conclusao_de_etapa"
    AUTOAVALIACAO = "autoavaliacao"


@dataclass(frozen=True, slots=True)
class EvidenciaRegistrada:
    """Fato que sustenta uma `CompetenciaDominada`. Sem isto, ela não existe."""

    competencia: str
    nivel: Nivel
    origem: Origem
    confianca: float = 1.0
    etapa: str | None = None
    etapa_rev: int | None = None

    def como_dados(self) -> dict[str, Any]:
        return {
            "competencia": self.competencia,
            "nivel": str(self.nivel),
            "origem": str(self.origem),
            "confianca": self.confianca,
            "etapa": self.etapa,
            "etapa_rev": self.etapa_rev,
        }

    @classmethod
    def de_dados(cls, d: dict[str, Any]) -> Self:
        return cls(
            competencia=str(d["competencia"]),
            nivel=Nivel.de_texto(str(d["nivel"])),
            origem=Origem(str(d["origem"])),
            confianca=float(d.get("confianca", 1.0)),
            etapa=d.get("etapa"),
            etapa_rev=d.get("etapa_rev"),
        )


@dataclass(frozen=True, slots=True)
class EvidenciaRetratada:
    """Diz que uma `EvidenciaRegistrada` foi emitida por engano (ADR-0014).

    Aponta para o `seq` do evento que retrata, e **não repete** a competência nem o
    nível dele: seria redundância capaz de contradizer o alvo. Gravar o que a outra
    fonte dizia — como `concluir_etapa` faz com `teaches` — existe porque o catálogo
    muda; o evento #29 não muda. O log é append-only, então consultar o alvo depois dá
    a mesma resposta que daria na escrita.
    """

    evidencia_seq: int
    motivo: str | None = None

    def como_dados(self) -> dict[str, Any]:
        return {"evidencia_seq": self.evidencia_seq, "motivo": self.motivo}

    @classmethod
    def de_dados(cls, d: dict[str, Any]) -> Self:
        return cls(int(d["evidencia_seq"]), d.get("motivo"))


@dataclass(frozen=True, slots=True)
class EtapaIniciada:
    etapa: str
    etapa_rev: int
    recurso: str | None = None

    def como_dados(self) -> dict[str, Any]:
        return {"etapa": self.etapa, "etapa_rev": self.etapa_rev, "recurso": self.recurso}

    @classmethod
    def de_dados(cls, d: dict[str, Any]) -> Self:
        return cls(str(d["etapa"]), int(d["etapa_rev"]), d.get("recurso"))


@dataclass(frozen=True, slots=True)
class EtapaConcluida:
    etapa: str
    etapa_rev: int

    def como_dados(self) -> dict[str, Any]:
        return {"etapa": self.etapa, "etapa_rev": self.etapa_rev}

    @classmethod
    def de_dados(cls, d: dict[str, Any]) -> Self:
        return cls(str(d["etapa"]), int(d["etapa_rev"]))


@dataclass(frozen=True, slots=True)
class EtapaAbandonada:
    etapa: str
    etapa_rev: int
    motivo: str | None = None

    def como_dados(self) -> dict[str, Any]:
        return {"etapa": self.etapa, "etapa_rev": self.etapa_rev, "motivo": self.motivo}

    @classmethod
    def de_dados(cls, d: dict[str, Any]) -> Self:
        return cls(str(d["etapa"]), int(d["etapa_rev"]), d.get("motivo"))


@dataclass(frozen=True, slots=True)
class RecursoPercorrido:
    """Material percorrido de ponta a ponta — e nada além disso (ADR-0012).

    **Não emite evidência**: percorrer uma fatia que vale 13% do esforço de uma etapa
    não prova competência alguma sobre ela. Foi concluir etapa como procuração de "li o
    livro" que gerou o caso da ADR, e o log não retira evidência emitida.

    `obra` de propósito não está aqui: o fato afirma "percorri este recurso", e o
    agrupamento por obra é apresentação, resolvida na leitura contra o catálogo de hoje.
    Gravá-lo partiria o histórico em dois ao renomear uma obra (ADR-0009).
    """

    recurso: str
    recurso_rev: int

    def como_dados(self) -> dict[str, Any]:
        return {"recurso": self.recurso, "recurso_rev": self.recurso_rev}

    @classmethod
    def de_dados(cls, d: dict[str, Any]) -> Self:
        return cls(str(d["recurso"]), int(d["recurso_rev"]))


@dataclass(frozen=True, slots=True)
class SugestaoEmitida:
    """Sugestão como fato: reproduzível porque guarda fatores e `catalogo_versao`."""

    etapa: str
    recurso: str
    score: float
    tipo: Tipo
    catalogo_versao: int | None
    fatores: tuple[tuple[str, float], ...] = ()

    def como_dados(self) -> dict[str, Any]:
        return {
            "etapa": self.etapa,
            "recurso": self.recurso,
            "score": self.score,
            "tipo": str(self.tipo),
            "catalogo_versao": self.catalogo_versao,
            "fatores": [list(par) for par in self.fatores],
        }

    @classmethod
    def de_dados(cls, d: dict[str, Any]) -> Self:
        return cls(
            etapa=str(d["etapa"]),
            recurso=str(d["recurso"]),
            score=float(d["score"]),
            tipo=Tipo(str(d["tipo"])),
            catalogo_versao=d.get("catalogo_versao"),
            fatores=tuple((str(n), float(v)) for n, v in d.get("fatores", [])),
        )


@dataclass(frozen=True, slots=True)
class FeedbackDado:
    etapa: str
    reacao: Reacao
    motivo: str | None = None

    def como_dados(self) -> dict[str, Any]:
        return {"etapa": self.etapa, "reacao": str(self.reacao), "motivo": self.motivo}

    @classmethod
    def de_dados(cls, d: dict[str, Any]) -> Self:
        return cls(str(d["etapa"]), Reacao(str(d["reacao"])), d.get("motivo"))


Evento = (
    EvidenciaRegistrada
    | EvidenciaRetratada
    | EtapaIniciada
    | EtapaConcluida
    | EtapaAbandonada
    | RecursoPercorrido
    | SugestaoEmitida
    | FeedbackDado
)

TIPOS: dict[str, type[Evento]] = {
    "evidencia_registrada": EvidenciaRegistrada,
    "evidencia_retratada": EvidenciaRetratada,
    "etapa_iniciada": EtapaIniciada,
    "etapa_concluida": EtapaConcluida,
    "etapa_abandonada": EtapaAbandonada,
    "recurso_percorrido": RecursoPercorrido,
    "sugestao_emitida": SugestaoEmitida,
    "feedback_dado": FeedbackDado,
}

_NOMES: dict[type, str] = {classe: nome for nome, classe in TIPOS.items()}


def nome_do_tipo(evento: Evento) -> str:
    return _NOMES[type(evento)]


def evento_de_dados(tipo: str, dados: dict[str, Any]) -> Evento | None:
    """Reconstrói um evento a partir do nome do tipo e do JSON gravado.

    Despacho explícito em vez de `TIPOS[tipo].de_dados(...)`: o dicionário apaga o
    tipo concreto, e o verificador deixa de conferir a desserialização justamente na
    borda em que o dado vem de fora.
    """
    match tipo:
        case "evidencia_registrada":
            return EvidenciaRegistrada.de_dados(dados)
        case "evidencia_retratada":
            return EvidenciaRetratada.de_dados(dados)
        case "etapa_iniciada":
            return EtapaIniciada.de_dados(dados)
        case "etapa_concluida":
            return EtapaConcluida.de_dados(dados)
        case "etapa_abandonada":
            return EtapaAbandonada.de_dados(dados)
        case "recurso_percorrido":
            return RecursoPercorrido.de_dados(dados)
        case "sugestao_emitida":
            return SugestaoEmitida.de_dados(dados)
        case "feedback_dado":
            return FeedbackDado.de_dados(dados)
        case _:
            return None


@dataclass(frozen=True, slots=True)
class Registro:
    """Um evento no log, com sua posição e instante. `seq` dá a ordem total."""

    evento: Evento
    em: datetime
    estudante: str
    seq: int = 0
    metadados: dict[str, Any] = field(default_factory=dict)

    @property
    def dia(self) -> date:
        return self.em.date()
