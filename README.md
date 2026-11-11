# trilhas_estudos

Controle e sugestão de trilhas de estudo: acompanha o avanço do estudante numa
trilha e recomenda o que estudar em seguida.

**Estado atual:** domínio modelado, catálogo validável, motor de sugestão implementado
como lógica pura (`src/trilhas/motor/`) e uma interface de leitura. O painel *Agora*
já mostra as sugestões do motor com os fatores que as produziram; o que ainda não há é
persistência do percurso — nada do que o estudante faz é gravado.

- [Domínio e glossário](docs/CONTEXT.md)
- [Motor de sugestão (v1)](docs/motor-de-sugestao.md) — especificação e escolhas da implementação
- [Interface gráfica](docs/interface.md) — stack, telas e fases; a fase 1 está no ar
- [Catálogo](docs/catalogo.md) — autoria em YAML, identidade e versionamento
- [Conteúdo do catálogo](catalogo/) — trilhas autoradas:
  - *Do transformer ao RAG em produção* ([trilha](catalogo/trilhas/llm-transformer-rag.yaml)) — fundamento e recuperação
  - *Do chat ao agente em produção com Claude* ([trilha](catalogo/trilhas/claude-do-chat-ao-agente.yaml)) — aplicação: API, hospedagem em nuvem, ferramentas, MCP e agentes
  - *Análise de dados com Python* ([trilha](catalogo/trilhas/dados-com-python.yaml)) — manipulação, exploração, estatística e enquadramento
  - *Web, do protocolo à interface* ([trilha](catalogo/trilhas/web-do-protocolo-a-interface.yaml)) — HTTP, documento, JavaScript, tipos e componentes
  - *Arquitetura e entrega de software* ([trilha](catalogo/trilhas/arquitetura-e-entrega.yaml)) — requisitos, trade-off, decomposição, pipeline e operação
  - *Matemática — da demonstração ao cálculo* ([trilha](catalogo/trilhas/matematica-prova-e-calculo.yaml)) — prova, geometria axiomática, cálculo e simetria
  - *Sistemas operacionais, do conceito ao núcleo* ([trilha](catalogo/trilhas/so-projeto-e-implementacao.yaml)) — processos, memória, E/S, arquivos e prática no MINIX
  - *Bancos de dados relacionais, do modelo à transação* ([trilha](catalogo/trilhas/bancos-de-dados-relacionais.yaml)) — arquitetura, modelo relacional, álgebra, SQL, normalização e transação
  - *Linguagem C, do tutorial à interface com o UNIX* ([trilha](catalogo/trilhas/linguagem-c-ansi.yaml)) — tipos, funções, apontadores, estruturas, E/S e chamadas de sistema
  - *O modelo de Markov da linguagem natural* ([trilha](catalogo/trilhas/modelo-de-markov-da-linguagem.yaml)) — n-gramas, perplexidade, suavização, gerador de texto, HMM e etiquetagem
  - *Tecnofeudalismo — economia política do capital de nuvem* ([trilha](catalogo/trilhas/tecnofeudalismo.yaml)) — lucro e renda, capital de nuvem, geopolítica e a crítica da tese
  - *Emulador de terminal, do protocolo à tela* ([trilha](catalogo/trilhas/emulador-de-terminal.yaml)) — ECMA-48 e a linhagem DEC, analisador de estados, grade de células, pseudoterminal, teclado, Unicode em grade, renderização e conformidade
  - *Sintaxe do inglês — da oração simples ao período composto* ([trilha](catalogo/trilhas/sintaxe-do-ingles.yaml)) — constituintes e funções, sintagmas, orações não finitas, sintagma complexo e construções
  - *Inglês geral no nível B2 — gramática em uso, conversação e escrita* ([trilha](catalogo/trilhas/ingles-geral-b2.yaml)) — o *Viewpoint 1* em quatro blocos de três unidades: tempos e relativas, condicionais e futuro, passiva e quantificadores, discurso indireto e comparação
  - *Bhagavad Gita — do porquê ler ao texto e à crítica* ([trilha](catalogo/trilhas/bhagavad-gita.yaml)) — contexto e conceitos centrais, os dezoito capítulos do diálogo e a Gita lida pela filosofia acadêmica
  - *Literatura em inglês — "The Raven" de Poe, do poema à poética e à crítica* ([trilha](catalogo/trilhas/poe-o-corvo.yaml)) — o poema no inglês de 1845, o ensaio em que Poe diz como o compôs e a crítica que o contradiz
  - *Estatística na avaliação de modelos* ([trilha](catalogo/trilhas/estatistica-na-avaliacao-de-modelos.yaml)) — dispersão do desempenho, viés e variância, viés de amostragem, intervalo de confiança, escolha do teste, tamanho de efeito e o t pareado corrigido de Nadeau e Bengio
  - *Compiladores — da análise do fonte ao código gerado* ([trilha](catalogo/trilhas/compiladores.yaml)) — estrutura e fases, análise léxica, análise sintática, análise semântica e geração de código, pela espinha de Price & Toscani
  - *Cinema — do primeiro cinema à invenção da vida moderna* ([trilha](catalogo/trilhas/primeiro-cinema-e-vida-moderna.yaml)) — vocabulário de leitura de filme em Bernardet, a era dos impérios em Hobsbawm, o primeiro cinema em Flávia Cesarino Costa e a modernidade urbana na coletânea de Charney & Schwartz
  - *TypeScript — do tipo primitivo à arquitetura de tipos* ([trilha](catalogo/trilhas/typescript-sistema-de-tipos.yaml)) — ambiente e anotação, objeto, função e classe, união e estreitamento, genéricos, derivação e transformação de tipos, predicado e função de asserção, configuração do compilador e arquitetura, pelo *Total TypeScript* de Matt Pocock com Taylor Bell
  - *Totalitarismo — do domínio total ao medo de ser livre* ([trilha](catalogo/trilhas/totalitarismo-e-fuga-da-liberdade.yaml)) — os mecanismos de fuga da liberdade em Fromm, o movimento e o regime totalitários na parte III de Arendt, o conceito enunciado em "Ideologia e terror" e as duas explicações da adesão postas em conflito
  - *Estetização da política — da reprodutibilidade técnica ao comício filmado* ([trilha](catalogo/trilhas/estetizacao-da-politica.yaml)) — a reprodutibilidade técnica em Benjamin, a massa como forma em Kracauer, *O triunfo da vontade* como objeto, a crítica de Susan Sontag e o espetáculo visto de dentro na memória de Albert Speer
  - *Edição de texto no terminal — o vi, dos modos ao `ex` e à repetição* ([trilha](catalogo/trilhas/edicao-de-texto-no-vi.yaml)) — modos e a gramática de operador e movimento, faixa de endereços e substituição global no `ex`, registros e macros gravadas, configuração e consulta à ajuda interna, e o editor entre processos: janelas, filtros do UNIX e compilação, pelo *vi Editor Pocket Reference* de Arnold Robbins
  - *Análise fílmica de uma saga — o plano, o mito, o som e o efeito especial* ([trilha](catalogo/trilhas/analise-filmica-de-uma-saga.yaml)) — forma narrativa e os quatro sistemas de estilo em Bordwell & Thompson, som e ponto de escuta em Chion com a música narrativa de Gorbman, o modo melodramático em Peter Brooks, o monomito de Campbell e a conta que ele deve, o efeito especial como sublime em Bukatman, a herança expressionista em Lotte Eisner, arte e indústria em Rosenfeld e Sklar, o filme como fonte histórica em Marc Ferro com o método de Chartier, a contracultura de Roszak e a saga lida de fora por Irwin e Mike Thorn
  - *Desinformação e resistência — da prova audiovisual falsificada ao transcrito oculto* ([trilha](catalogo/trilhas/desinformacao-e-resistencia.yaml)) — a língua estreitada e o arquivo corrigido em *1984*, o olhar que disciplina em *Vigiar e punir*, o fascismo como processo em Paxton, o deep fake como problema público em Chesney & Citron e em Fornasier, Cury e Holanda, o transcrito oculto de James Scott, a estrutura de oportunidade em McAdam e Goodwin, a ascensão narrada de perto por Konrad Heiden e a ruptura feita no rito em Fares Paulo e Lopes de Siqueira
  - *WebAssembly por dentro — do primeiro módulo ao binário e ao WASI* ([trilha](catalogo/trilhas/webassembly-por-dentro.yaml)) — o que o formato é e o que ele não é, máquina virtual e primeiro módulo compilado, a API do hospedeiro com memória linear, globais e tabelas, um editor de imagem medido contra a mesma conta em JavaScript, interface binária e vinculação, codificação de dados na travessia, memória compartilhada e atômicos, os três momentos de falha e o formato de texto, estrutura binária com WABT e Binaryen, e o WASI fora do navegador, pelo *Desmistificando WebAssembly* de Raphael Amorim
  - *Arquitetura de computadores — da máquina hipotética ao computador pessoal* ([trilha](catalogo/trilhas/arquitetura-de-computadores.yaml)) — organização de von Neumann nas máquinas Neander, Ahmes e Ramses, conjunto de instruções e montagem no Cesar, o computador pessoal por dentro e, opcional, a concepção de circuitos integrados, pelos livros de Raul Fernando Weber e Ricardo Reis
  - *Teoria da computação — linguagens formais, computabilidade e complexidade* ([trilha](catalogo/trilhas/teoria-da-computacao.yaml)) — autômatos e a hierarquia de Chomsky, máquinas universais e o indecidível, análise assintótica e NP-completude e, opcional, teoria das categorias, pelos livros de Menezes, Diverio, Toscani & Veloso e Menezes & Haeusler
  - *Computação intervalar — o resultado numérico com erro garantido* ([trilha](catalogo/trilhas/computacao-intervalar.yaml)) — aritmética intervalar, dependência e extensão intervalar, e computação verificada em Pascal-XSC, pelos livros de Oliveira, Diverio & Claudio e de Hoher, Holbig & Diverio

  Fora das trilhas, três [etapas avulsas](catalogo/etapas/avulsas.yaml) de
  pré-requisito compartilhado das trilhas de SO, de C, de emulador de terminal e de
  edição de texto no vi: duas de shell e linha de comando, declaradas em
  [ADR-0010](docs/adr/0010-shell-como-pre-requisito-declarado.md), e uma de
  programação de sistemas — descritor, estrutura em memória e programa em módulos,
  sem linguagem declarada —, em
  [ADR-0018](docs/adr/0018-programacao-de-sistemas-como-pre-requisito-compartilhado.md).
- [Decisões de arquitetura](docs/README.md)

## Uso

Requer Python 3.12+. O catálogo é autorado em `catalogo/` e compilado para
`catalogo.lock.json`, o único artefato que a aplicação consome.

```bash
uv run trilhas validar              # valida o catálogo (0 = válido, 1 = com erro)
uv run trilhas compilar             # grava o snapshot se o conteúdo mudou
uv run --extra dev pytest           # suíte completa
```

### Interface

Em `localhost`: o painel *Agora* com as sugestões do motor e os fatores que as
produziram, o grafo da trilha por onda de pré-requisito, a etapa com os recursos
comparados, a competência com o critério de verificação, e as 13 validações numa
tela ([docs/interface.md](docs/interface.md)).

```bash
uv run --extra web trilhas-web      # http://127.0.0.1:8000
```

Somente leitura: registrar progresso, evidência e feedback depende da decisão de
persistência do percurso.

## Licença

MIT — ver [LICENSE](LICENSE).
