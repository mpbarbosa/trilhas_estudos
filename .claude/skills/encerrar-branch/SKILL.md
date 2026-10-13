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

**Confira o branch no mesmo comando que commita**, e com uma guarda que de fato
aborta. Isto **não** serve:

```bash
git branch --show-current && git add CAMINHO && git commit   # NÃO protege
```

`git branch --show-current` sai com 0 sempre: ele imprime o branch errado e o
`&&` segue em frente. Aconteceu aqui — a saída mostrou
`claude-project/montador-derivado` e o commit foi feito mesmo assim. Compare o
valor:

```bash
[ "$(git branch --show-current)" = main ] && git add CAMINHO && git commit -m "…"
```

Agora o `[` falha quando o branch não é o esperado e a cadeia para antes do
`add`. Troque `main` pelo branch em que você pretende estar.

Se já foi para o branch errado, prefira deixar onde está: o commit entra na base
quando aquele branch for mesclado. Mover exige `git cherry-pick` mais remover o
commit do branch da outra sessão — reescrever histórico de quem está trabalhando
agora custa mais do que esperar.

## 6. `git add <arquivo>` varre a edição alheia no mesmo arquivo

A guarda da armadilha 5 confere **onde** você commita, não **o quê**. Se outra
sessão editou o mesmo arquivo que você, `git add CAMINHO` leva as duas
alterações, e a mensagem do commit descreve só a sua.

Aconteceu nos dois sentidos no mesmo arquivo, no mesmo dia: uma sessão escrevia
a seção de git do `CLAUDE.md` enquanto a outra corrigia duas frases ali perto —
e o commit de uma levou 22 linhas da outra, sob uma mensagem que não as
mencionava.

Arquivo compartilhado (`CLAUDE.md`, `README.md`, `docs/README.md`) pede conferir
o que está staged **antes** do commit:

```bash
git add CAMINHO && git diff --cached -- CAMINHO   # só então commitar
```

Se o diff staged tiver trecho que não é seu, desfaça com
`git restore --staged CAMINHO` e separe com `git add -p` (modo interativo, que
nem toda sessão tem). Sem `-p`, a saída honesta é pedir à outra sessão que
commite primeiro — ou commitar o arquivo inteiro **dizendo na mensagem** o que
veio junto e de quem.

Se já aconteceu e o commit foi empurrado, **não reescreva**: o histórico
publicado num checkout que outras sessões usam custa mais do que a atribuição
errada. Avise a sessão autora, para ela não recommitar o mesmo texto.

## 7. `git commit` leva o índice inteiro, não o que você acabou de adicionar

Variante da 6 com outro mecanismo e outra defesa. Na 6 o `git add CAMINHO` varre
edição alheia **no mesmo arquivo**. Aqui o arquivo é outro e o `add` nem o tocou:
num checkout compartilhado **o índice também é compartilhado**, e `git commit`
sem `--` commita tudo que estiver nele, staged por quem for.

Aconteceu em `8c87c15`: o comando foi
`git add claude-project/instrucoes.md && git commit -m "Inclui a bibliografia…"`,
um caminho só, explícito. O commit saiu com dois arquivos — o segundo era uma
seção do `CLAUDE.md` que outra sessão tinha deixado staged minutos antes.

Por isso `git diff --cached -- CAMINHO` **não** protege: ele confere o caminho
que você já sabe que está lá. Duas defesas, e a segunda é a que fecha:

```bash
git diff --cached --name-only          # o índice INTEIRO, sem filtro
git commit -m "…" -- CAMINHO           # commita só este caminho, ignora o resto
```

Verificado: com `alheio.txt` staged, `git commit -m "…" -- meu.txt` levou só
`meu.txt` e deixou `alheio.txt` no índice, intacto. O `git commit` seguinte, sem
`--`, levou o `alheio.txt` sozinho.

### A ressalva que torna as duas defesas incompatíveis

`git commit -- CAMINHO` commita a versão da **árvore de trabalho** desse caminho
e **descarta em silêncio** o que você tinha preparado para ele. Verificado: com
`versao-A` staged e `versao-B` na árvore, o commit levou `versao-B`.

