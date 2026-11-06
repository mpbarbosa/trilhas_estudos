# ADR-0020 — `obra` declarada também em exemplar não fatiado

- **Data**: 2026-11-01
- **Status**: aceito

## Contexto

Pediu-se que a tela da trilha mostrasse **os livros que a compõem**. A tela já lista os
recursos de todas as suas etapas ([interface.md §5.3](../interface.md)), e a lista de
recursos não responde essa pergunta: um livro que atende cinco etapas aparece cinco
vezes nela, com o preço repetido cinco vezes. A unidade de **aquisição** é o exemplar,
e quem monta a estante pergunta por ele.

O catálogo tem exatamente um campo que fala de exemplar: `obra`
([ADR-0009](0009-obra-como-campo-de-agrupamento-no-recurso.md)). Ele foi decidido como
**agrupamento de fatias** — "um livro que atende sete etapas é sete recursos, e as sete
fatias declaram a mesma `obra`" ([catalogo.md §2](../catalogo.md)) —, e daí veio a
leitura, aplicada na autoria desde então, de que um livro que entra inteiro numa etapa
só não tem o que agrupar e portanto não declara `obra`. O cabeçalho de
`catalogo/recursos/filosofia.yaml` registrava essa leitura por escrito, para os cinco
livros de Hari Chetan.

### O que o catálogo sabe de livro, medido

[bibliografia.md](../bibliografia.md) é uma ficha por livro, com os ids dos recursos
que o citam. Cruzando as fichas com o `obra` declarado no snapshot, antes desta ADR:

| | Livros |
|---|---|
| Fichas em bibliografia.md | 74 |
| …cujos recursos declaram `obra` | 24 |
| …que não declaram `obra` alguma | 50 |
| dessas 50, as que são **um recurso só** | 44 |

As 44 são exatamente o caso desta ADR: livro que entra inteiro numa etapa, invisível
como exemplar porque nunca precisou ser agrupado.

Por trilha, o efeito de montar a seção só com o que `obra` marcava hoje:

| Trilha | Obras declaradas | Livros com ficha | Recursos |
|---|---|---|---|
| `web/do-protocolo-a-interface` | 1 | 14 | 29 |
| `dados/analise-de-dados-com-python` | 2 | 16 | 21 |
| `ia/llm-transformer-rag` | 6 | 19 | 38 |
| `terminal/emulador` | 1 | 2 | 78 |
| `filosofia/bhagavad-gita` | **0** | 2 | 7 |

A trilha da Gita é o caso extremo e o mais recente: sete recursos, dos quais seis são
livros — os cinco de Hari Chetan e a tradução de Arnold —, e nenhum exemplar declarado.
A seção "Livros da trilha" montada sobre `obra` diria, naquela página, que a trilha não
tem livro nenhum.

### Opções

1. **Campo novo no recurso** (`exemplar: true`, ou `tipo: livro`) que diga "isto é um
   exemplar", deixando `obra` como agrupamento puro.
2. **Tornar bibliografia.md normativa**: compilá-la para o lock e ler os livros de lá.
3. **`obra` declarada em todo exemplar**, fatiado ou não — uma obra de uma fatia é uma
   obra.
4. **Derivar na tela**: tratar todo recurso sem `obra` como exemplar de si mesmo, pela
   regra de custo de [catalogo.md §2](../catalogo.md), sem tocar na autoria.

## Decisão

**Opção 3.** `obra` passa a querer dizer "este recurso é fatia de um exemplar
endereçável", e **uma fatia só é um número legítimo de fatias**. O campo segue
opcional, segue slug sem `<tipo>:`, segue fora da cerimônia de
[ADR-0005](0005-identidade-imutavel-e-depreciacao.md), e as regras de soma do ADR-0009
ficam intactas: duração soma fatias, dinheiro conta cada obra uma vez.

Duas coisas, que já eram verdade, passam a ter consequência prática:

- **Declarar `obra` é o que torna o exemplar endereçável.** Sem ela não há slug, não há
  `/obra/<slug>`, e a trilha não tem como listar o livro — é por isso que a decisão
  anterior, de omiti-la onde não havia agrupamento, custava caro sem economizar nada.
- **Recurso sem `obra` continua sendo obra de si mesmo para efeito de custo**
  ([catalogo.md §2](../catalogo.md)). O que ele não é, e nunca foi, é um exemplar que
  se possa nomear.

Primeira aplicação: os seis livros de `trilha:filosofia/bhagavad-gita`, com `rev` de 1
para 2 em cada um — `obra` é mudança substantiva ([catalogo.md §4](../catalogo.md)). O
artigo da *Internet Encyclopedia of Philosophy* **não** recebeu `obra`: não é exemplar
que se adquira. O slug repete o do recurso (`chetan-daily-bhakti`), porque é o mesmo
exemplar e um segundo nome só criaria duas maneiras de chamá-lo.

A opção 1 foi recusada por pagar um campo para dizer o que `obra` já diz. Um recurso
com `exemplar: true` e sem `obra` teria de ganhar slug de algum lugar para ser
endereçável — e aí é `obra` com outro nome —, ou ficaria endereçável por id de recurso,
o que faria a tela da obra ter dois tipos de URL para a mesma coisa. Pior: nada
impediria `obra` e `exemplar` de discordarem, e a validação que os conciliasse seria
nova superfície para um fato que não precisa de dois lugares.

