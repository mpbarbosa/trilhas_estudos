---
name: encerrar-branch
description: Procedimento para fechar o trabalho de um branch neste repositório compartilhado — publicar, mesclar, apagar local e remoto — sem destruir commit de outra sessão nem roubar o trabalho não commitado dela. Use ao terminar um branch, ao limpar o repositório, quando `git branch -d` recusa ou aceita com aviso, quando `git switch` é bloqueado por arquivos não commitados, antes de qualquer `git stash`, ou ao responder se a sessão pode ser encerrada.
---

# Encerrar um branch

**Outras sessões commitam, editam e fazem stash neste mesmo checkout**
(CLAUDE.md §Git). Isso não é detalhe: é o que torna errada quase toda a intuição
normal sobre limpeza de branch. As quatro armadilhas abaixo aconteceram de fato
aqui, e cada uma tem um comando que parece ter dado certo.

Antes de apagar ou trocar qualquer coisa:

```bash
scripts/conferir-branch.sh            # confere o branch atual
scripts/conferir-branch.sh meu-branch
```

Ele só lê. Saída 0 = pode apagar o branch local; 1 = não pode, e diz por quê.

## 1. `git branch -d` aceita apagar o que não está na main

É a armadilha principal. O `-d` aceita se o branch foi mesclado ao **remote
tracking ref** (`origin/<branch>`), e não à `main`:

```
warning: deleting branch 'X' that has been merged to
         'refs/remotes/origin/X', but not yet merged to HEAD
```

Esse aviso quer dizer: *o commit sumiu do seu clone e existe só no `origin`.*
Não é erro — mas se alguém apagar o branch remoto depois (o merge de PR apaga,
dependendo de `gh repo view --json deleteBranchOnMerge`), o trabalho some de vez.

**Um branch mora em três lugares, e apagar num não apaga nos outros.**
`git branch -d` dar certo não diz nada sobre o `origin`; o merge de um PR apagar
o remoto não apaga o local; e nenhum dos dois remove a **ref de rastreio**, que
fica pendurada apontando para um branch que já não existe no servidor:

| Camada | Como conferir | Como remover |
|---|---|---|
| local | `git branch --format='%(refname:short)'` | `git branch -d X` |
| remoto | `git ls-remote --heads origin` | `git push origin --delete X` |
| ref de rastreio | `git branch -r` | `git remote prune origin` |

A terceira é a que ninguém olha. `git ls-remote` pergunta ao servidor e dirá que
o branch sumiu; `git branch -r` lê o seu clone e continuará listando
`origin/X` por tempo indefinido. Quem conferir só a segunda conclui que está
limpo, e quem conferir só a terceira conclui que sobrou algo — ambos errados.

Se o repositório tem `deleteBranchOnMerge` ligado
(`gh repo view --json deleteBranchOnMerge`), o merge já apaga o remoto, e o
`--delete` depois falha com `remote ref does not exist`. **Isso é a limpeza
tendo funcionado**, não um erro: confirme com `git ls-remote` antes de
investigar, e rode o prune, que é o que de fato restava.

## 2. O branch que você criou pode não ser mais só seu

Outra sessão commita no branch que está em HEAD — que é o seu. Antes de apagar,
veja o que há nele fora da base e **quem se beneficia disso**:

```bash
git log --oneline origin/main..meu-branch
```

Se aparecer commit que você não escreveu, pare. Publicar é seguro e reversível;
apagar não é:

```bash
git push origin meu-branch     # tira a condição de cópia única
```

Não abra o PR desse commit por conta própria: descrever trabalho alheio é
inventar a intenção de quem o escreveu. Peça à sessão autora, ou confirme com a
pessoa.

## 3. `git stash` rouba o trabalho ao vivo de outra sessão

Quando `git switch` é bloqueado por arquivos não commitados, a saída óbvia é
`git stash`. **Não faça isso aqui.** Os arquivos podem ser edição em andamento de
outra sessão, e o stash os tira da árvore dela no meio do trabalho — da
perspectiva dela, o arquivo reverte sozinho.

O caminho é pedir que ela commite. Se o stash já aconteceu, `git stash pop`
devolve; confirme que a pilha ficou vazia e que os arquivos voltaram:

```bash
git stash list && git status --porcelain -uall
```

## 4. `git status` muda entre dois comandos seus

Neste checkout a árvore muda de segundo a segundo. Uma leitura limpa **não**
autoriza a conclusão de que ficou limpa: ela descreve um instante. Releia
imediatamente antes de agir, e desconfie de conclusão tirada de leitura anterior
— aqui já houve `git stash list` vazio seguido, segundos depois, de um
`git stash pop` que encontrou conteúdo.

## 5. O branch em HEAD muda entre dois comandos seus

A armadilha 4 vale também para `HEAD`: outra sessão pode rodar `git switch -c` no
checkout compartilhado, e o seu `git commit` seguinte vai para o branch dela —
sem erro, sem aviso, empilhado sobre trabalho que não é seu.

Aconteceu assim: um `git status` confirmou `main`, e o `git add && git commit`
logo depois reportou `[claude-project/montador-derivado 5e238d6]`.

Não se perde nada, mas o commit fica refém do ciclo de revisão do branch alheio.
**Confira o branch no mesmo comando que commita**, não antes:

```bash
git branch --show-current && git add <arquivos> && git commit
```

Se já foi para o branch errado, prefira deixar onde está: o commit entra na base
quando aquele branch for mesclado. Mover exige `git cherry-pick` mais remover o
commit do branch da outra sessão — reescrever histórico de quem está trabalhando
agora custa mais do que esperar.

## Sequência que funciona

```bash
scripts/conferir-branch.sh meu-branch     # 1. diagnóstico; respeite a saída 1
git push origin meu-branch                # 2. nada mais é cópia única
gh pr create --base main --head meu-branch --title "…"
# 3. depois do merge:
git switch main && git pull
git branch -d meu-branch                  # 4. local
# 5. remoto: o merge do PR costuma apagar. Confira e, se sobrou:
git ls-remote --heads origin | grep meu-branch
git push origin --delete meu-branch
# 6. ref de rastreio: sobra mesmo quando 4 e 5 deram certo
git remote prune origin
```

## Ao responder "posso encerrar?"

Rode os comandos de novo, não confie no que você relatou antes — é o que
`/session-dropped` exige. Classifique cada sobra em **sua e esquecida**, **sua e
deixada de propósito** ou **de outra sessão**; só a primeira é falha. Branch
remoto deixado de propósito (porque guarda commit ainda não mesclado) precisa ser
declarado como tal, ou a próxima sessão o apaga achando que é lixo.
