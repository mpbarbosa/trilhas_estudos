"""Motor de sugestão: responde "o que eu estudo agora?" (docs/motor-de-sugestao.md).

Lógica pura sobre o catálogo e o percurso em memória; não toca disco nem relógio.
"""

from .modelo import (
    CompetenciaDominada,
    Config,
    Eliminacao,
    EstadoEtapa,
    Fator,
    Feedback,
    Matricula,
    Motivo,
    MotivoVazio,
    Objetivo,
    Opcoes,
    Percurso,
    Pesos,
    ProgressoEtapa,
    Reacao,
    Restricoes,
    Resultado,
    Sugestao,
    Tipo,
)
from .sugerir import sugerir

__all__ = [
    "CompetenciaDominada",
    "Config",
    "Eliminacao",
    "EstadoEtapa",
    "Fator",
    "Feedback",
    "Matricula",
    "Motivo",
    "MotivoVazio",
    "Objetivo",
    "Opcoes",
    "Percurso",
    "Pesos",
    "ProgressoEtapa",
    "Reacao",
    "Restricoes",
    "Resultado",
    "Sugestao",
    "Tipo",
    "sugerir",
]