A opção 2 foi recusada pelo que o próprio ADR-0009 já tinha medido e esta ADR
remediu: bibliografia.md é mantida à mão e está atrasada — hoje nem os cinco livros de
Hari Chetan têm ficha, embora estejam no catálogo desde outubro. Compilar um documento
que ninguém confere o transformaria de descrição desatualizada em **fonte da verdade**
desatualizada, e o catálogo passaria a ter duas autorias para o mesmo recurso, em
arquivos diferentes, com ordem de precedência a inventar. O documento segue descritivo.

A opção 4 foi recusada por responder outra pergunta. Ela monta a lista sem autoria
nenhuma — e inclui o artigo de enciclopédia, o vídeo do YouTube e o exercício
interativo, porque a regra de custo não distingue livro de coisa nenhuma: ela diz como
somar, não o que a coisa é. A seção se chamaria "o que adquirir" e repetiria, com outro
agrupamento, a lista de recursos que a tela já tem. **Que algo seja um exemplar é fato
de autoria, e só quem escreve o recurso sabe.**

## Consequências

- **A autoria pendente foi feita na mesma mudança, trilha a trilha.** As 50 fichas sem
  `obra` foram marcadas: o catálogo passou de 23 obras em 85 fatias para **84 em 155**,
  e hoje **as 74 fichas de [bibliografia.md](../bibliografia.md) têm `obra`**. Não foi
  varredura: a ficha diz que a obra é livro, mas não diz qual recurso **é** o exemplar
  — o repositório de código do Raschka, os notebooks do *Hands-On LLMs* e o projeto do
  *LLM Engineer's Handbook* são citados pela ficha e ficaram de fora, por serem
  acompanhamento e não o livro. Onde a ficha reunia fatias de um mesmo livro livre
  (*Speech and Language Processing*, *Three Easy Pieces*, *The Linux Command Line*),
  entrou uma obra com as 5, 5 e 2 fatias.
- **A seção segue incompleta onde o material não é livro, e a tela diz isso.** Onze
  obras não têm ficha (seis marcadas aqui por julgamento: Beej ×2, Guia Foca, o livro
  do Rust, *Node.js Succinctly* e *Use The Index, Luke!*), e 144 recursos seguem sem
  exemplar — em `terminal/emulador` são 72 de 78, quase todos especificação, página de
  manual, código-fonte e artigo, que exemplar nenhum tem. A tela imprime esse número
  em toda trilha, para a estante não parecer completa.
- **A validação 12 deixa de pegar algo nas obras de uma fatia.** "Fatias da mesma obra
  declaram o mesmo custo" é trivialmente verdadeiro com uma fatia só. Não há regra nova
  propondo-se aqui: o que protege a obra de uma fatia é a mesma revisão de autoria que
  protege o `custo` do recurso.
- **Marcar um livro custa um `rev`.** São seis nesta leva. Isso é o preço de `obra` ser
  substantiva ([catalogo.md §4](../catalogo.md)), e é intencional: o agrupamento muda o
  custo que o sistema atribui a um caminho. Não há efeito no percurso — `rev` de recurso
  nunca altera a da etapa, e evidência é selada com a `rev` da etapa.
- **Recurso depreciado não recebe `obra` nova.** Marcá-lo criaria um exemplar cujas
  fatias estão todas depreciadas — endereçável, como [catalogo.md §6](../catalogo.md)
  exige de tudo que já existiu, mas nascido retirado, e a trilha passaria a listar como
  livro um material que ela mesma esmaece. Aconteceu nesta leva com *Python Fluente*,
  depreciado em 2026-10-22, e quem pegou foi `test_obra_do_catalogo_real`, que varre o
  catálogo autorado atrás de obra sem fatia viva. Fatia depreciada **dentro** de uma
  obra com fatias vivas continua normal, e é o caso que a §5.12 já tratava.
- **`/obra/<slug>` de uma fatia só repete a página do recurso**, com nome de livro em
  vez de título de fatia e uma linha de tabela. Aceita-se: é o endereço que a lista de
  livros da trilha precisa ter, e a alternativa é não ter endereço.
- **`obra` quer dizer exemplar, não livro.** Nada impede um curso pago ou um
  audiolivro de declará-la, e nenhuma validação o impediria. Hoje toda obra do catálogo
  é livro, e por isso a seção se chama "Livros da trilha"; no dia em que um exemplar não
  for livro, o rótulo é que terá de mudar — não o campo.
- **O custo da trilha já desconta o que está na estante.** A seção soma cada exemplar
  uma vez (ADR-0009) e mostra, ao lado, quanto ainda falta pagar, propagando a posse
  pela mesma `possuidos_em` que o motor usa
  ([ADR-0015](0015-posse-de-exemplar-como-estante-declarada.md)). Um livro marcado como
  exemplar passa, de graça, a poder entrar na estante — antes dele não havia o que
  declarar.
- **bibliografia.md fica conferível contra o catálogo** na direção que importa: ficha
  sem `obra` é agora uma lista de trabalho pendente, não uma diferença de significado.
  Esta ADR não cria a conferência nem a obriga.
