# Projeto no claude.ai

Um Projeto no [claude.ai](https://claude.ai) com este repositório como conhecimento:
serve para conversar sobre o domínio, autorar catálogo e — enquanto não há como
chamar o motor pela interface — responder "o que eu estudo agora?" seguindo a
especificação em vez da intuição.

| Arquivo | O que é |
|---|---|
| [instrucoes.md](instrucoes.md) | instruções do projeto, para colar em Projeto → Instruções |
| [montar.sh](montar.sh) | gera `conhecimento/` a partir dos docs, do catálogo e do código |
| `conhecimento/` | derivado, não versionado — some e volta com `montar.sh` |

O conhecimento é **derivado do repositório**, como o `catalogo.lock.json`: a fonte da
verdade continua em `docs/`, `catalogo/` e `src/`. Não edite `conhecimento/` à mão —
a edição se perde na próxima montagem e cria uma segunda fonte da verdade, o que este
projeto evita de propósito ([docs/catalogo.md §8](../docs/catalogo.md)).

## Criar

```bash
./claude-project/montar.sh
```

1. No claude.ai, **Projects → Create project**, nome `trilhas_estudos`.
2. **Instruções**: cole o conteúdo de [instrucoes.md](instrucoes.md) a partir da
   linha `---` (o comentário do topo é para você, não para o Claude).
3. **Conhecimento**: suba todos os arquivos de `claude-project/conhecimento/`.

## Atualizar

Depois de mexer em `docs/`, `catalogo/`, `percurso/` ou `src/`:

```bash
./claude-project/montar.sh
```

e substitua no conhecimento do projeto os arquivos que mudaram — na prática,
`catalogo-autorado.md` a cada trilha nova, `percurso.md` a cada avanço de estudo,
`estado-do-codigo.md` a cada capacidade entregue. Documento novo em `docs/` entra
no bundle sozinho, com o nome do arquivo: confira a listagem que a montagem imprime
e suba o que apareceu.

Vale repetir a montagem sempre que uma conversa no projeto citar algo que já não é
verdade: o bundle é o retrato de um commit, e `estado-do-codigo.md` registra qual —
inclusive a ordem de construção, extraída de [docs/README.md](../docs/README.md),
que é onde o estado do projeto se mantém.
