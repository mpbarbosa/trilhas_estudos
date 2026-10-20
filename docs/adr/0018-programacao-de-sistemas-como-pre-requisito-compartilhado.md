# ADR-0018 — Programação de sistemas como pré-requisito compartilhado, em terceira etapa avulsa

- **Data**: 2026-10-19
- **Status**: aceito

## Contexto

[ADR-0017](0017-trilha-de-emulador-sem-linguagem-declarada.md) decidiu que
`trilha:terminal/emulador` não declara linguagem de implementação nos `requires`, e
declarou o preço na própria seção de consequências: um estudante sem nenhuma
competência de programação se matricula, atravessa a especificação, o analisador e a
grade, e só bate no muro em `etapa:terminal/projeto-emulador-minimo`. Aquele texto
nomeia o que isso é — "precisamente o modo de falha que a ADR-0010 condenou" — e
nomeia a forma que o pagaria: a **forma (3)**, uma etapa avulsa nova de programação de
sistemas, recusada ali por ser trabalho de autoria de uma etapa compartilhada e não
detalhe daquela trilha.

Não declarar linguagem havia virado, na prática, **não declarar programação**. São
coisas diferentes, e só a primeira era a decisão de ADR-0017.

A mesma omissão existe, não notada até aqui, em `trilha:so/projeto-e-implementacao`.
Ela foi a ADR-0010 declarar o shell que o projeto do MINIX pressupunha, e o que o
projeto pressupõe também é escrever código: a verificação de
`comp:so/nucleo-na-pratica` manda introduzir uma chamada de sistema nova ou alterar o
escalonador e **demonstrar o efeito por um programa de usuário**. Nenhum `requires`
pedia programação alguma. Duas trilhas ativas, o mesmo buraco.

O que torna a forma (3) possível é um recorte que exista de verdade, e a dúvida
honesta era se existe. Uma competência de programação de sistemas que seja a trilha de
C com outro nome não serve — a cascata de sete etapas volta pela janela. Uma que seja
"saber programar" não é competência, é assunto, e a skill de autoria recusa isso: se
não se descreve como se verifica, dissolve-se em outras.

O recorte existe porque as duas trilhas cobram as **mesmas três coisas**, e só essas:

| O que as duas cobram | No emulador | No MINIX |
|---|---|---|
| Descritor como fluxo de bytes sem fronteira de registro, com estado entre leituras parciais | A sequência CSI que chega partida entre duas leituras do mestre do pseudoterminal | O programa de usuário que exercita a chamada de sistema nova |
| Estrutura agregada em memória, e cópia contra referência ao mesmo dado | A grade de células e o histórico que rola | A estrutura de processo que o escalonador percorre |
| Programa em mais de um módulo, com uma construção que o liga | Qualquer das três pilhas | O `make` da árvore do MINIX |

Fora do recorte fica o que é da trilha de C e não das duas: a biblioteca padrão,
argumentos variáveis, o alocador próprio, as declarações decifradas — e a sintaxe de C
em si. E fica de fora porque nenhuma das duas trilhas o cobra: as três pilhas do
emulador são Rust, C e JavaScript, e as três satisfazem a tabela acima.

## Decisão

**Uma competência e uma etapa avulsa**, a terceira de
`catalogo/etapas/avulsas.yaml`:

| Entidade | Papel |
|---|---|
| `comp:programacao/programacao-de-sistemas` | o pré-requisito; `verificacao` independente de linguagem |
| `etapa:programacao/programacao-de-sistemas` | `requires: []`, obrigatória, 1500 min |

A `verificacao` é um programa só, porque um programa só exercita as três linhas da
tabela de uma vez: dois módulos, um processo filho, a leitura do descritor em pedaços
que não respeitam fronteira de registro, e a demonstração de que uma entrada cortada
no meio de um delimitador não perde nem duplica nada. Daí sai também o que a etapa
**não** é: não pede linguagem, não pede alocador, não pede padrão de C.

**`requires: []`**, como nas duas avulsas de ADR-0010, e aqui a escolha tem um
custo que vale registrar. Exigir `comp:so/linha-de-comando` seria defensável — a
construção acontece na casca, e é por isso que
`etapa:programacao/c-funcoes-e-estrutura-de-programa` a exige — e não custaria nada às
duas trilhas de hoje, que já referenciam aquela etapa. Mas obrigaria **toda trilha
futura** que precise desta a referenciar duas avulsas em vez de uma, e a propriedade
pela qual a forma foi escolhida, nas três vezes, é exatamente que referenciar custa uma
linha. A cascata curta é cascata.

**Onde é cobrado.** Nas duas trilhas, no ponto em que o código começa — não no
projeto final:

- `trilha:terminal/emulador`: em `etapa:terminal/analisador-de-estados` **e** em
  `etapa:terminal/pseudoterminal-e-sinais`. São as duas entradas de código da trilha e
  nenhuma depende da outra: abrir um pseudoterminal e rodar um shell nele não passa
  pelo analisador. As demais etapas de código — grade, Unicode, renderização,
  conformidade, acessibilidade e o projeto — herdam o pré-requisito por dependerem de
  uma das duas, e por isso não o repetem.
