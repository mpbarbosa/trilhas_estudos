# ADR-0011 — Python no servidor como ramo opcional da trilha web

- **Data**: 2026-10-17
- **Status**: aceito

## Contexto

[docs/acervo-lido.md § 3.2](../acervo-lido.md) aponta que o catálogo tem servidor só
em Node. `etapa:web/javascript-no-servidor` é o único lugar onde alguém serve HTTP, e
Python aparece em `trilha:dados/analise-de-dados-com-python` e em
`etapa:programacao/python-para-ia` sempre como linguagem de análise.

O que torna esta lacuna diferente das outras cinco do § 3 é a origem: ela não vem da
estante, vem **de dentro do repositório**. A camada de entrega decidida em
[ADR-0007](0007-entrega-web-em-python-html-no-servidor.md) é Python com HTML no
servidor, está construída em `src/trilhas/web/` — Starlette, Jinja2, `apresentar/`
puro de propósito, SVG gerado no servidor — e **nenhuma etapa do catálogo ensina a
construí-la**. O catálogo descreve o que o estudante deve saber fazer; o repositório é
a prova de que esta competência é exercida e de que ela não está descrita.

Isso muda o peso do argumento com que
[ADR-0010](0010-shell-como-pre-requisito-declarado.md) recusou abrir trilha nova —
*"dois livros não são semente de trilha"*. Aqui não se trata de contar livros. Mas o
argumento se mantém por outro caminho, e está na Decisão.

Também não é o caso do § 3.1. Shell era **pré-requisito implícito**: duas trilhas
ativas o pressupunham sem declarar, e o estudante travava sem que o catálogo soubesse
dizer por quê. Nada no catálogo de hoje pressupõe servir HTTP em Python. Esta lacuna é
de **assunto ausente**, e a forma de fechá-la é outra.

Três formas foram consideradas:

1. **Etapa dentro de `trilha:web/do-protocolo-a-interface`**, que já se chama "do
   protocolo à interface" e já carrega um ramo de servidor.
2. **Etapa avulsa** em `catalogo/etapas/avulsas.yaml`, no padrão que ADR-0010
   estabeleceu, referenciada pelas trilhas que a comportem.
3. **Trilha nova** de aplicação web em Python.

A (2) tropeça no próprio arquivo: o cabeçalho de `avulsas.yaml` diz que ali moram as
etapas *"referenciadas por mais de uma"* trilha, e só uma tem razão de carregar esta.
As candidatas seriam `trilha:dados/analise-de-dados-com-python`, cujo objetivo é
analisar dado, e `trilha:engenharia/arquitetura-e-entrega`, que decide arquitetura e
opera entrega sem escrever servidor; referenciá-la em qualquer das duas a incluiria na
trilha sem razão — o mesmo erro que ADR-0010 evitou ao **não** referenciar a etapa de
script na trilha de C. Etapa avulsa com um referenciador só é a etapa de uma trilha,
escrita no arquivo errado.

A (3) é decisão de **escopo**, e uma competência não a sustenta. Uma trilha tem
objetivo declarado e matrícula própria ([CONTEXT.md §1](../CONTEXT.md)); "aplicação web
em Python" com uma etapa dentro é objetivo que se satisfaz na primeira etapa, e a
validação 6 passaria sem que a trilha significasse nada. O que sustentaria uma trilha
seria a cadeia inteira — formulário e escrita, sessão e autenticação, ORM e migração,
implantação —, e nada disso está decidido aqui: autenticação está fora de escopo
([CONTEXT §5](../CONTEXT.md)) e a persistência de percurso é ADR própria ainda não
escrita. Abrir a trilha hoje seria declarar um objetivo que o catálogo não pode cumprir.

## Decisão

**Uma etapa nova, opcional, dentro de `trilha:web/do-protocolo-a-interface`** —
a opção 1:

| Entidade | Papel |
|---|---|
| `comp:web/python-no-servidor` | a competência que faltava |
| `etapa:web/python-no-servidor` | `opcional: true`; ramo, irmão do de Node |

E a trilha passa a **referenciar** `etapa:programacao/python-para-ia`, que desenvolve
`comp:programacao/python-dados` — o pré-requisito que a etapa nova exige.

**`opcional: true` não é hesitação, é o modelo.** O objetivo declarado da trilha é
interface por componentes, HTTP e acessibilidade; servir HTTP em Python não é exigido
por nenhum dos três, e é exatamente o que `opcional` significa aqui — o mesmo papel
que `etapa:web/javascript-no-servidor` e `etapa:web/visualizacao-com-d3` já têm. A
consequência de percurso vem de graça: etapa opcional acrescentada é **cosmética** para
a trilha ([catalogo.md §4](../catalogo.md)), então a `rev` da trilha fica em 1, nenhuma
trilha concluída reabre e as etapas que `est:mpb` tem em andamento nesta trilha
(`etapa:web/interface-por-componentes`, `etapa:web/javascript-no-servidor`) não são
tocadas. Fechar a lacuna não custou `rev` nenhuma.

