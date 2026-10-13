# trilhas_estudos

Controle e sugestão de trilhas de estudo: acompanha o avanço do estudante numa
trilha e recomenda o que estudar em seguida.

**Estado atual:** domínio modelado, catálogo validável, motor de sugestão implementado
como lógica pura (`src/trilhas/motor/`) e uma interface de leitura. O painel *Agora*
já mostra as sugestões do motor com os fatores que as produziram; o que ainda não há é
persistência do percurso — nada do que o estudante faz é gravado.

- [Domínio e glossário](docs/CONTEXT.md)
- [Motor de sugestão (v1)](docs/motor-de-sugestao.md) — especificação e escolhas da implementação
- [Interface gráfica](docs/interface.md) — stack, telas e fases; a fase 1 está no ar
- [Catálogo](docs/catalogo.md) — autoria em YAML, identidade e versionamento
- [Conteúdo do catálogo](catalogo/) — trilhas autoradas:
  - *Do transformer ao RAG em produção* ([trilha](catalogo/trilhas/llm-transformer-rag.yaml)) — fundamento e recuperação
  - *Do chat ao agente em produção com Claude* ([trilha](catalogo/trilhas/claude-do-chat-ao-agente.yaml)) — aplicação: API, ferramentas, MCP e agentes
  - *Análise de dados com Python* ([trilha](catalogo/trilhas/dados-com-python.yaml)) — manipulação, exploração, estatística e enquadramento
  - *Web, do protocolo à interface* ([trilha](catalogo/trilhas/web-do-protocolo-a-interface.yaml)) — HTTP, documento, JavaScript, tipos e componentes
  - *Arquitetura e entrega de software* ([trilha](catalogo/trilhas/arquitetura-e-entrega.yaml)) — requisitos, trade-off, decomposição, pipeline e operação
  - *Matemática — da demonstração ao cálculo* ([trilha](catalogo/trilhas/matematica-prova-e-calculo.yaml)) — prova, geometria axiomática, cálculo e simetria
  - *Sistemas operacionais, do conceito ao núcleo* ([trilha](catalogo/trilhas/so-projeto-e-implementacao.yaml)) — processos, memória, E/S, arquivos e prática no MINIX
- [Decisões de arquitetura](docs/README.md)

## Uso

Requer Python 3.12+. O catálogo é autorado em `catalogo/` e compilado para
`catalogo.lock.json`, o único artefato que a aplicação consome.

```bash
uv run trilhas validar              # valida o catálogo (0 = válido, 1 = com erro)
uv run trilhas compilar             # grava o snapshot se o conteúdo mudou
uv run --extra dev pytest           # suíte completa
```

### Interface

Em `localhost`: o painel *Agora* com as sugestões do motor e os fatores que as
produziram, o grafo da trilha por onda de pré-requisito, a etapa com os recursos
comparados, a competência com o critério de verificação, e as 11 validações numa
tela ([docs/interface.md](docs/interface.md)).

```bash
uv run --extra web trilhas-web      # http://127.0.0.1:8000
```

Somente leitura: registrar progresso, evidência e feedback depende da decisão de
persistência do percurso.

## Licença

MIT — ver [LICENSE](LICENSE).
