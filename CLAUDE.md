# trilhas_estudos — instruções para o Claude Code

Controle e sugestão de trilhas de estudo. **Escreva, comente e nomeie em pt-BR**,
inclusive identificadores de código — é a convenção do repositório (`carregar`,
`validar`, `compilar`, `Problema`, `Severidade`).

## Leia antes de mexer

| Arquivo | Quando |
|---|---|
| [docs/CONTEXT.md](docs/CONTEXT.md) | sempre: glossário, entidades, invariantes |
| [docs/catalogo.md](docs/catalogo.md) | ao tocar em `catalogo/` ou em `src/trilhas/catalogo/` |
| [docs/motor-de-sugestao.md](docs/motor-de-sugestao.md) | ao mexer no motor: contrato, fatores e casos de borda |
| [docs/README.md](docs/README.md) | índice de ADRs e ordem de construção |

O glossário de CONTEXT.md §1 é a **linguagem única**: use `Competência`, `Etapa`,
`Recurso`, `Trilha`, `Evidência`, `Progresso`, `Sugestão`. Não introduza "curso",
"módulo", "aula", "lição" ou "tarefa" — foram descartados por ambiguidade.

## Comandos

```bash
uv run trilhas validar              # valida o catálogo; 0 = válido, 1 = com erro
uv run trilhas compilar             # grava catalogo.lock.json se o conteúdo mudou
uv run trilhas compilar --conferir  # não grava; falha se o snapshot está desatualizado
uv run pytest                       # suíte completa
uv run ruff check . && uv run ruff format --check .
uv run mypy                         # --strict sobre src/trilhas (configurado em pyproject)
```

Antes de considerar uma mudança pronta: `validar` (ou `compilar`), `pytest`, `ruff`,
`mypy`. O mesmo gate roda em CI
([.github/workflows/verificar.yml](.github/workflows/verificar.yml)) a cada push em
`main` e a cada pull request, com `--all-extras`; rodar antes de commitar continua
sendo o caminho curto, porque o CI só confirma.

## Estrutura

```
catalogo/            autoria em YAML — fonte da verdade (competencias/ trilhas/ etapas/ recursos/)
catalogo.lock.json   GERADO por `trilhas compilar`. Nunca editar à mão.
percurso/            estado por estudante. Formato provisório, nenhuma ADR o decidiu.
src/trilhas/catalogo/  carregar → validar → compilar; cli.py é a interface de CI
src/trilhas/motor/     sugerir: candidatos → filtros → fatores → top-N (lógica pura)
tests/fixtures/catalogo_exemplo/  catálogo-fixture dos cenários do motor
docs/                CONTEXT, especificações e ADRs
```

## Regras duras

1. **`catalogo.lock.json` é gerado.** Mudança de conteúdo se faz no YAML e se
   propaga com `trilhas compilar`. Commite o lock junto com o YAML que o gerou.
2. **Id de catálogo é imutável e nunca reaproveitado** — formato `<tipo>:<area>/<slug>`,
   minúsculas, dígitos e hífen. Corrigir um slug = criar outra entidade e depreciar a
   anterior com `substituido_por`. Nada é removido do catálogo (docs/catalogo.md §3 e §6).
3. **`rev` sobe só em mudança substantiva**, pela tabela de docs/catalogo.md §4.
   `titulo`, `descricao`, `url` equivalente e `verificado_em` são cosméticos.
4. **Domínio puro**: nenhum módulo em `src/trilhas/` abaixo de `cli.py` faz I/O,
   rede ou leitura de ambiente. `validar` é função pura. Modelo em `dataclasses`
   congeladas (ADR-0006).
5. **Sugestão é explicável por construção** — nenhuma sugestão sem os fatores que a
   produziram, e a explicação nunca cita fator ausente de `fatores` (ADR-0003,
   motor §2.5).
6. **Fato datado não retroage**: mudar o catálogo não recalcula evidência nem
   progresso já gravados (docs/catalogo.md §4).
7. **Decisão estrutural vira ADR** em `docs/adr/`, no formato dos existentes
   (Contexto / Decisão / Consequências), e entra na tabela de docs/README.md.
   Não altere uma ADR aceita para mudar de rumo: escreva a seguinte, ou uma
   "Nota de correção" como em ADR-0006.

## Catálogo atual

Não confie em contagem escrita aqui — ela envelhece a cada trilha nova. Consulte:

```bash
python3 -c 'import json;d=json.load(open("catalogo.lock.json"));print(d["catalogo_versao"],{k:len(d[k]) for k in ("trilhas","competencias","etapas","recursos")});[print(t["id"],t["titulo"]) for t in d["trilhas"]]'
```

O estado do projeto — o que está construído e o que vem a seguir — se mantém na
seção *Ordem de construção implicada* de [docs/README.md](docs/README.md).

## Autoria de trilha

Procedimento em [.claude/skills/autorar-catalogo/SKILL.md](.claude/skills/autorar-catalogo/SKILL.md).
Em resumo: etapas moram no arquivo da trilha que as introduz; recursos ficam em
`catalogo/recursos/<area>.yaml` por terem ciclo de vida próprio; outras trilhas
referenciam etapas por id em `etapas_referenciadas`, nunca redefinem.

## Git

Outras sessões commitam neste repositório em paralelo. Confira `git status` e
`git log` antes de escrever, e commite só o que você mudou: pode haver trabalho
não commitado de outra sessão na árvore.

Commits em pt-BR, no imperativo ou no padrão `catalogo: trilha "<título>"` usado
no histórico.

**O checkout é compartilhado, e isso inverte boa parte da intuição sobre git.**
O procedimento está em
[.claude/skills/encerrar-branch/SKILL.md](.claude/skills/encerrar-branch/SKILL.md):
cinco armadilhas observadas aqui, entre elas `git branch -d` aceitar apagar o que
só existe no `origin`, `git stash` tirar da árvore a edição ao vivo de outra
sessão, e o branch em `HEAD` mudar entre dois comandos seus.

Antes de apagar branch ou trocar de branch, rode o diagnóstico — ele só lê:

```bash
scripts/conferir-branch.sh [branch]   # 0 = pode apagar o local; 1 = não pode
```

Duas regras que valem mesmo sem ler a skill:

1. **Guarda de branch que funciona compara o valor.** `git branch --show-current &&`
   sai com 0 sempre e não aborta nada:
   `[ "$(git branch --show-current)" = main ] && git add CAMINHO && git commit -m "…"`
2. **Um branch mora em três lugares** — local, servidor e ref de rastreio — e
   apagar num não apaga nos outros. Quem decide se o remoto existe é
   `git ls-remote`, não `git branch -r`.