- `trilha:so/projeto-e-implementacao`: em `etapa:so/projeto-modificar-o-minix`, o
  único ponto em que ela manda escrever código.

**A trilha de C passa a conceder a competência.**
`etapa:programacao/c-interface-com-o-unix` ganha
`comp:programacao/programacao-de-sistemas` em `teaches`. Sem isso, quem cursasse a
trilha de C inteira chegaria à de emulador sem a competência e seria mandado a uma
etapa de 25 h que já ultrapassou — o que esta etapa verifica (`fopen`/`getc` sobre
`read`, um alocador com lista livre, em programa de vários arquivos) é estritamente
mais do que a avulsa cobra. A trilha de C **não** referencia a avulsa, porque uma
trilha não referencia a avulsa de uma competência que ela própria entrega.

`rev` sobe em seis entidades, pela tabela de [catalogo.md §4](../catalogo.md):
`etapa:terminal/analisador-de-estados` e `etapa:terminal/pseudoterminal-e-sinais` a 2 e
`etapa:so/projeto-modificar-o-minix` a 3 (`requires`);
`etapa:programacao/c-interface-com-o-unix` a 2 (`teaches`); `trilha:terminal/emulador`
a 2 e `trilha:so/projeto-e-implementacao` a 3 (etapa obrigatória nova). A trilha de C
não sobe: `teaches` de uma etapa não é mudança substantiva da trilha.

## Consequências

- **Etapa `nao_iniciada` volta a travar**, em três pontos: as duas entradas de código
  do emulador e o projeto do MINIX. É o comportamento da tabela de
  [catalogo.md §4](../catalogo.md) para `requires` mais exigente, e é o efeito
  pretendido — o travamento passa a ser visível e explicado, em vez de acontecer na
  cadeira do estudante. Etapa `em_andamento` ou `concluida` não re-trava, e
  `trilha:terminal/emulador`, publicada em 2026-10-19, não tem percurso para reabrir.
- **O que ADR-0017 corrige, e o que nela continua de pé.** A consequência que ela
  aceitou como custo — "o catálogo não barra quem não programa" — deixa de valer. A
  decisão de fundo não muda: nenhuma **linguagem** entra nos `requires` do emulador, e
  a cascata de sete etapas continua recusada. ADR-0017 previu esta ADR como caminho de
  migração e nada precisou ser recriado, porque o id é imutável
  ([ADR-0005](0005-identidade-imutavel-e-depreciacao.md)).
- **O piso do MINIX é verdadeiro e menor que o pré-requisito real.** O que continua
  por declarar ali é que o código é em C, especificamente; a avulsa é independente de
  linguagem. Exigir C traria a cascata de sete, e a escolha é a de ADR-0010: declarar o
  piso que se pode declarar, e dizer qual é o resto. Fica dito, não escondido.
- **A trilha de emulador alcança o primeiro recurso em pt-BR.** Por esta etapa
  referenciada, não pelas suas: ADR-0017 registrou que as etapas próprias dela são
  todas em inglês, e isso continua. O caminho em português desta etapa é um só, e é em
  Rust — o *Comprehensive Rust* traduzido. No caminho de C não há equivalente
  gratuito em pt-BR, porque o K&R em português é pago e é fatia da trilha de C, não
  desta etapa. Registrado em comentário no YAML dos recursos, com o que foi procurado.
- **Dois caminhos de linguagem nos recursos, e isso é estrutural.** Uma competência
  que se declara independente de linguagem e só oferece material de uma linguagem é
  uma competência de linguagem com outro nome. Daí quatro recursos em dois caminhos —
  os guias do Beej para C, os dois livros de Rust —, e daí o guia de IPC ao lado de um
  guia de linguagem em vez de no lugar dele: o descritor e a leitura parcial não estão
  em livro de linguagem.
- **Etapa longa, e de propósito.** 1500 min é o esforço de quem parte do zero, e por
  isso os recursos vão de um guia que começa em `hello, world` a um curso escrito para
  quem já programa em outra linguagem. Quem já programa passa direto pela
  `verificacao`, que é o que a etapa cobra: a etapa é o caminho, não o pedágio.
- **Uma competência pode ser ensinada por mais de uma etapa, e agora é.** A avulsa e
  `etapa:programacao/c-interface-com-o-unix` concedem as duas, no mesmo nível. A
  validação 3 já contava com isso — faz fecho progressivo em vez de ordenação
  topológica justamente porque a mesma competência aparece em mais de uma etapa — e
  nada no motor pressupõe etapa única por competência.
- **Custo**: uma competência e uma etapa a manter, quatro recursos a reverificar, e
  seis `rev` que sobem de uma vez. Em troca, as duas trilhas que mandam escrever
  código passam a dizer que mandam, e a próxima que mandar referencia uma etapa que já
  existe, por uma linha.
