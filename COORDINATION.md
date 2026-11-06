# Coordenação entre sessões

Várias sessões escrevem neste repositório ao mesmo tempo, no **mesmo checkout**
(CLAUDE.md §Git). O git registra o que **mudou**; ele não registra o que alguém
**está a ponto de mudar**. Essa é a única informação que mora aqui: a
reivindicação de área. Todo o resto é link.

## Onde cada pergunta se responde

| Pergunta | Onde |
|---|---|
| Quem está mexendo em quê agora? | **aqui**, §Reivindicações ativas |
| Que branches existem, local, remoto e ref de rastreio? | `git branch -vv`, `git ls-remote --heads origin`, `git branch -r` |
| Posso apagar este branch? Posso trocar de branch? | `scripts/conferir-branch.sh [branch]` — só lê; 0 = pode |
| Como fechar, publicar ou mesclar um branch sem destruir trabalho alheio? | [.claude/skills/encerrar-branch/SKILL.md](.claude/skills/encerrar-branch/SKILL.md) |
| O que está construído e o que vem a seguir? | [docs/README.md](docs/README.md) §Ordem de construção implicada |
| A mudança está pronta? | CLAUDE.md §Comandos — `validar`, `pytest`, `ruff`, `mypy` |

Não copie nada dessas fontes para cá. Contagem de branch, lista de PR e estado
de teste envelhecem em minutos, e um resumo desatualizado aqui contradiz a fonte
**em segredo**: ninguém relê este arquivo procurando divergência.

## Regras duras

1. **Reivindique antes de escrever.** Uma linha em §Reivindicações ativas, com o
   branch ou worktree, a área de arquivos e o que conta como terminado. Antes de
   editar, leia a tabela.
2. **Dois escritores nunca na mesma área.** Se a área já tem dono, não escreva
   nela: pegue outra, ou peça ao usuário para decidir. Área se declara por
   prefixo de caminho (`src/trilhas/web/`, `catalogo/recursos/`), não por
   arquivo avulso — quem mexe no apresentador mexe no template e no teste.
3. **Nunca reescreva a linha de outra sessão.** Acrescente a sua no fim da
   tabela e apague só a sua. Este arquivo é versionado: reescrever a tabela
   inteira produz conflito em cima do trabalho de quem ainda está escrevendo.
4. **Solte a reivindicação junto com a entrega.** A linha sai no mesmo commit
   ou PR que leva o trabalho. Reivindicação sem branch em `git ls-remote` e sem
   worktree em `git worktree list` está morta; quem a remover cola a saída do
   diagnóstico no commit.
5. **O git ganha de qualquer coisa escrita aqui.** Esta tabela é declaração de
   intenção, não prova. Antes de dizer que algo foi feito, confira o diff.
6. **Trabalho não commitado na árvore é de quem não commitou.** Não existe
   `git stash`, `git checkout --` nem troca de branch em cima de arquivo
   modificado que você não escreveu — o procedimento está na skill
   `encerrar-branch`, e vale também para esta tabela.
7. **Branch próprio, nunca o HEAD compartilhado.** Trabalho que vai gerar commit
   nasce em worktree próprio a partir de `origin/main`; o HEAD deste checkout é
   de todos e trocá-lo quebra as outras sessões.

## Reivindicações ativas

| Área (prefixo) | Branch ou worktree | Intenção / terminado quando | Dono | Desde |
|---|---|---|---|---|
| `CLAUDE.md` §Comandos | `worktree-claude-md-marcadores` | os três `<etapa>`/`<recurso>`/`<seq>` deixam de ser redirecionamento de shell; terminado quando as formas novas foram rodadas e mesclado | sessão Claude | 2026-11-06 |

Linha sem dono é área **ocupada**, não área livre: é trabalho de outra sessão,
em curso e fora do git. As duas primeiras linhas desta tabela eram as duas áreas
desta entrega — apareceram na árvore em minutos, uma depois da outra, e saíram
daqui no commit que as levou (regra 4). A tabela vale no momento em que você a
lê e não substitui um `git status -uall` antes de escrever.

## Observação datada — 2026-11-06

O [PR #32](https://github.com/mpbarbosa/trilhas_estudos/pull/32), que a observação
abaixo deixou de propósito, foi **mesclado hoje a pedido do usuário**. A observação de
05/11 dizia que o problema dele "foi resolvido por `obra` e fechado por ADR-0020":
isso **exagerava**. A ADR-0020 redefiniu `obra` para tornar o exemplar endereçável;
ela não dá como registrar capítulo lido sem concluir a etapa, que é o que o `parte_de`
resolve. O PR não estava redundante.

O que a mescla exigiu, além dos três conflitos previstos: a ADR virou **0021** (0019 e
0020 já existiam) e o `obra` do livro teve de ser reconciliado. O merge automático
passou no gate inteiro **contando um livro de 300 como duas obras de 300** — a main
dera `obra: berryman-ziegler-prompt-engineering` ao todo, o PR dera
`obra: prompt-engineering-for-llms` às partes, e a validação 12 só compara custo
*dentro* de uma obra. Decidido pelo usuário: slug único nas doze fatias. O registro
está na própria
[ADR-0021](docs/adr/0021-capitulo-como-parte-de-recurso.md), §Nota de reconciliação.

**Fica sem guarda automática**: nada no catálogo detecta dois slugs de `obra` para o
mesmo exemplar físico — em princípio não dá, porque só a autoria sabe que dois slugs
nomeiam um livro só.

## Observação datada — 2026-11-05

A observação de 2026-11-01 listava seis branches remotos `claude/project-thread-*`
e três worktrees em HEAD destacado, e **errava num ponto que importava**: dizia que
cinco daqueles branches não tinham PR. Tinham — os PRs #31, #33, #34, #35 e #36,
todos mesclados. O que os manteve de pé foi `deleteBranchOnMerge` desligado
(`gh repo view --json deleteBranchOnMerge`), não ausência de revisão.

Encerrados em 2026-11-05, depois de reconferir cada um imediatamente antes de
apagar (árvore limpa, HEAD ancestral de `origin/main`, zero commits exclusivos):
os três worktrees e os cinco branches com PR mesclado, nas três camadas.

**Deixado de propósito, não é lixo:** o branch remoto
`claude/project-thread-ipajii`, do [PR #32](https://github.com/mpbarbosa/trilhas_estudos/pull/32),
aberto desde 2026-10-22 e o único com commit fora da `main`. Propõe um campo
`parte_de` (capítulo como parte de um recurso) que a `main` **não** adotou: o
problema foi resolvido por `obra`
([ADR-0009](docs/adr/0009-obra-como-campo-de-agrupamento-no-recurso.md)) e fechado
por [ADR-0020](docs/adr/0020-obra-declarada-tambem-em-exemplar-nao-fatiado.md),
aceita depois do PR. Reviver exige renumerar a ADR (o número 0019 já é de outra,
aceita) e resolver três conflitos — `git merge-tree --write-tree origin/main
origin/claude/project-thread-ipajii` os nomeia. **Não apague sem decidir isso com
o usuário:** fechar o PR é decisão de rumo, não limpeza.

Nada aqui é lista de verdade: regenere com `git worktree list`,
`git ls-remote --heads origin`, `git branch -r` e `gh pr list --state all` antes de
agir, e siga a skill `encerrar-branch`.
