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

Desde [ADR-0020](adr/0020-obra-declarada-tambem-em-exemplar-nao-fatiado.md) a
confrontação vale nos dois sentidos. **Refeita em 2026-11-01, depois de escritas as
fichas que faltavam, ela fecha**: das 82 fichas deste documento, 81 têm `obra`
declarada no catálogo — antes da ADR eram 24 —, e **nenhuma das 81 obras do catálogo
está sem ficha**. A única ficha sem `obra` é a de *Python Fluente*, e é de propósito:
o recurso está depreciado desde 2026-10-22, e recurso depreciado não recebe `obra`
nova (ADR-0020).

As onze obras que a confrontação listava como pendentes saíram da lista por dois
caminhos. **Oito ganharam ficha**: as quatro de Hari Chetan
(`chetan-30-dias-gita`, `chetan-daily-bhakti`, `chetan-gita-resumida`,
`chetan-gita-traducao-autentica`), `flanagan-javascript-definitive-guide`,
`klabnik-nichols-rust-book`, `kurniawan-node-succinctly` e
`winand-use-the-index-luke`. **Três deixaram de declarar `obra`**, porque a ficha foi
o primeiro momento em que alguém olhou o material de perto e ele não era livro:
`beej-guide-c`, `beej-guide-ipc` e `guiafoca-linux` são referência aberta, sem editora,
sem ISBN e sem edição à venda, e estão no
[§ O que não tem ficha](#o-que-não-tem-ficha). Nos três, remover `obra` subiu a `rev`
de 2 para 3, pela mesma regra que a havia subido ao acrescentá-la: `rev` nunca
decresce (CAT-090, [catalogo.md §4](catalogo.md)).

A conferência se refaz com
`uv run python -c` sobre o lock e este arquivo; ela não entra na validação, pela
mesma razão de sempre — este documento é descritivo.

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
*Desenvolvimento Web com Flask*, acrescentadas em 2026-10-17, e as oito acrescentadas
em 2026-11-01 — as quatro de Hari Chetan, *JavaScript: The Definitive Guide*,
*Node.js Succinctly*, *SQL Performance Explained* e *The Rust Programming Language*
—, conferidas nessa data.

Preço, como regra, não entra aqui — vive em `custo` no recurso, com seu próprio
`verificado_em`, e a pesquisa de 2026-10-12 não o alterou: conferiu link e edição,
não preço. As nove fichas acrescentadas em 2026-10-17 são a exceção e **citam**
preço, porque nelas o `custo` do recurso foi fixado na mesma passada — no caso do
Tufte o preço é o próprio motivo de a ficha dizer qual tiragem o recurso aponta, e no
do *Shell Scripting Bible* ele registra que o Kindle sai mais caro que o impresso. As
quatro fichas de Hari Chetan de 2026-11-01 são a outra exceção, pela mesma razão: o
preço no Google Play BR é o que fixou o `custo` daqueles recursos, e a paginação delas
vem da mesma página de loja.

As divergências encontradas entre o catálogo e a obra real estão reunidas no
[§ Divergências](#divergências) no fim.

### Observação datada — 2026-11-05

A confrontação de 2026-11-01 (acima) **não fecha mais**, e não por causa dela: o
catálogo cresceu. Hoje são **85 obras com fatia ativa** e **83 fichas**, e quatro
obras não são citadas por ficha nenhuma. Uma é a deste dia,
`price-toscani-compiladores`, que ganhou ficha agora. As outras três entraram com as
trilhas de literatura e de estatística e seguem **sem ficha**:
`poe-o-corvo`, `lakens-statistical-inferences` e `reinhart-statistics-done-wrong`.

Regenere a lista em vez de confiar nesta:

```bash
python3 -c 'import json,pathlib;d=json.load(open("catalogo.lock.json"));b=pathlib.Path("docs/bibliografia.md").read_text();o={};[o.setdefault(r["obra"],[]).append(r["id"]) for r in d["recursos"] if r.get("obra")];print([k for k,v in o.items() if not any(i in b for i in v)])'
```

---

---

## Arquitetura de computadores

### Arquitetura de Computadores Pessoais

- **Autoria** — Raul Fernando Weber
- **Edição** — Série Livros Didáticos do Instituto de Informática da UFRGS (Sagra
  Luzzatto; reedições pela Bookman), pt-BR. Edição, data, páginas e ISBN **não
  confirmados**: o livro entrou no catálogo pela lista da série impressa num livro da
  coleção, fotografada pelo estudante em 2026-11-11, e não pelo exemplar
- **Amazon** — https://www.amazon.com.br/s?k=Arquitetura+de+Computadores+Pessoais+Raul+Weber — link de busca;
  página de produto não confirmada
- **Citada por** — `rec:arquitetura/weber-arquitetura-pcs` — declara `obra: weber-arquitetura-pcs`

### Concepção de Circuitos Integrados

- **Autoria** — Ricardo Augusto da Luz Reis (org.)
- **Edição** — Série Livros Didáticos do Instituto de Informática da UFRGS (Sagra
  Luzzatto; reedições pela Bookman), pt-BR. Edição, data, páginas e ISBN **não
  confirmados**: o livro entrou no catálogo pela lista da série impressa num livro da
  coleção, fotografada pelo estudante em 2026-11-11, e não pelo exemplar
- **Amazon** — https://www.amazon.com.br/s?k=Concep%C3%A7%C3%A3o+de+Circuitos+Integrados+Ricardo+Reis — link de busca;
  página de produto não confirmada
- **Citada por** — `rec:arquitetura/reis-concepcao-circuitos-integrados` — declara
  `obra: reis-concepcao-circuitos-integrados`

### Fundamentos de Arquitetura de Computadores

- **Autoria** — Raul Fernando Weber
- **Edição** — Série Livros Didáticos do Instituto de Informática da UFRGS (Sagra
  Luzzatto; reedições pela Bookman), pt-BR. Edição, data, páginas e ISBN **não
  confirmados**: o livro entrou no catálogo pela lista da série impressa num livro da
  coleção, fotografada pelo estudante em 2026-11-11, e não pelo exemplar
- **Amazon** — https://www.amazon.com.br/s?k=Fundamentos+de+Arquitetura+de+Computadores+Raul+Weber — link de busca;
  página de produto não confirmada
- **Citada por** — `rec:arquitetura/weber-fundamentos-maquinas-de-acumulador`,
  `rec:arquitetura/weber-fundamentos-cesar-e-montagem` — as duas declaram
  `obra: weber-fundamentos-arquitetura`
- **Nota** — fatias por **assunto** (máquinas de acumulador; o Cesar), não por capítulo:
  trocar por "cap. N, ..." com o exemplar em mão é cosmético ([catalogo.md §4](catalogo.md))

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

### Projeto de Banco de Dados

- **Autoria** — Carlos Alberto Heuser
- **Edição** — Série Livros Didáticos do Instituto de Informática da UFRGS (Sagra
  Luzzatto; reedições pela Bookman), pt-BR. Edição, data, páginas e ISBN **não
  confirmados**: o livro entrou no catálogo pela lista da série impressa num livro da
  coleção, fotografada pelo estudante em 2026-11-11, e não pelo exemplar
- **Amazon** — https://www.amazon.com.br/s?k=Projeto+de+Banco+de+Dados+Heuser — link de busca;
  página de produto não confirmada
- **Citada por** — `rec:dados/heuser-abordagem-relacional`, `rec:dados/heuser-normalizacao`,
  `rec:dados/heuser-modelagem-er-e-transformacao` — as três declaram
  `obra: heuser-projeto-de-banco-de-dados`
- **Nota** — fatias por **assunto**; o sumário não foi conferido em exemplar

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

### SQL Performance Explained: Everything Developers Need to Know about SQL Performance

- **Autoria** — Markus Winand
- **Edição** — edição do autor, 30/07/2012, 204 p., en-US. Cobre Oracle, MySQL,
  PostgreSQL, SQL Server e Db2 lado a lado. A edição alemã, de maio de 2012 e mesma
  paginação, tem ISBN-13 978-3-9503078-1-8.
- **Identificadores** — ISBN-13 978-3-9503078-2-5 · ISBN-10 `3950307826`
- **Amazon** — https://www.amazon.com.br/dp/3950307826 (página da loja brasileira não
  conferida; o autor vende brochura e PDF na própria loja, a partir de € 9,95)
- **Acesso aberto** — https://use-the-index-luke.com/ — *Use The Index, Luke!* é a
  edição web gratuita deste livro, nas palavras do próprio site ("free web-edition of
  my book"). É esta edição que o catálogo cita, e é dela que vem o `custo: 0` do
  recurso: o preço do impresso é outro.
- **Citada por** — `rec:dados/use-the-index-luke` — declara
  `obra: winand-use-the-index-luke`
- **Nota** — a `obra` leva o nome do site, não do livro, porque é o site que o recurso
  aponta. É o mesmo arranjo de *The Linux Command Line*: edição aberta citada pelo
  catálogo, impresso existindo ao lado.

### Tabelas: Organização e Pesquisa

- **Autoria** — Clésio dos Santos, Paulo de Azeredo
- **Edição** — Série Livros Didáticos do Instituto de Informática da UFRGS (Sagra
  Luzzatto; reedições pela Bookman), pt-BR. Edição, data, páginas e ISBN **não
  confirmados**: o livro entrou no catálogo pela lista da série impressa num livro da
  coleção, fotografada pelo estudante em 2026-11-11, e não pelo exemplar
- **Amazon** — https://www.amazon.com.br/s?k=Tabelas+Organiza%C3%A7%C3%A3o+e+Pesquisa+Cl%C3%A9sio+dos+Santos — link de busca;
  página de produto não confirmada
- **Citada por** — `rec:dados/santos-azeredo-tabelas` — declara `obra: santos-azeredo-tabelas`

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

### Implementação de Linguagens de Programação: Compiladores

- **Autoria** — Ana Maria de Alencar Price, Simão Sirineo Toscani
- **Edição citada pelo catálogo** — Instituto de Informática da UFRGS / Sagra Luzzatto,
  Porto Alegre, 2000, pt-BR; Série Livros Didáticos nº 9. É o exemplar que o estudante
  tem: ISBN-10 `8524106395`. ISBN-13 e paginação **não confirmados** — a listagem da
  Amazon dá 200 p., e não foi possível ler a página para conferir
- **Reimpressão posterior** — Bookman / Instituto de Informática da UFRGS, 2008, citada
  por ementa de disciplina; sem ISBN nem paginação confirmados
- **Amazon** — https://www.amazon.com.br/dp/8524106395 (o ISBN-10 como ASIN, pela
  convenção acima). A página devolveu HTTP 503 à leitura automatizada em 2026-11-05;
  abre no navegador
- **Citada por** — `rec:programacao/price-toscani-estrutura`,
  `rec:programacao/price-toscani-analise-lexica`,
  `rec:programacao/price-toscani-analise-sintatica`,
  `rec:programacao/price-toscani-analise-semantica`,
  `rec:programacao/price-toscani-geracao-de-codigo` — as cinco declaram
  `obra: price-toscani-compiladores`
- **Nota** — **o sumário não foi confirmado em fonte nenhuma**: Amazon 503, Estante
  Virtual 403, e nem a editora nem a UFRGS publicam a lista de capítulos. As cinco
  fatias são por **assunto** — estrutura, léxica, sintática, semântica, geração —,
  não por número de capítulo, e nisso divergem da convenção de Tanenbaum & Woodhull
  (ver [§ Divergências](#divergências)). A ordem dos assuntos vem de duas ementas que
  adotam o livro, não do livro: ela é plausível e não é verificada. Quem tiver o
  exemplar em mão: trocar os títulos por "cap. N, ..." é cosmético
  ([catalogo.md §4](catalogo.md)) e não sobe `rev`

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

### Natural Language Processing with Python: Analyzing Text with the Natural Language Toolkit

- **Autoria** — Steven Bird, Ewan Klein, Edward Loper
- **Edição** — 1ª ed., O'Reilly, 2009, en-US. O catálogo usa a edição on-line, que
  a página do livro diz "updated for Python 3 and NLTK 3"; a 1ª edição impressa
  segue em https://www.nltk.org/book_1ed/, e os autores dizem não haver plano de 2ª.
- **Identificadores** — ISBN-13 `9780596516499`
- **Amazon** — https://www.amazon.com.br/s?k=9780596516499 (link de busca)
- **Acesso aberto** — https://www.nltk.org/book/ (CC BY-NC-ND 3.0 US)
- **Sumário** — 1 Language Processing and Python; 2 Accessing Text Corpora and
  Lexical Resources; 3 Processing Raw Text; 4 Writing Structured Programs;
  5 Categorizing and Tagging Words; 6 Learning to Classify Text; 7 Extracting
  Information from Text; 8 Analyzing Sentence Structure; 9 Building Feature Based
  Grammars; 10 Analyzing the Meaning of Sentences; 11 Managing Linguistic Data;
  12 Afterword.
- **Citada por** — `rec:ia/nltk-book-caps-1-3`, `rec:ia/nltk-book-cap-6-classificar-texto`,
  `rec:ia/nltk-book-cap-6-exercicios` — declaram `obra: bird-klein-loper-nltk`

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
- **Citada por** — `rec:ia/prompt-engineering-for-llms`, e os capítulos `rec:ia/prompt-engineering-for-llms-cap-01` a `-cap-11` como partes dele (`obra: berryman-ziegler-prompt-engineering`, a mesma do todo, ADR-0021)

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

### Sentiment Analysis and Opinion Mining

- **Autoria** — Bing Liu
- **Edição** — Morgan & Claypool, série *Synthesis Lectures on Human Language
  Technologies*, maio/2012, en-US. A página do autor diz 165 páginas no cabeçalho e
  167 no corpo; nenhuma das duas foi conferida no exemplar.
- **Identificadores** — ISBN-13 `9781608458844` (brochura), `9781608458851` (e-book)
- **Amazon** — https://www.amazon.com.br/s?k=9781608458844 (link de busca)
- **Acesso aberto** — rascunho publicado pelo autor:
  https://www.cs.uic.edu/~liub/FBS/SentimentAnalysis-and-OpinionMining.pdf, a partir
  de https://www.cs.uic.edu/~liub/FBS/SentimentAnalysis-and-OpinionMining.html
- **Sumário** — 1 Sentiment Analysis: A Fascinating Problem; 2 The Problem of
  Sentiment Analysis; 3 Document Sentiment Classification; 4 Sentence Subjectivity
  and Sentiment Classification; 5 Aspect-based Sentiment Analysis; 6 Sentiment
  Lexicon Generation; 7 Opinion Summarization; 8 Analysis of Comparative Opinions;
  9 Opinion Search and Retrieval; 10 Opinion Spam Detection; 11 Quality of Reviews;
  12 Concluding Remarks.
- **Citada por** — `rec:ia/liu-2012-caps-1-2-o-problema`,
  `rec:ia/liu-2012-caps-3-4-classificacao`, `rec:ia/liu-2012-caps-5-7-aspecto-e-resumo`,
  `rec:ia/liu-2012-caps-8-10-11-comparativa-e-spam` — declaram
  `obra: liu-sentiment-analysis-opinion-mining`
- **Nota** — o cap. 6, de léxico, não tem fatia: a etapa de léxicos usa o cap. 7 da
  edição de 2020, que trata o mesmo assunto mais extenso.

### Sentiment Analysis: Mining Opinions, Sentiments, and Emotions

- **Autoria** — Bing Liu
- **Edição** — 2ª ed., Cambridge University Press (série *Studies in Natural
  Language Processing*), 2020, 448 p., en-US; 1ª ed. de 2015.
- **Identificadores** — ISBN-13 `9781108486378` (2ª ed., capa dura). A página do
  autor rotula como ISBN da capa dura o `9781107017894`, que é o da 1ª edição; o
  `9781108486378` é o que a própria página usa no link do sumário da Cambridge e o
  que as lojas listam para a 2ª.
- **Amazon** — https://www.amazon.com.br/s?k=9781108486378 (link de busca)
- **Acesso aberto** — só os caps. 1 e 2, publicados pelo autor:
  https://www.cs.uic.edu/~liub/FBS/chapter-1-and-chapter-2.pdf
- **Sumário** — https://www.cs.uic.edu/~liub/FBS/sentiment-opinion-emotion-analysis.html,
  sem número na página; a numeração abaixo é a ordem dela: 1 Introduction; 2 The
  Problem of Sentiment Analysis; 3 Document Sentiment Classification; 4 Sentence
  Subjectivity and Sentiment Classification; 5 Aspect Sentiment Classification;
  6 Aspect and Entity Extraction; 7 Sentiment Lexicon Generation; 8 Analysis of
  Comparative Opinions; 9 Opinion Summarization and Search; 10 Analysis of Debates
  and Comments; 11 Mining Intentions; 12 Detecting Fake or Deceptive Opinions;
  13 Quality of Reviews; 14 Conclusions.
- **Citada por** — `rec:ia/liu-2020-caps-1-2-o-problema`, `rec:ia/liu-2020-cap-7-geracao-de-lexico`,
  `rec:ia/liu-2020-caps-5-6-aspecto`, `rec:ia/liu-2020-caps-8-12-13-comparativa-e-falsa`
  — declaram `obra: liu-sentiment-analysis-2ed`
- **Nota** — **o `custo` de R$ 450 é estimativa** do impresso importado, fixada em
  2026-11-14: nenhuma loja cedeu preço ao `curl` deste ambiente. Como a numeração dos
  capítulos é inferida da ordem do sumário, confira o título ao abrir o livro.

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
  `rec:ia/jurafsky-martin-etiquetagem-sequencial`,
  `rec:ia/jurafsky-martin-naive-bayes-e-regressao-logistica`,
  `rec:ia/jurafsky-martin-lexicos-de-sentimento`
- **Nota** — a numeração de capítulo muda entre rascunhos da 3ª edição, e os
  recursos citam o PDF por número (`3.pdf`, `18.pdf`, `A.pdf`). Ao conferir um
  link, confira o **título** do capítulo, não o número.
  O rascunho de 2026-01-06, conferido em 2026-11-14, numera Naive Bayes como
  apêndice B, regressão logística como cap. 4 (*Logistic Regression and Text
  Classification*) e léxicos de sentimento como cap. 22; os dois recursos da
  trilha de análise de sentimentos apontam para o índice, não para o PDF, por isso.

### Text Mining with R: A Tidy Approach

- **Autoria** — Julia Silge, David Robinson
- **Edição** — O'Reilly, 2017, xi + 184 p., en-US. A edição on-line foi
  reconstruída em 2025-04-07, segundo a própria página.
- **Identificadores** — ISBN-13 `9781491981658`
- **Amazon** — https://www.amazon.com.br/s?k=9781491981658 (link de busca)
- **Acesso aberto** — https://www.tidytextmining.com/ (CC BY-NC-SA 3.0 US)
- **Sumário** — 1 The tidy text format; 2 Sentiment analysis with tidy data;
  3 Analyzing word and document frequency: tf-idf; 4 Relationships between words:
  n-grams and correlations; 5 Converting to and from non-tidy formats; 6 Topic
  modeling; 7–9 estudos de caso (Twitter, metadados da NASA, Usenet).
- **Citada por** — `rec:ia/silge-robinson-caps-1-4` — declara
  `obra: silge-robinson-text-mining-r`

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

### The Rust Programming Language

- **Autoria** — Steve Klabnik, Carol Nichols e, desde a 3ª edição, Chris Krycho, com
  contribuições da comunidade Rust
- **Edição** — 3ª ed., No Starch Press, 31/03/2026, 624 p., en-US. A 2ª edição é de
  2023. A edição web, que é a que o catálogo cita, acompanha o compilador: em
  2026-11-01 ela pressupõe Rust 1.97.0 e `edition = "2024"` no `Cargo.toml`.
- **Identificadores** — 3ª ed.: ISBN-13 978-1-7185-0444-8 · ISBN-10 `1718504446`;
  e-book 978-1-7185-0445-5
- **Amazon** — https://www.amazon.com.br/dp/1718504446 (página da loja brasileira não
  conferida)
- **Editora** — https://nostarch.com/rust-programming-language-3e
- **Acesso aberto** — https://doc.rust-lang.org/book/ (texto integral, mantido pelo
  projeto Rust, que é quem detém o direito autoral da 3ª edição)
- **Citada por** — `rec:programacao/rust-book-sistemas` (caps. 1 a 12) — declara
  `obra: klabnik-nichols-rust-book`
- **Nota** — ver [§ Divergências](#divergências): o recurso cita dois autores e um
  recorte por número de capítulo, e a edição web que ele aponta passou a ter três
  autores e a numeração da 3ª edição.

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

### Fundamentos da Matemática Intervalar

- **Autoria** — Paulo Werlang de Oliveira, Tiarajú Asmuz Diverio, Dalcidio Moraes Claudio
- **Edição** — Série Livros Didáticos do Instituto de Informática da UFRGS (Sagra
  Luzzatto; reedições pela Bookman), pt-BR. Edição, data, páginas e ISBN **não
  confirmados**: o livro entrou no catálogo pela lista da série impressa num livro da
  coleção, fotografada pelo estudante em 2026-11-11, e não pelo exemplar
- **Amazon** — https://www.amazon.com.br/s?k=Fundamentos+da+Matem%C3%A1tica+Intervalar — link de busca;
  página de produto não confirmada
- **Citada por** — `rec:matematica/oliveira-diverio-claudio-matematica-intervalar` — declara
  `obra: oliveira-diverio-claudio-matematica-intervalar`

### Fundamentos de Matemática Elementar 1: Conjuntos, Funções

- **Autoria** — Gelson Iezzi e Carlos Murakami
- **Edição** — 9ª ed., Atual Editora, 2013, 410 p., pt-BR; a capa traz o selo
  "Novas questões de vestibulares" desta edição. Volume 1 da coleção de onze. Dez
  capítulos — noções de lógica, conjuntos, conjuntos numéricos, relações,
  introdução às funções, função constante e afim, função quadrática, função
  modular, outras funções elementares, função composta e inversa — e dois
  apêndices, equações e inequações irracionais. Exercícios com gabarito no fim.
  Lido no Kindle.
- **Identificadores** — ISBN-13 978-85-357-1680-1 · ISBN-10 `8535716807`; ASIN do
  Kindle não conferido
- **Amazon** — https://www.amazon.com.br/dp/8535716807 — página e preço não
  conferidos em 2026-10-24; o `custo: 100` é estimativa
- **Citada por** — `rec:matematica/iezzi-fme-1-caps-1-2`,
  `rec:matematica/iezzi-fme-1-caps-3-10`
- **Nota** — os caps. 1 e 2 vão para a raiz de
  `trilha:matematica/prova-e-calculo`, como entrada em pt-BR antes do Book of
  Proof; o resto do livro sustenta `etapa:matematica/funcoes-elementares`, base
  opcional criada para ele, porque nenhuma etapa da trilha ensinava funções.

### Os mistérios matemáticos do Professor Stewart: resolvidos por Hemlock Soames e o dr. Watsup

- **Autoria** — Ian Stewart
- **Edição** — 1ª ed., Zahar, 16/07/2015, 320 p., pt-BR
- **Identificadores** — ISBN-13 978-85-378-1454-3 · ISBN-10 `8537814547`
- **Amazon** — https://www.amazon.com.br/dp/8537814547
- **Citada por** — `rec:matematica/stewart-misterios`

### Programando em Pascal XSC

- **Autoria** — Charles Hoher, Carlos Amaral Holbig, Tiarajú Asmuz Diverio
- **Edição** — Série Livros Didáticos do Instituto de Informática da UFRGS (Sagra
  Luzzatto; reedições pela Bookman), pt-BR. Edição, data, páginas e ISBN **não
  confirmados**: o livro entrou no catálogo pela lista da série impressa num livro da
  coleção, fotografada pelo estudante em 2026-11-11, e não pelo exemplar
- **Amazon** — https://www.amazon.com.br/s?k=Programando+em+Pascal+XSC — link de busca;
  página de produto não confirmada
- **Citada por** — `rec:matematica/hoher-holbig-diverio-pascal-xsc` — declara
  `obra: hoher-holbig-diverio-pascal-xsc`

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

### Sistemas Operacionais

- **Autoria** — Rômulo Silva de Oliveira, Alexandre da Silva Carissimi, Simão Sirineo Toscani
- **Edição** — Série Livros Didáticos do Instituto de Informática da UFRGS (Sagra
  Luzzatto; reedições pela Bookman), pt-BR. Edição, data, páginas e ISBN **não
  confirmados**: o livro entrou no catálogo pela lista da série impressa num livro da
  coleção, fotografada pelo estudante em 2026-11-11, e não pelo exemplar
- **Amazon** — https://www.amazon.com.br/s?k=Sistemas+Operacionais+Oliveira+Carissimi+Toscani — link de busca;
  página de produto não confirmada
- **Citada por** — `rec:so/oliveira-carissimi-toscani-introducao`,
  `rec:so/oliveira-carissimi-toscani-programacao-concorrente`,
  `rec:so/oliveira-carissimi-toscani-gerencia-do-processador`,
  `rec:so/oliveira-carissimi-toscani-gerencia-de-memoria`,
  `rec:so/oliveira-carissimi-toscani-gerencia-de-entrada-e-saida`,
  `rec:so/oliveira-carissimi-toscani-sistema-de-arquivos` — as seis declaram
  `obra: oliveira-carissimi-toscani-so`
- **Nota** — fatias por **assunto**, uma por etapa de conceito da trilha de SO; o livro não
  entra no projeto do MINIX, que é do Tanenbaum & Woodhull

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
  as duas fatias declaram `obra: shotts-tlcl`. Até 2026-11-01 não declaravam, pela
  razão que valia também para as cinco do OSTEP — obra gratuita soma zero em qualquer
  agregação monetária
  ([ADR-0009](adr/0009-obra-como-campo-de-agrupamento-no-recurso.md)) —, e a
  [ADR-0020](adr/0020-obra-declarada-tambem-em-exemplar-nao-fatiado.md) inverteu isso:
  `obra` é o que torna o exemplar endereçável, e sem ela a trilha não tem como listar
  o livro
- **Nota** — a tradução para português está listada como em andamento no site do
  autor, ainda sem versão publicada. É por isso que
  `etapa:so/linha-de-comando` depende do Guia Foca para o par "gratuito e em pt-BR".

---

## Teoria da computação

### Complexidade de Algoritmos

- **Autoria** — Laira Vieira Toscani, Paulo A. S. Veloso
- **Edição** — Série Livros Didáticos do Instituto de Informática da UFRGS (Sagra
  Luzzatto; reedições pela Bookman), pt-BR. Edição, data, páginas e ISBN **não
  confirmados**: o livro entrou no catálogo pela lista da série impressa num livro da
  coleção, fotografada pelo estudante em 2026-11-11, e não pelo exemplar
- **Amazon** — https://www.amazon.com.br/s?k=Complexidade+de+Algoritmos+Toscani+Veloso — link de busca;
  página de produto não confirmada
- **Citada por** — `rec:computacao/toscani-veloso-complexidade-de-algoritmos` — declara
  `obra: toscani-veloso-complexidade-de-algoritmos`

### Linguagens Formais e Autômatos

- **Autoria** — Paulo Blauth Menezes
- **Edição** — Série Livros Didáticos do Instituto de Informática da UFRGS (Sagra
  Luzzatto; reedições pela Bookman), pt-BR. Edição, data, páginas e ISBN **não
  confirmados**: o livro entrou no catálogo pela lista da série impressa num livro da
  coleção, fotografada pelo estudante em 2026-11-11, e não pelo exemplar
- **Amazon** — https://www.amazon.com.br/s?k=Linguagens+Formais+e+Aut%C3%B4matos+Paulo+Blauth+Menezes — link de busca;
  página de produto não confirmada
- **Citada por** — `rec:computacao/menezes-linguagens-formais-e-automatos` — declara
  `obra: menezes-linguagens-formais-e-automatos`

### Linguagens formais: teorias e conceitos

- **Autoria** — Marcus Vinicius Midena Ramos, João José Neto, Italo Santiago Vega
- **Edição** — Blucher (série *Research and Practice in Computing*), 2023, 1ª edição,
  608 p., brochura, 17×24 cm, pt-BR. Conferida na página da editora em 2026-11-12 —
  é a única ficha desta seção que não veio de lista fotografada
- **Identificadores** — ISBN-13 978-65-5506-716-3; ISBN-10 6555067160
- **Amazon** — https://www.amazon.com.br/dp/6555067160 — página de produto confirmada
- **Editora** — https://www.blucher.com.br/linguagens-formais-9786555067163 — publica
  o sumário em oito capítulos, e é ele que fatiou o exemplar entre as duas etapas, por
  número de capítulo e não por assunto
- **Preço** — ficha que cita preço, pela exceção do § *Como ler uma ficha*: o `custo`
  dos recursos foi fixado nesta passada. Em 2026-11-12, R$ 146,99 à vista no Pix na
  Amazon (lista R$ 163,33; outras 19 ofertas a partir de R$ 160,00) e R$ 235,00 na
  editora. Há e-book anunciado pela editora, de preço não observado
- **Citada por** — `rec:computacao/ramos-linguagens-regulares-e-livres-de-contexto` e
  `rec:computacao/ramos-linguagens-recursivas-e-decidibilidade` — ambos declaram
  `obra: ramos-neto-vega-linguagens-formais`
- **Nota** — venceu a 1ª edição do Prêmio Jabuti Acadêmico, segundo a página da
  editora. A capa da Amazon traz o título como *Linguagens Formais: Teorias e
  Conceitos*; a editora separa título e subtítulo (*Linguagens formais* /
  *Teorias e conceitos*). O catálogo usa a forma da editora

### Teoria da Computação: Máquinas Universais e Computabilidade

- **Autoria** — Tiarajú Asmuz Diverio, Paulo Blauth Menezes
- **Edição** — Série Livros Didáticos do Instituto de Informática da UFRGS (Sagra
  Luzzatto; reedições pela Bookman), pt-BR. Edição, data, páginas e ISBN **não
  confirmados**: o livro entrou no catálogo pela lista da série impressa num livro da
  coleção, fotografada pelo estudante em 2026-11-11, e não pelo exemplar
- **Amazon** — https://www.amazon.com.br/s?k=Teoria+da+Computa%C3%A7%C3%A3o+Diverio+Menezes — link de busca;
  página de produto não confirmada
- **Citada por** — `rec:computacao/diverio-menezes-teoria-da-computacao` — declara
  `obra: diverio-menezes-teoria-da-computacao`
- **Nota** — o subtítulo é o com que o livro circula nas edições da Bookman, não
  conferido em exemplar; a lista fotografada traz só *Teoria da Computação*

### Teoria das Categorias para Ciência da Computação

- **Autoria** — Paulo Blauth Menezes, Edward Hermann Haeusler
- **Edição** — Série Livros Didáticos do Instituto de Informática da UFRGS (Sagra
  Luzzatto; reedições pela Bookman), pt-BR. Edição, data, páginas e ISBN **não
  confirmados**: o livro entrou no catálogo pela lista da série impressa num livro da
  coleção, fotografada pelo estudante em 2026-11-11, e não pelo exemplar
- **Amazon** — https://www.amazon.com.br/s?k=Teoria+das+Categorias+Ci%C3%AAncia+da+Computa%C3%A7%C3%A3o+Menezes+Haeusler — link de busca;
  página de produto não confirmada
- **Citada por** — `rec:computacao/menezes-haeusler-teoria-das-categorias` — declara
  `obra: menezes-haeusler-teoria-das-categorias`
- **Nota** — a lista fotografada dá o título como *Teoria das Categorias e Ciência da
  Computação*; o catálogo usa "para", título com que o livro circula nas edições da
  Bookman — divergência não resolvida sem o exemplar

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

### JavaScript: The Definitive Guide

- **Autoria** — David Flanagan
- **Edição** — 7ª ed., O'Reilly Media, 23/06/2020, 704 p., en-US. Reescrita para
  JavaScript moderno, até ES2020.
- **Identificadores** — ISBN-13 978-1-491-95202-3 · ISBN-10 `1491952024`
- **Amazon** — https://www.amazon.com.br/dp/1491952024 (página da loja brasileira não
  conferida)
- **Editora** — https://www.oreilly.com/library/view/javascript-the-definitive/9781491952016/
  — é o endereço que o recurso aponta, que é a leitura pela assinatura O'Reilly e não
  a compra; o `custo: 300` é o do impresso
- **Citada por** — `rec:web/flanagan-javascript-linguagem-e-dom` (caps. 1 a 12, 14 e
  15) — declara `obra: flanagan-javascript-definitive-guide`
- **Nota** — dos 17 capítulos ficam de fora o 13 (assíncrono), o 16 (Node) e o 17
  (ferramental). Os dois primeiros não são lacuna da trilha: o assíncrono tem recurso
  próprio na mesma etapa (*Async JavaScript*, acima) e o Node tem
  `etapa:web/javascript-no-servidor`.

### Mastering D3.js

- **Autoria** — Pablo Navarro Castillo — série *Community Experience Distilled*
- **Edição** — Packt Publishing, ago./2014, 352 p., en-US
- **Identificadores** — ISBN-13 978-1-78328-627-0 · ASIN `B00N1X6926` (Kindle)
- **Amazon** — https://www.amazon.com.br/dp/B00N1X6926
- **Citada por** — `rec:web/mastering-d3-castillo`
- **Nota** — o código é de uma versão antiga da API do D3; o recurso já marca isso.

### Node.js Succinctly

- **Autoria** — Agus Kurniawan
- **Edição** — Syncfusion, abr./2014, 109 p., e-book, en-US. Série *Succinctly*, de
  e-books curtos que a Syncfusion publica de graça. Sem edição impressa e sem ISBN.
- **Amazon** — não se aplica
- **Acesso aberto** — era o PDF que a Syncfusion distribuía após cadastro, com
  licença de leitura condicionada a obtê-lo em syncfusion.com. Em 2026-11-01,
  https://www.syncfusion.com/succinctly-free-ebooks/nodejs serve um *Node.js
  Succinctly* **de outro autor** (Emanuele DelBono, out./2016, 76 p.), e a edição de
  Kurniawan não foi localizada em distribuição autorizada.
- **Citada por** — `rec:web/node-succinctly-kurniawan` — declara
  `obra: kurniawan-node-succinctly`
- **Nota** — ver [§ Divergências](#divergências): o recurso aponta para a ficha do
  Goodreads, que é catálogo e não o material. O próprio título do recurso já avisa que
  o código é da era Node 0.10, anterior a promessas, `async`/`await` e ESM.

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

## Filosofia

As cinco fichas de Hari Chetan abaixo são o que o catálogo cita do autor, e **não são
uma série de cinco**: o [site dele](https://harichetan.com/books/) numera quatro livros
como *The Bhagavad Gita Series* e lista *Daily Bhakti Practices* sem número, nem na
página de livros nem na do próprio título — a numeração "livro 5" que estava aqui e nos
comentários do YAML não vem do autor, e foi corrigida em 2026-11-02. A
[página de autor no Goodreads](https://www.goodreads.com/author/show/21384705.Hari_Chetan),
conferida nessa data, lista **seis** obras distintas: os quatro da série, uma entrada
duplicada do livro 3 e *God's Guide to Enlightenment: Unlock Your Consciousness, Meet
Your Real Self, and Discover Your True Purpose in Life* (Kindle, 05/04/2021), que não é
da série, não aparece no site do autor e não é citada por recurso nenhum — por isso não
tem ficha aqui. *Daily Bhakti Practices*, por sua vez, não está no Goodreads.

Preço e paginação das cinco vêm da página do Google Play BR em 2026-11-01, que é também
de onde saiu o `custo` dos recursos.

### 30 Days to Understanding the Bhagavad Gita: A Complete, Simple, and Step-by-Step Guide to the Million-Year-Old Confidential Knowledge

- **Autoria** — Hari Chetan
- **Edição** — edição do autor (independente), jun./2021, en-US. Livro 3 da série
  *The Bhagavad Gita Series*. E-book de 245 p., R$ 24,99 no Google Play; há também
  brochura e capa dura.
- **Identificadores** — ASIN `B09827G9M6` (Kindle), `B0986FRJ5R` (brochura),
  `B09GJML48Z` (capa dura); EAN `9791220819619` no Nook
- **Amazon** — https://www.amazon.com.br/dp/B09827G9M6 (ASIN obtido resolvendo o link
  do autor, que termina na loja brasileira; a página em si não foi conferida)
- **Citada por** — `rec:filosofia/chetan-30-dias-gita` — declara
  `obra: chetan-30-dias-gita`
- **Nota** — expõe a doutrina em trinta passos; é exposição do autor, não o diálogo, e
  por isso cita `etapa:filosofia/por-que-ler-a-gita`. Os "30 dias" são calendário e
  não esforço: a `duracao_min` do recurso vem do ritmo medido no livro 1 (~1,9
  min/p.), não do título.

### Bhagavad Gita (in English): The Authentic English Translation for Accurate and Unbiased Understanding

- **Autoria** — Hari Chetan
- **Edição** — edição do autor (independente), ago./2021, en-US. Livro 2 da série
  *The Bhagavad Gita Series*. E-book de 234 p., R$ 24,99 no Google Play; há também
  brochura e capa dura. Os 701 versos com esclarecimentos entre parênteses, notas e o
  contexto do Mahabharata.
- **Identificadores** — ASIN `B09D3YWKG7` (Kindle), `B09CRT941H` (brochura),
  `B09GJP4X6R` (capa dura); EAN `9791221311549` no Nook
- **Amazon** — https://www.amazon.com.br/dp/B09D3YWKG7 (ASIN obtido resolvendo o link
  do autor, que termina na loja brasileira; a página em si não foi conferida)
- **Citada por** — `rec:filosofia/chetan-gita-traducao-autentica` — declara
  `obra: chetan-gita-traducao-autentica`
- **Nota** — é a Gita, não comentário sobre ela, e por isso é o único livro de Hari
  Chetan que cita `etapa:filosofia/leitura-integral-da-gita`. Alternativa em prosa à
  tradução em verso de Arnold, que é gratuita: os R$ 24,99 são o preço de ler a letra
  em vez do tom.

### Bhagavad Gita - The Perfect Philosophy: 15 Reasons That Make the Song of God the Most Scientific Ideology

- **Autoria** — Hari Chetan (assinado "Chetan Hari" em algumas lojas)
- **Edição** — edição do autor (independente), 26/06/2021, en-US. Livro 1 da série
  *The Bhagavad Gita Series*. E-book de 97 p. no Google Play (95 no Goodreads); o
  impresso tem cerca de 100 p.
- **Identificadores** — ASIN `B09827WZX5` (Kindle); ISBN-13 `9798528163611`
  (brochura), `9798480260151` (capa dura); EAN `9791220819497` no Nook
- **Amazon** — https://www.amazon.com.br/dp/B09827WZX5 (ASIN confirmado no
  StoryGraph e no link do autor; página da loja brasileira não conferida)
- **Acesso aberto** — e-book gratuito por decisão do autor em todas as lojas,
  conferido em 2026-10-26 na [página do livro](https://harichetan.com/books/bhagavad-gita-perfect-philosophy/)
  e no Google Play
- **Citada por** — `rec:filosofia/chetan-gita-perfect-philosophy` — declara
  `obra: chetan-gita-perfect-philosophy`
- **Nota** — não há sumário público, então as quinze razões não estão nomeadas aqui
  e o livro entra inteiro numa etapa. É livro de convencimento, e a trilha o
  confronta com a entrada da *Internet Encyclopedia of Philosophy*.

### Daily Bhakti Practices: A Practical Guide to Living with Devotion and Purpose

- **Autoria** — Hari Chetan
- **Edição** — edição do autor (independente), dez./2024, en-US. Fora da série
  numerada — o site do autor o lista sem número — e o único livro dele que não trata
  da Gita. E-book de 87 p., R$ 25,99 no Google Play; a brochura da Lulu tem 100 p.,
  de 19/12/2024. Há audiolivro de 2h12 em voz digital, que não é
  `formato` do esquema — o recurso entra como texto.
- **Identificadores** — ISBN-13 do e-book 979-12-23904-02-2. Sem ASIN: não há edição
  na Amazon.
- **Amazon** — não se aplica. O autor lista Google Play, Streetlib, Nook e Kobo para
  o digital e a Lulu para o impresso:
  https://harichetan.com/books/daily-bhakti-practices/
- **Citada por** — `rec:filosofia/chetan-daily-bhakti` — declara
  `obra: chetan-daily-bhakti`
- **Nota** — é o único dos cinco que não está na Amazon (nem no Goodreads), e por
  isso o único cujo `custo` não tem preço de Kindle com que ser conferido. A etapa que o recebe,
  `etapa:filosofia/bhakti-na-pratica`, nasceu com ele e é opcional.

### Gozai por nós: Estudos sobre a subjetividade artificial

- **Autoria** — Alfredo Simonetti (organizador e autor principal), psiquiatra e
  psicanalista. **Obra coletiva**: o texto de orelha cita, além de psicanalistas e
  psicólogos clínicos, médicos, uma estudante universitária, um historiador, um
  jornalista e um linguista, e mais uma colaboração literária. **A amostra não atribui
  autoria capítulo a capítulo**, e nenhum nome além do de Simonetti foi conferido.
- **Edição** — 1ª ed., publicada em 20/12/2023, pt-BR. Capa comum de 348 p.; e-book
  Kindle de 412 p. (ASIN `B0CQRJ84FY`, 7,3 MB).
- **Identificadores** — ISBN-13 `9788571721159`, ISBN-10 `8571721157` (o mesmo ISBN-13
  consta na ficha do Kindle)
- **Editora** — **não resolvida**, e a divergência fica registrada em vez de arbitrada:
  a capa impressa na amostra diz *ALPENDRE Books*; o isbnsearch.org atribui o ISBN à
  *Editora Amoler*; `editoraamoler.com.br` não resolve DNS (14/11/2026) e a página da
  Amazon não traz campo de editora nem na capa comum nem no Kindle. Nenhum campo do
  catálogo depende disto.
- **Amazon** — https://www.amazon.com.br/dp/B0CQRJ84FY (Kindle, R$ 9,99 em 14/11/2026,
  incluído no Kindle Unlimited) e https://www.amazon.com.br/dp/8571721157 (capa comum,
  R$ 94,90, ou R$ 90,15 à vista no Pix, na mesma data). O `custo` e a `url` das cinco
  fatias são os do Kindle.
