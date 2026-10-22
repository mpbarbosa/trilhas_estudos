# Bibliografia do catálogo

Ficha de cada **livro** citado por algum recurso do catálogo, uma ficha por *obra* —
não por recurso. Sete recursos citam *A Bíblia do Claude AI* e seis citam
*Three Easy Pieces*; cada obra aparece aqui uma vez, com a lista dos recursos que a
citam.

Este documento é **descritivo**, não normativo: a fonte da verdade continua sendo
`catalogo/`. Nada aqui entra na validação nem no `catalogo.lock.json`.

O agrupamento de **Citada por** é mantido à mão aqui, mas desde
[ADR-0009](adr/0009-obra-como-campo-de-agrupamento-no-recurso.md) ele é **conferível**:
as fatias pagas de um mesmo exemplar declaram `obra` no recurso
([catalogo.md §2](catalogo.md)), e é esse campo, não esta lista, que a compilação
valida.

## Como ler uma ficha

| Campo | O que traz |
|---|---|
| **Autoria** | autores e, quando há, tradução |
| **Edição** | editora, data, páginas e idioma da edição identificada |
| **Identificadores** | ISBN-13/ISBN-10 do impresso, ASIN do Kindle |
| **Amazon** | link direto do produto |
| **Acesso aberto** | quando existe edição livre e legítima publicada pelo autor ou editora |
| **Citada por** | ids dos recursos do catálogo |

**Convenção dos links.** O endereço é `https://www.amazon.com.br/dp/<ASIN>`, onde o
ASIN é o da edição Kindle ou, no caso do impresso, o próprio ISBN-10. Onde não foi
possível confirmar uma página de produto, o link é de busca e a ficha diz isso.

**Verificado em 2026-10-12**, exceto a ficha de *An Introduction to Database
Systems*, conferida em 2026-10-15, e as de *Foundations of Statistical Natural
Language Processing*, *The Practice of Programming*, *Neural Machine Translation*
e *Pure React*, conferidas em 2026-10-17, e as de *The Visual Display of
Quantitative Information*, *Engenharia de Prompts na Prática*, *Álgebra Linear com
Python*, *Python for Everybody*, *Spec Driven Development — PT*, *Linux Command Line
and Shell Scripting Bible*, *Shell Script Profissional*, *The Linux Command Line* e
*Desenvolvimento Web com Flask*, acrescentadas em 2026-10-17.

Preço, como regra, não entra aqui — vive em `custo` no recurso, com seu próprio
`verificado_em`, e a pesquisa de 2026-10-12 não o alterou: conferiu link e edição,
não preço. As nove fichas acrescentadas em 2026-10-17 são a exceção e **citam**
preço, porque nelas o `custo` do recurso foi fixado na mesma passada — no caso do
Tufte o preço é o próprio motivo de a ficha dizer qual tiragem o recurso aponta, e no
do *Shell Scripting Bible* ele registra que o Kindle sai mais caro que o impresso.

As divergências encontradas entre o catálogo e a obra real estão reunidas no
[§ Divergências](#divergências) no fim.

---

## Dados

### Álgebra Linear com Python: Aprenda na prática os principais conceitos

- **Autoria** — Rafael F.V.C. Santos
- **Edição** — 1ª ed., edição do autor, 17/07/2018, 104 p., Kindle, pt-BR. Livro 1 da
  série *Cientista de dados — Analista Quant*. Apresenta-se como material de apoio,
  não como texto único de álgebra linear.
- **Identificadores** — ASIN `B07FNWM2P8` (sem ISBN)
- **Amazon** — https://www.amazon.com.br/dp/B07FNWM2P8 (R$ 9,99 para comprar;
  R$ 0,00 só na assinatura Kindle, que não é edição gratuita — por isso o recurso
  declara `custo: 10`, não 0)
- **Citada por** — `rec:dados/santos-algebra-linear-python`
- **Nota** — cobre a álgebra linear de `etapa:dados/matematica-para-dados` e não o
  cálculo que a mesma etapa pede (derivada, gradiente, otimização). O comentário em
  `catalogo/recursos/dados.yaml` registra o limite.

### An Introduction to Database Systems, vol. I

- **Autoria** — C. J. Date
- **Edição** — 5ª ed., Addison-Wesley, 1990, 800 p., en-US. Fora de catálogo: só
  circula usada. A mesma 5ª edição teve duas tiragens, capa dura (01/04/1990) e capa
  comum (01/12/1990), e é daí que vêm os dois ISBN que as fontes trocam entre si.
- **Identificadores** — capa dura: ISBN-13 978-0-201-51381-3 · ISBN-10 `0201513811` —
  capa comum: ISBN-13 978-0-201-52878-7 · ISBN-10 `0201528789`
- **Amazon** — https://www.amazon.com.br/dp/0201513811 (capa dura, só usada) ·
  https://www.amazon.com.br/dp/0201528789 (capa comum, indisponível)
- **Citada por** — `rec:dados/date-vol1-arquitetura`,
  `rec:dados/date-vol1-modelo-relacional`, `rec:dados/date-vol1-algebra-e-calculo`,
  `rec:dados/date-vol1-sql`, `rec:dados/date-vol1-normalizacao`,
  `rec:dados/date-vol1-normalizacao-superior`, `rec:dados/date-vol1-armazenamento`,
  `rec:dados/date-vol1-protecao` — as oito fatias declaram `obra: date-vol1`