Logo, **não combine com a defesa da 6**. Se você usou `git add -p` para separar
só as suas linhas num arquivo que outra sessão também editou, um
`git commit -- CAMINHO` depois joga esse trabalho fora e commita o arquivo
inteiro — inclusive as linhas alheias que você acabou de isolar. As duas
orientações, seguidas nessa ordem, produzem exatamente o acidente da 6, e falham
para quem estava sendo cuidadoso.

| Situação | Defesa |
|---|---|
| Arquivo que **só você** tocou, índice sujo de outros | `git commit -m "…" -- CAMINHO` — a árvore é sua, não há o que preservar |
| Arquivo que **outra sessão também** tocou | `git add -p`, conferir `git diff --cached --name-only`, e `git commit` **sem** pathspec |

Corolário: **deixar algo staged é por si só o risco.** A janela entre `git add` e
`git commit` pertence a todas as sessões do checkout, então prepare e commite no
mesmo comando em vez de deixar o índice carregado.

Isso elimina a janela do índice e **não dispensa a tabela acima**: a escolha
entre as duas defesas se faz pelo *arquivo*, não pelo índice. Num arquivo que
outra sessão também editou, `git commit -- CAMINHO` com índice vazio commita a
árvore inteira daquele arquivo — as linhas dela junto. Ali a defesa continua
sendo `git add -p` e commit sem pathspec.

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

## Ao editar esta skill: "verificado" não autoriza a generalização

Esta skill foi corrigida quatro vezes em um dia, sempre por defeito de quem a
escreveu. As quatro não têm a mesma causa, e a diferença importa:

| Correção | O que estava errado | Causa |
|---|---|---|
| `b0fd1c2` | `git branch --show-current &&` como guarda | recomendado **sem nunca ter sido executado** |
| `67fdb02` | `git commit -- CAMINHO` "é a defesa da 7" | dois eixos testados, o terceiro nem imaginado — por duas sessões em sequência |
| `0314adc` | "o corolário dispensa a tabela" | generalização de uma defesa que funcionava |
| `655062e` | a regra 2 abaixo, escrita como lei | generalização da própria lição |

A segunda é a mais instrutiva, porque **a frase "verificado em repositório
isolado" estava no texto e era verdadeira**: o eixo testado passou. O eixo não
testado nem foi imaginado — verificar o que se imaginou e publicar com confiança
o que não se imaginou é um único movimento, e não dá para senti-lo por dentro.

Vale o detalhe de quem errou: o comando veio recomendado por uma sessão par, que
não tinha testado esse eixo; quem o publicou como regra testou dois eixos e
também não imaginou o terceiro; e foi a sessão que recomendou quem voltou, por
conta própria, para dizer que tinha recomendado sem testar. **Duas sessões
independentes não imaginaram o mesmo eixo** — revisão por pares reduz a chance
de ponto cego, não a elimina, porque o ponto cego pode ser do formato do
problema e não de quem olha.

A primeira é mais banal e mais comum: escrever um comando que parece óbvio e não
rodá-lo. Ela foi descoberta por alguém **executando** a recomendação, que é a
única coisa que pega esse caso.

Daí duas regras para quem mexer aqui:

1. **Escreva a regra no escopo do teste, não no escopo da intuição.** Se você
   testou que um comando isola um caminho, escreva isso — não "é a defesa".
2. **Olhe de onde vieram as quatro correções, não só quantas foram.** Duas
   (`67fdb02`, `0314adc`) vieram de uma sessão par lendo o texto publicado; uma
   (`b0fd1c2`) de alguém executar o comando recomendado, que falhou na frente de
   quem o usava; uma (`655062e`) do próprio autor, relendo. É uma skill num dia
   e não dá lei, mas as três origens são diferentes e nenhuma cobre as outras:
   revisão pega a regra ampla demais, execução pega o comando que nunca rodou,
   releitura pega o que você já sabe procurar. Quando houver sessão par no mesmo
   checkout, mandar o texto custa uma mensagem.
