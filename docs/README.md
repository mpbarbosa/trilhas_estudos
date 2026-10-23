# Documentação

| Documento | Conteúdo |
|---|---|
| [CONTEXT.md](CONTEXT.md) | Glossário, entidades, relações e invariantes do domínio |
| [motor-de-sugestao.md](motor-de-sugestao.md) | Especificação do motor de sugestão (v1) |
| [catalogo.md](catalogo.md) | Autoria, identidade e versionamento do catálogo |
| [interface.md](interface.md) | Plano da interface gráfica: stack, entidades de leitura e telas |
| [bibliografia.md](bibliografia.md) | Ficha bibliográfica de cada livro citado pelo catálogo |
| [acervo-lido.md](acervo-lido.md) | Cruzamento datado entre a estante lida do estudante e o catálogo |
| [estante-goodreads.md](estante-goodreads.md) | Extração datada da estante lida do estudante, fonte do cruzamento |

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
| [0008](adr/0008-percurso-como-log-de-fatos-datados.md) | Percurso como log append-only de fatos datados, perfil derivado | aceito |
| [0009](adr/0009-obra-como-campo-de-agrupamento-no-recurso.md) | Obra como campo de agrupamento no recurso, não como entidade | aceito |
| [0010](adr/0010-shell-como-pre-requisito-declarado.md) | Shell como pré-requisito declarado, em etapa avulsa compartilhada | aceito |
| [0011](adr/0011-python-no-servidor-como-ramo-da-trilha-web.md) | Python no servidor como ramo opcional da trilha web | aceito |
| [0012](adr/0012-fato-de-recurso-no-percurso.md) | Percurso registra fato de recurso; posse fica fora do log | aceito |
| [0013](adr/0013-hospedagem-do-modelo-como-ramo-da-trilha-de-claude.md) | Hospedagem do modelo como ramo opcional da trilha de Claude | aceito |
| [0014](adr/0014-retratacao-de-evidencia-por-seq.md) | Retratação de evidência como fato novo, endereçada pelo `seq` do log | aceito |
| [0015](adr/0015-posse-de-exemplar-como-estante-declarada.md) | Posse de exemplar como estante declarada no perfil, aplicada ao custo efetivo | aceito |
| [0016](adr/0016-retratacao-pela-tela-da-competencia.md) | Retratação pela tela da competência, com a evidência lida do log | aceito |
| [0017](adr/0017-trilha-de-emulador-sem-linguagem-declarada.md) | Emulador de terminal em área própria, sem linguagem de implementação nos `requires` | aceito |
| [0018](adr/0018-programacao-de-sistemas-como-pre-requisito-compartilhado.md) | Programação de sistemas como pré-requisito compartilhado, em terceira etapa avulsa | aceito |

## Pendente

Nada no momento. O gate de verificação que vários documentos tratam como garantia
roda em CI, em [.github/workflows/verificar.yml](../.github/workflows/verificar.yml):
`trilhas compilar --conferir`, `pytest`, `ruff check`, `ruff format --check` e
`mypy --strict`, a cada push em `main` e a cada pull request.

## Pendente de decisão

- Calibração dos pesos dos fatores de score — ver [ADR-0003](adr/0003-motor-de-sugestao-por-regras-explicavel.md).

## Ordem de construção implicada

1. ~~Compilador/validador de catálogo~~ — feito, em `src/trilhas/catalogo/` ([catalogo.md §7](catalogo.md)).
2. ~~Catálogo-fixture~~ — feito, em `tests/fixtures/catalogo_exemplo/`.
3. ~~Motor de sugestão como lógica pura~~ — feito, em `src/trilhas/motor/`, com os 7 cenários de [motor §5](motor-de-sugestao.md).
4. ~~Persistência de percurso~~ — feita, em `src/trilhas/percurso/`: log append-only em
   SQLite, com `UPDATE` e `DELETE` proibidos por trigger, projeção pura e CLI
   `trilhas-percurso` ([ADR-0008](adr/0008-percurso-como-log-de-fatos-datados.md)). O
   banco é local e fica fora do git; o histórico durável é a exportação em JSONL.
5. **Camada de entrega** — em `src/trilhas/web/`
   ([ADR-0007](adr/0007-entrega-web-em-python-html-no-servidor.md)). ← em construção

   De pé: painel *Agora* com os fatores à vista, grafo da trilha, etapa, competência,
   explorador e diagnóstico do catálogo, índice e página da obra com exportação em
   Markdown ([interface.md §5.13](interface.md)) — e a escrita de percurso pela própria
   tela, que dependia de 4: iniciar, concluir e abandonar etapa, autoavaliar competência
   e retratar evidência ([interface.md §5.10 a §5.12](interface.md)).
6. O que falta da interface, na ordem em que [interface.md §5](interface.md) as descreve:
   `/perfil` (§5.5), `/catalogo/autoria` como gerador de diff de YAML (§5.7) e
   `/sugestao/{id}` com os candidatos eliminados e o motivo de cada eliminação (§5.8).
