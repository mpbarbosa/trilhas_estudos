# trilhas_estudos

Controle e sugestão de trilhas de estudo: acompanha o avanço do estudante numa
trilha e recomenda o que estudar em seguida.

**Estado atual: modelagem.** Ainda não há código nem stack escolhida — a decisão de
começar pelo domínio está em [ADR-0001](docs/adr/0001-modelar-dominio-antes-da-stack.md).

- [Domínio e glossário](docs/CONTEXT.md)
- [Motor de sugestão (v1)](docs/motor-de-sugestao.md) — primeira capacidade a construir
- [Catálogo](docs/catalogo.md) — autoria em YAML, identidade e versionamento
- [Conteúdo do catálogo](catalogo/) — trilhas autoradas:
  - *Do transformer ao RAG em produção* ([trilha](catalogo/trilhas/llm-transformer-rag.yaml)) — fundamento e recuperação
  - *Do chat ao agente em produção com Claude* ([trilha](catalogo/trilhas/claude-do-chat-ao-agente.yaml)) — aplicação: API, ferramentas, MCP e agentes
- [Decisões de arquitetura](docs/README.md)

## Licença

MIT — ver [LICENSE](LICENSE).