**Uma competência, não duas.** ADR-0010 partiu shell em duas porque só a primeira era
pré-requisito das trilhas que a pressupunham — a divisão tinha consequência. Aqui não
há o que dividir: separar "HTTP em Python" de "template no servidor" criaria uma etapa
cujo único diferencial em relação à de Node é a linguagem — fraca — e outra que não se
sustenta sozinha, porque template sem pedido que o renderize não é competência. O que
há de novo é precisamente a **junção**, e é ela que a `verificacao` cobra.

**Irmã da de Node e distinta dela.** `comp:web/javascript-no-servidor` cobra servir API
sem framework e medir o que custa bloquear o laço de eventos. Esta cobra a página
montada no servidor: URL endereçável que abre sempre o mesmo conteúdo sem estado de
sessão, template base herdado, e o cálculo exibido vivendo **fora** do template,
exercitável por teste que não sobe servidor. São os três requisitos de ADR-0007 virados
em critério de verificação.

**Flask é o recurso primário; Starlette é o segundo; o livro do acervo é apoio.**
A pergunta "Flask ou o que o projeto usa?" tem resposta só se a competência for a
*forma* e não o framework, e é assim que ela está escrita. Decidido:

- **Documentação oficial do Flask** (`rec:web/flask-docs`, gratuita) como primária: é
  WSGI e síncrona, tem o tutorial canônico do assunto — aplicação completa com fábrica,
  blueprint, template, teste e implantação — e é o framework do livro que o estudante
  tem.
- **Documentação oficial do Starlette** (`rec:web/starlette-docs`, gratuita) como
  segunda via: é ASGI, é o que este repositório usa, e tem o mesmo Jinja2 por baixo. A
  diferença entre WSGI e ASGI é **conteúdo** da etapa, não detalhe a esconder atrás da
  escolha de um framework só — e a mesma forma vista nos dois modelos de execução é o
  que separa aprender a camada de aprender uma API.
- **O livro do acervo como apoio conceitual**, com o limite dito no título, na
  convenção que `recursos/web.yaml` e `dados.yaml` já usam para os livros de D3.

**Não se escolheu FastAPI**, pelo motivo de ADR-0007 e por outro: as respostas são
HTML, e serialização automática não resolve problema que exista aqui.

## Consequências

- **O repositório passa a ser descrito pelo próprio catálogo.** A camada construída em
  `src/trilhas/web/` tem agora a competência que a descreve, e a `verificacao` dela
  cobra os três requisitos que ADR-0007 listou. Quem concluir a etapa sabe ler esse
  código.
- **`rev` de nada subiu.** Uma competência nova, uma etapa nova, três recursos novos,
  uma referência nova — e nenhuma `rev` alterada em entidade que já existia, porque
  etapa opcional é cosmética para a trilha e recurso nunca altera a `rev` da etapa
  ([catalogo.md §4](../catalogo.md)). Nenhum fato de percurso é afetado.
- **A referência a `etapa:programacao/python-para-ia` é o que faz a etapa alcançável.**
  Sem ela, `comp:programacao/python-dados` seria pré-requisito que a trilha exige e não
  oferece: a etapa que o desenvolve ficaria fora do grafo da matrícula e o estudante
  travaria sem receber o que o destrava ([motor §2.1](../motor-de-sugestao.md)). É o
  mesmo mecanismo que ADR-0010 chamou de "referenciar não é decoração", e é a terceira
  trilha a referenciar essa etapa — o padrão de `etapas_referenciadas` funcionando como
  foi desenhado.
- **Pré-requisito cruzando área.** `comp:programacao/python-dados` é pré-requisito de
  uma etapa de `web/`, como `comp:so/linha-de-comando` é de uma de `programacao/`.
  `area` é organizacional, não semântica ([catalogo.md §3](../catalogo.md)).
- **O único recurso pt-BR da etapa é pago.** Quem estudar com `custo_maximo: 0` fica
  com as duas documentações, ambas en-US
  ([motor §2.2](../motor-de-sugestao.md)). Registrado em comentário no YAML. É o
  inverso do caso de ADR-0010, onde faltava o pago em pt-BR.
- **Dois frameworks numa etapa é custo de manutenção.** Duas documentações para
  reverificar, e duas que podem divergir no que ensinam sobre a mesma forma. Aceito:
  esconder a divisão WSGI/ASGI atrás de um framework só ensinaria a API em vez da
  camada, e é a camada que ADR-0007 decidiu.
- **A trilha ganhou um segundo ramo de servidor e segue sem dizer isso no título.**
  "Do protocolo à interface" cobre o que a trilha faz; os ramos são ramos. Se os ramos
  crescerem — formulário e escrita, sessão, ORM, implantação —, a trilha de aplicação
  web em Python nasce **referenciando** esta etapa, sem recriá-la, porque o id é imutável
  ([ADR-0005](0005-identidade-imutavel-e-depreciacao.md)). Esta decisão é caminho de
  migração, não obstáculo — igual ao que ADR-0010 deixou aberto para a trilha de UNIX.
- **Fica aberto** se o catálogo deve ensinar escrita no servidor (formulário, validação,
  CSRF, sessão). A etapa de agora é de leitura, como a primeira entrega de ADR-0007. A
  decisão depende da ADR de persistência de percurso, que ainda não existe.
