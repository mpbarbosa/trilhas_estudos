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
- **Comparação.** Por título **e** autor contra os 163 recursos do snapshot, não
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

## 1. Já catalogada — 1 obra

| # | Obra | Recurso | Etapa |
|---|---|---|---|
| 11 | *Ry's Git Tutorial* (Ryan Hodson) | `rec:engenharia/rys-git-tutorial` | `etapa:engenharia/controle-de-versao` |

Correspondência exata, confirmada contra a ficha de bibliografia.md (RyPress,
2014, ASIN `B00QFIA5OC`). É a única: **16 das 17 obras técnicas da estante não
estão no catálogo**, e o catálogo foi construído sem consultar a estante.

---

## 2. Não catalogada, mas cabe numa etapa ativa — 8 obras

Ordenadas por quanto acrescentam, não por nota. "Acrescenta" aqui é uma de duas
coisas: cobrir uma etapa que hoje depende de um recurso só, ou dar idioma ou
custo que os recursos atuais da etapa não dão — os dois são filtros do motor
([motor §2.2](motor-de-sugestao.md)).

### 2.1 Tufte, *The Visual Display of Quantitative Information* (#90, nota 5)

→ `etapa:dados/visualizacao-para-analise`

A competência da etapa é "escolher a forma gráfica adequada à pergunta e à
natureza da variável, e ler um gráfico criticamente: escala, agregação, **o que
foi omitido**". Isso é a tese do livro, não uma vizinhança dela: *lie factor*,
*data-ink ratio* e *chartjunk* são exatamente o critério de leitura crítica que
a competência pede. A etapa hoje tem dois recursos — Wilke (aberto) e os
tutoriais de matplotlib/seaborn —, ambos sobre **como fazer**; nenhum é o
clássico sobre **o que não fazer**. É a melhor candidata da estante inteira, e a
única que não carrega risco de defasagem (§ 4).

### 2.2 Edney Souza, *Engenharia de Prompts na Prática* (#3, nota 3)

→ `etapa:ia/engenharia-de-prompt`

A etapa de maior fragilidade de cobertura do catálogo: **um único recurso**
(`rec:ia/prompt-engineering-for-llms`, en-US, R$ 300). A validação §5.5 exige
≥ 1 recurso ativo e disponível, então a etapa passa — mas passa por um fio, e
qualquer estudante com restrição de idioma ou `custo_maximo` abaixo de 300 vê a
etapa filtrada. Uma alternativa pt-BR e barata é o maior ganho de cobertura
disponível na estante.

Ressalva honesta: a etapa também desenvolve `comp:ia/uso-de-llm-por-api`
(parâmetros de decodificação, saída estruturada, janela de contexto, custo e
latência). Um livro de prompts em português provavelmente não cobre essa
metade — entraria como recurso **parcial** da etapa, e isso precisa ser
verificado no exemplar antes de catalogar, não depois.

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

## 3. Sem etapa que a comporte — 7 obras, 6 lacunas

Aqui a obra importa menos que a lacuna. Uma lacuna real não se fecha com o livro
que a revelou: o livro é só a evidência de que ela existe.

### 3.1 Linha de comando e shell — a lacuna mais consequente

**#13** *Linux Command Line and Shell Scripting Bible* (Blum) · **#16** *Shell
Script Profissional* (Aurélio Jargas, pt-BR)

Nenhuma etapa do catálogo trata linha de comando, shell ou automação de tarefa.
O mais próximo é `etapa:programacao/c-interface-com-o-unix`, que é a API do
UNIX vista do C (`read`, `write`, `open`, `lseek`) — o sistema por baixo da
biblioteca padrão, não a casca por cima dele.

Isso é consequente porque **duas trilhas ativas pressupõem a casca sem ensiná-la**:
`trilha:so/projeto-e-implementacao` manda compilar e modificar o MINIX em
máquina virtual (`rec:so/minix3-projeto`), e
`trilha:programacao/linguagem-c-ansi` supõe compilação separada e `make`. O
estudante que não domina shell não é barrado por nenhum `requires` — ele
simplesmente trava no projeto. É o tipo de pré-requisito implícito que o modelo
de competências existe para tornar explícito ([CONTEXT.md §3.2](CONTEXT.md)).

