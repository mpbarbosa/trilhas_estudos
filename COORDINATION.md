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
| `src/trilhas/web/apresentar/`, `src/trilhas/web/modelos/trilha.html`, `src/trilhas/web/estatico/estilo.css`, `src/trilhas/web/rotas.py`, `tests/test_apresentar.py`, `tests/test_web.py`, `docs/interface.md` | nenhum — modificado e **não commitado** no checkout compartilhado | passa `hoje` ao detalhe da trilha e rende algo datado na página; terminado quando commitado com o gate de CLAUDE.md §Comandos verde | **não declarado** | em árvore em 2026-11-01 |
| `src/trilhas/catalogo/obras.py`, `catalogo/recursos/filosofia.yaml`, `catalogo.lock.json`, `tests/test_obras.py`, `docs/adr/0020-obra-declarada-tambem-em-exemplar-nao-fatiado.md` | nenhum — modificado e **não commitado** no checkout compartilhado | obra declarada também em exemplar não fatiado, com ADR-0020; terminado quando commitado com o gate verde e a ADR na tabela de `docs/README.md` | **não declarado** | em árvore em 2026-11-01 |

Linha sem dono é área **ocupada**, não área livre: é trabalho de outra sessão,
em curso e fora do git. As duas acima apareceram na árvore em minutos, uma
depois da outra — por isso a tabela vale no momento em que você a lê e não
substitui um `git status -uall` antes de escrever.

## Observação datada — 2026-11-01

Fatos que o git mostra mas que ninguém reivindicou. Não são lista de verdade:
regenere com os comandos antes de agir sobre qualquer um deles.

- **Seis branches remotos `claude/project-thread-*`, um só com PR aberto**
  ([#32](https://github.com/mpbarbosa/trilhas_estudos/pull/32), parado desde
  2026-10-22). Os outros cinco não têm PR e não têm dono aqui.
  `gh pr list --state open` e `git ls-remote --heads origin`.
- **Três worktrees em `.claude/worktrees/` em HEAD destacado**, nos commits
  `4ae7d54`, `fb3410d` e `0aa384a` — os dois últimos são merges de PR já
  fechados (#23, #22). O diretório está em `.git/info/exclude`, então nada disso
  aparece em `git status`. `git worktree list`.

Cada um desses é candidato a encerramento, não lixo comprovado: um worktree em
HEAD destacado pode guardar trabalho não commitado, e um branch remoto sem PR
pode ser a única cópia de um commit. Rode `scripts/conferir-branch.sh` e siga a
skill `encerrar-branch` antes de apagar qualquer coisa — e pergunte ao usuário,
porque nenhum desses é seu.
