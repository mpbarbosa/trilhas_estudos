---
name: rodar-app
description: Procedimento para subir e dirigir a interface web de trilhas_estudos (`trilhas-web`) e a CLI (`trilhas`) — qual entrypoint é "o app", como montar a URL de uma entidade, e os três modos de falha que não são bug seu. Use ao rodar, iniciar ou tirar screenshot do app, ao conferir no navegador que uma mudança funciona, ou quando o servidor não sobe.
---

# Rodar o app

Dois entrypoints, declarados em `pyproject.toml`:

| Entrypoint | O que é | Quando |
|---|---|---|
| `trilhas-web` | interface web (Starlette + uvicorn, ADR-0007) | **é "o app"** — pedido de rodar/ver/screenshot cai aqui |
| `trilhas` | CLI do catálogo (`validar`, `compilar`) | verificação e CI; veja `/verificar` |

A interface é **só-leitura sobre `catalogo.lock.json`** (ADR-0004): ela nunca lê o
YAML de autoria. Exceção única é `/catalogo/diagnostico`, que compara autoria e
snapshot justamente para dizer o que a CLI diria (docs/interface.md §5.6).

## 1. Antes de subir: a árvore roda?

Outras sessões commitam neste mesmo checkout (CLAUDE.md §Git). Um merge por
resolver deixa marcador de conflito **dentro do `.py`**, e o app morre assim:

```
File "src/trilhas/catalogo/validar.py", line 221
    <<<<<<< HEAD
SyntaxError: invalid syntax
```

Isso **não é bug do seu código**. Cheque `git status` e `.git/MERGE_HEAD` antes de
investigar. `scripts/fumaca-web.sh` já faz essa checagem e falha com a lista de
arquivos conflitados — rode-o primeiro e economize a caçada.

Um lock conflitado dá a mesma classe de erro mais tarde, em JSON: sem snapshot
válido não há app. `uv run trilhas compilar` regenera.

## 2. Subir

Há `.claude/launch.json` com a configuração `trilhas-web` na porta **8042**. Use a
ferramenta de preview com `name: "trilhas-web"` — **nunca** `uv run ... &` pelo
Bash para servidor de desenvolvimento.

Fora do harness, ou para smoke test:

```bash
scripts/abrir-app.sh             # sobe e abre no navegador; Ctrl-C derruba
scripts/abrir-app.sh --rota /catalogo/diagnostico   # abre numa rota
scripts/fumaca-web.sh            # sobe, exercita todas as rotas, derruba; 0 = verde
scripts/fumaca-web.sh --manter   # deixa de pé para você navegar
uv run --extra web trilhas-web --porta 8042   # manual
```

`abrir-app.sh` é para **olhar** o app: faz as mesmas checagens de árvore e de
snapshot do smoke test, espera o servidor responder antes de chamar o navegador,
e reaproveita um servidor que já esteja na porta em vez de falhar.

O extra `web` não é instalado por padrão. Sem ele o `trilhas-web` avisa e sai 1 —
não é falha de ambiente, é `uv run --extra web` faltando.

Só escuta em `127.0.0.1`. Expor em rede exige ADR nova; não passe `--host`.

## 3. Dirigir

Rotas reais (`src/trilhas/web/rotas.py`):

```
/                              acervo: trilhas, números do catálogo
/catalogo                      lista todas as entidades, com filtros
/catalogo/diagnostico          as 11 validações, como a CLI as diria
/trilha/{id}  /etapa/{id}  /competencia/{id}
```

**A URL de uma entidade leva o id inteiro, prefixo incluído.** O id já começa com o
tipo, então o tipo aparece duas vezes:

```
✅ /trilha/trilha:matematica/prova-e-calculo
❌ /trilha/matematica/prova-e-calculo        → página "Não encontrado"
```

Errar isso devolve a 404 tratada, não um erro — e ela se parece com "a entidade
sumiu do catálogo", que é a conclusão errada. **Não monte a URL de cabeça**: pegue o
href da página inicial, ou tire o id de `catalogo.lock.json`.

Prefira `read_page`/`get_page_text` a screenshot para conferir texto e estrutura.
Screenshot serve para o que é visual — o grafo de pré-requisitos, sobretudo.

## 4. Ao mudar código

O servidor não recarrega sozinho: ele segue servindo o código que carregou ao subir.
Depois de editar `src/trilhas/web/`, **derrube e suba de novo** — senão você confere
a versão antiga e conclui que a mudança não funcionou.

Mudou o catálogo? `uv run trilhas compilar` antes de reiniciar: a interface lê o
lock, e sem recompilar o YAML novo não aparece.

## 5. Ruído conhecido

`GET /favicon.ico 404` em toda página. Não há favicon; é esperado e não é regressão.
É o único erro de console numa execução sadia — qualquer outro merece atenção.
