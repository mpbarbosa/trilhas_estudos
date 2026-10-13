---
description: Roda a verificação completa (catálogo, testes, lint, tipos) e reporta o que falhou
allowed-tools: Bash(uv run:*), Bash(git status:*), Bash(git diff:*)
---

O CI roda este mesmo gate (`.github/workflows/verificar.yml`), mas só depois do push:
aqui é onde a mudança se prova antes de virar commit. Rode os quatro passos, **todos**,
mesmo que um falhe antes:

```bash
uv run trilhas compilar --conferir
uv run pytest
uv run ruff check . && uv run ruff format --check .
uv run mypy
```

Depois reporte, em pt-BR e sem rodeios:

- uma linha por passo com o veredito e, se falhou, a mensagem relevante (não o traceback inteiro);
- se `compilar --conferir` falhou por snapshot desatualizado, diga que basta
  `uv run trilhas compilar` e commitar o lock junto do YAML;
- avisos do validador (recurso verificado há mais de 180 dias, etapa órfã) listados
  separadamente dos erros — não bloqueiam, mas contam;
- se tudo passou, diga isso em uma linha e pare. Não proponha melhorias que ninguém pediu.

Não corrija nada sem que eu peça: este comando diagnostica.