- **Nota** — ver [§ Divergências](#divergências)

### Análise Exploratória de Dados com Python, Pandas e Numpy

- **Autoria** — Fernando Feltrin
- **Edição** — edição do autor, 30/06/2021, 162 p., Kindle, pt-BR
- **Identificadores** — ASIN `B098DF8BZ5` (sem ISBN)
- **Amazon** — https://www.amazon.com.br/dp/B098DF8BZ5
- **Citada por** — `rec:dados/feltrin-analise-exploratoria`

### Calculus: An Intuitive and Physical Approach

- **Autoria** — Morris Kline
- **Edição** — 2ª ed., Dover Publications, 19/06/1998 (original de 1977), 960 p., en-US
- **Identificadores** — ISBN-13 978-0-486-40453-0 · ISBN-10 `0486404536`
- **Amazon** — https://www.amazon.com.br/dp/0486404536
- **Editora** — https://store.doverpublications.com/products/9780486404530
- **Citada por** — `rec:dados/kline-calculus`, `rec:matematica/kline-calculus-limites`,
  `rec:matematica/kline-calculus-derivada`, `rec:matematica/kline-calculus-integral`

### Data science para negócios: o que você precisa saber sobre mineração de dados e pensamento analítico de dados

- **Autoria** — Foster Provost, Tom Fawcett (tradução brasileira)
- **Edição** — 1ª ed., Alta Books, 22/03/2016, 404 p., pt-BR
- **Identificadores** — ISBN-13 978-85-7608-972-8 · ISBN-10 `8576089726`
- **Amazon** — https://www.amazon.com.br/dp/8576089726
- **Original** — *Data Science for Business*, O'Reilly, 2013
- **Citada por** — `rec:dados/data-science-para-negocios`

### Dominando Python: 100+ Exercícios Resolvidos e Comentados para Acelerar seu Aprendizado

- **Autoria** — Ruhan Conceição — série *Dominando a Programação*
- **Edição** — edição do autor, 09/06/2023, 205 p., Kindle, pt-BR
- **Identificadores** — ASIN `B0C7NDPKFR` (sem ISBN)
- **Amazon** — https://www.amazon.com.br/dp/B0C7NDPKFR
- **Citada por** — `rec:dados/dominando-python-exercicios`

### Fundamentals of Data Visualization: A Primer on Making Informative and Compelling Figures

- **Autoria** — Claus O. Wilke
- **Edição** — O'Reilly Media, 14/05/2019, 387 p., en-US
- **Identificadores** — ISBN-13 978-1-4920-3108-6 · ISBN-10 `1492031089`
- **Amazon** — https://www.amazon.com.br/dp/1492031089
- **Acesso aberto** — https://clauswilke.com/dataviz/
- **Citada por** — `rec:dados/fundamentals-data-visualization`

### Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow

- **Autoria** — Aurélien Géron
- **Edição** — 3ª ed., O'Reilly Media, 08/11/2022, 861 p., en-US
- **Identificadores** — ISBN-13 978-1-09-812597-4 · ISBN-10 `1098125975`
- **Amazon** — https://www.amazon.com.br/dp/1098125975
- **Código** — https://github.com/ageron/handson-ml3
- **Em português** — *Mãos à obra: aprendizado de máquina com Scikit-Learn, Keras &
  TensorFlow*, Alta Books
- **Citada por** — `rec:dados/handson-ml-parte1` (parte I), `rec:ia/handson-ml-3ed` (parte II)

### Matemática para Ciência de Dados: Fundamentos teóricos e aplicações práticas em Python

- **Autoria** — Eugenio Nelson Dianguila
- **Edição** — edição do autor; Kindle 17/12/2024, 254 p.; impresso 18/12/2024, 202 p.; pt-BR
- **Identificadores** — ASIN `B0DQVMKS9N` (Kindle) · ISBN-13 979-8-3041-4156-7, ASIN
  `B0DR1SHVGF` (impresso)
- **Amazon** — https://www.amazon.com.br/dp/B0DQVMKS9N
- **Citada por** — `rec:dados/dianguila-matematica-ciencia-de-dados`

### Python Data Science Handbook: Essential Tools for Working with Data

- **Autoria** — Jake VanderPlas
- **Edição** — 2ª ed., O'Reilly Media, 17/01/2023, 588 p., en-US
- **Identificadores** — ISBN-13 978-1-09-812122-8 · ISBN-10 `1098121228`
- **Amazon** — https://www.amazon.com.br/dp/1098121228
- **Acesso aberto** — https://jakevdp.github.io/PythonDataScienceHandbook/
- **Citada por** — `rec:dados/python-data-science-handbook`

### Python para Análise de Dados — 3ª edição: Tratamento de Dados com pandas, NumPy & Jupyter

- **Autoria** — Wes McKinney
- **Edição** — Novatec Editora, 17/03/2023, Kindle, pt-BR
- **Identificadores** — ASIN `B0BYQ916JY`
- **Amazon** — https://www.amazon.com.br/dp/B0BYQ916JY
- **Acesso aberto** — https://wesmckinney.com/book/ (3ª ed. em inglês, liberada pelo autor)
- **Original** — *Python for Data Analysis*, 3rd ed., O'Reilly, 2022
- **Citada por** — `rec:dados/mckinney-python-analise-3ed`

### The Visual Display of Quantitative Information

- **Autoria** — Edward R. Tufte
- **Edição** — 2ª ed., Graphics Press, 01/05/2001, 197 p., en-US. A 1ª é de 1983; a 2ª
  acrescenta reprodução em cor dos gráficos de William Playfair e incorpora as
  correções acumuladas ao longo de 17 tiragens da primeira. **Só existe em papel**:
  a Graphics Press nunca publicou edição eletrônica, e o site do autor vende apenas
  capa dura (US$ 50) e capa comum (US$ 40).
- **Identificadores** — capa dura: ISBN-13 978-0-9613921-4-7 · ISBN-10 `0961392142` —
  a tiragem em capa comum circula sob ISBN-13 978-1-930824-13-3 · ISBN-10 `1930824130`
- **Amazon** — https://www.amazon.com.br/dp/0961392142 (capa dura; em 2026-10-17,
  R$ 218,80 com uma unidade em estoque, capa comum a R$ 210,36)
- **Citada por** — `rec:dados/tufte-visual-display`

### Think Stats: Exploratory Data Analysis

- **Autoria** — Allen B. Downey
- **Edição** — 3ª ed., O'Reilly Media, 13/05/2025, 321 p., en-US
- **Identificadores** — ISBN-13 978-1-09-819025-5 · ISBN-10 `1098190254`
- **Amazon** — https://www.amazon.com.br/dp/1098190254
- **Acesso aberto** — https://allendowney.github.io/ThinkStats/
- **Citada por** — `rec:dados/think-stats`

---

## Engenharia

### Arquitetura de software: as partes difíceis — análises modernas de trade-off para arquiteturas distribuídas

- **Autoria** — Neal Ford, Mark Richards, Pramod Sadalage, Zhamak Dehghani;
  trad. Leandro Menegaz
- **Edição** — 1ª ed., Alta Books, 30/04/2024, 448 p., pt-BR
- **Identificadores** — ISBN-13 978-85-508-1984-6 · ISBN-10 `8550819840`
- **Amazon** — https://www.amazon.com.br/dp/8550819840
- **Original** — *Software Architecture: The Hard Parts*, O'Reilly, 2021
- **Citada por** — `rec:engenharia/partes-dificeis-trade-off`,
  `rec:engenharia/partes-dificeis-decomposicao`, `rec:engenharia/partes-dificeis-dados`

### Effective DevOps: Building a Culture of Collaboration, Affinity, and Tooling at Scale

- **Autoria** — Jennifer Davis, Ryn Daniels
- **Edição** — 1ª ed., O'Reilly Media, 19/07/2016, 408 p., en-US
- **Identificadores** — ISBN-13 978-1-4919-2630-7 · ISBN-10 `1491926309`
- **Amazon** — https://www.amazon.com.br/dp/1491926309
- **Citada por** — `rec:engenharia/effective-devops`

### Engenharia de Requisitos: software orientado ao negócio

- **Autoria** — Carlos Eduardo Vazquez, Guilherme Siqueira Simões
- **Edição** — 1ª ed., Brasport; impresso 10/08/2016, 328 p.; Kindle 19/10/2016; pt-BR
- **Identificadores** — ISBN-13 978-85-7452-790-1 · ISBN-10 `8574527904` (impresso) ·
  ASIN `B01M3S7HT7` (Kindle)
- **Amazon** — https://www.amazon.com.br/dp/B01M3S7HT7 (Kindle) ·
  https://www.amazon.com.br/dp/8574527904 (impresso)
- **Citada por** — `rec:engenharia/vazquez-engenharia-de-requisitos`

### Functional and Non-Functional Requirements Simply Put!

- **Autoria** — Thomas Hathaway, Angela Hathaway — série *Advanced Business Analysis
  Topics*, v. 3
- **Edição** — 2ª ed., CreateSpace, 01/08/2016, 70 p., en-US
- **Identificadores** — ISBN-13 978-1-5349-8348-9 · ISBN-10 `1534983481` (impresso) ·
  ASIN `B01LIUJQF0` (Kindle)
- **Amazon** — https://www.amazon.com.br/dp/1534983481
- **Citada por** — `rec:engenharia/hathaway-requisitos-nao-funcionais`

### Google SRE — coletânea

Não é um livro, e sim a biblioteca aberta de SRE do Google. As duas obras centrais:

