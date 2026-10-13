# Documentação

| Documento | Conteúdo |
|---|---|
| [CONTEXT.md](CONTEXT.md) | Glossário, entidades, relações e invariantes do domínio |
| [motor-de-sugestao.md](motor-de-sugestao.md) | Especificação do motor de sugestão (v1) |
| [catalogo.md](catalogo.md) | Autoria, identidade e versionamento do catálogo |
| [interface.md](interface.md) | Plano da interface gráfica: stack, entidades de leitura e telas |

## Decisões (ADR)

| # | Decisão | Status |
|---|---|---|
| [0001](adr/0001-modelar-dominio-antes-da-stack.md) | Modelar o domínio antes de escolher a stack | aceito |
| [0002](adr/0002-trilha-como-grafo-de-etapas.md) | Trilha é um grafo de etapas com pré-requisitos por competência | aceito |
| [0003](adr/0003-motor-de-sugestao-por-regras-explicavel.md) | Motor de sugestão por regras com score explicável (v1) | aceito |
| [0004](adr/0004-catalogo-em-yaml-compilado-para-snapshot.md) | Catálogo autorado em YAML, compilado para um snapshot validado | aceito |
| [0005](adr/0005-identidade-imutavel-e-depreciacao.md) | Identidade imutável, revisão por entidade e depreciação em vez de remoção | aceito |
| [0006](adr/0006-stack-python.md) | Stack: Python, domínio puro, CLI como primeira entrega | aceito |
| [0007](adr/0007-entrega-web-em-python-html-no-servidor.md) | Camada de entrega web em Python, HTML no servidor | aceito |

## Pendente

- Workflow de CI que rode `trilhas compilar --conferir`, `pytest`, `ruff` e
  `mypy --strict` — vários documentos tratam a detecção em CI como garantia, e ela
  ainda depende de execução manual.

## Pendente de decisão

- Calibração dos pesos dos fatores de score — ver [ADR-0003](adr/0003-motor-de-sugestao-por-regras-explicavel.md).

## Ordem de construção implicada

1. ~~Compilador/validador de catálogo~~ — feito, em `src/trilhas/catalogo/` ([catalogo.md §7](catalogo.md)).
2. ~~Catálogo-fixture~~ — feito, em `tests/fixtures/catalogo_exemplo/`.
3. ~~Motor de sugestão como lógica pura~~ — feito, em `src/trilhas/motor/`, com os 7 cenários de [motor §5](motor-de-sugestao.md).
4. **Persistência de percurso.** ← próximo
5. Camada de entrega — fase 1 (explorador de catálogo, somente leitura) feita, em
   `src/trilhas/web/` ([interface.md §10](interface.md)); as fases seguintes dependem
   de 4.
