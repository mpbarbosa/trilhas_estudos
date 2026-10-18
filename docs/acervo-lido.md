# Acervo lido × catálogo — cruzamento de 2026-10-17

Cruzamento entre a estante **Read** do Goodreads do estudante (122 registros,
extraídos em 2026-10-17) e os recursos de `catalogo/recursos/`.

Este documento é **descritivo e datado**, no mesmo gênero de
[bibliografia.md](bibliografia.md): nada aqui entra na validação nem no
`catalogo.lock.json`, e nada aqui autoriza uma mudança de catálogo. Ele existe
para embasar a decisão de catalogar — que é do estudante — e para registrar o
que foi considerado e **descartado**, que é a parte que se perde quando a
decisão é tomada numa conversa.

Ele envelhece de dois lados: a estante cresce, e cada obra catalogada muda de
seção. A ficha bibliográfica de qualquer obra que venha a ser catalogada é
mantida em [bibliografia.md](bibliografia.md), não aqui — aqui ficam só o
veredito e o motivo.

## Como o cruzamento foi feito

- **Universo.** Das 122 linhas, 17 carregam alguma das estantes técnicas
  declaradas no pedido (`programming`, `computer-science`, `data-analysis`,
  `technology`, `javascript`, `python`, `java`, `linux`, `shell-script`, `git`,
  `ia`, `iot`, `agile`, `bpmn`, `project-management`, `math`,
  `system-analysis`, `web-development`, `data-migration`). A estante
  `system-analysis` não ocorre em nenhuma linha da lista — o filtro a cita, a
  estante não existe no recorte.
- **Comparação.** Por título **e** autor contra os 163 recursos do snapshot de
  então (`catalogo_versao` 17), não
  só por título: o catálogo tem obras de autor repetido em livros diferentes
  (Downey entra por *Think Stats*, não por *Think Python*).
- **Fatias.** Uma obra do catálogo pode estar fatiada em vários recursos
  ([ADR-0009](adr/0009-obra-como-campo-de-agrupamento-no-recurso.md)), e nesse
  caso nenhum título de recurso é o título do livro. Conferi as 13 `obra`
  declaradas uma a uma — `date-vol1`, `handson-ml`, `kline-calculus`,
  `partes-dificeis`, `ai-engineering`, `ai-powered-search`, `biblia-claude`,
  `kernighan-pike-tpop`, `kernighan-ritchie-c`, `koehn-nmt`,
  `llm-eng-handbook`, `manning-schutze-fsnlp`, `tanenbaum-woodhull`: **nenhuma**
  corresponde a obra da estante. O risco de falso negativo por fatiamento está
  afastado, não assumido.
- **Fora do filtro.** Cinco linhas sem estante alguma são técnicas e entram no
  § 5, porque o filtro por estante as perde: a estante do Goodreads é
  incompleta, não é esquema.

---

## 1. Já catalogada — 5 obras

| # | Obra | Recurso | Etapa | Desde |
|---|---|---|---|---|
| 11 | *Ry's Git Tutorial* (Ryan Hodson) | `rec:engenharia/rys-git-tutorial` | `etapa:engenharia/controle-de-versao` | antes deste cruzamento |
| 90 | *The Visual Display of Quantitative Information* (Tufte) | `rec:dados/tufte-visual-display` | `etapa:dados/visualizacao-para-analise` | 2026-10-17 |
| 3 | *Engenharia de Prompts na Prática* (Edney Souza) | `rec:ia/souza-engenharia-de-prompts` | `etapa:ia/engenharia-de-prompt` | 2026-10-17 |
| 16 | *Shell Script Profissional* (Aurélio Jargas) | `rec:so/jargas-shell-script-profissional` | `etapa:so/script-shell` | 2026-10-17 |
| 13 | *Linux Command Line and Shell Scripting Bible* (Blum) | `rec:so/blum-bible-linha-de-comando`, `rec:so/blum-bible-script-shell` | `etapa:so/linha-de-comando`, `etapa:so/script-shell` | 2026-10-17 |