- *Site Reliability Engineering: How Google Runs Production Systems* — Betsy Beyer,
  Chris Jones, Jennifer Petoff, Niall Richard Murphy; O'Reilly, 2016, ~550 p.;
  ISBN-13 978-1-4919-2912-4 · https://www.amazon.com.br/dp/149192912X
- *The Site Reliability Workbook: Practical Ways to Implement SRE* — Betsy Beyer,
  Niall Richard Murphy, David K. Rensin, Kent Kawahara, Stephen Thorne; O'Reilly,
  2018, 512 p.; ISBN-13 978-1-4920-2950-2 · https://www.amazon.com.br/dp/1492029505
- **Acesso aberto** — https://sre.google/books/ (texto integral, inclusive dos demais
  volumes da coletânea)
- **Citada por** — `rec:engenharia/google-sre-books`

### Pro Git

- **Autoria** — Scott Chacon, Ben Straub
- **Edição** — 2ª ed., Apress, 09/11/2014, 419 p., en-US
- **Identificadores** — ISBN-13 978-1-4842-0077-3 · ISBN-10 `1484200772`
- **Amazon** — https://www.amazon.com.br/dp/1484200772
- **Acesso aberto** — https://git-scm.com/book/pt-br/v2 (tradução pt-BR completa)
- **Citada por** — `rec:engenharia/pro-git`

### Ry's Git Tutorial

- **Autoria** — Ryan Hodson
- **Edição** — RyPress, 30/11/2014, 228 p., Kindle, en-US
- **Identificadores** — ISBN-13 978-0-9850723-1-5 · ASIN `B00QFIA5OC`
- **Amazon** — https://www.amazon.com.br/dp/B00QFIA5OC
- **Citada por** — `rec:engenharia/rys-git-tutorial`

---

## IA e programação

### A Bíblia do Claude AI: o guia completo da IA da Anthropic — modelos, prompts, Cowork, Claude Code, Skills, MCP e API, do primeiro chat ao agente em produção

- **Autoria** — Thierry Gustin
- **Edição** — edição do autor, 14/07/2026, 605 p., Kindle, pt-BR
- **Identificadores** — ASIN `B0H8S9BKKZ` (sem ISBN)
- **Amazon** — https://www.amazon.com.br/dp/B0H8S9BKKZ
- **Citada por** — `rec:ia/biblia-claude-chat`, `rec:ia/biblia-claude-prompts`,
  `rec:ia/biblia-claude-api`, `rec:ia/biblia-claude-mcp`,
  `rec:ia/biblia-claude-code-skills`, `rec:ia/biblia-claude-agentes`,
  `rec:ia/biblia-claude-producao`
- **Nota** — há também uma edição em capa comum com subtítulo diferente
  (*O guia completo do power user*), ASIN `B0HGR3WHHV`. O catálogo cita a de Kindle.

### AI Engineering: Building Applications with Foundation Models

- **Autoria** — Chip Huyen
- **Edição** — O'Reilly Media, 07/01/2025, 532 p., en-US
- **Identificadores** — ISBN-13 978-1-09-816630-4 · ISBN-10 `1098166302`
- **Amazon** — https://www.amazon.com.br/dp/1098166302
- **Material de apoio** — https://github.com/chiphuyen/aie-book
- **Citada por** — `rec:ia/ai-engineering-avaliacao`, `rec:ia/ai-engineering-producao`,
  `rec:ia/ai-engineering-agentes-producao`, `rec:ia/aie-book-material`

### AI-Powered Search

- **Autoria** — Trey Grainger, Doug Turnbull, Max Irwin
- **Edição** — Manning Publications, 28/01/2025, 520 p., en-US
- **Identificadores** — ISBN-13 978-1-61729-697-0 · ISBN-10 `161729697X`
- **Amazon** — https://www.amazon.com.br/dp/161729697X
- **Editora** — https://www.manning.com/books/ai-powered-search
- **Citada por** — `rec:ia/ai-powered-search`, `rec:ia/ai-powered-search-rag`

### Automate the Boring Stuff with Python: Practical Programming for Total Beginners

- **Autoria** — Al Sweigart
- **Edição** — 3ª ed., No Starch Press, 20/05/2025, 672 p., en-US
- **Identificadores** — ISBN-13 978-1-7185-0340-3 · ISBN-10 `1718503407`
- **Amazon** — https://www.amazon.com.br/dp/1718503407
- **Acesso aberto** — https://automatetheboringstuff.com/
- **Citada por** — `rec:programacao/automate-boring-stuff`

### Build a Large Language Model (From Scratch)

- **Autoria** — Sebastian Raschka
- **Edição** — Manning Publications, 29/10/2024, 368 p., en-US
- **Identificadores** — ISBN-13 978-1-63343-716-6 · ISBN-10 `1633437167`
- **Amazon** — https://www.amazon.com.br/dp/1633437167
- **Código** — https://github.com/rasbt/LLMs-from-scratch
- **Citada por** — `rec:ia/build-llm-from-scratch`, `rec:ia/llms-from-scratch-codigo`,
  `rec:ia/llms-from-scratch-finetuning`

### C: A Linguagem de Programação — Padrão ANSI

- **Autoria** — Brian W. Kernighan, Dennis M. Ritchie
- **Edição** — 8ª ed., Editora Campus, pt-BR; tradução da 2ª edição de *The C
  Programming Language* (Prentice Hall, 1988). Identificada pela capa do exemplar do
  estudante; data, páginas e ISBN desta edição não foram conferidos.
- **Amazon** — link de busca, sem página de produto confirmada:
  https://www.amazon.com.br/s?k=C+A+Linguagem+de+Programa%C3%A7%C3%A3o+Padr%C3%A3o+ANSI+Kernighan+Ritchie
- **Citada por** — `rec:programacao/kernighan-ritchie-introducao`,
  `rec:programacao/kernighan-ritchie-tipos-e-controle`,
  `rec:programacao/kernighan-ritchie-funcoes`,
  `rec:programacao/kernighan-ritchie-apontadores`,
  `rec:programacao/kernighan-ritchie-estruturas`,
  `rec:programacao/kernighan-ritchie-entrada-e-saida`,
  `rec:programacao/kernighan-ritchie-interface-unix` — as sete fatias declaram
  `obra: kernighan-ritchie-c`

### Deep Learning Book

- **Autoria** — Data Science Academy
- **Edição** — obra online em pt-BR, 100 capítulos; sem edição impressa e sem ISBN
- **Acesso aberto** — https://www.deeplearningbook.com.br/
- **Amazon** — não se aplica
- **Citada por** — `rec:ia/deep-learning-book-br`

### Deep Learning with Python

- **Autoria** — François Chollet, Matthew Watson
- **Edição** — 3ª ed., Manning Publications, 30/09/2025, 648 p., en-US
- **Identificadores** — ISBN-13 978-1-63343-658-9 · ISBN-10 `1633436586`
- **Amazon** — https://www.amazon.com.br/dp/1633436586
- **Código** — https://github.com/fchollet/deep-learning-with-python-notebooks
- **Citada por** — `rec:ia/deep-learning-with-python-3ed`

### Engenharia de Prompts na Prática: Do Zero ao Avançado com ChatGPT, Gemini e Claude

- **Autoria** — Edney "InterNey" Souza
- **Edição** — edição do autor, atualizada em outubro/2026; 320 p. no Kindle e 333 p.
  no impresso (07/06/2026), pt-BR. 15 capítulos e 3 apêndices, com biblioteca de
  prompts por área e glossário. Título anterior: *ChatGPT: Do Zero aos Prompts
  Avançados* — **mesmo ASIN**, retitulado e ampliado com Gemini, Claude e agentes.