A estante traz os dois lados dessa lacuna: um livro de referência em inglês e um
livro pt-BR curto e bem avaliado no assunto. Se alguma lacuna deste relatório
merece virar etapa, é esta.

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
| 3 | *Engenharia de Prompts na Prática* (2023) | Era GPT-3.5/4. As técnicas que sobreviveram estão no recurso que a etapa já tem. Não anula o argumento de cobertura de § 2.2, mas define o teto: apoio pt-BR, não autoridade. |
| 1 | *Fundamentos do React JS* | Conferir a edição antes de qualquer coisa. React introdutório anterior a 2019 ensina componente de classe, que é justamente o que os recursos atuais da etapa evitam (`rec:web/pure-react-ceddia` é descrito como "sem Redux nem ferramental"). |
| 75 | *The Silent Intelligence* (2013) | Previsão de mercado de IoT de 2013 — hoje é documento histórico, não material de estudo. |

### Defasagem presente mas tolerável

| # | Obra | Leitura |
|---|---|---|
| 14 | *All About Java 8 Lambdas* | O recurso de linguagem em si não mudou; o que datou é tudo em volta (record, sealed, adições a stream, thread virtual) e o fato de que o LTS atual está muito à frente do 8. Se a JVM entrar no catálogo (§ 3.4), não entra por aqui. |
| 11 | *Ry's Git Tutorial* (2014) | **Já catalogado.** O modelo de objetos do git é estável e a ficha de bibliografia.md já registra a data. Sem ação. |
| 13 / 16 | *Shell Scripting Bible* · *Shell Script Profissional* | Bash e o shell POSIX são conservadores. As duas obras de § 3.1 estão entre as menos defasadas da estante, o que reforça a lacuna em vez de enfraquecê-la. |
| 39 / 108 | *Python for Everybody* · *Think Python* | Python 3 básico, estável, ambas de acesso aberto. |
| 36 | *Álgebra Linear com Python* | API de NumPy estável. |
| 83 | *The BPMN Graphic Handbook* | BPMN 2.0 (2011) **continua sendo o padrão corrente**. A obra não está defasada — é a lacuna que não convence (§ 3.6). |
| 90 / 97 | Tufte · Tabak | Fora do eixo: forma gráfica e história da álgebra não têm versão. A ausência de defasagem é parte do argumento de § 2.1. |

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
visualização tem melhores opções em § 2.1) e **#49** *Excel Dashboards &
Reports* (planilha como ferramenta de análise não tem ponto de contato no
catálogo, e provavelmente é escopo fora de propósito). A conclusão prática: a
estante do Goodreads é dica, não esquema — um cruzamento futuro deve varrer a
lista inteira e usar a estante para ordenar, não para filtrar.

**Estante declarada e inexistente.** O filtro pedido inclui `system-analysis`,
que não ocorre em nenhuma das 122 linhas.

---

## 6. O que este relatório não decide

- **Não altera o catálogo.** Nenhum recurso, etapa ou competência foi criado ou
  editado. Catalogar é decisão do estudante.
- **Não confere exemplar.** Os vereditos de § 2 e § 4 vêm de título, autor e
  data; a edição e o sumário de cada obra precisam ser conferidos no exemplar
  antes de virar recurso — sobretudo § 2.2 (cobertura da metade de API) e
  § 4 (edição do React e do Flask). A ressalva de `disponivel` dos comentários
  de `recursos/dados.yaml` vale aqui: parte do acervo Kindle é amostra, não
  exemplar íntegro, e amostra não satisfaz a validação §5.5.
- **Não fecha lacuna.** § 3 nomeia seis lacunas; abrir etapa ou trilha para
  qualquer uma é decisão de escopo, com ADR se for estrutural
  ([catalogo.md](catalogo.md), regra 7 do CLAUDE.md). A ordem sugerida, se
  houver ordem: § 3.1 (shell) primeiro, porque é pré-requisito implícito de duas
  trilhas que já existem; § 3.2 (servidor em Python) depois, porque é a forma de
  aplicação que o próprio repositório construiu.