Ry's Git Tutorial era a **única** correspondência quando o cruzamento foi feito —
16 das 17 obras técnicas da estante não estavam no catálogo, que foi construído
sem consultá-la. As outras quatro entraram no mesmo dia, por decisão do estudante:
Tufte e Souza sobre o § 2, Jargas e Blum sobre a lacuna do § 3.1, que deixou de ser
lacuna. O que a conferência de exemplar encontrou está abaixo, porque é o que
justifica a forma como cada recurso ficou.

**#90 Tufte** — 2ª ed., Graphics Press, 2001, 197 p., ISBN-10 `0961392142`.
Confirmado pelo site do autor e pela loja brasileira. Entrou como `custo: 220`
(preço de loja em 2026-10-17), `idioma: en-US`, `formato: texto`. Achado que mudou
a entrada: a obra **só existe em papel** — a Graphics Press nunca publicou edição
eletrônica —, então a ressalva de `disponivel` do cabeçalho de
`catalogo/recursos/dados.yaml`, que trata de amostra de acervo Kindle, não a
alcança. O YAML registra isso num comentário, e também que `custo` ali é preço de
reposição, não o que foi pago — a ambiguidade entre os dois é a divergência 7 de
[bibliografia.md](bibliografia.md) e não se resolveu aqui.

**#3 Souza** — ASIN `B0CKNQ92PK`, atualizado em outubro/2026, 320 p., 15 capítulos
e 3 apêndices. Dois achados, em sentidos opostos:

- *A favor, mais do que se previa:* o livro é **gratuito**, em PDF completo, pelo
  próprio autor (https://interney.net/livro-ia, mediante formulário). O § 2.2
  pedia "uma alternativa pt-BR e barata"; a etapa ganhou uma de `custo: 0`.
- *Contra, e confirmado:* a ressalva do § 2.2 estava certa e é pior do que
  "provavelmente". O livro é declaradamente "sem escrever código" e não trata
  parâmetro de decodificação, saída estruturada por API, custo nem latência por
  chamada — ou seja, **não cobre `comp:ia/uso-de-llm-por-api`**, que é a segunda
  das duas competências que a etapa desenvolve. Foi catalogado como alternativa
  parcial, com o limite dito no título do recurso e num comentário em
  `catalogo/recursos/ia.yaml`; `rec:ia/prompt-engineering-for-llms` segue sendo o
  único recurso que carrega a etapa inteira, e por isso não foi tocado.

Isso deixa à vista um limite do esquema, não um erro desta entrada: um recurso
pertence a uma etapa e a realiza por inteiro ou não — não há como declarar que
cobre uma das duas competências de `teaches`. Enquanto não houver,
`etapa:ia/engenharia-de-prompt` credita `comp:ia/uso-de-llm-por-api` a quem a
concluir só pelo Souza. Decidir se isso merece ADR, etapa separada ou nada é
assunto de escopo, fora deste relatório.

**#16 Jargas e #13 Blum** — entraram juntas, porque entraram pela lacuna e não pelo
livro: a decisão de forma está em
[ADR-0010](adr/0010-shell-como-pre-requisito-declarado.md), e as duas etapas novas
são `etapa:so/linha-de-comando` (obrigatória, referenciada pelas duas trilhas que a
pressupunham) e `etapa:so/script-shell` (opcional). Três achados mudaram as entradas:

- **Jargas não serve a etapa de linha de comando.** 1ª ed., Novatec, 2008, 480 p.,
  ISBN-13 978-85-7522-152-5, à venda na editora por R$ 109,00. Conferido o conteúdo,
  é livro sobre **escrever script que se mantenha** — portabilidade, POSIX contra
  bash, estilo — e pressupõe a casca em vez de ensiná-la. Foi para
  `etapa:so/script-shell` só. O relatório o trazia como "livro pt-BR curto e bem
  avaliado no assunto", o que era vago sobre qual metade do assunto.
- **Blum está numa edição posterior à lida.** 5ª ed., Wiley, 30/12/2025, 688 p.,
  ISBN-13 978-1-394-36494-7 — a edição do exemplar da estante não se identificou. O
  catálogo aponta a 5ª, que é a que se compra, e a diferença não morde: é o caso de
  defasagem tolerável do § 4. Fatiado em dois recursos, um por etapa, com
  `obra: blum-bible` e `custo: 270` nas duas
  ([ADR-0009](adr/0009-obra-como-campo-de-agrupamento-no-recurso.md)). Curiosidade de
  loja que ficou registrada na ficha: o Kindle (R$ 323,00) sai mais caro que a capa
  comum (R$ 268,78).
- **A estante não dava o gratuito, e as duas etapas precisavam de um.** Etapa servida
  só por livro pago é filtrada por `custo_maximo` ([motor §2.2](motor-de-sugestao.md)).
  Entrou *The Linux Command Line* de William Shotts, 7ª edição de internet, 596 p.,
  PDF livre em Creative Commons, fatiado nas duas etapas. Sobrou um vão declarado:
  para `etapa:so/linha-de-comando` **não há material gratuito e em pt-BR que a
  carregue inteira** — a tradução do Shotts está em andamento, e o que entrou foi o
  Guia Foca Linux, parado desde julho de 2020. As apostilas do próprio Jargas
  (*Introdução ao Shell Script*, 22 p.; o *Canivete Suíço*, tabela de consulta) são
  curtas demais para realizar uma etapa. Está em comentário em
  `catalogo/recursos/so.yaml` para não ser pesquisado de novo.

---

## 2. Não catalogada, mas cabe numa etapa ativa — 6 obras

Ordenadas por quanto acrescentam, não por nota. "Acrescenta" aqui é uma de duas
coisas: cobrir uma etapa que hoje depende de um recurso só, ou dar idioma ou
custo que os recursos atuais da etapa não dão — os dois são filtros do motor
([motor §2.2](motor-de-sugestao.md)).

### 2.1 Tufte · 2.2 Souza — catalogadas em 2026-10-17

As duas candidatas mais fortes saíram desta seção e estão no § 1, com o resultado
da conferência de exemplar. A numeração das subseções seguintes **não** foi
remexida: 2.3 continua sendo 2.3 em qualquer referência a este relatório.

### 2.3 Severance, *Python for Everybody* (#39, nota 3)

→ `etapa:programacao/python-para-ia`

A competência resultante é `comp:programacao/python-dados` em nível
**iniciante**. Os dois recursos atuais ficam acima disso: *Python Fluente* é
livro de Python intermediário-avançado, e *Automate the Boring Stuff* é
automação, não dado. PY4E é o único material de nível iniciante de fato, é de
acesso aberto e tem tradução em português. Encaixe de nível, não só de assunto.

### 2.4 Downey, *Think Python* (#108, sem nota de leitura, nota 4)

→ `etapa:programacao/python-para-ia`

Mesma vaga de 2.3, mesmo argumento, acesso aberto. Vale como **alternativa** a
PY4E, não como adição às duas: três recursos de introdução a Python na mesma
etapa é redundância, não escolha. Atenção ao autor: o catálogo já cita Downey em
`rec:dados/think-stats`, obra diferente — não é fatia, é outro livro.
*(Fora do filtro por estante; ver § 5.)*

### 2.5 Rafael Santos, *Álgebra Linear com Python* (#36, nota 3)

→ `etapa:dados/matematica-para-dados`

A etapa exige `comp:programacao/python-dados` ≥ iniciante e desenvolve
"álgebra linear e cálculo **na medida em que sustentam o método**: vetores,
matrizes, produto interno, derivada, gradiente e otimização". Um texto de
álgebra linear que já vem em Python casa com o pré-requisito em vez de pedir
tradução mental. Ficaria como quarto recurso ao lado de Dianguila (pt-BR),
3Blue1Brown (vídeo) e Kline (cálculo) — a etapa está bem servida, então o ganho
é de alternativa, não de cobertura.

### 2.6 Tabak, *Algebra: Sets, Symbols, and the Language of Thought* (#97, nota 3)

→ `etapa:matematica/simetria-e-grupos`

A etapa já usa dois livros de divulgação do Ian Stewart (`stewart-simetria`,
`stewart-misterios`), rotulados como divulgação nos próprios títulos de recurso,
ao lado do Judson (texto formal aberto). Tabak é história da álgebra na mesma
chave: motiva a abstração antes do formalismo. Entra num padrão já estabelecido
pela etapa, o que é o melhor argumento que uma obra de divulgação pode ter aqui.

### 2.7 J.C. Ködel, *Spec Driven Development* (#2, nota 2)

→ `etapa:ia/claude-code-e-skills`

A competência é "trabalhar num repositório com um agente de codificação:
instruções de projeto, skills, subagentes, **revisão do que o agente propõe e
decisão sobre o que aceitar**". Especificar antes de gerar é método para
exatamente essa última parte, e o livro é pt-BR e recente (2025) — raro nesta
etapa, onde o outro recurso pt-BR é uma fatia da Bíblia do Claude. Contra:
nota 2 do estudante, e a etapa já tem dois recursos.

### 2.8 Mike Turner, *User Stories....Unleashed* (#116, sem nota)

→ `etapa:engenharia/requisitos-e-atributos`

Cabe pela metade. A competência tem duas: "elicitar e decompor o que o sistema
deve fazer" — história de usuário é técnica canônica disso — e "atributo de
qualidade **mensurável**", que história de usuário notoriamente não entrega, e é
justamente por isso que a etapa tem o arc42 e o Hathaway. Entraria como recurso
da primeira metade. Sem nota de leitura registrada, o que também é sinal.

### 2.9 Matheus Battisti, *Fundamentos do React JS* (#1, nota 2)

→ `etapa:web/interface-por-componentes`

Cabe pelo assunto e **não acrescenta**. A etapa já tem três recursos, entre eles
um pt-BR (*React Fluente*); a nota do estudante é 2; e o título sugere React
introdutório, que é o caso em que a defasagem morde (§ 4). Listada para que o
descarte fique registrado, não como candidata.

---

## 3. Sem etapa que a comporte — 5 obras, 5 lacunas

Aqui a obra importa menos que a lacuna. Uma lacuna real não se fecha com o livro
que a revelou: o livro é só a evidência de que ela existe.

A numeração das subseções **não** foi remexida: 3.2 continua sendo 3.2 em qualquer
referência a este relatório, e o 3.1 fica como registro da lacuna que se fechou.

### 3.1 Linha de comando e shell — fechada em 2026-10-17

**#13** *Linux Command Line and Shell Scripting Bible* (Blum) · **#16** *Shell
Script Profissional* (Aurélio Jargas, pt-BR) — **as duas estão no § 1.**

Era a lacuna mais consequente do relatório, e foi a primeira a ser fechada, na ordem
que o § 6 sugeria. Nenhuma etapa do catálogo tratava linha de comando, shell ou
automação de tarefa. O mais próximo era `etapa:programacao/c-interface-com-o-unix`,
que é a API do UNIX vista do C (`read`, `write`, `open`, `lseek`) — o sistema por
baixo da biblioteca padrão, não a casca por cima dele.

Era consequente porque **duas trilhas ativas pressupunham a casca sem ensiná-la**:
`trilha:so/projeto-e-implementacao` manda compilar e modificar o MINIX em
máquina virtual (`rec:so/minix3-projeto`), e
`trilha:programacao/linguagem-c-ansi` supõe compilação separada e `make`. O
estudante que não dominasse shell não era barrado por nenhum `requires` — ele
simplesmente travava no projeto. Era o tipo de pré-requisito implícito que o modelo
de competências existe para tornar explícito ([CONTEXT.md §3.2](CONTEXT.md)).

Hoje é declarado. `comp:so/linha-de-comando` entrou nos `requires` das duas etapas
que o pressupunham, e as duas etapas novas vivem em `catalogo/etapas/avulsas.yaml`,
referenciadas pelas trilhas em vez de redefinidas por elas. O que foi decidido e o
que foi recusado — inclusive a trilha de fundamentos de ambiente UNIX, que não se
abriu — está em
[ADR-0010](adr/0010-shell-como-pre-requisito-declarado.md).

### 3.2 Aplicação de servidor em Python

**#32** *Desenvolvimento Web com Flask* (Grinberg, trad. pt-BR)

`trilha:web/do-protocolo-a-interface` tem servidor — mas
`etapa:web/javascript-no-servidor` é Node. Python aparece no catálogo em
`trilha:dados/analise-de-dados-com-python` e em
`etapa:programacao/python-para-ia`, sempre como linguagem de análise, nunca
servindo HTTP.

A lacuna é visível de dentro do próprio repositório: a camada de entrega
decidida em [ADR-0007](adr/0007-entrega-web-em-python-html-no-servidor.md) é
Python com HTML no servidor, e nenhuma etapa do catálogo ensina a construí-la.
Flask é o framework dessa forma exata de aplicação. Pesa contra: a tradução
pt-BR é da 1ª edição (§ 4).

### 3.3 Integração e movimentação de dado (ETL)

**#115** *Pentaho Data Integration Beginner's Guide* (Roldán)

As duas trilhas de dados cobrem **analisar** dado (pandas → EDA → visualização →
estatística → modelo) e **modelar e guardar** dado (modelo relacional → SQL →
índices → transação). Nenhuma cobre **mover e transformar** dado entre sistemas:
extração, carga incremental, reconciliação, dado sujo na fronteira. A estante
`data-migration` do estudante marca um interesse que o catálogo não atende.

A lacuna é real; o Pentaho é um mau ponto de partida para ela (§ 4).

### 3.4 Nada na JVM

**#14** *All About Java 8 Lambdas* (Konda)

O catálogo tem C, Python, JavaScript e TypeScript; nenhuma linguagem de JVM. Pode
ser escopo deliberado — nenhuma ADR diz nada a respeito. Registre-se como fato,
com a ressalva de que um livro curto sobre um recurso de linguagem não é semente
de trilha: abrir a JVM no catálogo é decisão de escopo, não de catalogação.

### 3.5 O computador abaixo do sistema operacional

**#106** *Code: The Hidden Language of Computer Hardware and Software* (Petzold)
*(fora do filtro por estante; ver § 5)*

`trilha:so/projeto-e-implementacao` começa em
`etapa:so/visao-geral-e-chamadas-de-sistema` — "o que é um SO". Abaixo disso não
há nada: porta lógica, representação binária, como uma CPU executa uma
instrução. O Petzold é o livro canônico desse degrau, e é o único material da
estante que o ocupa. Se catalogado, fixar a **2ª edição (2022)**: a 1ª (1999)
termina em hardware da época.

### 3.6 Modelagem de processo de negócio · Ferramenta de BI sem código

**#83** *The BPMN Graphic Handbook* (Herrera) · **#64** *Tableau 10 for
Beginners* (Sinha) · **#75** *The Silent Intelligence: The Internet of Things*
(Kellmereit)

Três lacunas que o relatório nomeia e **não recomenda fechar**:

- **BPMN** é notação de processo de negócio. Nenhuma etapa do catálogo ensina
  notação; `etapa:engenharia/requisitos-e-atributos` chega perto pelo
  `rec:engenharia/vazquez-engenharia-de-requisitos` ("software orientado ao
  negócio"), mas requisito e processo não são a mesma coisa, e forçar a obra ali
  distorceria a competência da etapa.
- **Tableau** é ferramenta de BI sem código. Cabe no *assunto* de
  `etapa:dados/visualizacao-para-analise`, mas não na *competência* dela, que é
  escolher e ler forma gráfica — não operar uma ferramenta. Somado à defasagem
  (§ 4), não há caso.
- **IoT** não tem nenhum ponto de contato no catálogo, e o exemplar é livro de
  mercado de 2013, não material técnico.

---

## 4. Defasagem

Mesma convenção dos comentários de
[`catalogo/recursos/web.yaml`](../catalogo/recursos/web.yaml) e
[`dados.yaml`](../catalogo/recursos/dados.yaml): quando a parte conceitual
envelhece bem e o código não, a documentação oficial é o recurso primário da
etapa e o livro entra como **apoio conceitual**. O que segue aplica esse
critério às obras da estante.

### Defasagem que impede catalogar como recurso primário

| # | Obra | O que mudou |
|---|---|---|
| 64 | *Tableau 10 for Beginners* (2016) | Pior caso da lista: tutorial de ferramenta cuja interface e conjunto de recursos mudaram por completo desde a versão 10. Tutorial de ferramenta defasada não tem metade conceitual que se aproveite. |
| 115 | *Pentaho Data Integration Beginner's Guide* (Kettle 4) | A ferramenta trocou de dono e o campo migrou para dbt/Airflow/Spark. O conceito de ETL (passo, salto, transformação, carga incremental) envelheceu bem; o produto, não. Serviria de apoio conceitual à lacuna de § 3.3 — nunca de recurso primário. |
| 9 | *Learning GitHub Copilot* (Laster) | A categoria mais rápida de todas: modo agente e agente no repositório chegaram depois do livro. Exatamente o caso que o catálogo já resolve nos recursos de IA, onde a documentação oficial é primária e o livro é apoio. |
| 32 | *Desenvolvimento Web com Flask* | Tradução pt-BR da **1ª** edição (2014, Flask 0.10). Flask 2/3 trouxe view assíncrona, e Flask-SQLAlchemy 3 quebrou os padrões do livro. Grinberg publicou 2ª edição (2018) — também anterior a Flask 2. |
| 1 | *Fundamentos do React JS* | Conferir a edição antes de qualquer coisa. React introdutório anterior a 2019 ensina componente de classe, que é justamente o que os recursos atuais da etapa evitam (`rec:web/pure-react-ceddia` é descrito como "sem Redux nem ferramental"). |
| 75 | *The Silent Intelligence* (2013) | Previsão de mercado de IoT de 2013 — hoje é documento histórico, não material de estudo. |

### Defasagem presente mas tolerável

| # | Obra | Leitura |
|---|---|---|
| 14 | *All About Java 8 Lambdas* | O recurso de linguagem em si não mudou; o que datou é tudo em volta (record, sealed, adições a stream, thread virtual) e o fato de que o LTS atual está muito à frente do 8. Se a JVM entrar no catálogo (§ 3.4), não entra por aqui. |
| 11 | *Ry's Git Tutorial* (2014) | **Já catalogado.** O modelo de objetos do git é estável e a ficha de bibliografia.md já registra a data. Sem ação. |
| 13 / 16 | *Shell Scripting Bible* · *Shell Script Profissional* | **Já catalogadas** (§ 1). Bash e o shell POSIX são conservadores, e as duas estão entre as menos defasadas da estante — o que reforçou a lacuna de § 3.1 em vez de enfraquecê-la, e foi parte do argumento para fechá-la. A conferência de exemplar acrescentou um dado: o Blum está na 5ª edição (12/2025), posterior ao exemplar lido, e o catálogo aponta a 5ª; para estas etapas a diferença entre edições não morde, que é exatamente o que "conservador" quer dizer aqui. O Jargas, de 2008, segue correto no que ensina. |
| 39 / 108 | *Python for Everybody* · *Think Python* | Python 3 básico, estável, ambas de acesso aberto. |
| 36 | *Álgebra Linear com Python* | API de NumPy estável. |
| 83 | *The BPMN Graphic Handbook* | BPMN 2.0 (2011) **continua sendo o padrão corrente**. A obra não está defasada — é a lacuna que não convence (§ 3.6). |
| 90 / 97 | Tufte · Tabak | Fora do eixo: forma gráfica e história da álgebra não têm versão. A ausência de defasagem é parte do argumento que levou Tufte ao § 1. |
| 3 | *Engenharia de Prompts na Prática* | **Correção de 2026-10-17.** A primeira versão deste relatório deu o livro como "de 2023, era GPT-3.5/4", pela data do ASIN. Errado: a obra é mantida — o exemplar conferido está "atualizado em outubro/2026" e já cobre Gemini, Claude e agentes. Não há defasagem a sinalizar. O que o exemplar revelou foi outra coisa, e é de cobertura, não de idade: § 1. |

---

## 5. Ruído na lista

A lista é extração de estante pessoal, não cadastro. Três formas de ruído, e
todas afetam como ela deve ser lida:

**Registro duplicado.** *O Nome da Rosa* (Umberto Eco) aparece duas vezes,
**#78** e **#81**, ambas lidas em maio de 2018 com nota 5 e estante `literature`.
É duplicata **do Goodreads**, não do catálogo: a obra é literatura, nunca chega
ao cruzamento, e nenhum recurso do catálogo a cita. O valor dela é de alerta —
"122 obras" são no máximo 121 obras distintas, e qualquer contagem derivada
desta estante é aproximada.

Vale separar isso de um caso que **se parece** e é o oposto: no catálogo, vários
recursos para uma mesma obra é correto por construção
([ADR-0009](adr/0009-obra-como-campo-de-agrupamento-no-recurso.md)) — oito
fatias de Date são um exemplar. No Goodreads, dois registros para uma obra é
erro. Os dois se apresentam como "a mesma obra aparecendo mais de uma vez", e
confundi-los faria o cruzamento errar nos dois sentidos: ver duplicata onde há
fatia, ou aceitar duplicata como se fosse fatia.

**Estante incompleta.** Cinco obras técnicas não têm estante nenhuma e escapam
do filtro declarado no pedido: **#16** *Shell Script Profissional* (§ 3.1),
**#106** *Code* (§ 3.5), **#108** *Think Python* (§ 2.4) — as três já tratadas
acima por serem relevantes — e mais duas que ficam aqui com veredito curto:
**#38** *Data Visualization: Python, R and Tableau* (nota 1, e a etapa de
visualização tem melhores opções, Tufte entre elas — § 1) e **#49** *Excel Dashboards &
Reports* (planilha como ferramenta de análise não tem ponto de contato no
catálogo, e provavelmente é escopo fora de propósito). A conclusão prática: a
estante do Goodreads é dica, não esquema — um cruzamento futuro deve varrer a
lista inteira e usar a estante para ordenar, não para filtrar.

**Estante declarada e inexistente.** O filtro pedido inclui `system-analysis`,
que não ocorre em nenhuma das 122 linhas.

---

## 6. O que este relatório não decide

- **Não decide catalogação.** O relatório recomenda; catalogar é decisão do
  estudante. As quatro obras do § 1 datadas de 2026-10-17 entraram **por essa
  decisão**, não por iniciativa do relatório, e nada mais do § 2 ou do § 3 foi
  tocado. Tufte e Souza não mexeram no modelo: são dois recursos novos, e recurso
  não altera a `rev` da etapa ([catalogo.md §4](catalogo.md)). Jargas e Blum
  mexeram, porque entraram pela lacuna — duas competências, duas etapas avulsas,
  quatro `rev` que subiram — e é o que [ADR-0010](adr/0010-shell-como-pre-requisito-declarado.md)
  decide. **Correção de 2026-10-17:** a versão anterior desta linha dizia que
  "nenhuma etapa, competência ou trilha foi criada ou alterada em momento algum".
  Valia para Tufte e Souza e deixou de valer no mesmo dia.
- **Não confere exemplar, exceto onde diz que conferiu.** Os vereditos do § 2 e
  do § 4 vêm de título, autor e data — só as quatro obras do § 1 datadas de
  2026-10-17 tiveram o exemplar conferido, e em todas a conferência mudou a entrada
  (§ 1). O resto precisa do mesmo tratamento antes de virar recurso, sobretudo § 4
  (edição do React e do Flask). A ressalva de `disponivel` dos comentários de
  `recursos/dados.yaml` vale aqui: parte do acervo Kindle é amostra, não exemplar
  íntegro, e amostra não satisfaz a validação §5.5. Nos recursos de shell a ressalva
  não morde, porque os três pagos ou gratuitos apontam para editora ou para o autor,
  não para o acervo Kindle do estudante.
- **Não fecha lacuna — e uma se fechou depois.** § 3 nomeava seis lacunas; abrir
  etapa ou trilha para qualquer uma é decisão de escopo, com ADR se for estrutural
  ([catalogo.md](catalogo.md), regra 7 do CLAUDE.md). A ordem sugerida era § 3.1
  (shell) primeiro, porque é pré-requisito implícito de duas trilhas que já existem;
  § 3.2 (servidor em Python) depois, porque é a forma de aplicação que o próprio
  repositório construiu. **§ 3.1 foi fechada em 2026-10-17**, nessa ordem e por
  decisão do estudante. Restam cinco, e § 3.2 segue sendo a próxima.
