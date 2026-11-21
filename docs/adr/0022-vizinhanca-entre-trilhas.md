# ADR-0022 — Vizinhança entre trilhas, declarada onde não há pré-requisito

- **Data**: 2026-11-21
- **Status**: aceito

## Contexto

Perguntou-se se as três trilhas da área `so/` — o núcleo
(`trilha:so/projeto-e-implementacao`), o sistema construído do fonte
(`trilha:so/sistema-linux-do-zero`) e o editor
(`trilha:so/edicao-de-texto-no-vi`) — têm relação entre si, e como essa relação
é registrada e mostrada.

**Tinham, e o catálogo já a registrava**: as três referenciam
`etapa:so/linha-de-comando`, definida em `catalogo/etapas/avulsas.yaml` e
emprestada por cinco trilhas ao todo ([ADR-0010](0010-shell-como-pre-requisito-declarado.md)).
Essa ligação é de pré-requisito, entra no fecho progressivo, e a interface já a
mostra em quatro lugares: a contagem de emprestadas no acervo, a etiqueta e o
traço tracejado no grafo da trilha, a seção *Etapas emprestadas*, e o
*Também em* da página da própria etapa.

O que **não** tinha onde ser registrado é a outra relação, a que o próprio
`catalogo/trilhas/sistema-linux-do-zero.yaml` havia escrito num comentário:

> O que esta trilha **não** é: `trilha:so/projeto-e-implementacao` estuda o núcleo
> por dentro, lendo e modificando o MINIX. Aqui o núcleo é um pacote entre oitenta
> […]. As duas se completam e nenhuma pressupõe a outra.

Isso é um fato sobre o catálogo, autorado com cuidado, e estava num lugar onde
**só quem abre o YAML o lê**. A página da trilha não o mostra, o motor não o
conhece, e a próxima sessão que se perguntasse a mesma coisa teria de reler o
arquivo inteiro para achá-lo.

### A saída errada, e por que é errada

A saída imediata seria declarar um `requires` — fazer o LFS exigir, digamos,
`comp:so/sistemas-de-arquivos`, que o núcleo ensina. Ela foi considerada e
recusada por três razões:

1. **Seria falsa.** O livro declara seus pré-requisitos em "Prerequisites", e o
   YAML já registra qual é o corte: saber operar o sistema pela casca, sem
   pré-requisito de programação. Escrever a dependência contradiria a decisão de
   autoria registrada no mesmo arquivo.
2. **Teria efeito no percurso.** `requires` mais exigente re-trava etapa
   `nao_iniciada` ([catalogo.md §4](../catalogo.md)). O preço de registrar uma
   afinidade seria mexer no que o estudante pode estudar amanhã.
3. **Diria a coisa errada.** "A destrava B" e "A e B se completam" não são a
   mesma afirmação, e o grafo não tem como distingui-las depois.

## Decisão

Criar o campo **`relacionadas`** na trilha: lista de `{trilha, nota}`, fora do
grafo de pré-requisitos.

```yaml
  relacionadas:
    - trilha: trilha:so/projeto-e-implementacao
      nota: >
        Estuda o núcleo por dentro, lendo e modificando o MINIX. Aqui o núcleo é um
        pacote entre oitenta, que se configura e se compila: o objeto de estudo é o
        espaço de usuário em torno dele e a integração das peças. As duas se
        completam e nenhuma pressupõe a outra.
```

Quatro regras o sustentam:

- **`nota` é obrigatória**, na carga (erro de forma, `CAT-001`). O link sozinho
  não diz nada que a lista de trilhas já não diga; a informação acionável é qual
  é o corte de cada uma. É o mesmo princípio de `ArestaDerivada`, que carrega as
  competências que a produziram: "sem elas, a aresta esconde a única informação
  acionável" (`catalogo/grafo.py`).
- **Declara-se num lado só**, e a tela deriva o outro sentido. Declarar nos dois
  produz duas versões de um fato só, que divergem na primeira correção.
- **Não se declara onde há aresta real.** Se alguma etapa própria de uma ensina
  competência que alguma etapa própria da outra exige, a ligação é de
  pré-requisito e já aparece como `destrava` / `destravada por`, com a
  competência nomeada.
- **A conta usa só as etapas próprias.** Etapa emprestada não é de nenhuma das
  duas trilhas. Contá-la faria cada uma das cinco que referenciam
  `etapa:so/linha-de-comando` parecer professora das outras quatro, e a
  validação recusaria exatamente a vizinhança que motivou este ADR.

As três últimas regras são a **validação 14** (`CAT-140`), em
[catalogo.md §5](../catalogo.md). A referência em si resolve pela validação 2.

`relacionadas` é **cosmético** na tabela de revisão: não sobe `rev`. Não muda o
que a trilha ensina, não muda o caminho e não toca em evidência gravada.

## Consequências

- A página da trilha ganha a seção **Trilhas vizinhas**, com a nota de quem
  declarou — inclusive do lado que não declarou. Reescrever a nota na voz do
  outro lado seria inventar texto que ninguém autorou.
- O comentário do LFS saiu do YAML e virou dado. É a regra deste repositório
  aplicada a si mesma: fato com casa mantida noutro lugar não se repete em prosa.
- **O motor não muda.** `relacionadas` não gera candidato, não filtra e não
  pontua. Uma trilha vizinha não é sugerida por ser vizinha.
- Declaradas agora: o LFS com o núcleo (a nota existente), e o vi com as duas —
  nos dois casos o vi é ferramenta, não pré-requisito, e nenhuma das duas o
  exige. As demais áreas continuam sem vizinhança declarada, o que é o estado
  correto: o campo registra o que alguém decidiu, não o que se parece.
- **Fica sem guarda automática**: nada detecta vizinhança *ausente*. Duas trilhas
  que se completam e não se declaram passam no gate — e é assim que tem de ser,
  porque só a autoria sabe que se completam. O que a validação 14 garante é o
  contrário: que a vizinhança declarada não esteja encobrindo uma dependência.
