"""Catálogo: carregar YAML, validar e compilar o snapshot.

Fluxo em três passos, conforme docs/catalogo.md:

    carregar  ->  validar  ->  compilar

Nenhum módulo deste pacote, exceto `cli` e `carregar`, toca o sistema de arquivos.
"""
