"""Visão do diagnóstico: as 11 validações, para quem não roda a CLI.

Cada código leva à seção de docs/catalogo.md §5 que o define — um problema que não diz
qual regra foi violada obriga a procurar, e quem autora catálogo procura muito.
"""

from __future__ import annotations

from dataclasses import dataclass

from ...catalogo.problemas import Codigo, Problema, Severidade
from ..dados import Diagnostico

SECAO_DO_CODIGO = {
    Codigo.YAML_INVALIDO: ("forma", "§1"),
    Codigo.SCHEMA_INVALIDO: ("forma", "§2"),
    Codigo.ID_INVALIDO: ("ids únicos e no formato", "§5.1"),
    Codigo.REFERENCIA_QUEBRADA: ("toda referência resolve", "§5.2"),
    Codigo.ETAPA_INALCANCAVEL: ("etapa alcançável de perfil vazio", "§5.3"),
    Codigo.BECO_SEM_SAIDA: ("sem beco sem saída", "§5.4"),
    Codigo.SEM_RECURSO: ("etapa com recurso disponível", "§5.5"),
    Codigo.OBJETIVO_INALCANCAVEL: ("objetivo alcançável", "§5.6"),
    Codigo.NIVEL_REBAIXA: ("nível nunca rebaixa", "§5.7"),
    Codigo.DEPRECIACAO_INCOERENTE: ("depreciação coerente", "§5.8"),
    Codigo.REV_DECRESCEU: ("rev não decresce", "§5.9"),
    Codigo.RECURSO_NAO_VERIFICADO: ("recurso verificado há ≤ 180 dias", "§5.10"),
    Codigo.ETAPA_ORFA: ("etapa fora de trilha ativa", "§5.11"),
}


@dataclass(frozen=True, slots=True)
class Linha:
    codigo: str
    regra: str
    secao: str
    severidade: str
    mensagem: str
    entidade: str
    href: str
    local: str


@dataclass(frozen=True, slots=True)
class VisaoDiagnostico:
    fonte: str
    erros: tuple[Linha, ...]
    avisos: tuple[Linha, ...]
    lock_desatualizado: bool | None
    catalogo_versao: int
    gerado_em: str
    hash_curto: str

    @property
    def valido(self) -> bool:
        return not self.erros

    @property
    def total(self) -> int:
        return len(self.erros) + len(self.avisos)


def diagnostico(
    resultado: Diagnostico,
    *,
    catalogo_versao: int,
    gerado_em: str,
    hash_completo: str,
) -> VisaoDiagnostico:
    linhas = [_linha(p) for p in resultado.problemas]
    return VisaoDiagnostico(
        fonte=resultado.fonte,
        erros=tuple(linha for linha in linhas if linha.severidade == Severidade.ERRO.value),
        avisos=tuple(linha for linha in linhas if linha.severidade == Severidade.AVISO.value),
        lock_desatualizado=resultado.lock_desatualizado,
        catalogo_versao=catalogo_versao,
        gerado_em=gerado_em,
        hash_curto=hash_completo[7:19] if hash_completo else "",
    )


def _linha(problema: Problema) -> Linha:
    regra, secao = SECAO_DO_CODIGO.get(problema.codigo, ("", ""))
    local = problema.arquivo or ""
    if local and problema.linha:
        local = f"{local}:{problema.linha}"
    return Linha(
        codigo=problema.codigo.value,
        regra=regra,
        secao=secao,
        severidade=problema.severidade.value,
        mensagem=problema.mensagem,
        entidade=problema.entidade or "",
        href=_href(problema.entidade),
        local=local,
    )


def _href(entidade: str | None) -> str:
    if not entidade or ":" not in entidade:
        return ""
    tipo = entidade.split(":", 1)[0]
    return {
        "trilha": f"/trilha/{entidade}",
        "etapa": f"/etapa/{entidade}",
        "comp": f"/competencia/{entidade}",
    }.get(tipo, "")
