"""Camada de entrega web (ADR-0007).

Segunda borda de I/O do projeto, ao lado de `catalogo/cli.py`: aqui se lê arquivo e
se responde HTTP. Nada abaixo destas bordas faz I/O.

Dentro do pacote, `apresentar/` é puro de propósito — é onde mora a lógica de tela, e
é testável sem subir servidor. Regra que o sustenta (docs/interface.md §3.3): **a
interface não calcula domínio**. Fecho progressivo, arestas derivadas e níveis vêm de
`trilhas.catalogo`; os templates apenas formatam.
"""