- **Identificadores** — ASIN `B0CKNQ92PK` (Kindle) · ISBN-13 979-8-2556-8399-4 (impresso)
- **Amazon** — https://www.amazon.com.br/dp/B0CKNQ92PK (Kindle R$ 0,00 na assinatura
  ou R$ 5,99 para comprar; capa comum R$ 61,48)
- **Acesso aberto** — https://interney.net/livro-ia — PDF do livro completo, de graça
  pelo próprio autor, mediante formulário com nome e e-mail. É esta a URL do recurso,
  e é por ela que `custo` é 0.
- **Citada por** — `rec:ia/souza-engenharia-de-prompts`
- **Nota** — cobre a metade de técnica de prompt de `etapa:ia/engenharia-de-prompt` e
  não a de API: é declaradamente "sem escrever código". O comentário em
  `catalogo/recursos/ia.yaml` registra o limite.

### Foundations of Statistical Natural Language Processing

- **Autoria** — Christopher D. Manning, Hinrich Schütze
- **Edição** — MIT Press, 1999, 680 p., en-US. Nunca teve 2ª edição nem tradução;
  fora de catálogo no Brasil, circula importada ou usada.
- **Identificadores** — ISBN-13 978-0-262-13360-9 · ISBN-10 `0262133601`
- **Amazon** — https://www.amazon.com.br/dp/0262133601
- **Acesso aberto** — não há edição livre. A página dos autores
  (https://nlp.stanford.edu/fsnlp/) traz sumário, errata e os capítulos de amostra,
  e é o endereço que as seis fatias citam.
- **Citada por** — `rec:ia/manning-schutze-fundamentos-matematicos`,
  `rec:ia/manning-schutze-inferencia-estatistica`,
  `rec:ia/manning-schutze-suavizacao`, `rec:ia/manning-schutze-hmm`,
  `rec:ia/manning-schutze-etiquetagem`,
  `rec:ia/manning-schutze-exercicios-inferencia` — as seis fatias declaram
  `obra: manning-schutze-fsnlp`
- **Nota** — é de 1999 e anterior a tudo que é neural. O que a trilha usa dela —
  suposição de Markov, perplexidade, suavização, HMM, etiquetagem — não envelheceu;
  o estado da arte que ela descreve, sim.

### Hands-On Large Language Models: Language Understanding and Generation

- **Autoria** — Jay Alammar, Maarten Grootendorst
- **Edição** — O'Reilly Media, set./2024, 428 p., en-US
- **Identificadores** — ISBN-13 978-1-09-815096-9 · ISBN-10 `1098150961` ·
  ASIN `B0DGZ46G88` (Kindle)
- **Amazon** — https://www.amazon.com.br/dp/B0DGZ46G88
- **Código** — https://github.com/HandsOnLLM/Hands-On-Large-Language-Models
- **Citada por** — `rec:ia/hands-on-llms-embeddings`, `rec:ia/hands-on-llms-notebooks`,
  `rec:ia/hands-on-llms-rag`

### Introduction to Information Retrieval

- **Autoria** — Christopher D. Manning, Prabhakar Raghavan, Hinrich Schütze
- **Edição** — Cambridge University Press, 01/07/2008, 482 p., en-US
- **Identificadores** — ISBN-13 978-0-521-86571-5 · ISBN-10 `0521865719`
- **Amazon** — https://www.amazon.com.br/dp/0521865719
- **Acesso aberto** — https://nlp.stanford.edu/IR-book/
- **Citada por** — `rec:ia/intro-information-retrieval`

### LLM Engineer's Handbook: Master the Art of Engineering Large Language Models from Concept to Production

- **Autoria** — Paul Iusztin, Maxime Labonne
- **Edição** — Packt Publishing, 22/10/2024, 522 p., en-US
- **Identificadores** — ISBN-13 978-1-83620-007-9 · ISBN-10 `1836200072`
- **Amazon** — https://www.amazon.com.br/dp/1836200072
- **Código** — https://github.com/PacktPublishing/LLM-Engineers-Handbook
- **Citada por** — `rec:ia/llm-engineers-handbook-rag`,
  `rec:ia/llm-engineers-handbook-finetuning`, `rec:ia/llm-twin-projeto`

### LLM, Transformer, RAG AI: Mastering Large Language Models, Transformer Models, and Retrieval-Augmented Generation (RAG) Technology

- **Autoria** — Et Tu Code
- **Edição** — 2024, en-US
- **Identificadores** — o ISBN 979-8-8824-4648-1 registrado no catálogo é o do
  **audiolivro** (narração de Helen Green, 9 h 29 min), não o de uma edição em texto
- **Amazon** — não localizei página de produto;
  busca: https://www.amazon.com.br/s?k=LLM+Transformer+RAG+AI+Et+Tu+Code
- **Citada por** — `rec:ia/ettucode-llm-transformer-rag`
- **Nota** — ver [§ Divergências](#divergências)

### Loops de Harness com LangGraph: construindo agentes que iteram até acertar

- **Autoria** — Eduardo Vieira
- **Edição** — edição do autor, 14/06/2026, 341 p., Kindle, pt-BR; livro 5 de 5 da
  série *SDA + SDD Na Prática*
- **Identificadores** — ASIN não conferido
- **Amazon** — não localizei página de produto;
  busca: https://www.amazon.com.br/s?k=Loops+de+Harness+com+LangGraph
- **Citada por** — `rec:ia/loops-de-harness-langgraph`

### Neural Machine Translation

- **Autoria** — Philipp Koehn
- **Edição** — Cambridge University Press, 06/2020, 394 p. em capa dura, en-US.
  As fontes divergem na contagem (393, 394 ou 406 p.) por contarem a matéria
  pré-textual de formas diferentes; 394 é a do próprio autor.
- **Identificadores** — ISBN-13 978-1-108-49732-9 · ISBN-10 `1108497322` —
  e-book (epub): ISBN-13 978-1-108-60848-0
- **Amazon** — https://www.amazon.com.br/dp/1108497322 — não foi possível confirmar
  a página de produto no amazon.com.br; o link segue a convenção do ISBN-10. O
  `custo: 450` do recurso é conversão aproximada de vendedores estrangeiros
  (£63 no Reino Unido, €78 na Itália), não preço conferido no Brasil.
- **Acesso aberto** — não há. A página do autor
  (https://www2.statmt.org/nmt-book/) publica errata e os exemplos de código.
- **Citada por** — `rec:ia/koehn-nmt-seq2seq-atencional` — declara `obra: koehn-nmt`
- **Nota** — o precursor do livro é aberto: *Neural Machine Translation*
  (arXiv:1709.07809, 09/2017), o capítulo de rascunho que Koehn escreveu para a aula
  de MT na JHU e que depois virou a parte II desta obra. Serve de amostra, não de
  substituto: o livro reorganiza e amplia o material em 17 capítulos. É a única
  obra do catálogo em que o modelo sequência-a-sequência com atenção é **o
  assunto**, e não um capítulo — caps. 7 a 9 cobrem modelo de linguagem neural,
  codificador-decodificador com atenção e decodificação por feixe, que a trilha do
  transformer pressupõe.

### Natural Language Processing with Transformers, Revised Edition: Building Language Applications with Hugging Face

- **Autoria** — Lewis Tunstall, Leandro von Werra, Thomas Wolf
- **Edição** — ed. revisada, O'Reilly Media, 05/07/2022, 406 p., en-US
- **Identificadores** — ISBN-13 978-1-09-813679-6 · ISBN-10 `1098136799`
- **Amazon** — https://www.amazon.com.br/dp/1098136799
- **Código** — https://github.com/nlp-with-transformers/notebooks
- **Citada por** — `rec:ia/nlp-with-transformers`

### Prompt Engineering for LLMs: The Art and Science of Building Large Language Model-Based Applications

- **Autoria** — John Berryman, Albert Ziegler
- **Edição** — O'Reilly Media, 31/12/2024, 280 p., en-US
- **Identificadores** — ISBN-13 978-1-09-815615-2 · ISBN-10 `1098156153`
- **Amazon** — https://www.amazon.com.br/dp/1098156153
- **Citada por** — `rec:ia/prompt-engineering-for-llms`, e os capítulos `rec:ia/prompt-engineering-for-llms-cap-01` a `-cap-11` como partes dele (`obra: prompt-engineering-for-llms`, ADR-0019)

### Python Fluente

- **Autoria** — Luciano Ramalho
- **Edição** — 1ª ed., Novatec, 04/11/2015, 800 p., pt-BR
- **Identificadores** — ISBN-13 978-85-7522-462-5 · ISBN-10 `857522462X`
- **Amazon** — https://www.amazon.com.br/dp/857522462X (1ª edição)
- **Acesso aberto** — https://pythonfluente.com/ — a 2ª edição em português, traduzida
  pelo próprio autor. Não há edição impressa dela pela Novatec; a 2ª edição em papel
  existe em inglês (*Fluent Python*, O'Reilly, 2022).
- **Citada por** — `rec:programacao/python-fluente-2ed`

### Python for Everybody: Exploring Data in Python 3

- **Autoria** — Charles R. Severance
- **Edição** — CreateSpace, 2016, 246 p., en-US. A tradução em português, *Python Para
  Todos: Explorando Dados com Python 3*, é listada pelo próprio autor entre as
  traduções em py4e.com/book e está viva: o PDF respondeu 200 em 2026-10-17 com
  `Last-Modified` do mesmo dia.
- **Identificadores** — ISBN-13 978-1-5300-5112-0 · ISBN-10 `1530051126`
- **Amazon** — https://www.amazon.com.br/dp/1530051126 (impresso, R$ 84,12 em
  2026-10-17 — informativo: o recurso aponta para a edição aberta e declara `custo: 0`)
- **Acesso aberto** — https://www.py4e.com/book (licença Creative Commons
  Attribution 4.0; PDF e EPUB em vários idiomas). Direto em português:
  http://do1.dr-chuck.com/pythonlearn/PT_br/pythonlearn.pdf
- **Citada por** — `rec:programacao/py4e-severance`

### Spec Driven Development — PT: Da vibe-coding à engenharia de software

- **Autoria** — J.C. Ködel
- **Edição** — Independently Published, 14/07/2026, 270 p., capa comum, pt-BR. **Sem
  edição Kindle.** A edição em inglês tem outro título — *Spec Driven Design — EN:
  From vibe-coding to software engineering* —, e são duas: capa comum (ISBN-13
  979-8184775289, 267 p., 14/07/2026, ASIN `B0H8X2BFG2`) e Kindle (ASIN
  `B0H73WV7Q7`, 01/07/2026). Não confundir com os vários outros livros de título
  parecido publicados em 2026 por outros autores.
- **Identificadores** — ASIN `B0H8Y7QD9N` · ISBN-13 979-8-1873-4808-4
- **Amazon** — https://www.amazon.com.br/dp/B0H8Y7QD9N — em 2026-10-17, "Não
  disponível. Não temos previsão de quando este produto estará disponível
  novamente". Sem preço exibido, por isso o `custo: 90` do recurso é **estimativa**
  por comparável, não preço conferido.
- **Citada por** — `rec:ia/kodel-spec-driven-development` — único recurso do catálogo
  com `disponivel: false`; o comentário em `catalogo/recursos/ia.yaml` diz por quê e
  o que fazer quando voltar ao estoque.
- **Nota** — o eixo do livro é o GitHub Spec Kit. Cobre a parte de instrução de
  projeto e de revisão do que o agente propõe em `etapa:ia/claude-code-e-skills`;
  skills e subagentes, que a mesma competência cita, ficam de fora.

### Speech and Language Processing: An Introduction to Natural Language Processing, Computational Linguistics, and Speech Recognition

- **Autoria** — Daniel Jurafsky, James H. Martin
- **Edição** — a 3ª edição, que o catálogo usa, é **rascunho aberto e não publicado**.
  A última edição impressa é a 2ª: Pearson/Prentice Hall, 2008, ISBN-13
  978-0-13-187321-6 · ISBN-10 `0131873210`
- **Amazon** — https://www.amazon.com.br/s?k=9780131873216 (busca: a 2ª edição não tem
  página ativa na loja brasileira)
- **Acesso aberto** — https://web.stanford.edu/~jurafsky/slp3/
- **Citada por** — `rec:ia/slp3-transformers`, `rec:ia/jurafsky-martin-ngramas`,
  `rec:ia/jurafsky-martin-suavizacao`, `rec:ia/jurafsky-martin-apendice-hmm`,
  `rec:ia/jurafsky-martin-etiquetagem-sequencial`
- **Nota** — a numeração de capítulo muda entre rascunhos da 3ª edição, e os
  recursos citam o PDF por número (`3.pdf`, `18.pdf`, `A.pdf`). Ao conferir um
  link, confira o **título** do capítulo, não o número.

### The Practice of Programming

- **Autoria** — Brian W. Kernighan, Rob Pike
- **Edição** — Addison-Wesley Professional (Professional Computing Series),
  04/02/1999, 288 p., en-US
- **Identificadores** — ISBN-13 978-0-201-61586-9 · ISBN-10 `020161586X`
- **Amazon** — https://www.amazon.com.br/dp/020161586X
- **Acesso aberto** — não há edição livre, mas a página do livro
  (https://www.cs.princeton.edu/~bwk/tpop.webpage/) publica o código de todos os
  capítulos, inclusive as cinco implementações do gerador de Markov do cap. 3.
- **Código** — https://www.cs.princeton.edu/~bwk/tpop.webpage/code.html
- **Citada por** — `rec:ia/kernighan-pike-cadeia-de-markov` (cap. 3, o gerador de
  Markov) e `rec:programacao/kernighan-pike-tpop` (o resto do livro) — as duas
  fatias declaram `obra: kernighan-pike-tpop`, cruzando as áreas `ia/` e
  `programacao/`, que são organizacionais e não semânticas
  ([catalogo.md §3](catalogo.md))

---

## Matemática

### Abstract Algebra: Theory and Applications

- **Autoria** — Thomas W. Judson
- **Edição** — tiragem anual impressa, Orthogonal Publishing L3C; edição 2023, 422 p., en-US
- **Identificadores** — ISBN-13 978-1-944325-21-3 · ISBN-10 `1944325212`
- **Amazon** — https://www.amazon.com.br/dp/1944325212
- **Acesso aberto** — https://abstract.ups.edu/
- **Citada por** — `rec:matematica/judson-abstract-algebra`
- **Nota** — sai uma tiragem por ano com ISBN próprio; o texto aberto é sempre o mais
  recente.

### Book of Proof

- **Autoria** — Richard Hammack
- **Edição** — 3ª ed., edição do autor, 01/10/2018, 382 p., en-US
- **Identificadores** — ISBN-13 978-0-9894721-2-8 · ISBN-10 `0989472124`
- **Amazon** — https://www.amazon.com.br/dp/0989472124
- **Acesso aberto** — https://www.people.vcu.edu/~rhammack/BookOfProof/
- **Citada por** — `rec:matematica/book-of-proof`, `rec:matematica/projeto-demonstracao`

### Calculus Volume 1

- **Autoria** — OpenStax (autores sêniores Gilbert Strang e Edwin "Jed" Herman)
- **Edição** — versão impressa oficial, XanEdu Publishing, 30/03/2016, 873 p., en-US
- **Identificadores** — ISBN-13 978-1-938168-02-4 · ISBN-10 `193816802X`
- **Amazon** — https://www.amazon.com.br/dp/193816802X
- **Acesso aberto** — https://openstax.org/details/books/calculus-volume-1
- **Citada por** — `rec:matematica/openstax-calculus-v1`

### Calculus Volume 2

- **Autoria** — OpenStax (autores sêniores Gilbert Strang e Edwin "Jed" Herman)
- **Edição** — versão impressa oficial, OpenStax/XanEdu, en-US
- **Identificadores** — ISBN-13 978-1-938168-06-2 · ASIN `1506698077` (brochura P&B)
- **Amazon** — https://www.amazon.com.br/dp/1506698077
- **Acesso aberto** — https://openstax.org/details/books/calculus-volume-2
- **Citada por** — `rec:matematica/openstax-calculus-v2`

### Elementos de Geometria

- **Autoria** — Euclides; tradução de Frederico Commandino
- **Edição** — 01/12/2012, Kindle, pt-BR
- **Identificadores** — ASIN `B00AGZCDLS`
- **Amazon** — https://www.amazon.com.br/dp/B00AGZCDLS
- **Edição interativa** — https://mathcs.clarku.edu/~djoyce/elements/elements.html
  (David E. Joyce, em inglês — é o recurso `rec:matematica/euclides-interativo`)
- **Citada por** — `rec:matematica/euclides-elementos`

### Os mistérios matemáticos do Professor Stewart: resolvidos por Hemlock Soames e o dr. Watsup

- **Autoria** — Ian Stewart
- **Edição** — 1ª ed., Zahar, 16/07/2015, 320 p., pt-BR
- **Identificadores** — ISBN-13 978-85-378-1454-3 · ISBN-10 `8537814547`
- **Amazon** — https://www.amazon.com.br/dp/8537814547
- **Citada por** — `rec:matematica/stewart-misterios`

### Uma história da simetria na matemática

- **Autoria** — Ian Stewart
- **Edição** — 1ª ed., Zahar, 16/04/2012, 348 p., pt-BR
- **Identificadores** — ISBN-13 978-85-378-0821-4 · ISBN-10 `8537808210`
- **Amazon** — https://www.amazon.com.br/dp/8537808210
- **Citada por** — `rec:matematica/stewart-simetria`

---

## Sistemas operacionais

### Linux Command Line and Shell Scripting Bible

- **Autoria** — Richard Blum, Christine Bresnahan
- **Edição** — 5ª ed., Wiley, 30/12/2025, 688 p., en-US
- **Identificadores** — ISBN-13 978-1-394-36494-7 · ISBN-10 `1394364946`
- **Amazon** — https://www.amazon.com.br/dp/1394364946 — capa comum R$ 268,78
  (importado, tributos inclusos) e Kindle R$ 323,00: o eletrônico sai **mais caro**
  que o impresso. `custo: 270` nos recursos segue o impresso.
- **Citada por** — `rec:so/blum-bible-linha-de-comando`,
  `rec:so/blum-bible-script-shell` — as duas fatias declaram `obra: blum-bible`
- **Nota** — a 5ª edição é de dezembro de 2025 e é a que se compra; a edição do
  exemplar da estante lida ([acervo-lido.md § 1](acervo-lido.md)) não se identificou.
  A diferença não afeta as etapas que a citam: bash e o shell POSIX são
  conservadores. O que a 5ª acrescenta — `zsh`, `tcsh`, ksh e implantação em nuvem —
  está fora da competência das duas etapas, e é por isso que os títulos dos recursos
  dizem quais partes do livro valem.

### Operating Systems: Three Easy Pieces

- **Autoria** — Remzi H. Arpaci-Dusseau, Andrea C. Arpaci-Dusseau
- **Edição** — edição dos autores, 01/09/2018, 708 p., en-US
- **Identificadores** — ISBN-13 978-1-9850-8659-3 · ISBN-10 `198508659X`
- **Amazon** — https://www.amazon.com.br/dp/198508659X
- **Acesso aberto** — https://pages.cs.wisc.edu/~remzi/OSTEP/
- **Citada por** — `rec:so/ostep-introducao`, `rec:so/ostep-concorrencia`,
  `rec:so/ostep-escalonamento`, `rec:so/ostep-memoria`, `rec:so/ostep-persistencia`

### Shell Script Profissional

- **Autoria** — Aurélio Marinho Jargas
- **Edição** — 1ª ed., Novatec, 2008, 480 p., pt-BR. À venda na editora por R$ 109,00
  (impresso); o e-book é vendido na Amazon.
- **Identificadores** — impresso: ISBN-13 978-85-7522-152-5 · ISBN-10 `8575221525` —
  e-book: ISBN-13 978-85-7522-576-9
- **Amazon** — sem página de produto do impresso: `/dp/8575221525` devolve "não foi
  possível encontrar esta página" na loja brasileira. O recurso aponta a editora.
- **Editora** — https://novatec.com.br/livros/shellscript/
- **Citada por** — `rec:so/jargas-shell-script-profissional`
- **Nota** — é livro sobre **escrever script que se mantenha** (portabilidade, POSIX
  contra bash, estilo), e pressupõe a linha de comando em vez de ensiná-la. Por isso
  cita `etapa:so/script-shell` e não `etapa:so/linha-de-comando`
  ([ADR-0010](adr/0010-shell-como-pre-requisito-declarado.md)).

### Sistemas Operacionais: Projeto e Implementação

- **Autoria** — Andrew S. Tanenbaum, Albert S. Woodhull; trad. João Tortello (3ª ed.)
- **Edição citada pelo catálogo** — 2ª ed., Bookman, 2000; ISBN-13 978-85-7307-530-4 ·
  ISBN-10 `8573075309`. Sem página ativa na Amazon brasileira.
- **Edição à venda** — 3ª ed., Bookman, 01/01/2008, 759 p., pt-BR; ISBN-13
  978-85-7780-057-5 · ISBN-10 `8577800571`
- **Amazon** — https://www.amazon.com.br/dp/8577800571 (3ª edição)
- **Citada por** — `rec:so/tanenbaum-woodhull-introducao`,
  `rec:so/tanenbaum-woodhull-processos`, `rec:so/tanenbaum-woodhull-escalonamento`,
  `rec:so/tanenbaum-woodhull-entrada-saida`, `rec:so/tanenbaum-woodhull-memoria`,
  `rec:so/tanenbaum-woodhull-arquivos`
- **Nota** — os recursos mapeiam capítulos por número; ver [§ Divergências](#divergências).

### The Linux Command Line

- **Autoria** — William Shotts
- **Edição citada pelo catálogo** — 7ª edição de internet, 596 p., en-US, sem ISBN:
  é o PDF que o autor publica, em licença Creative Commons BY-NC-ND
- **Edição impressa** — 3ª ed., No Starch Press, 2026, 544 p.; ISBN-13
  978-1-7185-0452-3 · ISBN-10 `1718504527`. Baseada na mesma 7ª edição de internet
- **Acesso aberto** — https://linuxcommand.org/tlcl.php
- **Citada por** — `rec:so/shotts-linha-de-comando`, `rec:so/shotts-script-shell` —
  as duas fatias **não** declaram `obra`, pela mesma razão das cinco do OSTEP: obra
  gratuita soma zero em qualquer agregação monetária
  ([ADR-0009](adr/0009-obra-como-campo-de-agrupamento-no-recurso.md))
- **Nota** — a tradução para português está listada como em andamento no site do
  autor, ainda sem versão publicada. É por isso que
  `etapa:so/linha-de-comando` depende do Guia Foca para o par "gratuito e em pt-BR".

---

## Web

### Async JavaScript: Build More Responsive Apps with Less Code

- **Autoria** — Trevor Burnham — série *Pragmatic Express*
- **Edição** — The Pragmatic Bookshelf, nov./2012 (tiragem de 01/2013), 106 p., en-US
- **Identificadores** — ISBN-13 978-1-937785-27-7 · ISBN-10 `1937785270`
- **Amazon** — https://www.amazon.com.br/dp/1937785270
- **Editora** — https://pragprog.com/titles/tbajs/async-javascript/
- **Citada por** — `rec:web/burnham-async-javascript`

### CSS and Documents

- **Autoria** — Eric A. Meyer
- **Edição** — O'Reilly Media, set./2012, 19 p., en-US — extrato da 4ª edição de
  *CSS: The Definitive Guide*
- **Identificadores** — ISBN-13 978-1-4493-5837-2 (O'Reilly) · 978-1-4493-5838-9
  (ebook) · ASIN `B008RBQHTW` (Kindle)
- **Amazon** — https://www.amazon.com/dp/B008RBQHTW — **não confirmado**: não achei
  página desse extrato na loja brasileira
- **Editora** — https://www.oreilly.com/library/view/css-and-documents/9781449358372/
- **Citada por** — `rec:web/meyer-css-and-documents`

### Data Visualization with D3.js Cookbook

- **Autoria** — Nick Qi Zhu
- **Edição** — Packt Publishing, 24/08/2013, 338 p., en-US
- **Identificadores** — ISBN-13 978-1-78216-216-2 · ISBN-10 `178216216X`
- **Amazon** — https://www.amazon.com.br/dp/178216216X
- **Citada por** — `rec:web/d3-cookbook-zhu`
- **Nota** — o código é de uma versão antiga da API do D3; o recurso já marca isso.

### Desenvolvimento Web com Flask: Desenvolvendo aplicações web com Python

- **Autoria** — Miguel Grinberg — tradução de *Flask Web Development* (O'Reilly)
- **Edição** — Novatec, 2018, 312 p., pt-BR
- **Identificadores** — ISBN-13 978-85-7522-681-0 · ISBN-10 `8575226819` · ebook
  ISBN 978-85-7522-744-2 · ASIN `B07QH2SK7R` (Kindle)
- **Amazon** — https://www.amazon.com.br/dp/8575226819 — impresso R$ 105,00 na
  editora (preço do Kindle não confirmado)
- **Citada por** — `rec:web/grinberg-flask-pt`
- **Nota** — **a conferência corrigiu o relatório.**
  [acervo-lido.md § 4](acervo-lido.md) dava esta tradução como sendo da **1ª** edição
  em inglês (2014, Flask 0.10). A tradução que a Novatec publica e vende é a da **2ª**
  (2018): a própria página da editora a descreve como "edição atualizada" que
  considera "as mudanças importantes de tecnologia ocorridas nos últimos três anos",
  e as 312 páginas batem com as da 2ª edição em inglês, não com as 258 da 1ª. A
  defasagem é real, mas menor do que o relatório afirmava, e segue impedindo o uso
  como recurso primário: a 2ª edição é anterior ao Flask 2 — sem view assíncrona — e
  o capítulo 5, de banco, usa Flask-SQLAlchemy 2, cujos padrões a versão 3 quebrou. A
  parte conceitual (ciclo de pedido e resposta, fábrica de aplicação, blueprint,
  template, teste, implantação, a aplicação *Flasky* construída ao longo do livro)
  envelheceu bem, e é como apoio conceitual que o recurso a cita, com o limite dito no
  título — a mesma convenção dos livros de D3 acima.

### Eloquent JavaScript

- **Autoria** — Marijn Haverbeke
- **Edição** — 4ª ed., No Starch Press, nov./2024, 456 p., en-US
- **Identificadores** — ISBN-13 978-1-7185-0410-3 · ISBN-10 `1718504101` ·
  ASIN `B0D9J9QWK9` (Kindle)
- **Amazon** — https://www.amazon.com.br/dp/B0D9J9QWK9
- **Acesso aberto** — https://eloquentjavascript.net/ (CC BY-NC)
- **Citada por** — `rec:web/eloquent-javascript`

### Mastering D3.js

- **Autoria** — Pablo Navarro Castillo — série *Community Experience Distilled*
- **Edição** — Packt Publishing, ago./2014, 352 p., en-US
- **Identificadores** — ISBN-13 978-1-78328-627-0 · ASIN `B00N1X6926` (Kindle)
- **Amazon** — https://www.amazon.com.br/dp/B00N1X6926
- **Citada por** — `rec:web/mastering-d3-castillo`
- **Nota** — o código é de uma versão antiga da API do D3; o recurso já marca isso.

### Pure React

- **Autoria** — Dave Ceddia
- **Edição** — edição do autor, versão 4.3 do livro, 21 capítulos, en-US. Lançado em
  2016 e revisado desde então; em 2019 ganhou também um curso em vídeo, vendido à
  parte. Só digital: leitura no site, PDF, EPUB e MOBI; não há impresso. A contagem
  de 158 p. que circula é da listagem do Gumroad e corresponde a uma revisão
  anterior.
- **Identificadores** — sem ISBN nem ASIN: venda direta do autor, sem registro
  editorial nem distribuição por livraria.
- **Loja** — https://www.purereact.com/ · também em
  https://dceddia.gumroad.com/l/pure-react
- **Editora** — https://daveceddia.com/ (venda direta)
- **Citada por** — `rec:web/pure-react-ceddia`
- **Nota sobre o preço** — a página oficial não publica valor: os dois pacotes
  aparecem como `$--`, preenchidos por script. As duas consultas que sustentam o
  `custo: 210` divergem — cerca de US$ 39 pelo pacote só do livro no site do autor e
  US$ 29 na listagem do Gumroad. Nenhuma das duas é preço brasileiro nem foi
  conferida no carrinho; ficam ambas registradas, e o `custo` segue pela maior até
  que alguém confira.
- **Nota** — o recorte do livro é deliberado: só React, sem Redux, roteador nem
  ferramenta de build, em exercícios curtos de componente, props e estado. Por isso é
  porta de entrada mais suave da etapa de interface por componentes que *React
  Fluente*, que trata de reconciliação e desempenho. O ferramental é do tempo do
  Create React App, hoje descontinuado — o que envelheceu é o andaime do projeto,
  não a parte de componentes e estado, que é o que a etapa pede.

### React Fluente: crie aplicações web rápidas, eficazes e intuitivas

- **Autoria** — Tejas Kumar
- **Edição** — Novatec Editora, 27/05/2024; 392 p. (impresso), 377 p. (Kindle); pt-BR
- **Identificadores** — ISBN-13 978-85-7522-909-5 (impresso) · 978-85-7522-910-1
  (digital) · ASIN `B0D4FD47PW` (Kindle)
- **Amazon** — https://www.amazon.com.br/dp/B0D4FD47PW
- **Original** — *Fluent React*, O'Reilly, 2024
- **Citada por** — `rec:web/react-fluente`

### TypeScript Básico: Fundamentos e Práticas Essenciais

- **Autoria** — Jardel Vieira Alves
- **Edição** — edição do autor, 13/01/2026, Kindle, pt-BR
- **Identificadores** — ASIN `B0GGKMPH2X` (sem ISBN)
- **Amazon** — https://www.amazon.com.br/dp/B0GGKMPH2X
- **Citada por** — `rec:web/typescript-basico-pt`

### What Every Web Developer Should Know About HTTP

- **Autoria** — K. Scott Allen — série *OdeToCode Programming*, v. 1
- **Edição** — OdeToCode LLC, 06/02/2012, 86 p., Kindle, en-US
- **Identificadores** — ASIN `B0076Z6VMI` (sem ISBN)
- **Amazon** — https://www.amazon.com.br/dp/B0076Z6VMI
- **Citada por** — `rec:web/what-every-web-developer-http`

---

## Economia

### Tecnofeudalismo: o que matou o capitalismo

- **Autoria** — Yanis Varoufakis. Original: *Technofeudalism: What Killed
  Capitalism* (Bodley Head, 2023).
- **Edição** — 1ª ed., Crítica (selo da Planeta), 2025, pt-BR. Kindle publicado em
  28/04/2025, 329 p.; o impresso tem 240 p.
- **Identificadores** — ISBN-13 `9788542233193` (impresso), `9788542233841` (e-book)
- **Amazon** — https://www.amazon.com.br/s?k=9788542233841 (link de busca: o ASIN
  do Kindle não se confirmou. R$ 44,46 no Kindle em 2026-10-18, incluído no Prime;
  o impresso estava a R$ 79,90 na Martins Fontes — o recurso declara o do Kindle)
- **Citada por** — `rec:economia/varoufakis-tecnofeudalismo-caps-1-2`,
  `rec:economia/varoufakis-tecnofeudalismo-caps-3-4`,
  `rec:economia/varoufakis-tecnofeudalismo-caps-5-7`
- **Nota** — o fatiamento por capítulo segue o original em inglês; os títulos da
  edição brasileira não foram conferidos.

## Línguas

### Introducing English Syntax: A Basic Guide for Students of English

- **Autoria** — Peter Fenn e Götz Schwab
- **Edição** — 1ª ed., Routledge, 2018 (lançada em 26/11/2017), 274 p., en-US.
  Exercícios por capítulo, com gabarito comentado nos eResources da editora.
- **Identificadores** — brochura: ISBN-13 978-1-138-03749-6 · ISBN-10 `1138037494`
  — capa dura: ISBN-13 978-1-138-03748-9
- **Amazon** — não conferida. O recurso aponta para a página da editora:
  https://www.routledge.com/Introducing-English-Syntax-A-Basic-Guide-for-Students-of-English/Fenn-Schwab/p/book/9781138037496
- **Citada por** — `rec:linguas/fenn-schwab-english-syntax-caps-1-3`,
  `rec:linguas/fenn-schwab-english-syntax-caps-4-5`,
  `rec:linguas/fenn-schwab-english-syntax-caps-6-9`,
  `rec:linguas/fenn-schwab-english-syntax-caps-10-12`
- **Nota** — lido no Google Play Livros. O `custo: 280` é conversão aproximada do
  preço de lista da brochura em dólar, não o preço pago; a página da editora não
  mostrou preço em 2026-10-21.

## O que não tem ficha

Recursos que não são livros ficam de fora: documentação oficial (MDN, pandas,
scikit-learn, TypeScript Handbook, react.dev, docs.claude.com, MCP), material aberto
de referência (arc42, microservices.io, adr.github.io, DORA, web.dev, ARIA APG,
Paul's Online Math Notes, LibreTexts, Guia Foca Linux), artigos (*Attention Is All You Need*, *The
Illustrated Transformer*, Fowler, fitness functions, *A Mathematical Theory of
Communication* de Shannon, *Notes on Programming in C* de Pike), vídeo (3Blue1Brown, aulas de
*Statistical Rethinking*), repositórios de exercício (anthropic-cookbook) e os
recursos de projeto.

*Statistical Rethinking* (`rec:dados/statistical-rethinking-aulas`) tem livro
homônimo, mas o recurso aponta para as aulas gravadas e o material aberto, não para
o livro — por isso não ganhou ficha.

## Divergências

O que a pesquisa encontrou de desencontrado entre catálogo e obra. Fora a troca de
`url` do item 3, nada foi alterado em `catalogo/` — são apontamentos para decidir
depois.

1. **`rec:ia/ettucode-llm-transformer-rag`** declara o ISBN 9798882446481 e
   `formato: texto`. Esse ISBN é o do **audiolivro**. Ou o formato está errado, ou o
   identificador — e não localizei uma edição em texto à venda na Amazon.
2. **`rec:so/tanenbaum-woodhull-*`** citam a 2ª edição, que não está à venda na Amazon
   brasileira; o que circula é a 3ª (2008). Os seis recursos mapeiam capítulos por
   número, e a numeração **muda** entre as edições — vale fixar qual edição o catálogo
   assume.
3. **URL de busca em vez de página de produto.** Eram 35 recursos assim
   (`/s?k=...`). Em 2026-10-13, 27 passaram a apontar para a página do produto, sem
   subir `rev` — troca de `url` equivalente é cosmética (docs/catalogo.md §4). As
   oito fatias de Date entraram em 2026-10-15 com URL de busca e, no mesmo dia e sem
   subir `rev` pelo mesmo motivo, passaram para a página da capa dura (ISBN-10
   `0201513811`), que é a tiragem à venda na loja brasileira. Seguem em busca, de
   propósito, 8 recursos: os 6 de Tanenbaum & Woodhull, porque o link direto seria o
   da 3ª edição e o título diz 2ª (item 2); o de *LLM, Transformer, RAG AI*, porque
   não há página de produto (item 1); e o de *CSS and Documents*, que só existe na
   loja americana (item 5). `rec:web/pure-react-ceddia` **não** entra nesta
   lista: o livro não é vendido na Amazon, e o recurso aponta para a loja do próprio
   autor (https://www.purereact.com/), que é a página de produto.
4. **`rec:programacao/python-fluente-2ed`** aponta para a 2ª edição aberta em
   português, que não existe impressa; a edição impressa em português é a 1ª (2015).
   O recurso está correto, mas o título dele pode induzir a procurar um livro que não
   há na loja.
5. **`rec:web/meyer-css-and-documents`** é um extrato de 19 páginas da 4ª edição de
   *CSS: The Definitive Guide*, não um livro próprio, e não achei página dele na loja
   brasileira.
6. **`rec:engenharia/google-sre-books`** é uma coletânea de vários livros tratada como
   um recurso só. Se o motor for pesar esforço por recurso, isso vai distorcer.
7. **`rec:dados/date-vol1-*`** declaram `custo: 90` cada uma, para um exemplar só
   ([ADR-0009](adr/0009-obra-como-campo-de-agrupamento-no-recurso.md) agrupou as oito
   em `obra: date-vol1`). O comentário do YAML diz que 90 é o preço de um usado, mas em
   2026-10-15 a loja brasileira pedia **R$ 548,00** pela capa dura usada, e a capa comum
   estava indisponível. O mesmo comentário diz que o exemplar já está na estante — então
   `custo` ora parece ser o que foi pago, ora o preço de reposição, e os dois não são a
   mesma coisa para o filtro de `custo_maximo`. Vale fixar qual dos dois `custo`
   significa antes de corrigir o número.