- **Título** — a capa diz *Estudos* no plural; a Amazon anuncia *Estudo* no singular,
  nos dois formatos. Esta ficha segue a capa; os recursos citam só o título principal.
- **Sumário** — 19 capítulos, 3 apêndices e um posfácio, conferidos um a um na amostra
  Kindle em 14/11/2026: 1 A Subjetividade artificial; 2 A estranha familiar; 3 A
  condição pós-humana; 4 A inteligência artificial e mais além; 5 A Subjetividade na
  filosofia; 6 Que outro é esse?; 7 Nós achamos que você vai gostar disso; 8 O
  Mal-estar Tecnológico: e o Eu com isso?; 9 O novo amor: as tecnologias do encontro;
  10 A felicidade é mais que uma vontade; 11 Quantas vezes você já traiu amanhã?; 12
  Perdão Isabela; 13 Cinema artificial; 14 Sala de aula artificial; 15 A qualidade da
  lágrima; 16 (Não) sois máquina; 17 Não me toque, doutor!; 18 Tempo é dinheiro; 19 Os
  algoritmos do fim; Apêndice 1 ISABELA ANTES DA TECNOLOGIA; Apêndice 2 LEIA POR NÓS:;
  Apêndice 3 UM COMENTÁRIO; POSFÁCIO. **A paginação por capítulo não está no sumário da
  amostra** e não foi conferida em lugar nenhum.
