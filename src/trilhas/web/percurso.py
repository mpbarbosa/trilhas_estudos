"""Leitura do percurso do estudante — borda de I/O, como `dados.py`.

**Formato provisório.** `percurso/*.yaml` declara-se transitório e nenhuma ADR decidiu
o esquema; a decisão de persistência está prevista em docs/interface.md §9. Este
módulo existe para a interface poder *mostrar* a sugestão sem antecipar essa decisão:
lê, nunca escreve. Quando a ADR vier, só este arquivo muda.

A tolerância aqui é deliberada: campo ausente vira ausência, não exceção. Um percurso
pela metade tem de render uma tela, e o motor já sabe responder a perfil insuficiente
(motor §4) — travar na leitura esconderia esse caso de borda em vez de mostrá-lo.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from ..catalogo.modelo import Alvo, Formato, Nivel
from ..motor.modelo import (
    CompetenciaDominada,
    EstadoEtapa,
    Feedback,
    Matricula,
    Objetivo,
    Percurso,
    ProgressoEtapa,
    Reacao,
    Restricoes,
)

NOME_DO_DIRETORIO = "percurso"


def carregar_percurso(caminho: Path) -> Percurso | None:
    """Lê um arquivo de percurso. Devolve `None` se não há o que ler."""
    dados = _mapa(_ler(caminho))
    if not dados:
        return None

    estudante = _mapa(dados.get("estudante"))
    perfil = _mapa(dados.get("perfil"))

    return Percurso(
        estudante_id=str(estudante.get("id", caminho.stem)),
        competencias=tuple(_dominadas(perfil.get("competencias_dominadas"))),
        restricoes=_restricoes(_mapa(perfil.get("restricoes"))),
        objetivo=_objetivo(_mapa(dados.get("objetivo"))),
        matriculas=tuple(_matriculas(dados.get("matriculas"))),
        progresso=tuple(_progresso(dados.get("progresso"))),
        feedback=tuple(_feedback(dados.get("feedback"))),
    )


def nome_do_estudante(caminho: Path) -> str:
    dados = _mapa(_ler(caminho))
    estudante = _mapa(dados.get("estudante"))
    return str(estudante.get("nome") or estudante.get("id") or caminho.stem)


def percursos_em(diretorio: Path) -> dict[str, Path]:
    """Mapeia `estudante_id` → arquivo, para as rotas aceitarem `?estudante=`."""
    if not diretorio.is_dir():
        return {}
    achados: dict[str, Path] = {}
    for arquivo in sorted(diretorio.glob("*.yaml")):
        dados = _mapa(_ler(arquivo))
        identificador = str(_mapa(dados.get("estudante")).get("id", arquivo.stem))
        achados[identificador] = arquivo
    return achados


# --- leitura de campos ---------------------------------------------------------


def _ler(caminho: Path) -> Any:
    if not caminho.is_file():
        return None
    try:
        return yaml.safe_load(caminho.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None


def _mapa(valor: Any) -> Mapping[str, Any]:
    return valor if isinstance(valor, Mapping) else {}


def _lista(valor: Any) -> list[Mapping[str, Any]]:
    if not isinstance(valor, list):
        return []
    return [item for item in valor if isinstance(item, Mapping)]


def _data(valor: Any) -> date | None:
    if isinstance(valor, date):
        return valor
    try:
        return date.fromisoformat(str(valor))
    except (TypeError, ValueError):
        return None


def _nivel(valor: Any) -> Nivel | None:
    try:
        return Nivel.de_texto(str(valor))
    except ValueError:
        return None


def _dominadas(bruto: Any) -> Iterable[CompetenciaDominada]:
    for item in _lista(bruto):
        competencia = item.get("competencia")
        nivel = _nivel(item.get("nivel"))
        quando = _data(item.get("ultima_evidencia_em"))
        if not competencia or nivel is None or quando is None:
            continue
        yield CompetenciaDominada(
            competencia=str(competencia),
            nivel=nivel,
            ultima_evidencia_em=quando,
            confianca=float(item.get("confianca", 1.0)),
        )


def _restricoes(bruto: Mapping[str, Any]) -> Restricoes:
    formatos = []
    for valor in bruto.get("formatos_aceitos", []) or []:
        try:
            formatos.append(Formato(str(valor)))
        except ValueError:
            continue
    custo = bruto.get("custo_maximo")
    minutos = bruto.get("minutos_por_semana")
    return Restricoes(
        minutos_por_semana=int(minutos) if minutos is not None else None,
        idiomas=frozenset(str(i) for i in bruto.get("idiomas", []) or []),
        custo_maximo=float(custo) if custo is not None else None,
        formatos_aceitos=frozenset(formatos),
    )


def _objetivo(bruto: Mapping[str, Any]) -> Objetivo | None:
    alvos = []
    for item in _lista(bruto.get("alvos")):
        competencia = item.get("competencia")
        nivel = _nivel(item.get("nivel"))
        if competencia and nivel is not None:
            alvos.append(Alvo(str(competencia), nivel))
    if not alvos:
        return None
    return Objetivo(tuple(alvos), _data(bruto.get("declarado_em")) or date.min)


def _matriculas(bruto: Any) -> Iterable[Matricula]:
    for item in _lista(bruto):
        trilha = item.get("trilha")
        iniciada = _data(item.get("iniciada_em"))
        estado = str(item.get("estado", "em_andamento"))
        if not trilha or iniciada is None or estado != "em_andamento":
            continue
        yield Matricula(trilha=str(trilha), iniciada_em=iniciada)


def _progresso(bruto: Any) -> Iterable[ProgressoEtapa]:
    for item in _lista(bruto):
        etapa = item.get("etapa")
        if not etapa:
            continue
        try:
            estado = EstadoEtapa(str(item.get("estado", "nao_iniciada")))
        except ValueError:
            continue
        atualizado = (
            _data(item.get("concluida_em"))
            or _data(item.get("abandonada_em"))
            or _data(item.get("iniciada_em"))
        )
        if atualizado is None:
            continue
        yield ProgressoEtapa(etapa=str(etapa), estado=estado, atualizado_em=atualizado)


def _feedback(bruto: Any) -> Iterable[Feedback]:
    for item in _lista(bruto):
        etapa = item.get("etapa")
        quando = _data(item.get("em") or item.get("data"))
        try:
            reacao = Reacao(str(item.get("reacao", "")))
        except ValueError:
            continue
        if not etapa or quando is None:
            continue
        yield Feedback(etapa=str(etapa), reacao=reacao, em=quando)
