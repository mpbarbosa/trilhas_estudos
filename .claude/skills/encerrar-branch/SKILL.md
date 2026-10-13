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

**Local e remoto são duas exclusões separadas.** `git branch -d` dar certo não
diz nada sobre o `origin`, e o merge de um PR apagar o remoto não apaga o local.
Confira os dois:

```bash
git ls-remote --heads origin
git branch --format='%(refname:short)'
```

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
```

## Ao responder "posso encerrar?"

Rode os comandos de novo, não confie no que você relatou antes — é o que
`/session-dropped` exige. Classifique cada sobra em **sua e esquecida**, **sua e
deixada de propósito** ou **de outra sessão**; só a primeira é falha. Branch
remoto deixado de propósito (porque guarda commit ainda não mesclado) precisa ser
declarado como tal, ou a próxima sessão o apaga achando que é lixo.