- **Citada por** — `rec:filosofia/simonetti-gozai-caps-1-3`,
  `rec:filosofia/simonetti-gozai-caps-4-6`, `rec:filosofia/simonetti-gozai-caps-7-12`,
  `rec:filosofia/simonetti-gozai-caps-13-19` e
  `rec:filosofia/simonetti-gozai-apendices-e-posfacio` — as cinco declaram
  `obra: simonetti-gozai-por-nos`
- **Nota** — o livro se autoclassifica "ciência poética", expressão do próprio
  organizador citada na orelha. O título é trocadilho com a ladainha "rogai por nós", e
  o Apêndice 2 ("LEIA POR NÓS:") o devolve ao leitor — mas **que leitura psicanalítica
  o livro faz do gozo não foi conferida**: nada além do sumário e da orelha foi lido.

### The Bhagavad Gita Summarized and Simplified: A Comprehensive and Easy-to-Read Summary of the Divine Song of God

- **Autoria** — Hari Chetan
- **Edição** — edição do autor (independente), set./2021, en-US. Livro 4 da série
  *The Bhagavad Gita Series*. E-book de 149 p., R$ 19,99 no Google Play; há também
  brochura e capa dura. Segue os dezoito capítulos, cada um com "Key Takeaways", e
  fecha com os ensinamentos agrupados por tema.
