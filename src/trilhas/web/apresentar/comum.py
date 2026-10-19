"""Rótulos e formatação. O vocabulário da tela, num lugar só.

O domínio usa tokens sem acento (`intermediario`, `video`) porque são identificadores
(docs/catalogo.md §3). A tela mostra pt-BR escrito corretamente. A tradução é aqui, e
não espalhada em template.
"""

from __future__ import annotations

from datetime import date

from ...catalogo.modelo import Catalogo, Formato, Nivel, Status
from ...motor.modelo import EstadoEtapa
from ...percurso.eventos import Origem

ROTULO_NIVEL = {
    Nivel.DESCONHECE: "desconhece",
    Nivel.INICIANTE: "iniciante",
    Nivel.INTERMEDIARIO: "intermediário",
    Nivel.AVANCADO: "avançado",
}

ROTULO_FORMATO = {
    Formato.VIDEO: "vídeo",
    Formato.TEXTO: "texto",
    Formato.EXERCICIO: "exercício",
    Formato.PROJETO: "projeto",
}

ROTULO_STATUS = {
    Status.RASCUNHO: "rascunho",
    Status.ATIVO: "ativo",
    Status.DEPRECIADO: "depreciado",
}

ROTULO_ESTADO = {
    EstadoEtapa.NAO_INICIADA: "não iniciada",
    EstadoEtapa.EM_ANDAMENTO: "em andamento",
    EstadoEtapa.CONCLUIDA: "concluída",
    EstadoEtapa.ABANDONADA: "abandonada",
}

ROTULO_ORIGEM = {
    Origem.CONCLUSAO_DE_ETAPA: "conclusão de etapa",
    Origem.AUTOAVALIACAO: "autoavaliação",
}
"""De onde veio a evidência. Pesa na confiança (CONTEXT §1), e por isso a tela a diz
por extenso em vez de mostrar o token."""

ROTULO_TIPO = {
    "trilha": "trilha",
    "etapa": "etapa",
    "comp": "competência",
    "rec": "recurso",
}

ROTULO_TIPO_PLURAL = {
    "trilha": "trilhas",
    "etapa": "etapas",
    "comp": "competências",
    "rec": "recursos",
}

DIAS_ATE_REVERIFICAR = 180


def nivel(valor: Nivel) -> str:
    return ROTULO_NIVEL[valor]


def formato(valor: Formato) -> str:
    return ROTULO_FORMATO[valor]


def estado_de_etapa(valor: EstadoEtapa) -> str:
    return ROTULO_ESTADO[valor]


def duracao(minutos: int) -> str:
    """`90` → `1 h 30 min`. Esforço de etapa chega a 900 minutos: minuto cru não comunica."""
    if minutos <= 0:
        return "—"
    if minutos < 60:
        return f"{minutos} min"
    horas, resto = divmod(minutos, 60)
    if resto == 0:
        return f"{horas} h"
    return f"{horas} h {resto} min"


def dinheiro(custo: float) -> str:
    if custo <= 0:
        return "grátis"
    if custo == int(custo):
        return f"R$ {int(custo)}"
    return f"R$ {custo:.2f}".replace(".", ",")


def tipo_do_id(ident: str) -> str:
    return ident.split(":", 1)[0] if ":" in ident else ""


def area_do_id(ident: str) -> str:
    resto = ident.split(":", 1)[-1]
    return resto.split("/", 1)[0] if "/" in resto else ""


def titulo_de(catalogo: Catalogo, ident: str) -> str:
    """Título de qualquer entidade por id; o próprio id quando não resolve.

    Referência quebrada é erro de catálogo (validação §5.2) e não deve derrubar a
    tela — ela aparece como id cru, que é exatamente o que o autor precisa ver.
    """
    entidade = catalogo.por_id().get(ident)
    return entidade.titulo if entidade is not None else ident


def dias_desde(quando: date | None, hoje: date) -> int | None:
    return None if quando is None else (hoje - quando).days


def vencido(verificado_em: date | None, hoje: date) -> bool:
    """Recurso sem verificação há mais de 180 dias — o aviso CAT-100, visível a quem estuda."""
    dias = dias_desde(verificado_em, hoje)
    return dias is None or dias > DIAS_ATE_REVERIFICAR


def quebrar(texto: str, largura: int = 26, linhas: int = 2) -> tuple[str, ...]:
    """Quebra um título em até `linhas` linhas de ~`largura` caracteres, com elipse.

    SVG não quebra texto sozinho: quem desenha o nó precisa das linhas prontas.
    """
    palavras = texto.split()
    saida: list[str] = []
    atual = ""
    for palavra in palavras:
        candidato = f"{atual} {palavra}".strip()
        if len(candidato) <= largura or not atual:
            atual = candidato
            continue
        saida.append(atual)
        atual = palavra
        if len(saida) == linhas:
            break
    if atual and len(saida) < linhas:
        saida.append(atual)
    if not saida:
        return ("",)
    consumido = sum(len(linha.split()) for linha in saida)
    if consumido < len(palavras):
        ultima = saida[-1]
        saida[-1] = ultima[: max(0, largura - 1)].rstrip() + "…"
    return tuple(saida)
