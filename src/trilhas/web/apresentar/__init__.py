"""Projeções de tela — funções puras, testáveis sem servidor (docs/interface.md §3.3).

Entra modelo de domínio, sai dado já formatado para o template. Nada aqui lê arquivo,
e nada aqui decide regra de domínio: o fecho progressivo e as arestas derivadas vêm
prontos de `trilhas.catalogo.grafo`.
"""
