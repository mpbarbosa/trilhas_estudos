"""Lê os arquivos YAML de `catalogo/` e monta um `Catalogo` indexado.

Só reporta erros de **forma** (YAML inválido, campo ausente, valor fora do domínio,
id duplicado). Coerência entre entidades é trabalho de `validar`.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from .modelo import (
    VERSAO_SCHEMA_SUPORTADA,
    Alvo,
    Catalogo,
    Competencia,
    Ensino,
    Etapa,
    Formato,
    Nivel,
    Recurso,
    Requisito,
    Status,
    Trilha,
)
from .problemas import Codigo, Problema, erro

SUBDIRETORIOS = ("competencias", "etapas", "trilhas", "recursos")


class _Coletor:
    """Acumula problemas de forma, mantendo o arquivo corrente no contexto."""

    def __init__(self) -> None:
        self.problemas: list[Problema] = []
        self._arquivo: str = ""

    def arquivo(self, caminho: str) -> None:
        self._arquivo = caminho

    def falha(self, codigo: Codigo, mensagem: str, entidade: str | None = None) -> None:
        self.problemas.append(erro(codigo, mensagem, entidade=entidade, arquivo=self._arquivo))


def carregar(raiz: Path) -> tuple[Catalogo, list[Problema]]:
    """Carrega o catálogo a partir do diretório raiz (ex. `catalogo/`)."""
    col = _Coletor()
    catalogo = Catalogo()

    if not raiz.is_dir():
        col.arquivo(str(raiz))
        col.falha(Codigo.YAML_INVALIDO, "diretório de catálogo não encontrado")
        return catalogo, col.problemas

    for caminho in sorted(raiz.rglob("*.yaml")):
        rel = str(caminho.relative_to(raiz.parent))
        col.arquivo(rel)
        try:
            dados = yaml.safe_load(caminho.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            col.falha(Codigo.YAML_INVALIDO, f"YAML inválido: {exc}")
            continue
        if dados is None:
            continue
        if not isinstance(dados, Mapping):
            col.falha(Codigo.SCHEMA_INVALIDO, "arquivo deve conter um mapeamento no topo")
            continue
        _conferir_versao_schema(dados, col)
        _absorver(dados, catalogo, col)

    return catalogo, col.problemas


def _conferir_versao_schema(dados: Mapping[str, Any], col: _Coletor) -> None:
    versao = dados.get("versao_schema")
    if versao is None:
        col.falha(Codigo.SCHEMA_INVALIDO, "campo obrigatório ausente: versao_schema")
    elif versao != VERSAO_SCHEMA_SUPORTADA:
        col.falha(
            Codigo.SCHEMA_INVALIDO,
            f"versao_schema {versao!r} não suportada (esperado {VERSAO_SCHEMA_SUPORTADA})",
        )


def _absorver(dados: Mapping[str, Any], catalogo: Catalogo, col: _Coletor) -> None:
    for item in _lista(dados, "competencias", col):
        _registrar(catalogo.competencias, _competencia(item, col), col)
    for item in _lista(dados, "etapas", col):
        _registrar(catalogo.etapas, _etapa(item, col, trilha=None), col)
    for item in _lista(dados, "recursos", col):
        _registrar(catalogo.recursos, _recurso(item, col), col)

    bruto = dados.get("trilha")
    if bruto is not None:
        if not isinstance(bruto, Mapping):
            col.falha(Codigo.SCHEMA_INVALIDO, "`trilha` deve ser um mapeamento")
            return
        trilha = _trilha(bruto, catalogo, col)
        if trilha is not None:
            _registrar(catalogo.trilhas, trilha, col)


def _lista(dados: Mapping[str, Any], chave: str, col: _Coletor) -> Iterable[Mapping[str, Any]]:
    bruto = dados.get(chave, [])
    if not isinstance(bruto, list):
        col.falha(Codigo.SCHEMA_INVALIDO, f"`{chave}` deve ser uma lista")
        return []
    saida = []
    for item in bruto:
        if isinstance(item, Mapping):
            saida.append(item)
        else:
            col.falha(Codigo.SCHEMA_INVALIDO, f"item de `{chave}` deve ser um mapeamento")
    return saida


def _registrar(indice: dict[str, Any], entidade: Any, col: _Coletor) -> None:
    if entidade is None:
        return
    if entidade.id in indice:
        col.falha(Codigo.ID_INVALIDO, "id duplicado no catálogo", entidade=entidade.id)
        return
    indice[entidade.id] = entidade


# --- construtores por entidade -------------------------------------------------


def _competencia(item: Mapping[str, Any], col: _Coletor) -> Competencia | None:
    ident = _texto(item, "id", col)
    if ident is None:
        return None
    verificacao = _texto(item, "verificacao", col, entidade=ident)
    if verificacao is None:
        return None
    return Competencia(
        id=ident,
        titulo=_texto(item, "titulo", col, entidade=ident) or ident,
        rev=_inteiro(item, "rev", col, ident),
        status=_status(item, col, ident),
        verificacao=verificacao,
        descricao=str(item.get("descricao", "")),
        substituido_por=_opcional_texto(item, "substituido_por"),
        depreciado_em=_data(item, "depreciado_em", col, ident),
    )


def _etapa(item: Mapping[str, Any], col: _Coletor, *, trilha: str | None) -> Etapa | None:
    ident = _texto(item, "id", col)
    if ident is None:
        return None
    return Etapa(
        id=ident,
        titulo=_texto(item, "titulo", col, entidade=ident) or ident,
        rev=_inteiro(item, "rev", col, ident),
        status=_status(item, col, ident),
        esforco_estimado_min=_inteiro(item, "esforco_estimado_min", col, ident),
        trilha=trilha,
        opcional=bool(item.get("opcional", False)),
        requires=tuple(
            Requisito(c, n)
            for c, n in _pares(item, "requires", "nivel_minimo", col, ident)
        ),
        teaches=tuple(
            Ensino(c, n)
            for c, n in _pares(item, "teaches", "nivel_resultante", col, ident)
        ),
        substituido_por=_opcional_texto(item, "substituido_por"),
        depreciado_em=_data(item, "depreciado_em", col, ident),
    )


def _recurso(item: Mapping[str, Any], col: _Coletor) -> Recurso | None:
    ident = _texto(item, "id", col)
    if ident is None:
        return None
    etapa = _texto(item, "etapa", col, entidade=ident)
    if etapa is None:
        return None
    formato_bruto = str(item.get("formato", ""))
    try:
        formato = Formato(formato_bruto)
    except ValueError:
        col.falha(
            Codigo.SCHEMA_INVALIDO,
            f"formato {formato_bruto!r} inválido (use: {', '.join(f.value for f in Formato)})",
            entidade=ident,
        )
        return None
    return Recurso(
        id=ident,
        titulo=_texto(item, "titulo", col, entidade=ident) or ident,
        rev=_inteiro(item, "rev", col, ident),
        status=_status(item, col, ident),
        etapa=etapa,
        formato=formato,
        idioma=str(item.get("idioma", "pt-BR")),
        custo=float(item.get("custo", 0)),
        duracao_min=_inteiro(item, "duracao_min", col, ident),
        url=str(item.get("url", "")),
        disponivel=bool(item.get("disponivel", True)),
        verificado_em=_data(item, "verificado_em", col, ident),
        substituido_por=_opcional_texto(item, "substituido_por"),
        depreciado_em=_data(item, "depreciado_em", col, ident),
    )


def _trilha(item: Mapping[str, Any], catalogo: Catalogo, col: _Coletor) -> Trilha | None:
    ident = _texto(item, "id", col)
    if ident is None:
        return None

    proprias: list[str] = []
    for bruto in _lista(item, "etapas", col):
        etapa = _etapa(bruto, col, trilha=ident)
        if etapa is not None:
            _registrar(catalogo.etapas, etapa, col)
            proprias.append(etapa.id)

    referenciadas = item.get("etapas_referenciadas", []) or []
    if not isinstance(referenciadas, list):
        col.falha(Codigo.SCHEMA_INVALIDO, "`etapas_referenciadas` deve ser uma lista", ident)
        referenciadas = []

    return Trilha(
        id=ident,
        titulo=_texto(item, "titulo", col, entidade=ident) or ident,
        rev=_inteiro(item, "rev", col, ident),
        status=_status(item, col, ident),
        objetivo_declarado=tuple(
            Alvo(c, n) for c, n in _pares(item, "objetivo_declarado", "nivel", col, ident)
        ),
        etapas=tuple(proprias),
        etapas_referenciadas=tuple(str(r) for r in referenciadas),
        substituido_por=_opcional_texto(item, "substituido_por"),
        depreciado_em=_data(item, "depreciado_em", col, ident),
    )


# --- leitura de campos ---------------------------------------------------------


def _texto(
    item: Mapping[str, Any], chave: str, col: _Coletor, entidade: str | None = None
) -> str | None:
    valor = item.get(chave)
    if not isinstance(valor, str) or not valor.strip():
        col.falha(
            Codigo.SCHEMA_INVALIDO, f"campo obrigatório ausente ou vazio: {chave}", entidade
        )
        return None
    return valor.strip()


def _opcional_texto(item: Mapping[str, Any], chave: str) -> str | None:
    valor = item.get(chave)
    return valor.strip() if isinstance(valor, str) and valor.strip() else None


def _inteiro(item: Mapping[str, Any], chave: str, col: _Coletor, entidade: str) -> int:
    valor = item.get(chave)
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
        col.falha(
            Codigo.SCHEMA_INVALIDO, f"`{chave}` deve ser inteiro não negativo", entidade
        )
        return 0
    return valor


def _status(item: Mapping[str, Any], col: _Coletor, entidade: str) -> Status:
    bruto = str(item.get("status", Status.ATIVO.value))
    try:
        return Status(bruto)
    except ValueError:
        col.falha(
            Codigo.SCHEMA_INVALIDO,
            f"status {bruto!r} inválido (use: {', '.join(s.value for s in Status)})",
            entidade,
        )
        return Status.RASCUNHO


def _data(
    item: Mapping[str, Any], chave: str, col: _Coletor, entidade: str
) -> date | None:
    valor = item.get(chave)
    if valor is None:
        return None
    if isinstance(valor, date):
        return valor
    try:
        return date.fromisoformat(str(valor))
    except ValueError:
        col.falha(Codigo.SCHEMA_INVALIDO, f"`{chave}` deve ser data ISO (AAAA-MM-DD)", entidade)
        return None


def _pares(
    item: Mapping[str, Any], chave: str, campo_nivel: str, col: _Coletor, entidade: str
) -> list[tuple[str, Nivel]]:
    saida: list[tuple[str, Nivel]] = []
    for bruto in _lista(item, chave, col):
        competencia = bruto.get("competencia")
        if not isinstance(competencia, str) or not competencia.strip():
            col.falha(Codigo.SCHEMA_INVALIDO, f"`{chave}` exige `competencia`", entidade)
            continue
        try:
            nivel = Nivel.de_texto(str(bruto.get(campo_nivel, "")))
        except ValueError as exc:
            col.falha(Codigo.SCHEMA_INVALIDO, f"`{chave}`: {exc}", entidade)
            continue
        saida.append((competencia.strip(), nivel))
    return saida
