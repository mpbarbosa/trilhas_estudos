# ADR-0017 — Emulador de terminal em área própria, sem linguagem de implementação nos `requires`

- **Data**: 2026-10-19
- **Status**: aceito

## Contexto

`trilha:terminal/emulador` entrou no catálogo a partir de uma bibliografia de emulador
de terminal: a máquina de estados de Paul Williams, `ctlseqs`, a ECMA-48, `esctest` e
`vttest`, os motores VT embutíveis (`alacritty_terminal`, `vte`, `libvterm`,
`wezterm-term`, xterm.js), a abertura de pseudoterminal (`portable-pty`, `node-pty`), a
pilha de texto e GPU (HarfBuzz, `cosmic-text`, `swash`, fontconfig, wgpu, `winit`), as
codificações modernas de teclado e as sequências OSC de integração com o shell.

Duas decisões não se resolviam por procedimento.

**Primeira: onde a trilha mora.** O assunto é meio sistema operacional
(pseudoterminal, disciplina de linha, grupo de processos, sinais), meio renderizador de
texto (Unicode em grade, atlas de glifos, latência) e meio implementação de protocolo
(ECMA-48 e a linhagem DEC). Nenhuma das áreas existentes o contém sem distorcer as
outras duas.

**Segunda, e a que custou:** um emulador se escreve em alguma linguagem, e a
bibliografia é de três — Rust, C e JavaScript. O pré-requisito honesto parecia ser
`comp:programacao/c-interface-unix`, na forma que [ADR-0010](0010-shell-como-pre-requisito-declarado.md)
fixou para o shell: declarar o que a trilha pressupõe, em vez de deixar o estudante
travar sem explicação.

Só que o shell e a linguagem não são o mesmo caso, e o que os separa está no validador.
A validação 6 ([catalogo.md §5](../catalogo.md)) só conta as etapas **da própria
trilha**, `etapas_referenciadas` incluídas — em `src/trilhas/catalogo/validar.py`,
`_v6_objetivo_alcancavel` monta o fecho sobre `trilha.todas_as_etapas` e parte de perfil
vazio. `comp:so/linha-de-comando` é servida por uma etapa avulsa com `requires: []`:
referenciá-la custa uma linha e nada mais. `comp:programacao/c-interface-unix` é servida
por `etapa:programacao/c-interface-com-o-unix`, que exige estruturas e E/S, que exigem
apontadores, que exigem funções e estrutura de programa, que exigem os fundamentos e o
tutorial. Declarar a linguagem obrigaria a referenciar **sete** etapas, e a trilha de
emulador passaria a conter a trilha de C inteira.

Três formas foram consideradas:

1. **Declarar C** e referenciar a cascata de sete etapas.
2. **Não declarar linguagem**; o pré-requisito de linguagem fica fora do modelo.
3. **Etapa avulsa nova** de programação de sistemas, na forma da ADR-0010, servindo de
   pré-requisito a esta trilha e a outras.

A (1) é precisa e mentirosa ao mesmo tempo: precisa porque a cascata é real, mentirosa
porque C não é a linguagem desta trilha — `vte` e `alacritty_terminal` são Rust,
xterm.js é JavaScript, e as três pilhas resolvem o mesmo problema. A trilha ficaria
com 20 etapas, sete delas de C, para exigir uma linguagem que seus próprios recursos
não usam na maioria. A (3) é o caminho certo e é **grande**: uma etapa avulsa de
programação de sistemas precisa de competência com verificação, recursos próprios e um
recorte que sirva a mais de uma trilha — é trabalho de autoria de uma etapa
compartilhada, não um detalhe desta.

## Decisão

**Área própria `terminal`**, com `catalogo/competencias/terminal.yaml`,
`catalogo/recursos/terminal.yaml` e a trilha em
`catalogo/trilhas/emulador-de-terminal.yaml`. `area` é organizacional, não semântica
([catalogo.md §3](../catalogo.md)): o que ela decide é onde o próximo autor procura.

**Nenhuma linguagem de implementação nos `requires`** — a forma (2), por ora. O único
pré-requisito externo declarado é `comp:so/linha-de-comando`, por
`etapas_referenciadas`, exigido em `etapa:terminal/pseudoterminal-e-sinais`: é ali que
ele é cobrado, porque sinal, grupo de processos e descritor vistos de dentro supõem os
mesmos vistos de fora.

As competências da área descrevem o emulador, não a linguagem, e as verificações
são de comportamento observável — a máquina de estados para num estado nomeável diante
de entrada hostil, `Ctrl-C` chega ao grupo de processos em primeiro plano, o emoji com
ZWJ ocupa o número de células que o anexo do Unicode manda. Qualquer das três pilhas as
satisfaz.

## Consequências

- **O catálogo não barra quem não programa.** Um estudante sem nenhuma competência de
  programação pode se matricular e vai atravessar a especificação, o analisador e a
  grade antes de bater no projeto de `etapa:terminal/projeto-emulador-minimo`, que
  pressupõe escrever código em alguma linguagem. Isso é precisamente o modo de falha
  que a ADR-0010 condenou, aceito aqui por não haver como declará-lo sem a forma (3) ou
  sem a cascata de sete. Fica dito, não escondido.
- **A forma (3) é o caminho de migração, e esta decisão não o fecha.** Se a etapa
  avulsa de programação de sistemas nascer, ela entra nos `requires` desta trilha e em
  `etapas_referenciadas`, a etapa afetada sobe `rev` e a trilha também, pela tabela de
  [catalogo.md §4](../catalogo.md). O id é imutável
  ([ADR-0005](0005-identidade-imutavel-e-depreciacao.md)) e nada precisa ser recriado.
- **A diferença entre esta decisão e a ADR-0010 é a cascata, não o princípio.** As
  duas querem pré-requisito declarado. O que decide é o custo: uma etapa com
  `requires: []` se referencia por uma linha; uma etapa no meio de uma trilha arrasta
  tudo que a destrava, porque a validação 6 parte de perfil vazio sobre as etapas da
  própria trilha. Quem for declarar pré-requisito entre trilhas no futuro mede essa
  cascata antes de escolher a forma.
- **A trilha é toda de acesso aberto e toda em inglês.** Nenhum recurso dela custa
  nada, o que a torna imune ao filtro de `custo_maximo` do motor
  ([motor §2.2](../motor-de-sugestao.md)) e dispensa `obra`
  ([ADR-0009](0009-obra-como-campo-de-agrupamento-no-recurso.md)); e nenhum está em
  pt-BR, porque material de estudo em português sobre o assunto não foi encontrado em
  2026-10-19. A consequência é de alcance: a trilha exclui quem não lê inglês técnico,
  e nenhuma etapa tem alternativa. Registrado em comentário no YAML dos recursos, com
  o que foi procurado, para não ser pesquisado de novo.
- **`docs/bibliografia.md` não ganha ficha nenhuma.** O assunto não tem livro-texto: a
  literatura é especificação, página de manual, documentação de biblioteca e
  código-fonte. A bibliografia é ficha de livro, e uma trilha inteira sem livro é fato
  novo no catálogo — até aqui, toda trilha tinha ao menos um.
- **Custo**: uma área nova a manter — competências, etapas e recursos, cuja contagem
  se lê do lock e não daqui —, e um pré-requisito de linguagem que o catálogo afirma
  por omissão, o oposto do que a ADR-0010 conquistou, em troca de não duplicar a trilha
  de C dentro desta.
