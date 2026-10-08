# Documentação

| Documento | Conteúdo |
|---|---|
| [CONTEXT.md](CONTEXT.md) | Glossário, entidades, relações e invariantes do domínio |
| [motor-de-sugestao.md](motor-de-sugestao.md) | Especificação do motor de sugestão (v1) |
| [catalogo.md](catalogo.md) | Autoria, identidade e versionamento do catálogo |

## Decisões (ADR)

| # | Decisão | Status |
|---|---|---|
| [0001](adr/0001-modelar-dominio-antes-da-stack.md) | Modelar o domínio antes de escolher a stack | aceito |
| [0002](adr/0002-trilha-como-grafo-de-etapas.md) | Trilha é um grafo de etapas com pré-requisitos por competência | aceito |
| [0003](adr/0003-motor-de-sugestao-por-regras-explicavel.md) | Motor de sugestão por regras com score explicável (v1) | aceito |
| [0004](adr/0004-catalogo-em-yaml-compilado-para-snapshot.md) | Catálogo autorado em YAML, compilado para um snapshot validado | aceito |
| [0005](adr/0005-identidade-imutavel-e-depreciacao.md) | Identidade imutável, revisão por entidade e depreciação em vez de remoção | aceito |

## Pendente de decisão

- Stack de implementação (linguagem, persistência, camada de entrega) — ver [ADR-0001](adr/0001-modelar-dominio-antes-da-stack.md).
- Calibração dos pesos dos fatores de score — ver [ADR-0003](adr/0003-motor-de-sugestao-por-regras-explicavel.md).
- Catálogo-fixture canônico dos cenários de teste do motor — ver [catalogo.md §7](catalogo.md).

## Ordem de construção implicada

1. Compilador/validador de catálogo ([ADR-0004](adr/0004-catalogo-em-yaml-compilado-para-snapshot.md)) — o motor não tem entrada sem ele.
2. Catálogo-fixture e os 7 cenários de [motor §5](motor-de-sugestao.md).
3. Motor de sugestão como lógica pura.
4. Persistência de percurso e camada de entrega (depende da stack).
