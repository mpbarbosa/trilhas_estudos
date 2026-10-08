# trilhas_estudos

Controle e sugestão de trilhas de estudo: acompanha o avanço do estudante numa
trilha e recomenda o que estudar em seguida.

**Estado atual:** domínio modelado e catálogo validável. O motor de sugestão ainda
não foi implementado.

- [Domínio e glossário](docs/CONTEXT.md)
- [Motor de sugestão (v1)](docs/motor-de-sugestao.md) — primeira capacidade a construir
- [Catálogo](docs/catalogo.md) — autoria em YAML, identidade e versionamento
- [Conteúdo do catálogo](catalogo/) — trilhas autoradas:
  - *Do transformer ao RAG em produção* ([trilha](catalogo/trilhas/llm-transformer-rag.yaml)) — fundamento e recuperação
  - *Do chat ao agente em produção com Claude* ([trilha](catalogo/trilhas/claude-do-chat-ao-agente.yaml)) — aplicação: API, ferramentas, MCP e agentes
  - *Análise de dados com Python* ([trilha](catalogo/trilhas/dados-com-python.yaml)) — manipulação, exploração, estatística e enquadramento
- [Decisões de arquitetura](docs/README.md)

## Uso

Requer Python 3.12+. O catálogo é autorado em `catalogo/` e compilado para
`catalogo.lock.json`, o único artefato que a aplicação consome.

```bash
uv run trilhas validar              # valida o catálogo (0 = válido, 1 = com erro)
uv run trilhas compilar             # grava o snapshot se o conteúdo mudou
uv run pytest                       # 46 testes
```

## Licença

MIT — ver [LICENSE](LICENSE).
