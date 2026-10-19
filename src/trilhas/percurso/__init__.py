"""Percurso: fatos datados em log append-only, perfil derivado (ADR-0008).

    ação  ->  registrar (puro)  ->  repositorio (I/O)  ->  projecao (puro)  ->  motor

`eventos`, `registrar` e `projecao` são domínio puro. `repositorio` é borda de I/O,
a terceira do projeto ao lado de `catalogo/cli.py` e `web/dados.py`.
"""

from .eventos import (
    EtapaAbandonada,
    EtapaConcluida,
    EtapaIniciada,
    Evento,
    EvidenciaRegistrada,
    EvidenciaRetratada,
    FeedbackDado,
    Origem,
    RecursoPercorrido,
    Registro,
    SugestaoEmitida,
)
from .migrar import eventos_do_yaml
from .projecao import (
    Percorrido,
    competencias_de,
    feedback_de,
    montar_percurso,
    percorridos_de,
    progresso_de,
    retratadas_em,
)
from .registrar import (
    abandonar_etapa,
    concluir_etapa,
    conferir_recurso,
    conferir_recurso_avulso,
    conferir_retratacao,
    dar_feedback,
    emitir_sugestao,
    iniciar_etapa,
    percorrer_recurso,
    registrar_autoavaliacao,
    retratar_evidencia,
)
from .repositorio import Repositorio

__all__ = [
    "EtapaAbandonada",
    "EtapaConcluida",
    "EtapaIniciada",
    "Evento",
    "EvidenciaRegistrada",
    "EvidenciaRetratada",
    "FeedbackDado",
    "Origem",
    "Percorrido",
    "RecursoPercorrido",
    "Registro",
    "Repositorio",
    "SugestaoEmitida",
    "abandonar_etapa",
    "competencias_de",
    "concluir_etapa",
    "conferir_recurso",
    "conferir_recurso_avulso",
    "conferir_retratacao",
    "dar_feedback",
    "emitir_sugestao",
    "eventos_do_yaml",
    "feedback_de",
    "iniciar_etapa",
    "montar_percurso",
    "percorrer_recurso",
    "percorridos_de",
    "progresso_de",
    "registrar_autoavaliacao",
    "retratadas_em",
    "retratar_evidencia",
]