- **Identificadores** — ASIN `B09G168NZ9` (Kindle), `B09FS31N65` (brochura),
  `B09GJJCVY1` (capa dura); ISBN-13 979-8480077049 na capa dura
- **Amazon** — https://www.amazon.com.br/dp/B09G168NZ9 (ASIN obtido resolvendo o link
  do autor, que termina na loja brasileira; a página em si não foi conferida)
- **Citada por** — `rec:filosofia/chetan-gita-resumida` — declara
  `obra: chetan-gita-resumida`
- **Nota** — cita `etapa:filosofia/por-que-ler-a-gita` e não a da leitura integral,
  porque resumo é exatamente o que a `comp:filosofia/argumento-da-gita` exclui ("a
  leitura do texto inteiro, não do resumo"). Antes do diálogo ele serve como visão de
  conjunto.

### The Song Celestial, or Bhagavad-Gîtâ

- **Autoria** — tradução de Sir Edwin Arnold
- **Edição** — Trübner, 1885, em verso, en-US. Domínio público.
- **Acesso aberto** — https://www.gutenberg.org/ebooks/2388
- **Citada por** — `rec:filosofia/arnold-song-celestial`

### Pós-humano, transumano e ciborgue — as fichas de 2026-11-15

As sete fichas abaixo são da trilha `trilha:filosofia/pos-humano-transumano-e-ciborgue`,
que nasce das notas 37 a 45 de uma página fotografada pelo estudante — muito
provavelmente do cap. 3 de *Gozai por nós*, inferência não conferida. **Nenhuma cita
preço conferido**: Amazon, Wiley e Estante Virtual recusaram a leitura automática, e o
`custo` dos recursos é ordem de grandeza, dito como tal em
`catalogo/recursos/filosofia.yaml`. Os ISBNs abaixo marcados "não conferido" vêm da
referência ou de memória, não de página lida. O artigo de Clynes e Kline (notas 42 e
43, a mesma referência repetida) não é livro e não tem ficha; a divergência de
paginação dele está no comentário do recurso.

#### Antropologia do ciborgue: as vertigens do pós-humano

- **Autoria** — Donna Haraway, Hari Kunzru e Tomaz Tadeu (org. e tradução)
- **Edição** — Autêntica (Belo Horizonte), 2ª ed., 2009, pt-BR; 128 p. segundo o
  Skoob, que lista também uma entrada de 2025 com 120 p. e o mesmo ISBN, não resolvida
- **Identificadores** — ISBN-13 `9788575263952` (Skoob); ISBN-10 `8575263951`, calculado
- **Amazon** — https://www.amazon.com.br/dp/8575263951 (não aberto)
- **Citada por** — `rec:filosofia/haraway-manifesto-ciborgue` (o "Manifesto ciborgue",
  pp. 33-118, paginação da referência do estudante, não conferida)

#### The Cyborg Handbook

- **Autoria** — Chris Hables Gray (org.), com Steven Mentor e Heidi J. Figueroa-Sarriera
  (não conferidos)
- **Edição** — Routledge (New York), 1ª ed., 1995, 568 p., en-US — conferido na página
  da editora, que trazia, porém, o sumário de outro livro
- **Identificadores** — ISBN-13 `9780415908498` (editora); ISBN-10 `0415908493`
- **Editora** — https://www.routledge.com/The-Cyborg-Handbook/Gray/p/book/9780415908498
- **Citada por** — `rec:filosofia/hess-low-tech-cyborgs` (David Hess, "On Low-tech
  Cyborgs", pp. 371-378)

#### The Transhumanist Reader: Classical and Contemporary Essays on the Science, Technology, and Philosophy of the Human Future

- **Autoria** — Max More e Natasha Vita-More (orgs.)
- **Edição** — Wiley-Blackwell (Oxford), 2013, en-US
- **Identificadores** — ISBN-13 `9781118334317`, ISBN-10 `1118334310` (brochura; não
  conferido)
- **Amazon** — https://www.amazon.com.br/dp/1118334310 (não aberto)
- **Citada por** — `rec:filosofia/more-vita-more-transhumanist-reader`

#### The Age of Spiritual Machines: When Computers Exceed Human Intelligence

- **Autoria** — Ray Kurzweil
- **Edição** — Viking, 1999; brochura Penguin; en-US. A referência do estudante dá
  "New York, NY: Penguin, 1999"
- **Identificadores** — ISBN-10 `0140282025` (brochura Penguin; não conferido)
- **Amazon** — https://www.amazon.com.br/dp/0140282025 (não aberto)
- **Citada por** — `rec:filosofia/kurzweil-age-of-spiritual-machines`

#### The Singularity Is Near: When Humans Transcend Biology

- **Autoria** — Ray Kurzweil
- **Edição** — Viking (New York), 2005; brochura Penguin; en-US
- **Identificadores** — ISBN-10 `0143037889` (brochura Penguin; não conferido)
- **Amazon** — https://www.amazon.com.br/dp/0143037889 (não aberto)
- **Citada por** — `rec:filosofia/kurzweil-singularity-is-near`

#### How We Became Posthuman: Virtual Bodies in Cybernetics, Literature, and Informatics

- **Autoria** — N. Katherine Hayles
- **Edição** — University of Chicago Press, 1999, 364 p., en-US — conferido na página da
  editora em 2026-11-15
- **Identificadores** — a editora lista `9780226321462` e `9780226321394` sem dizer qual
  é a brochura
- **Editora** — https://press.uchicago.edu/ucp/books/book/chicago/H/bo3769963.html
- **Sumário** — Prólogo; 1 Toward Embodied Virtuality; 2 Virtual Bodies and Flickering
  Signifiers; 3 Contesting for the Body of Information: The Macy Conferences on
  Cybernetics; 4 Liberal Subjectivity Imperiled: Norbert Wiener and Cybernetic Anxiety;
  5 From Hyphen to Splice; 6 The Second Wave of Cybernetics; 7 (Philip K. Dick); 8 The
  Materiality of Informatics; 9 Narratives of Artificial Life; 10 The Semiotics of
  Virtuality: Mapping the Posthuman; 11 Conclusion: What Does It Mean to Be Posthuman?
- **Citada por** — `rec:filosofia/hayles-how-we-became-posthuman`

#### The Posthuman

- **Autoria** — Rosi Braidotti
- **Edição** — Polity Press (Cambridge, UK; Malden, MA), 2013, en-US
- **Identificadores** — ISBN-13 `9780745641584`, ISBN-10 `074564158X` (brochura, dígito
  verificador calculado; ISBNs não conferidos em página)
- **Amazon** — https://www.amazon.com.br/dp/074564158X (não aberto)
- **Citada por** — `rec:filosofia/braidotti-the-posthuman`

## IHC

As cinco fichas da trilha `trilha:ihc/captologia`, conferidas em 2026-11-14. Como nas
fichas de 2026-10-17, **elas citam preço**, porque o `custo` dos recursos foi fixado
na mesma passada — e em dois casos o `custo` é estimativa, dita como tal. Amazon e
lojas brasileiras recusam o `curl` deste ambiente: nenhuma página de produto da
Amazon foi conferida, e os links abaixo são de busca pelo ISBN.

### Persuasive Technology: Using Computers to Change What We Think and Do

- **Autoria** — B.J. Fogg
- **Edição** — Morgan Kaufmann (série *Interactive Technologies*), jan./2003, 312 p.,
  en-US. Nenhuma tradução brasileira encontrada.
- **Identificadores** — ISBN-13 `9781558606432`
- **Amazon** — https://www.amazon.com.br/s?k=9781558606432 (link de busca)
- **Sumário** — https://www.oreilly.com/library/view/persuasive-technology/9781558606432/:
  introdução; 1 Overview of Captology; 2 The Functional Triad; 3 Computers as
  Persuasive Tools; 4 … as Persuasive Media: Simulation; 5 … as Persuasive Social
  Actors; 6 Credibility and Computers; 7 Credibility and the World Wide Web;
  8 Increasing Persuasion through Mobility and Connectivity; 9 The Ethics of
  Persuasive Technology; 10 Captology: Looking Forward; apêndice com o resumo dos
  princípios.
- **Citada por** — `rec:ihc/fogg-persuasive-technology-caps-1-5`,
  `rec:ihc/fogg-persuasive-technology-caps-6-10` — declaram
  `obra: fogg-persuasive-technology`
- **Nota** — **o `custo` de R$ 300 é estimativa** do impresso importado: nenhuma página
  lida mostrou preço. O fatiamento é por número de capítulo, pelo sumário acima.

### Micro-hábitos: pequenas mudanças que mudam tudo

- **Autoria** — B.J. Fogg; trad. Bruno Fiuza e Roberta Clapp. Original: *Tiny Habits:
  The Small Changes That Change Everything* (2019).
- **Edição** — 1ª ed., HarperCollins Brasil, 2020, 336 p., brochura, pt-BR
- **Identificadores** — ISBN-13 `9788595086883`
- **Amazon** — https://www.amazon.com.br/s?k=9788595086883 (link de busca). R$ 38,43 à
  vista (de R$ 54,90) na [Martins Fontes Paulista](https://www.martinsfontespaulista.com.br/micro-habitos-905206/p),
  cuja página diz ao mesmo tempo "esgotado" e "sob encomenda"; editora, ano, páginas e
  ISBN conferem no [Skoob](https://www.skoob.com.br/book/1135342).
- **Citada por** — `rec:ihc/fogg-micro-habitos` — declara `obra: fogg-micro-habitos`

### Hooked (Engajado): como construir produtos e serviços formadores de hábitos

- **Autoria** — Nir Eyal (com Ryan Hoover no original); tradutor não informado pela
  loja. Original: *Hooked: How to Build Habit-Forming Products* (Portfolio/Penguin,
  2014).
- **Edição** — 1ª ed., 2020, 218 p., brochura, pt-BR. A
  [Martins Fontes Paulista](https://www.martinsfontespaulista.com.br/hooked--engajado--900793/p)
  cadastra a editora como "AlfaCon Concursos Públicos" — o prefixo do ISBN é coerente
  com isso, mas não se conferiu em outra fonte.
- **Identificadores** — ISBN-13 `9788583394761`
- **Amazon** — https://www.amazon.com.br/s?k=9788583394761 (link de busca). R$ 88,81 à
  vista na Martins Fontes Paulista, com a disponibilidade contraditória na página.
- **Citada por** — `rec:ihc/eyal-hooked-engajado` — declara `obra: eyal-hooked-engajado`

### Irresistível: por que você é viciado em tecnologia e como lidar com ela

- **Autoria** — Adam Alter; trad. Cássio de Arantes Leite. Original: *Irresistible:
  The Rise of Addictive Technology and the Business of Keeping Us Hooked* (Penguin
  Press, 2017).
- **Edição** — Objetiva (Companhia das Letras), lançada em 16/04/2018, 296 p.,
  brochura, pt-BR
- **Identificadores** — ISBN-13 `9788547000585`
- **Editora** — https://www.companhiadasletras.com.br/livro/9788547000585/irresistivel,
  R$ 92,90, sem dizer se é preço de capa — é a `url` do recurso.
- **Citada por** — `rec:ihc/alter-irresistivel` — declara `obra: alter-irresistivel`

### Algoritmos de destruição em massa: como o big data aumenta a desigualdade e ameaça a democracia

- **Autoria** — Cathy O'Neil; tradutor não encontrado. Original: *Weapons of Math
  Destruction* (Crown, 2016).
- **Edição** — 1ª ed., Rua do Sabão, Santo André (SP), 2020, 341 p., pt-BR, pela
  referência da [resenha na ReCiC/UESB](https://periodicos2.uesb.br/index.php/recic/article/download/10883/6817/29565).
  Doze capítulos com introdução e conclusão, segundo a mesma resenha.
- **Identificadores** — ISBN-13 `9786586460025` (pela resenha; não conferido em
  catálogo de loja)
- **Amazon** — https://www.amazon.com.br/s?k=9786586460025 (link de busca)
- **Citada por** — `rec:ihc/oneil-algoritmos-de-destruicao-em-massa` — declara
  `obra: oneil-algoritmos-de-destruicao-em-massa`
- **Nota** — **o `custo` de R$ 70 é estimativa**: nenhuma página lida mostrou preço.
  Duas referências acadêmicas divergem — a da UESB dá Santo André e doze capítulos, a
  de *Estudos de Sociologia* (UNESP, 2022) dá São Paulo e dez —, e um post de leitor
  traz um ISBN-10 brasileiro (`6586460166`) que não corresponde ao ISBN-13 acima. Vale
  o exemplar, quando houver um em mãos.

As nove fichas da trilha `trilha:ihc/computacao-afetiva`, conferidas em 2026-11-14 e
acrescentadas na mesma data. **Elas citam preço, e nenhum é estimativa**: cada um saiu
de uma página de produto lida no navegador embutido, que é também a `url` do recurso.
A Amazon BR recusa o `curl` deste ambiente mas responde ao navegador — foi assim que
os cinco importados saíram —, e as duas editoras brasileiras consultadas publicam a
ficha sem o preço, que veio então de livraria.

### Affective Computing

- **Autoria** — Rosalind W. Picard
- **Edição** — MIT Press; brochura de 24/07/2000 do original de 1997, 306 p., en-US.
  Nenhuma tradução brasileira encontrada. Dois catálogos de livraria dão 304 p. e um
  registro de biblioteca dá 292 p. de texto mais o material inicial; 306 é o número
  mais repetido.
- **Identificadores** — ISBN-13 `9780262661157` · ISBN-10 `0262661158`
- **Amazon** — https://www.amazon.com.br/s?k=9780262661157 (link de busca; a página de
  produto por ISBN-10 devolve 404). R$ 473,48 em capa comum, com "6 ofertas de
  produtos novos e usados" a partir de R$ 259,99 ao lado.
- **Citada por** — `rec:ihc/picard-affective-computing` — declara
  `obra: picard-affective-computing`

### The Oxford Handbook of Affective Computing

- **Autoria** — Rafael A. Calvo, Sidney K. D'Mello, Jonathan Gratch e Arvid Kappas
  (orgs.), série *Oxford Library of Psychology*
- **Edição** — Oxford University Press, 2015 (uma livraria dá 15/01/2015), capa dura,
  624 p., en-US. O catálogo da Texas A&M registra xvii + 603 p., diferença que deve
  ser do material inicial, não conferida.
- **Identificadores** — ISBN-13 `9780199942237` · ISBN-10 `0199942234`
- **Amazon** — https://www.amazon.com.br/s?k=9780199942237 (link de busca). R$ 1.513,82
  em capa dura, e a mesma página anuncia R$ 1.593,50 "à vista no Pix" — **mais alto**
  que o preço normal. A contradição está registrada como lida.
- **Sumário** — 41 capítulos em cinco seções, pela descrição da editora: história e
  teoria, detecção, geração, metodologias e aplicações; o cap. 1 é introdução dos
  quatro organizadores e a seção um traz um capítulo de Rosalind Picard. ⚠️ **Os
  números de capítulo de cada seção não foram conferidos em nenhuma página lida**, e é
  por isso que as duas fatias do catálogo são nomeadas por seção, não por intervalo de
  capítulos.
- **Citada por** — `rec:ihc/oxford-handbook-affective-computing-deteccao`,
  `rec:ihc/oxford-handbook-affective-computing-geracao` — declaram
  `obra: oxford-handbook-affective-computing`
- **Nota** — é a obra mais cara do catálogo, e sozinha custa mais que as cinco da
  captologia somadas.

### Emotion Recognition: A Pattern Analysis Approach

- **Autoria** — Amit Konar e Aruna Chakraborty (orgs.); capítulos com outros
  contribuintes, entre eles Anisha Halder e Atulya K. Nagar
- **Edição** — John Wiley & Sons, Hoboken, 2015, capa dura, 584 p., en-US. Um registro
  de biblioteca dá xxxi + 548 p. e um recurso eletrônico dá 583 p.; as datas de
  lançamento divergem entre 27/01 e 20/03/2015.
- **Identificadores** — ISBN-13 `9781118130667` · ISBN-10 `1118130669`. Edições
  eletrônicas em `9781118910603` e `9781118910610`; DOI `10.1002/9781118910566`.
- **Amazon** — https://www.amazon.com.br/s?k=9781118130667 (link de busca). R$ 814,37
  em capa dura, com entrega prevista entre 30/12/2026 e 13/01/2027, e "5 ofertas de
  produtos novos e usados" a partir de R$ 762,00.
- **Citada por** — `rec:ihc/konar-chakraborty-emotion-recognition` — declara
  `obra: konar-chakraborty-emotion-recognition`

### O erro de Descartes: emoção, razão e o cérebro humano

- **Autoria** — António R. Damásio; trad. Dora Vicente e Georgina Segurado. Original:
  *Descartes' Error: Emotion, Reason and the Human Brain* (Putnam, 1994).
- **Edição** — Companhia das Letras, selo Edição Econômica, lançada em 19/11/2012,
  264 p., brochura, 23x16 cm, pt-BR. A ficha da editora dá 264 p.; o Skoob dá 360 p.
  para o mesmo ISBN-13, e a primeira edição brasileira (1996, ISBN-10 `8571645302`)
  tinha 336 p.
- **Identificadores** — ISBN-13 `9788535922004`
- **Amazon** — não conferida. Preço de R$ 67,90 à vista na
  [Martins Fontes Paulista](https://www.martinsfontespaulista.com.br/o-erro-de-descartes-695903/p),
  que é a `url` do recurso; a
  [página da Companhia das Letras](https://www.companhiadasletras.com.br/9788535922004-o-erro-de-descartes-595/p)
  traz a ficha técnica completa e **nenhum preço**.
- **Citada por** — `rec:ihc/damasio-o-erro-de-descartes` — declara
  `obra: damasio-o-erro-de-descartes`

### The Emotion Machine: Commonsense Thinking, Artificial Intelligence, and the Future of the Human Mind

- **Autoria** — Marvin Minsky
- **Edição** — Simon & Schuster; brochura de 13/11/2007 do original em capa dura de
  07/11/2006, 400 p., en-US. Um registro de biblioteca dá 387 p. Nenhuma tradução
  brasileira encontrada.
- **Identificadores** — ISBN-13 `9780743276641` · ISBN-10 `0743276647`
- **Amazon** — https://www.amazon.com.br/s?k=9780743276641 (link de busca). R$ 110,96,
  de R$ 211,88.
- **Citada por** — `rec:ihc/minsky-the-emotion-machine` — declara
  `obra: minsky-the-emotion-machine`

### The Man Who Lied to His Laptop: What We Can Learn About Ourselves from Our Machines

- **Autoria** — Clifford Nass e Corina Yen
- **Edição** — Current/Penguin; brochura de 24/04/2013 do original em capa dura de 2010
  (*What Machines Teach Us about Human Relationships*, ISBN-13 `9781617230011`), 256 p.,
  en-US. As contagens divergem muito entre edições: 256 p. na brochura e no e-book,
  208 p. pela *Publishers Weekly* e vii + 230 p. num catálogo de biblioteca para a capa
  dura de 2010. Nenhuma tradução brasileira encontrada.
- **Identificadores** — ISBN-13 `9781617230042`
- **Amazon** — https://www.amazon.com.br/s?k=9781617230042 (link de busca). R$ 100,67,
  com o aviso "Somente 1 em estoque".
- **Citada por** — `rec:ihc/nass-yen-the-man-who-lied-to-his-laptop` — declara
  `obra: nass-yen-the-man-who-lied-to-his-laptop`
- **Nota** — o estoque de um exemplar é o motivo de esta ficha ser a primeira a
  reconferir quando a validação 10 cobrar os 180 dias.

### Emotional Design: Why We Love (or Hate) Everyday Things

- **Autoria** — Donald A. Norman
- **Edição** — Basic Books, brochura, 272 p., en-US. A capa dura original tem ISBN-10
  `0465051359`.
- **Identificadores** — ISBN-13 `9780465051366` · ISBN-10 `0465051367`
- **Amazon** — https://www.amazon.com.br/s?k=9780465051366 (link de busca). R$ 103,79,
  com "Economize R$ 15,00 nas compras de 2 ou mais".
- **Citada por** — `rec:ihc/norman-emotional-design` — declara
  `obra: norman-emotional-design`
- **Nota** — ⚠️ **a tradução brasileira existe e está fora de catálogo.** *Design
  Emocional: por que adoramos (ou detestamos) os objetos do dia-a-dia*, Rocco, 2008,
  278 p., ISBN-13 `9788532523327` pelo [Skoob](https://www.skoob.com.br/book/35397) —
  fonte única, catálogo colaborativo, não confirmada na editora. A busca da Martins
  Fontes Paulista por "design emocional" devolve **um** produto, de outro autor. O
  recurso entra em inglês porque é o exemplar que se compra hoje; se a Rocco reeditar,
  o movimento é recurso novo com a mesma `obra`, não troca de `url`.

### Como as emoções são feitas: a vida secreta do cérebro

- **Autoria** — Lisa Feldman Barrett; trad. Cássio de Arantes Leite. Original:
  *How Emotions Are Made: The Secret Life of the Brain* (2017).
- **Edição** — Objetiva (Grupo Companhia das Letras), lançada em 28/07/2026, 472 p.,
  brochura, 23x16 cm, 695 g, pt-BR
- **Identificadores** — ISBN-13 `9788539009619`. O Google Books traz outro par
  (`8539010100` / `9788539010103`) para o mesmo título, não conferido.
- **Amazon** — não conferida. R$ 99,90 na
  [busca da Martins Fontes Paulista](https://www.martinsfontespaulista.com.br/como%20as%20emocoes%20sao%20feitas?_q=como%20as%20emocoes%20sao%20feitas&map=ft),
  que é a `url` do recurso, sem marca de "Sob Encomenda".
- **Citada por** — `rec:ihc/barrett-como-as-emocoes-sao-feitas` — declara
  `obra: barrett-como-as-emocoes-sao-feitas`
- **Nota** — ⚠️ **armadilha de leitura de página, registrada para não se repetir.** A
  [página da Companhia das Letras](https://www.companhiadasletras.com.br/9788539009619-como-as-emocoes-sao-feitas-4213/p)
  traz a ficha técnica completa e **não traz o preço deste livro**; logo abaixo dela,
  a vitrine "Você também pode gostar" exibe R$ 99,90 ao lado de *Felicidade autêntica*,
  de Seligman. O preço deste recurso coincide por acidente, e veio da livraria, não
  dessa vitrine.

### Atlas da IA: poder, política e os custos planetários da inteligência artificial

- **Autoria** — Kate Crawford; trad. Humberto do Amaral. Original: *Atlas of AI:
  Power, Politics, and the Planetary Costs of Artificial Intelligence* (Yale
  University Press, 2021, 336 p., ISBN-13 `9780300209570`).
- **Edição** — 1ª ed., Edições Sesc São Paulo, lançada em 16/07/2025, 380 p., brochura,
  pt-BR. Duas livrarias dão 138 p., número que não se sustenta.
- **Identificadores** — ISBN-13 `9788594933287`
- **Amazon** — não conferida. R$ 98,00 na
  [Travessa](https://www.travessa.com.br/atlas-da-ia-poder-politica-e-os-custos-planetarios-da-inteligencia-artificial/artigo/48fa31a0-b199-4b13-854e-47555d594d1f),
  com "Adicionar à sacola" — é a `url` do recurso.
- **Citada por** — `rec:ihc/crawford-atlas-da-ia` — declara `obra: crawford-atlas-da-ia`
- **Nota** — ⚠️ **preço mais baixo de exemplar que não se compra.** A
  [Livraria Loyola](https://www.livrarialoyola.com.br/produto/atlas-da-ia-poder-politica-e-os-custos-planetarios-da-inteligencia-artificial-418663)
  anuncia R$ 78,40 (20% sobre R$ 98,00, mesmo valor no Pix) e na mesma página diz
  **"Produto esgotado"**, com formulário de aviso de reposição. O `custo` do recurso é
  o da Travessa. Não há edição brasileira da Ubu nem de outra editora que não a Sesc;
  há uma portuguesa da Relógio D'Água (2024, 304 p., ISBN-13 `9789897834356`), que não
  é esta.


As cinco fichas da trilha `trilha:ihc/reconhecimento-de-emocao-na-voz`, conferidas em
2026-11-14 e acrescentadas na mesma data. **Nenhum preço é estimativa**: os cinco são
importados e saíram da Amazon BR lida no navegador embutido, que é a `url` de cada
recurso. Duas fichas registram inversão de preço ou coincidência que enganaria quem
lesse rápido — estão nas notas.

Os **dois recursos gratuitos** daquela trilha não têm ficha aqui, de propósito, pela
regra que deixou `beej-guide-c` fora: o capítulo aberto do livro de PLN brasileiro e o
repositório do CORAA SER não são exemplares — sem editora, sem ISBN, sem edição à
venda — e estão no [§ O que não tem ficha](#o-que-não-tem-ficha).

### Computational Paralinguistics: Emotion, Affect and Personality in Speech and Language Processing

- **Autoria** — Björn Schuller e Anton Batliner
- **Edição** — 1ª ed., Wiley, Hoboken; anúncio da editora em nov./2013 e imprenta de
  biblioteca 2014 — é a mesma edição —, 344 p., capa dura, en-US. Registros de
  recurso eletrônico dão 345 p.
- **Identificadores** — ISBN-13 `9781119971368` · ISBN-10 `1119971365`. Eletrônicos:
  `9781118706633` (PDF), `9781118706626` (ePub); DOI `10.1002/9781118706664`.
- **Amazon** — https://www.amazon.com.br/s?k=9781119971368 (link de busca).
  R$ 785,83 em capa dura, entrega grátis prevista para 14–16/12.
- **Citada por** — `rec:ihc/schuller-batliner-computational-paralinguistics` — declara
  `obra: schuller-batliner-computational-paralinguistics`
- **Nota** — é a obra de referência do canal vocal, e a razão é de autoridade
  verificável, não de resenha: Schuller organizou os *Emotion Challenges* do
  INTERSPEECH e assina o openSMILE, o extrator de atributos que a literatura da área
  usa como padrão.

### Emotion Recognition using Speech Features

- **Autoria** — K. Sreenivasa Rao e Shashidhar G. Koolagudi
- **Edição** — SpringerBriefs in Speech Technology, 07/11/2012, XII+124 p., brochura,
  en-US. Alguns catálogos datam 2013.
- **Identificadores** — ISBN-13 `9781461451426` (impresso) · `9781461451433`
  (eletrônico); DOI `10.1007/978-1-4614-5143-3`
- **Amazon** — https://www.amazon.com.br/s?k=9781461451426 (link de busca). R$ 320,80
  em capa comum.
- **Sumário** — capítulos de reconhecimento por informação da fonte de excitação, por
  informação do tracto vocal e por informação prosódica, pelas descrições de catálogo
  consultadas.
- **Citada por** — `rec:ihc/rao-koolagudi-emotion-recognition-speech-features` —
  declara `obra: rao-koolagudi-emotion-recognition-speech-features`

### Robust Emotion Recognition using Spectral and Prosodic Features

- **Autoria** — K. Sreenivasa Rao e Shashidhar G. Koolagudi
- **Edição** — SpringerBriefs in Speech Technology, jan./2013, 118 p., brochura, en-US
- **Identificadores** — ISBN-13 `9781461463597` (brochura) · `9781461463603`
  (eletrônico); DOI `10.1007/978-1-4614-6360-3`
- **Amazon** — https://www.amazon.com.br/s?k=9781461463597 (link de busca). R$ 320,80
  em capa comum.
- **Citada por** — `rec:ihc/rao-koolagudi-robust-emotion-recognition` — declara
  `obra: rao-koolagudi-robust-emotion-recognition`
- **Nota** — ⚠️ **R$ 320,80 é exatamente o preço da ficha anterior, e é coincidência
  de loja, não erro de digitação.** São dois exemplares distintos, dos mesmos autores
  e na mesma série, com ISBN, paginação e slug de `obra` próprios. A validação 12
  cobra preço único **dentro** de uma obra e não tem nada a dizer entre obras — quem
  encontrar os dois números iguais no lock não achou um defeito.

### The Oxford Handbook of Voice Perception

- **Autoria** — Sascha Frühholz e Pascal Belin (orgs.), série *Oxford Library of
  Psychology*
- **Edição** — Oxford University Press, 29/01/2019, 976 p., capa dura, en-US. O Google
  Books lista uma edição eletrônica com 939 p. e outro ISBN (`9780191841668`).
- **Identificadores** — ISBN-13 `9780198743187` · ISBN-10 `0198743181`
- **Amazon** — https://www.amazon.com.br/s?k=9780198743187 (link de busca).
  R$ 1.804,57 em capa dura.
- **Citada por** — `rec:ihc/fruhholz-belin-oxford-handbook-voice-perception` — declara
  `obra: fruhholz-belin-oxford-handbook-voice-perception`
- **Nota** — **é a obra mais cara do catálogo**, à frente do *Oxford Handbook of
  Affective Computing* (R$ 1.513,82). Uma fatia só: o sumário capítulo a capítulo não
  foi conferido em nenhuma página lida, e nomear intervalo seria inventar — o mesmo
  critério aplicado às duas fatias do handbook de computação afetiva.

### Intelligent Audio Analysis

- **Autoria** — Björn W. Schuller, série *Signals and Communication Technology*
- **Edição** — Springer, capa dura de 08/05/2013, XXVIII+345 p., en-US; brochura de
  19/05/2015.
- **Identificadores** — capa dura ISBN-13 `9783642368059` · brochura
  `9783642442773` · eletrônico `9783642368066`; DOI `10.1007/978-3-642-36806-6`
- **Amazon** — https://www.amazon.com.br/s?k=9783642368059 (link de busca).
  R$ 550,16 em capa dura.
- **Citada por** — `rec:ihc/schuller-intelligent-audio-analysis` — declara
  `obra: schuller-intelligent-audio-analysis`
- **Nota** — ⚠️ **a capa comum sai mais cara que a capa dura**: a brochura de 2015
  (`9783642442773`) está a R$ 657,83 na mesma loja, contra R$ 550,16 da capa dura. O
  recurso aponta a capa dura por ser a barata. É o mesmo tipo de inversão registrada
  na ficha do *Shell Scripting Bible*, em que o Kindle saía mais caro que o impresso:
  vale conferir os dois formatos antes de fixar `custo`, porque a suposição usual
  erra.


As oito fichas da trilha `trilha:ihc/reconhecimento-de-emocao-em-expressao-facial`,
conferidas em 2026-11-14. Diferença em relação às fichas anteriores desta seção:
**as páginas de produto foram lidas**, no navegador embutido, e não substituídas por
link de busca pelo ISBN — a Amazon BR e a Estante Virtual recusam o `curl` deste
ambiente, mas cedem ao navegador. Cada ficha diz qual formato o `custo` cita, porque
em três delas o Kindle é muito mais barato que o impresso.

### A expressão das emoções no homem e nos animais

- **Autoria** — Charles Darwin; trad. Leon de Souza Lobo Garcia, introdução de Konrad
  Lorenz. Original: *The Expression of the Emotions in Man and Animals* (1872).
- **Edição** — Companhia de Bolso (Companhia das Letras), 19/02/2009, 344 p., capa
  comum, pt-BR. A primeira edição brasileira é de 2000, na Companhia das Letras, com
  ISBN-10 `8571649758`.
- **Identificadores** — ISBN-13 `9788535913989` · ISBN-10 `853591398X`
- **Amazon** — https://www.amazon.com.br/dp/853591398X — **página de produto lida no
  navegador embutido**, não link de busca. R$ 48,00 praticado pela Amazon, R$ 74,90 de
  preço sugerido pela editora.
- **Citada por** — `rec:ihc/darwin-expressao-das-emocoes` — declara
  `obra: darwin-expressao-das-emocoes`
- **Nota** — ⚠️ **havia hoje uma oferta relâmpago a R$ 34,78**, marcada "42%
  reservado(s)", que é o tipo de preço que não se catalogar: expira. O `custo` ficou
  em R$ 48,00, o praticado estável. Sobre o conteúdo, uma ressalva que a trilha usa:
  Darwin argumenta por **continuidade evolutiva**, não por um conjunto fechado de
  categorias discretas — a leitura categórica é posterior a ele.

### Emotions Revealed

- **Autoria** — Paul Ekman
- **Edição** — 2ª edição, 20/03/2007, 290 p., capa comum, en-US. A editora não aparece
  na página da Amazon (é Owl Books / Henry Holt); a 1ª edição é de 2003.
- **Identificadores** — ISBN-13 `9780805083392` · ISBN-10 `0805083391`
- **Amazon** — https://www.amazon.com.br/dp/0805083391 — página de produto lida.
  R$ 79,77 em capa comum, outras ofertas a partir de R$ 66,00; há audiolivro a
  R$ 0,99 com assinatura.
- **Citada por** — `rec:ihc/ekman-emotions-revealed` — declara
  `obra: ekman-emotions-revealed`
- **Nota** — entra **na mesma etapa** da tradução brasileira, e não no lugar dela: a
  tradução está esgotada e só circula usada a partir de R$ 345,00, e este exemplar
  custa R$ 79,77. São duas `obra`s distintas, de modo que a validação 12 (custo único
  por obra) não é violada — ela compara preço só *dentro* de uma obra. Quem filtra por
  `custo_maximo` baixo recebe o inglês e a etapa não trava.

### A linguagem das emoções

- **Autoria** — Paul Ekman; trad. Carlos Szlak. Original: *Emotions Revealed* (2003).
- **Edição** — Lua de Papel (selo da LeYa), 01/03/2011, 288 p., capa comum, pt-BR
- **Identificadores** — ISBN-13 `9788563066428` · ISBN-10 `8563066420`
- **Amazon** — https://www.amazon.com.br/dp/8563066420 — página lida, e **não é a `url`
  do recurso**: R$ 539,00 por exemplar novo de terceiro. O recurso aponta a
  [página do livro na Estante Virtual](https://www.estantevirtual.com.br/livro/a-linguagem-das-emocoes-0MK-3469-000-BK),
  com 4 usados e 2 novos a partir de R$ 345,00.
- **Citada por** — `rec:ihc/ekman-a-linguagem-das-emocoes` — declara
  `obra: ekman-a-linguagem-das-emocoes`
- **Nota** — ⚠️ **esgotada na editora, e o preço é de mercado de usado.** É a única
  tradução brasileira de qualquer obra desta trilha, e é por isso que ela entra apesar
  do preço. Item de mercado de usado tem estoque único e volátil: `disponivel: true`
  descreve hoje, não um estado estável, e a `url` é a do livro na plataforma, não a de
  um anúncio.

### What the Face Reveals

- **Autoria** — Paul Ekman e Erika L. Rosenberg (orgs.), série *Series in Affective
  Science*
- **Edição** — 2ª edição, Oxford University Press, 01/02/2005, 672 p. pela Amazon
  (xxi+639 p. em registro de biblioteca), capa dura, en-US. Há brochura indiana
  (`9780195398960`) e uma tiragem de 2020 com 656 p. (`9780190202941`).
- **Identificadores** — ISBN-13 `9780195179644` · ISBN-10 `0195179641`
- **Amazon** — https://www.amazon.com.br/dp/0195179641 — página lida. **R$ 342,05 em
  Kindle**, R$ 495,38 em capa dura; usado a partir de R$ 422,61.
- **Citada por** — `rec:ihc/ekman-rosenberg-what-the-face-reveals` — declara
  `obra: ekman-rosenberg-what-the-face-reveals`
- **Nota** — ⚠️ **o `custo` é o do Kindle**, que aqui é R$ 153 mais barato que o
  impresso e R$ 80 mais barato que o usado. A página não exibe autoria nem editora nos
  campos que o `ficha-livro.sh` lê — os dois vieram de busca separada, não da loja.
  Uma fatia só, do exemplar inteiro: o sumário capítulo a capítulo não apareceu em
  nenhuma página lida, e nomear intervalo seria inventar.

### Facial Action Coding System (manual e guia do investigador)

- **Autoria** — Paul Ekman, Wallace V. Friesen e Joseph C. Hager
- **Edição** — revisão de 2002, vendida pelo Paul Ekman Group como PDF: manual de 527
  páginas mais guia do investigador de 197 páginas, com fotos e vídeos de exemplo,
  en-US. O FACS foi publicado pela primeira vez em 1978, por Ekman e Friesen.
- **Identificadores** — **nenhum ISBN**: não é livro de livraria, é material vendido
  direto pelo detentor.
- **Amazon** — não existe. A venda é só em
  https://www.paulekman.com/facial-action-coding-system/, que é a `url` do recurso —
  **página lida no navegador embutido em 2026-11-14**, e é dela que saem o preço, a
  paginação e as 50 a 100 horas de estudo.
- **Citada por** — `rec:ihc/manual-do-facs` — declara `obra: manual-do-facs-2002`
- **Nota** — ⚠️ **preço em dólar, e a conversão é ordem de grandeza, não cotação.**
  US$ 350 convertidos a **R$ 1.984,50** pelo câmbio de 2026-11-13 (US$ 1 = R$ 5,67,
  Morningstar via Google). **Não inclui IOF nem spread de cartão internacional**, e o
  número envelhece com o câmbio, não com a loja — é o primeiro recurso do catálogo
  nessa situação. Com isso ele passa a ser **a obra mais cara do catálogo**, à frente
  do *Oxford Handbook of Voice Perception* (R$ 1.804,57).
  Dois fatos vizinhos, conferidos na mesma página: o **FACS Final Test** custa US$ 50 e
  é comprado **em separado** — é o único padrão de proficiência que existe, e não está
  no `custo` do recurso; e o treinamento presencial endossado é o curso de cinco dias
  de Erika Rosenberg, sem versão on-line aprovada. Não há edição em português nem
  revendedor brasileiro.

### Human Facial Expression: An Evolutionary View

- **Autoria** — Alan J. Fridlund
- **Edição** — Academic Press, 26/08/1994, 369 p. pela Amazon (xiv+369 em registro de
  biblioteca), capa dura, en-US
- **Identificadores** — ISBN-13 `9780122676307` · ISBN-10 `0122676300`
- **Amazon** — https://www.amazon.com.br/dp/0122676300 — página lida. **R$ 172,00 em
  Kindle**, R$ 2.132,00 em capa dura, usado a partir de R$ 474,24.
- **Citada por** — `rec:ihc/fridlund-human-facial-expression` — declara
  `obra: fridlund-human-facial-expression`
- **Nota** — ⚠️ **a diferença entre formatos é de 12 vezes**, o maior salto registrado
  neste arquivo: R$ 172,00 em Kindle contra R$ 2.132,00 em capa dura, num livro de 1994
  fora de catálogo impresso. Conferido que o Kindle é o mesmo título, no seletor de
  formatos da própria página. Há também
  [cópia para empréstimo no Internet Archive](https://archive.org/details/humanfacialexpre0000frid),
  que **não** entrou como recurso: empréstimo tem fila e prazo, e `disponivel: true`
  mentiria. O valor do livro na trilha é a data — a objeção ecológica é de 1994,
  contemporânea do auge do paradigma, não um arrependimento recente.

### The Science of Facial Expression

- **Autoria** — James A. Russell e José-Miguel Fernández-Dols (orgs.), série *Oxford
  Series in Social Cognition and Social Neuroscience*
- **Edição** — Oxford University Press, 15/05/2017, 552 p. pela Amazon (xii+540 em
  registro de biblioteca), capa dura, en-US
- **Identificadores** — ISBN-13 `9780190613501` · ISBN-10 `0190613505`
- **Amazon** — https://www.amazon.com.br/dp/0190613505 — página lida. **R$ 926,84 em
  Kindle**, R$ 1.341,78 em capa dura.
- **Citada por** — `rec:ihc/science-of-facial-expression` — declara
  `obra: science-of-facial-expression`
- **Nota** — o `custo` é o do Kindle, R$ 415 mais barato. A página não exibe a autoria
  nos campos lidos pelo `ficha-livro.sh` e devolve o título sem o artigo
  ("Science of Facial Expression"); os organizadores vieram de busca separada. É o
  volume em que defensores e críticos do paradigma escrevem em capítulos vizinhos — a
  razão de ele estar na trilha é essa, e não a abrangência.

### Emotional Expressions Reconsidered: Challenges to Inferring Emotion From Human Facial Movements

- **Autoria** — Lisa Feldman Barrett, Ralph Adolphs, Stacy Marsella, Aleix M. Martinez
  e Seth D. Pollak
- **Edição** — *Psychological Science in the Public Interest*, 20(1):1–68, 2019, en-US.
  **Artigo de revisão, não exemplar** — por isso é o único recurso desta trilha **sem
  `obra`**, pela regra de docs/catalogo.md.
- **Identificadores** — DOI `10.1177/1529100619832930`
- **Amazon** — não se aplica. Texto integral aberto em
  https://pmc.ncbi.nlm.nih.gov/articles/PMC6640856/, que é a `url` do recurso.
  `custo: 0`.
- **Citada por** — `rec:ihc/barrett-et-al-expressoes-reconsideradas`
- **Nota** — ⚠️ **prefira o PMC ou o repositório institucional ao PDF avulso**: o
  arquivo que circula no site da *Association for Affective Science* está rotulado como
  **corrigendum**, não como o artigo. É a leitura mais importante da trilha e a única
  gratuita, e a conclusão que a trilha usa é tripla: falta confiabilidade, falta
  especificidade e falta generalização no mapeamento entre movimento facial e categoria
  de emoção. Não confundir com `rec:ihc/barrett-como-as-emocoes-sao-feitas`, que é o
  livro da mesma autora e trata da teoria da emoção em geral; este é a instância
  facial, com a evidência reunida.

As seis fichas da trilha `trilha:ihc/reconhecimento-de-emocao-em-sinais-fisiologicos`, conferidas em
2026-11-15: quatro exemplares e dois conjuntos de artigo. Páginas de produto lidas no
navegador embutido, urls gratuitas conferidas por `curl`. Dois padrões apareceram de
novo e valem como aviso: **o formato barato não é o que se supõe** (em duas das quatro
obras a capa dura ou a reimpressão sai muito mais barata que a capa comum), e **acesso
aberto anunciado por agregador não é acesso aberto conferido**.

### Handbook of Psychophysiology

- **Autoria** — John T. Cacioppo, Louis G. Tassinary e Gary G. Berntson (orgs.)
- **Edição** — 4ª edição, Cambridge University Press. **Duas tiragens da mesma
  edição**: capa dura de 15/12/2016, 730 p., e reimpressão em capa comum de
  07/02/2019, 759 p. pela Amazon (760 em outras listagens), en-US.
- **Identificadores** — capa dura ISBN-13 `9781107058521` · ISBN-10 `110705852X`;
  capa comum `9781108723404` · `1108723403`; eletrônico `9781316728581`. ⚠️ O
  registro da Max Planck Digital Library traz `9781107415782` para uma versão
  eletrônica — **fonte única, não confirmada**.
- **Amazon** — https://www.amazon.com.br/dp/1108723403 — página lida, e é a `url` do
  recurso. **R$ 388,79 em capa comum, "Em estoque"**; Kindle R$ 407,21; capa dura
  R$ 1.129,14.
- **Citada por** — `rec:ihc/cacioppo-handbook-of-psychophysiology` — declara
  `obra: cacioppo-handbook-of-psychophysiology`
- **Nota** — ⚠️ **o exemplar barato é a reimpressão, não a edição original**, e a
  diferença é de R$ 740. A página da capa dura de 2016
  ([dp/110705852X](https://www.amazon.com.br/dp/110705852X)) diz "Somente 1 em
  estoque" e **não exibe preço no campo principal** — só no seletor de formatos. Como
  é a mesma 4ª edição, o recurso aponta a de 2019 sem perda de conteúdo. Sobre o
  porquê de ela estar na trilha: é onde mora a lógica da inferência psicofisiológica
  — relações um-para-um, um-para-muitos, muitos-para-um e muitos-para-muitos entre
  medida e construto —, não a abrangência.

### Psychophysiological Recording

- **Autoria** — Robert M. Stern, William J. Ray e Karen S. Quigley
- **Edição** — 2ª edição, Oxford University Press, 21/12/2000 pela Amazon (2001 nos
  registros de biblioteca e nos revendedores), 296 p., capa comum, en-US
- **Identificadores** — capa comum ISBN-13 `9780195113594` · ISBN-10 `0195113594`;
  encadernado `0195113586` / `9780195113587`; eletrônico `9780199880560`; edição
  on-line da OUP `9780199846962`
- **Amazon** — https://www.amazon.com.br/dp/0195113594 — página lida. **R$ 279,71 em
  capa comum**, Kindle R$ 313,22, capa dura R$ 2.071,07.
- **Citada por** — `rec:ihc/stern-ray-quigley-psychophysiological-recording` — declara
  `obra: stern-ray-quigley-psychophysiological-recording`
- **Nota** — o único dos quatro livros desta trilha em que a capa comum é o formato
  barato **e** o normal. Entra porque é o livro de *como registrar*, e a maior parte
  do erro em trabalho de emoção por fisiologia é de aquisição e não de modelo —
  nenhum artigo de computação afetiva ensina isso, porque todos o pressupõem.

### Electrodermal Activity

- **Autoria** — Wolfram Boucsein
- **Edição** — 2ª edição, Springer. ⚠️ **As fontes divergem na data e na paginação**:
  a Amazon diz 02/12/2011 e 636 p.; a Springer diz 2012 e XVIII+618 p. Há brochura de
  03/03/2014. en-US.
- **Identificadores** — capa dura ISBN-13 `9781461411253` · ISBN-10 `1461411254`;
  eletrônico `9781461411260`; brochura de 2014 `9781489990204`; DOI
  `10.1007/978-1-4614-1126-0` — **o identificador mais consistente entre as fontes**,
  que divergem nos ISBN por formato.
- **Amazon** — https://www.amazon.com.br/dp/1461411254 — página lida. **R$ 987,60 em
  Kindle**, R$ 1.893,71 em capa dura, R$ 1.220,55 em capa comum. A brochura de 2014
  (`1489990204`) dá **HTTP 404** na Amazon BR.
- **Citada por** — `rec:ihc/boucsein-electrodermal-activity` — declara
  `obra: boucsein-electrodermal-activity`
- **Nota** — ⚠️ **é o recurso mais caro desta trilha, e a etapa dele tem via grátis.**
  Seiscentas páginas sobre uma única medida: é a monografia definitiva da atividade
  eletrodérmica, que é o sinal das pulseiras do laboratório da Picard. Como o preço
  travaria a etapa para quem filtra por `custo_maximo`, o primer de EDA do grupo de
  Cowley entra na **mesma etapa**, a custo 0 — recurso distinto, não fatia: um é
  exemplar com `obra`, o outro é artigo sem.

### Advances in Physiological Computing

- **Autoria** — Stephen H. Fairclough e Kiel Gilleade (orgs.), série *Human–Computer
  Interaction Series*
- **Edição** — Springer London, 08/04/2014, 238 p., capa dura, en-US. Brochura de
  03/09/2016.
- **Identificadores** — capa dura ISBN-13 `9781447163916` · ISBN-10 `1447163915`;
  eletrônico `9781447163923`; brochura `9781447169932`. ⚠️ O Bookshare lista
  `9781447163923` como ISBN da obra, que é o do eletrônico — para o impresso vale
  `9781447163916`.
- **Amazon** — https://www.amazon.com.br/dp/1447163915 — página lida. **R$ 371,69 em
  capa dura**, R$ 916,25 em capa comum, R$ 543,57 em Kindle; envio estimado em 9 a 10
  dias. A brochura (`1447169932`) dá **HTTP 404** na Amazon BR.
- **Citada por** — `rec:ihc/fairclough-gilleade-physiological-computing` — declara
  `obra: fairclough-gilleade-physiological-computing`
- **Nota** — ⚠️ **a capa dura é a barata, e por larga margem**: R$ 371,69 contra
  R$ 916,25 da capa comum. É a mesma inversão registrada na ficha do *Intelligent
  Audio Analysis*, agora nos três formatos de uma vez — e mais uma razão para conferir
  o seletor de formatos antes de fixar `custo`, porque a suposição usual erra duas
  vezes seguidas nesta seção.

### Primers de psicofisiologia para IHC (seis revisões curtas em arXiv)

- **Autoria** — Benjamin Cowley, Marco Filetti, Kristian Lukander, Jari Torniainen,
  Andreas Henelius, Lauri Ahonen, Oswald Barral, Ilkka Kosunen, Teppo Valtonen, Minna
  Huotilainen, Niklas Ravaja e Giulio Jacucci
- **Edição** — seis **capítulos-companheiros**, publicados em arXiv em 2016, do
  *Psychophysiology Primer: A Guide to Methods and a Broad Review with a Focus on
  Human–Computer Interaction* (*Foundations and Trends in HCI* 9(3–4):151–308, DOI
  `10.1561/1100000065`). **Artigos, não exemplares** — sem `obra`.
- **Identificadores** — arXiv `1608.06986` (atividade eletrodérmica) · `1609.00183`
  (eletroencefalografia) · `1608.08041` (eletromiografia) · `1608.08353` (potenciais
  evocados) · `1609.07342` (rastreamento ocular) · `1609.02016` (aplicações
  multimodais em trabalho)
- **Amazon** — não se aplica. As seis urls dão HTTP 200 por `curl` em 2026-11-15;
  `custo: 0`.
- **Citada por** — `rec:ihc/primer-eeg-em-ihc`, `rec:ihc/primer-emg-em-ihc`,
  `rec:ihc/primer-potenciais-evocados-em-ihc`,
  `rec:ihc/primer-rastreamento-ocular-em-ihc`, `rec:ihc/primer-multimodal-em-ihc` (na
  etapa de abertura) e `rec:ihc/primer-atividade-eletrodermal-em-ihc` (na etapa de
  atividade eletrodérmica, como via grátis ao lado do Boucsein)
- **Nota** — ⚠️ **são os capítulos, não o primer inteiro, e a diferença importa.** O
  *Psychophysiology Primer* completo sai pela now publishers e **o acesso aberto não
  foi confirmado**: o OpenAlex marca como OA verde apontando o repositório da
  Universidade de Helsinque, o registro do editor não diz isso, e a página do editor
  redireciona para o emerald.com, que respondeu **HTTP 403 atrás de verificação de
  robô — que esta sessão não contorna**. O que está catalogado são os seis extratos em
  arXiv, cujo acesso é certo. O de EDA é o mais longo e é o que carrega a via grátis
  da etapa do Boucsein.

### Emotion Fingerprints or Emotion Populations? A Meta-Analytic Investigation of Autonomic Features of Emotion Categories

- **Autoria** — Erika H. Siegel, Molly K. Sands, Wim Van den Noortgate, Paul Condon,
  Yale Chang, Jennifer Dy, Karen S. Quigley e Lisa Feldman Barrett
- **Edição** — *Psychological Bulletin* 144(4):343–393, 2018, en-US. **Meta-análise em
  periódico, não exemplar** — sem `obra`.
- **Identificadores** — PMC `PMC5876074`
- **Amazon** — não se aplica. Texto integral aberto em
  https://pmc.ncbi.nlm.nih.gov/articles/PMC5876074/, conferida no navegador embutido
  (título confere, PDF disponível) e por `curl` (HTTP 200). `custo: 0`.
- **Citada por** — `rec:ihc/siegel-et-al-impressao-digital-ou-populacao`
- **Nota** — 202 estudos de reatividade autonômica sob indução de emoção, e a
  conclusão é que **não há mapeamento um-para-um** entre categoria de emoção e padrão
  autonômico: os tamanhos de efeito crescem, mas o padrão deles não separa uma
  categoria da outra, e corrigir viés de publicação os reduz e aumenta a
  heterogeneidade. É o análogo autonômico exato do que
  `rec:ihc/barrett-et-al-expressoes-reconsideradas` faz com a face, com a mesma autora
  sênior — e, como lá, ⚠️ **há um PDF circulando no site da Association for Affective
  Science; prefira o PMC**, que foi a fonte conferida. Leia contra a revisão de
  Kreibig de 2010, que conclui o oposto e não está no catálogo (ver §O que não tem
  ficha).

As quatro fichas da trilha `trilha:ihc/reconhecimento-multimodal-de-emocao`,
conferidas em 2026-11-15: dois exemplares e dois levantamentos livres. Novidade de
procedimento que vale registrar: **a Amazon devolveu muro de robô ao `curl`** nos três
ISBN desta trilha, e não apenas campos faltando como nas fichas anteriores — o
`ficha-livro.sh` saiu com `BLOQUEIO` e todo o preço veio do navegador embutido.

### The Handbook of Multimodal-Multisensor Interfaces, Volume 2

- **Autoria** — Sharon Oviatt, Björn Schuller, Philip R. Cohen, Daniel Sonntag,
  Gerasimos Potamianos e Antonio Krüger (orgs.). Subtítulo: *Signal Processing,
  Architectures, and Detection of Emotion and Cognition*.
- **Edição** — Association for Computing Machinery (ACM Books; alguns revendedores
  dizem Morgan & Claypool), 08/10/2018, 556 p., capa dura, en-US
- **Identificadores** — capa dura ISBN-13 `9781970001716` · ISBN-10 `1970001712`.
  ⚠️ As listagens divergem nos outros formatos: `9781970001709` (eletrônico, Perlego),
  `9781970001693` e `9781970001709` (PDF e ePub, Reference Global) e `9781970001686`
  numa listagem de brochura. Confira na ACM antes de usar qualquer um deles.
- **Amazon** — https://www.amazon.com.br/dp/1970001712 — página lida. **R$ 420,05 em
  Kindle**, R$ 1.033,88 em capa dura, R$ 732,20 em capa comum; "Somente 1 em estoque"
  na capa dura.
- **Citada por** — `rec:ihc/oviatt-handbook-multimodal-vol2` — declara
  `obra: oviatt-handbook-multimodal-vol2`
- **Nota** — ⚠️ **é o volume 2 e só ele, e isso resolve o que barrou a obra antes.** O
  comentário de `catalogo/recursos/ihc.yaml` na trilha de computação afetiva registra
  que este handbook foi deixado de fora porque três volumes tornavam a `obra`
  indecidível — um exemplar ou três? A resposta é que apenas o volume 2 trata detecção
  de emoção e de estado cognitivo; o 1 é fundamentos e modelagem de usuário, o 3 é
  processamento de linguagem e comercialização. Um volume, um exemplar, uma `obra`. O
  comentário antigo fica como está: ele registra corretamente por que a decisão foi
  adiada, e não por que estava errada.

### Social Signal Processing

- **Autoria** — Judee K. Burgoon, Nadia Magnenat-Thalmann, Maja Pantic e Alessandro
  Vinciarelli (orgs.)
- **Edição** — Cambridge University Press, 08/05/2017, 440 p. pela Amazon (xii+428 em
  registro de biblioteca, que provavelmente conta só o corpo), capa dura, en-US
- **Identificadores** — capa dura ISBN-13 `9781107161269` · ISBN-10 `1107161266`;
  brochura `9781316613832` · `1316613836`; eletrônico `9781316676202`; DOI
  `10.1017/9781316676202`
- **Amazon** — https://www.amazon.com.br/dp/1107161266 — página lida. **R$ 619,27 em
  Kindle**, R$ 693,90 em capa dura; "Somente 1 em estoque".
- **Citada por** — `rec:ihc/burgoon-et-al-social-signal-processing` — declara
  `obra: burgoon-et-al-social-signal-processing`
- **Nota** — ⚠️ **a brochura não existe na Amazon BR**: `dp/1316613836` dá HTTP 404 e a
  busca por `9781316613832` devolve **zero** resultado — não "sem preço", zero. É a
  primeira vez que esta seção registra um ISBN de brochura ausente do catálogo da loja
  inteira, e é por isso que o recurso aponta a capa dura. Sobre o conteúdo: é o livro
  que troca o alvo, de "emoção como rótulo" para "comportamento não verbal em
  interação", e com isso torna o multimodal a unidade natural de análise em vez de um
  truque de acurácia.

### Multimodal Machine Learning: A Survey and Taxonomy

- **Autoria** — Tadas Baltrušaitis, Chaitanya Ahuja e Louis-Philippe Morency
- **Edição** — *IEEE Transactions on Pattern Analysis and Machine Intelligence*
  41(2):423–443, 18/02/2019, en-US. **Artigo de levantamento, não exemplar** — sem
  `obra`.
- **Identificadores** — [arXiv:1705.09406](https://arxiv.org/abs/1705.09406) (v2 de
  01/08/2017)
- **Amazon** — não se aplica. Texto integral livre em arXiv, HTTP 200 por `curl` em
  2026-11-15, que é a `url` do recurso. `custo: 0`.
- **Citada por** — `rec:ihc/baltrusaitis-multimodal-survey-e-taxonomia`
- **Nota** — é a obra que dá o vocabulário da trilha: **cinco** desafios —
  representação, tradução, alinhamento, fusão e co-aprendizado —, dos quais a
  literatura de afeto nomeia um e chama de "fusão" os outros quatro. ⚠️ Um resumo
  gerado por IA (emergentmind) acrescenta alegações sobre modalidades futuras —
  háptica, molecular — que **não se confirmaram no texto do artigo**; para citação,
  use o PDF do arXiv ou a versão IEEE, não os agregadores.

### Foundations and Trends in Multimodal Machine Learning: Principles, Challenges, and Open Questions

- **Autoria** — Paul Pu Liang, Amir Zadeh e Louis-Philippe Morency
- **Edição** — levantamento em arXiv, 2022, en-US. **Artigo, não exemplar** — sem
  `obra`.
- **Identificadores** — [arXiv:2209.03430](https://arxiv.org/abs/2209.03430)
- **Amazon** — não se aplica. HTTP 200 por `curl` em 2026-11-15. `custo: 0`.
- **Citada por** — `rec:ihc/liang-foundations-trends-multimodal`
- **Nota** — sucessor do mesmo grupo do levantamento de 2017, atualizado para a era dos
  modelos grandes. Entra **ao lado** e não em lugar do outro: a taxonomia de 2017
  organiza melhor o problema, este diz onde o campo está e o que continua aberto — e
  uma trilha cuja competência central é julgar ganho precisa saber o que ainda não se
  sabe. Não confundir o título com a revista *Foundations and Trends in HCI*, que
  publicou o *Psychophysiology Primer* da trilha de fisiologia: são coisas diferentes
  com nomes parecidos.

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

### Longman Student Grammar of Spoken and Written English

- **Autoria** — Douglas Biber, Susan Conrad e Geoffrey Leech
- **Edição** — Longman (Pearson Education), Harlow, 2002, 487 p., inglês. Versão
  para estudante da *Longman Grammar of Spoken and Written English* (1999), baseada
  no mesmo corpus; 13 capítulos, do 1 (a perspectiva do discurso) ao 13 (a
  gramática da conversa). Há caderno de exercícios vendido à parte, não catalogado.
- **Identificadores** — brochura: ISBN-13 978-0-582-23726-1 · ISBN-10 `0582237262`
- **Amazon** — https://www.amazon.com.br/dp/0582237262 — capa comum a R$ 300,18 em
  2026-10-22 (capa dura só usada, R$ 539,74); o recurso declara o da capa comum
- **Citada por** — `rec:linguas/longman-student-grammar-caps-1-3-e-8`,
  `rec:linguas/longman-student-grammar-caps-4-7`,
  `rec:linguas/longman-student-grammar-caps-10-11`,
  `rec:linguas/longman-student-grammar-caps-9-e-12`
- **Nota** — a ordem dos capítulos não é a de
  `trilha:linguas/sintaxe-do-ingles`, e as fatias seguem a trilha: o cap. 8 (a
  gramática da oração) vai com os caps. 1 a 3 na oração simples, e o 12 (ordem das
  palavras: clivadas, existenciais, inversão) vai com o 9 nas construções. O cap. 13
  ficou sem etapa. A edição de 2002 é a que circula; não achei revisão posterior.

### A University Grammar of English

- **Autoria** — Randolph Quirk e Sidney Greenbaum
- **Edição** — Longman, Londres, 1973, inglês. Versão condensada, para estudante,
  de *A Grammar of Contemporary English* (Quirk, Greenbaum, Leech e Svartvik,
  1972); 14 capítulos e três apêndices. Reeditada em 1990, com outro título, como
  *A Student's Grammar of the English Language*.
- **Identificadores** — brochura: ISBN-10 `0582552079`
- **Amazon** — https://www.amazon.com.br/s?k=0582552079 — link de **busca**: fora
  de catálogo, só circula usado, e o anúncio de origem não mostrava preço; o
  recurso declara R$ 150 como estimativa
- **Citada por** — `rec:linguas/quirk-greenbaum-university-grammar-caps-2-7-8`,
  `rec:linguas/quirk-greenbaum-university-grammar-caps-3-6`,
  `rec:linguas/quirk-greenbaum-university-grammar-caps-9-11-12`,
  `rec:linguas/quirk-greenbaum-university-grammar-caps-10-13-14`
- **Nota** — fatias pela trilha, não pela ordem do livro: caps. 2, 7 e 8 na oração
  simples; 3 a 6 nos sintagmas; 9, 11 e 12 no período composto; 10, 13 e 14 nas
  construções. Ficam sem etapa o cap. 1 (variedades do inglês) e os apêndices
  (formação de palavras, prosódia, pontuação).

### A Student's Introduction to English Grammar

- **Autoria** — Rodney Huddleston e Geoffrey K. Pullum
- **Edição** — 1ª ed., Cambridge University Press, 2005, 312 p., inglês. Versão
  para graduação da *Cambridge Grammar of the English Language* (2002); 16
  capítulos, do 1 (introdução) ao 16 (morfologia), com exercícios por capítulo.
  Há 2ª edição (2022, brochura ISBN-13 978-1-009-08801-5), não catalogada: o
  exemplar indicado é o de 2005.
- **Identificadores** — brochura: ISBN-13 978-0-521-61288-3 · ISBN-10 `0521612888`
- **Amazon** — https://www.amazon.com.br/dp/0521612888 — preço não conferido em
  2026-10-22 (a página não abriu daqui); o `custo: 250` é estimativa a partir do
  preço de lista da brochura em dólar
- **Citada por** — `rec:linguas/huddleston-pullum-student-grammar-caps-1-2-4-8-9`,
  `rec:linguas/huddleston-pullum-student-grammar-caps-3-5-7-e-12`,
  `rec:linguas/huddleston-pullum-student-grammar-caps-10-13-14`,
  `rec:linguas/huddleston-pullum-student-grammar-caps-11-e-15`
- **Nota** — as fatias seguem `trilha:linguas/sintaxe-do-ingles`, não o livro: o
  cap. 3 (verbos, tempo, aspecto, modo) vai com os sintagmas, onde a trilha põe o
  sintagma verbal; negação (8) e tipos de oração (9) vão com a oração simples; as
  relativas (11) vão com o sintagma complexo, como a pós-modificação oracional da
  competência. O cap. 16 (morfologia) ficou sem etapa.

### Viewpoint 1 Student's Book

- **Autoria** — Michael McCarthy, Jeanne McCarten e Helen Sandiford
- **Edição** — 1ª ed., Cambridge University Press, 2012, inglês norte-americano.
  Livro-texto de inglês geral, nível B2 do QECR segundo a editora; continuação da
  série *Touchstone*. Doze unidades (pp. 10–135) com um Checkpoint a cada três, e
  as seções de cada unidade no fim do livro (Speaking naturally, pp. 138–143;
  Vocabulary notebook, Grammar extra, leitura e escuta, pp. 144–167). Sumário
  conferido no *frontmatter* da editora. Há edição atualizada (2015, ISBN-13
  978-1-107-60151-2), não catalogada: a capa do exemplar é a de 2012.
- **Identificadores** — ISBN-13 978-0-521-13186-5 · ISBN-10 `0521131863`
- **Amazon** — https://www.amazon.com.br/dp/0521131863 — página e preço não
  conferidos em 2026-10-22; o `custo: 250` é estimativa. O exemplar é o do curso
  Alumni (Master 1 e 2).
- **Citada por** — `rec:linguas/viewpoint-1-unidades-1-3`,
  `rec:linguas/viewpoint-1-unidades-4-6`, `rec:linguas/viewpoint-1-unidades-7-9`,
  `rec:linguas/viewpoint-1-unidades-10-12`
- **Nota** — as fatias são os quatro blocos entre Checkpoints, cada um com o
  próprio Checkpoint, e espinha de `trilha:linguas/ingles-geral-b2`.

## O que não tem ficha

Recursos que não são livros ficam de fora: documentação oficial (MDN, pandas,
scikit-learn, TypeScript Handbook, react.dev, docs.claude.com, MCP), material aberto
de referência (arc42, microservices.io, adr.github.io, DORA, web.dev, ARIA APG,
Paul's Online Math Notes, LibreTexts, Guia Foca Linux, os dois guias do Beej), artigos (*Attention Is All You Need*, *The
Illustrated Transformer*, Fowler, fitness functions, *A Mathematical Theory of
Communication* de Shannon, *Notes on Programming in C* de Pike), vídeo (3Blue1Brown, aulas de
*Statistical Rethinking*), repositórios de exercício (anthropic-cookbook) e os
recursos de projeto.

*Statistical Rethinking* (`rec:dados/statistical-rethinking-aulas`) tem livro
homônimo, mas o recurso aponta para as aulas gravadas e o material aberto, não para
o livro — por isso não ganhou ficha.

Três chegaram aqui pelo caminho mais caro. Os dois guias do Beej
(`rec:programacao/beej-c-sistemas`, `rec:programacao/beej-ipc-descritores`) e o Guia
Foca Linux (`rec:so/guiafoca-linha-de-comando`) foram marcados como exemplar em
2026-11-01, por julgamento feito a partir de título e URL, e a `obra` saiu quando a
ficha foi escrita e olhou o material. Nenhum dos três tem editora, ISBN ou edição à
venda. O Beej revisa continuamente, chama o próprio texto de guia e de "beta-quality
document", e vende em brochura justamente os outros dois guias dele — *Network
Programming* e *Git* —, não estes. O Guia Foca são cinco volumes versionados cada um
por conta, parados em 27/07/2020, e já constava da lista acima desde a pesquisa de
outubro: a marcação o contradisse. Remover `obra` subiu a `rev` dos três de 2 para 3
([catalogo.md §4](catalogo.md)).

Dois entraram em 2026-11-14 com a trilha de reconhecimento de emoção na voz, e
**nasceram sem `obra`** em vez de perdê-la depois — é o caso dos três guias acima
aplicado na hora de escrever, não na hora de corrigir. O capítulo de recursos de fala
do livro aberto de PLN da comunidade brasileira
(`rec:ihc/pln-brasileiras-recursos-de-fala`) é material aberto de referência: tem
edição numerada, mas é publicado em PDF aberto pela própria comunidade, sem editora
comercial, sem ISBN e sem edição à venda. E o CORAA SER
(`rec:ihc/projeto-corpus-coraa-ser`) é **corpus**, não leitura: o recurso é de
`formato: projeto` e aponta o repositório em que o corpus se baixa, de modo que não é
exemplar por dois motivos independentes. Os dois estão com url conferida por `curl`
(HTTP 200 em 2026-11-14).

Em 2026-11-14 a trilha de expressão facial acrescentou **um** recurso sem `obra`, e
por motivo diferente dos cinco acima: `rec:ihc/barrett-et-al-expressoes-reconsideradas`
é **artigo de revisão** em periódico — a *Psychological Science in the Public
Interest* —, e artigo não é exemplar. Tem ficha, ao contrário dos artigos listados no
primeiro parágrafo, porque é a leitura central de uma etapa e porque há uma armadilha
de fonte a registrar (o PDF que circula fora do PMC está rotulado como corrigendum).

Três obras ficaram **fora do catálogo** na mesma passada, e a decisão vale escrita:

1. **Handbook of Face Recognition** (Li e Jain) — é de **identidade**, não de emoção.
   Entraria pelo título e sairia na primeira leitura.
2. **A cópia do Fridlund no Internet Archive** — empréstimo com fila e prazo, de modo
   que `disponivel: true` seria falso. O exemplar comprável está catalogado; a cópia
   está citada na ficha.
3. **O FACS Final Test** (US$ 50, Paul Ekman Group) — é avaliação de proficiência, não
   material de estudo, e é comprado em separado do manual. Está na ficha do manual,
   fora do `custo` do recurso.

Em 2026-11-15 a trilha de sinais fisiológicos acrescentou **sete** recursos sem
`obra` — seis primers em arXiv e uma meta-análise —, todos artigos. Os seis primers
ganharam **uma ficha só**, porque são capítulos de um mesmo trabalho e o que havia a
registrar é comum aos seis.

E **duas obras que a trilha usa ficaram fora do catálogo**, cada uma por um motivo
que vale escrito, porque os dois se repetem:

1. **A revisão de Kreibig de 2010** (*Autonomic nervous system activity in emotion: A
   review*, *Biological Psychology* 84(3):394–421, DOI
   `10.1016/j.biopsycho.2010.03.010`) — **acesso fechado**: o registro do repositório
   suíço que a indexa diz literalmente "open access status closed", e os
   repositórios de Genebra e Friburgo trazem o registro sem PDF. Há uma cópia numa
   página de disciplina da Universidade de Milão, **de autorização não verificada**,
   que por isso não serve como `url` de recurso. Ela é citada na `descricao` de
   `etapa:ihc/especificidade-autonomica-reconsiderada`, porque a competência central
   da trilha é justamente comparar as duas meta-análises — e sem a comparação não se
   cobra. Artigo essencial e inacessível é um caso que o catálogo não resolve: o
   honesto é dizer onde ele está e que custa.
2. **O *Psychophysiology Primer* completo** (Cowley et al., *Foundations and Trends in
   HCI* 9(3–4):151–308, DOI `10.1561/1100000065`) — **acesso aberto não confirmado**.
   O OpenAlex marca OA verde apontando o repositório da Universidade de Helsinque; o
   registro do editor não diz isso; e a página do editor redireciona para o
   emerald.com, que respondeu HTTP 403 atrás de **verificação de robô, que esta sessão
   não contorna**. Catalogados ficaram os seis extratos em arXiv, de acesso certo.
   `custo: 0` com acesso incerto seria pior que ausência.

Em 2026-11-15 a trilha multimodal acrescentou **três** recursos sem `obra`: dois
levantamentos em arXiv, que ganharam ficha por serem leitura central de etapa, e um
**projeto**, que não ganhou — `rec:ihc/projeto-auditar-ganho-da-fusao` aponta o
[CMU Multimodal SDK](https://github.com/CMU-MultiComp-Lab/CMU-MultimodalSDK), do grupo
de Morency, com CMU-MOSI e CMU-MOSEI. É ferramenta e corpus, não leitura: mesmo caso
de `rec:ihc/projeto-corpus-coraa-ser`, e por dois motivos independentes não é exemplar.
Conferido em 2026-11-15 pela API do GitHub: licença MIT, não arquivado, último push em
2023-12-04.

E **a meta-análise que sustenta a competência central da trilha ficou fora**, pela
terceira vez nesta série de cinco trilhas afetivas — o que já é padrão e não acidente:

**D'Mello & Kory, "A Review and Meta-Analysis of Multimodal Affect Detection Systems"**
(*ACM Computing Surveys* 47(3), artigo 43, fevereiro de 2015, 36 p., DOI
`10.1145/2682899`). A página da ACM responde **HTTP 403 atrás de verificação de robô,
que esta sessão não contorna** — nem por `curl` nem pelo navegador. A única cópia livre
que apareceu está numa página de disciplina do ICT/USC, **com licenciamento não
confirmado**, que por isso não serve como `url`. Os números que a trilha usa — 85% de
vitória sobre o melhor unimodal, mediana de 6,60%, e ganho em dado natural (4,59%) a um
terço do ganho em dado atuado (12,7%) — estão na `descricao` de
`etapa:ihc/ganho-real-da-fusao` e na de `comp:ihc/ganho-real-da-fusao`, para que a
competência se cobre. ⚠️ **Eles vieram de resumos e agregadores, não do PDF do artigo**,
e estão declarados como tais.

**O padrão, dito de uma vez.** Três vezes o artigo decisivo de uma trilha afetiva foi
inacessível: o Kreibig de 2010 (acesso fechado), o *Psychophysiology Primer* completo
(403 atrás de verificação de robô) e este (idem). Nos três casos a decisão foi a mesma
— o fato vai para a `descricao` da etapa, a obra não vai para o catálogo, e o motivo
vem para cá. `custo: 0` com acesso incerto, ou `url` de cópia não autorizada, seriam
piores que a ausência: o catálogo passaria a prometer o que não entrega.

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
8. **`rec:programacao/rust-book-sistemas`** cita dois autores, Klabnik & Nichols, e o
   recorte "caps. 1 a 12", e aponta para https://doc.rust-lang.org/book/, que é a
   edição web **viva**: ela acompanha o compilador e hoje corresponde à 3ª edição,
   assinada também por Chris Krycho e pressupondo Rust 1.97.0. A numeração de
   capítulos muda entre edições, como no item 2, e o slug da obra
   (`klabnik-nichols-rust-book`) guarda a autoria de duas pessoas. Vale fixar qual
   edição o catálogo assume; nada foi alterado.
9. **`rec:web/node-succinctly-kurniawan`** aponta para a ficha do Goodreads, que é
   catálogo e não o material. A Syncfusion, que publicou o livro, hoje serve em
   https://www.syncfusion.com/succinctly-free-ebooks/nodejs um *Node.js Succinctly*
   **de outro autor** (Emanuele DelBono, 2016), e a edição de Kurniawan de 2014 não
   foi localizada em distribuição autorizada. Ou o recurso precisa de uma URL de onde
   se obtenha o material, ou precisa ser depreciado.
