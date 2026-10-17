"""Desligamento do servidor local, pedido pela própria tela.

A interface roda em `localhost`, para um estudante, e quem a sobe pelo navegador não
tem terminal à mão para dar Ctrl-C (docs/interface.md §0). O botão "Desligar" fecha o
servidor pelo caminho que o uvicorn já conhece: `SIGINT` no próprio processo, que
dispara o encerramento graciosos — a resposta em curso termina antes de a porta cair.

Mora fora de `rotas.py` por ser o único ponto da camada web que toca o processo: a rota
recebe a função pelo `Contexto` e o teste injeta outra, sem matar o pytest.
"""

from __future__ import annotations

import os
import signal


def encerrar_processo() -> None:
    """Pede o encerramento gracioso do servidor que serve esta tela."""
    os.kill(os.getpid(), signal.SIGINT)
