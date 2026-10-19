# ADR-0013 — Posse de exemplar como estante declarada no perfil, aplicada ao custo efetivo

- **Data**: 2026-10-18
- **Status**: aceito

## Contexto

[ADR-0009](0009-obra-como-campo-de-agrupamento-no-recurso.md) fechou o agrupamento das
fatias de um exemplar e nomeou, nas Consequências, o viés que não resolveu: "quem já
comprou o livro continua vendo o preço cheio em cada fatia restante. Posse é percurso,
não catálogo, e nenhuma entidade a registra."
[ADR-0012](0012-fato-de-recurso-no-percurso.md) recusou a posse como evento de log — a
data da aquisição não é lida por ninguém, e posse muda enquanto o log proíbe `UPDATE` e
`DELETE` por *trigger* ([ADR-0008](0008-percurso-como-log-de-fatos-datados.md)) — e
deixou para cá duas perguntas: **em que chave** a posse é declarada, e **o que o motor
faz com ela**.

O acervo tem hoje 183 recursos, 92 pagos. Desses, 59 são fatias de 16 obras (14 com mais
de uma fatia); os outros **33 são pagos sem `obra`** — exemplares de fatia única, que se
compram igual.

### O que já estava medido, e o que a frase não distinguia

ADR-0012 mediu: 69 etapas têm dois ou mais recursos viáveis para `est:mpb`; em 25 o
`custo` já troca o recurso escolhido em
[`sugerir.py:370`](../../src/trilhas/motor/sugerir.py); e zerar o custo de uma fatia
possuída trocaria a escolha em **14** etapas. Os dois primeiros números reproduzem
exatamente. O terceiro é correto para a pergunta que a frase faz — "uma fatia" —, e
essa não é a pergunta que o sistema responde:

| Pergunta | Etapas em que a escolha muda |
|---|---|
| zerar **uma** obra por vez, e somar as etapas atingidas | **14** |
| zerar as **16** obras de uma vez (o estudante possui tudo) | **12** |

As duas etapas da diferença são `etapa:ia/agente-em-producao` e
`etapa:ia/rag-em-producao`, e elas têm uma propriedade em comum: **todo** recurso viável
delas pertence a uma obra, nenhuma tem alternativa gratuita.

| Etapa | Recursos viáveis |
|---|---|
| `ia/agente-em-producao` | `biblia-claude-producao` R$ 30 / 30 min · `ai-engineering-agentes-producao` R$ 350 / 600 min |
| `ia/rag-em-producao` | `ai-powered-search-rag` R$ 350 / 600 min · `ai-engineering-producao` R$ 350 / 900 min |

Possuir só uma das duas obras vira o resultado; possuir as duas devolve o empate em
custo, e o desempate seguinte — `duracao_min` — reescolhe o que já era escolhido hoje.
**Posse não é aditiva**: cada obra a mais pode desfazer o efeito da anterior. Nos dois
casos o resultado final está certo, porque quando o dinheiro deixa de distinguir, é o
esforço que deve decidir.

Esta ADR adota o número da pergunta que o sistema realmente responde — o estudante tem
um conjunto de obras, não uma de cada vez: **12 etapas**, das quais **6** são da Bíblia
do Claude, a única obra cuja posse o próprio repositório registra (commit `5c6bcb1`
concluiu as sete etapas lidas nela).

### Posse de `biblia-claude` sozinha, medida

| Etapa | Hoje | Com posse |
|---|---|---|
| `ia/claude-modelos-e-chat` | `claude-docs-overview` (grátis) | `biblia-claude-chat` (R$ 30) |
| `ia/claude-prompt-e-saida-estruturada` | `anthropic-cookbook-prompts` (grátis) | `biblia-claude-prompts` (R$ 30) |
| `ia/claude-api-e-sdk` | `claude-docs-api` (grátis) | `biblia-claude-api` (R$ 30) |
| `ia/tool-use-e-mcp` | `mcp-spec-e-guias` (grátis) | `biblia-claude-mcp` (R$ 30) |
| `ia/claude-code-e-skills` | `claude-code-docs` (grátis) | `biblia-claude-code-skills` (R$ 30) |
| `ia/agentes-com-claude` | `anthropic-cookbook-agentes` (grátis) | `biblia-claude-agentes` (R$ 30) |

Seis etapas em que a sugestão manda ler a documentação de graça tendo o estudante o
livro na mão — **e nenhuma delas aparece no painel hoje**. O mesmo commit `5c6bcb1` que
é a evidência da posse concluiu as sete etapas da Bíblia, e etapa concluída é eliminada
por `Motivo.CONCLUIDA` antes de qualquer recurso ser escolhido. Das 12 etapas da medição
geral, 6 ainda não foram concluídas, e todas pertencem a obras que o repositório **não**
registra como adquiridas:

| Etapa viva | Obra que a mudaria |
|---|---|
| `dados/sql-contra-o-modelo`, `dados/armazenamento-e-indices` | `date-vol1` |
| `matematica/limite-e-continuidade`, `matematica/integral-e-acumulacao` | `kline-calculus` |
| `ia/ngramas-e-perplexidade` | `manning-schutze-fsnlp` |
| `so/gerenciamento-de-memoria` | `tanenbaum-woodhull` |

Ou seja: o efeito imediato desta ADR sobre `est:mpb` é **zero sugestão trocada**. Ela não
é escrita por causa do que muda hoje; é escrita porque o viés está medido, o caso que o
revelou já passou, e os outros quinze exemplares ainda vão chegar. Isso é dito aqui para
não ser descoberto depois como decepção.

### A chave da declaração

**`obra`.** Dezesseis linhas cobrem as 59 fatias, e o agrupamento vem pronto. Mas gasta
a propriedade que ADR-0009 comprou de propósito: "renomear uma obra é um rename mecânico
(…) porque `obra` não é id e nada histórico aponta para ela". Um percurso que aponte para
`obra` passa a ser esse "algo histórico": renomear `date-vol1` deixa de ser mecânico e
passa a apagar uma posse em silêncio, porque o percurso não entra na validação do
catálogo e nada cruzaria os dois. E os **33 pagos sem `obra`** ficam indeclaráveis até
alguém lhes dar um slug — 33 mudanças substantivas de `rev` (ADR-0009 pôs `obra` na
linha de `custo`) para declarar uma coisa que não é do catálogo.

**`recurso`.** Id imutável e nunca reaproveitado ([ADR-0005](0005-identidade-imutavel-e-depreciacao.md)),
conferível contra o catálogo, e cobre os 33 de fatia única sem tocar em nada. O preço é
a propagação: declarar `rec:ia/biblia-claude-chat` e não as outras seis fatias dá, medido,
**1 etapa** em vez de 6 — o exemplar inteiro foi comprado, mas só um capítulo dele saiu
barato.

A propagação não é um custo novo: é exatamente a leitura que ADR-0012 já escolheu para
`RecursoPercorrido` — "o rollup por obra se faz na leitura, contra o catálogo de hoje".
`obra` serve de caminho entre irmãs **no momento da consulta**, sem ser gravada em lugar
nenhum.

| | linhas para declarar as 16 obras | cobre os 33 de fatia única | preserva o rename mecânico de `obra` |
|---|---|---|---|
| chave `obra` | 16 | não | **não** |
| chave `recurso`, sem propagação | 59 | sim | sim |
| chave `recurso`, propagando por `obra` na leitura | **16** | **sim** | **sim** |

### Filtro, desempate, ou os dois

O risco que a pergunta carrega é o de ADR-0009: ela recusou a entidade `obra` com `custo`
zero na parte porque "um estudante com `custo_maximo = 0` veria as fatias de Date passarem
o filtro, embora lê-las exija comprar um livro de R$ 90". A posse **inverte** essa frase:
lê-las não exige comprar nada, porque já foi comprado. O zero de ADR-0009 era
incondicional e falso para todo mundo; este é condicional a um fato declarado sobre quem
pergunta.

Medido, com posse de `biblia-claude` e `custo_maximo` variando — "só no desempate"
significa filtrar pelo custo de catálogo e desempatar pelo custo efetivo:

| `custo_maximo` | `SEM_RECURSO_VIAVEL` hoje | com posse nos dois | etapas em que "só no desempate" diverge de "nos dois" |
|---|---|---|---|
| 0 | 18 | **17** | **7** |
| 30 | 16 | 16 | 0 |
| 50 | 13 | 13 | 0 |
| 100 | 1 | 1 | 0 |
| ausente (o caso de `est:mpb`) | 0 | 0 | 0 |

A etapa que muda de lado em `custo_maximo = 0` é `etapa:ia/agente-em-producao`: seu único
recurso viável é a fatia da Bíblia a R$ 30, hoje eliminada com `SEM_RECURSO_VIAVEL` —
motivo que se lê como lacuna de catálogo para uma etapa cujo material está na estante do
estudante.

E a linha de cima mostra que **"só no desempate" não é uma versão mais tímida de "nos
dois": é uma versão que não faz nada** justamente quando faria falta. Abaixo do preço do
exemplar, o filtro elimina a fatia antes de o desempate existir — as 7 divergências em
`custo_maximo = 0` são as 6 da Bíblia mais `agente-em-producao`. Acima do preço, filtro e
desempate concordam em tudo, e separar os dois seria código sem consequência.

### Explicação

[ADR-0003](0003-motor-de-sugestao-por-regras-explicavel.md) e
[motor §2.5](../motor-de-sugestao.md): a explicação nunca menciona fator ausente de
`fatores`. A escolha do recurso **não é um fator** — acontece em `_aplicar_filtros`,
antes de `_pontuar`, e os seis fatores são todos sobre a etapa, com pesos que somam 1.
Inventar um sétimo fator "posse" para poder falar dela mentiria sobre o que produziu o
score.

O problema real não está na frase da explicação, está no preço ao lado dela:
`agora.html` mostra `{{ c.recurso.custo }}`, e o cartão passaria a exibir *A Bíblia do
Claude AI · R$ 30* como material escolhido de uma etapa cujo concorrente é grátis — sem
nada que diga por quê. E `comum.dinheiro(0)` devolve `"grátis"`, de modo que zerar o
`custo` do próprio `Recurso` faria a tela chamar de grátis um livro de R$ 350.

## Decisão

**Posse é `estante`: uma lista de ids de recurso no perfil, propagada às fatias irmãs
por `obra` na leitura, e consumida pelo motor como `custo_efetivo` — no filtro e no
desempate, por ser a mesma grandeza.**

### Declaração

```yaml
perfil:
  # Exemplares já adquiridos. Uma fatia basta: a posse vale para a obra inteira.
  estante:
    - rec:ia/biblia-claude-chat
```

- **Chave `recurso`**, pelos três motivos da tabela: 16 linhas como `obra`, cobre os 33
  exemplares de fatia única, e não transforma `obra` em referência histórica.
- **Uma fatia basta.** Declarar mais fatias da mesma obra é idempotente, não erro.
- **`estante` entra no glossário** ([CONTEXT §1](../CONTEXT.md)) como atributo de
  **Perfil** — "estado declarado + inferido do estudante" —, não como entidade nova. A
  palavra já é a do repositório para a prateleira do estudante
  ([estante-goodreads.md](../estante-goodreads.md)) e não colide com *acervo*, que é a
  coleção do catálogo.
- **Tolerante na leitura**, como todo o resto de `web/percurso.py`: id desconhecido é
  ignorado, não é exceção. Um percurso pela metade tem de render uma tela.

### Custo efetivo

```python
def _custo_efetivo(ctx: _Contexto, recurso: Recurso) -> float:
    return 0.0 if recurso.id in ctx.possuidos else recurso.custo
```

`ctx.possuidos` é o fecho da `estante` pelas obras do catálogo de hoje, calculado uma vez
em `_Contexto.montar`. Entra em dois lugares, que são um:

- **No filtro** de `custo_maximo` ([`_recursos_viaveis`](../../src/trilhas/motor/sugerir.py)):
  o que já foi pago não gasta orçamento nenhum.
- **No desempate** de `min(viaveis, …)`: o material da estante ganha de um concorrente
  gratuito só pelo empate em zero, e perde para ele se for mais longo.

`Recurso.custo` **não muda**, nem na dataclass congelada nem no lock: o livro custa
R$ 350 para quem for comprá-lo, e é esse o número do catálogo. O efetivo é derivado, vive
no motor, e some quando a `estante` some.

### Explicação e apresentação

- **Nenhum fator novo, nenhuma frase nova em `explicar.py`.** Os pesos continuam somando
  1 e a regra de §2.5 fica intacta por construção, não por cuidado.
- **O preço do recurso sugerido passa a dizer que é da estante.** `RecursoSugerido` ganha
  `na_estante: bool`, e o cartão mostra *R$ 30 · já seu* em vez de *R$ 30* — o valor de
  catálogo continua à vista, com a razão ao lado. Nada é renderizado como "grátis":
  `comum.dinheiro` não é chamado com zero que não seja zero.
- **As telas de catálogo não mudam.** `acervo.py` conta `gratuitos` pelo custo de
  catálogo e `detalhe.py` ordena recursos por ele: são vistas do catálogo, não do
  percurso, e um acervo que mudasse de preço conforme quem olha deixaria de ser o acervo.

### Cenários de [motor §5](../motor-de-sugestao.md)

Os sete seguem verdes sem alteração: nenhum declara `estante`, e `estante` vazia deixa
`_custo_efetivo` igual a `recurso.custo`. Entra um **cenário 8**: *recurso possuído vence
alternativa gratuita mais longa, e passa `custo_maximo` abaixo do seu preço.* As duas
metades num cenário só, porque é uma decisão só.

**A dívida de teste que ADR-0009 registrou já está paga, e não por esta ADR.** Aquela
ADR escreveu que "o filtro de `custo_maximo` não tem teste; `custo_maximo` não aparece em
`tests/`" — verdade quando foi escrita, e o commit que a implementou (`3cd41d6`) pagou a
dívida no mesmo gesto: `test_teto_abaixo_do_custo_do_recurso_elimina_a_etapa_por_custo`,
`test_teto_igual_ao_custo_do_recurso_nao_elimina` e
`test_filtro_de_custo_e_por_recurso_nao_por_caminho` cobrem o ramo de custo nos dois
lados do corte. Esta ADR mexe no mesmo filtro, então **acrescenta** o lado que aqueles
três não podiam ter: o teto que a posse atravessa, e a posse que não atravessa teto
nenhum quando não foi declarada.

### O que foi recusado

- **Chave `obra`**, pela tabela acima: barata nas 16 e impossível nos 33, e cobra de
  ADR-0009 uma propriedade que ela comprou.
- **Posse só no desempate**, por não fazer nada abaixo do preço do exemplar — medido: 7
  etapas divergem em `custo_maximo = 0`, nenhuma em `custo_maximo = 30`. É a metade do
  comportamento que não tem caso.
- **Posse só no filtro**, pelo espelho: para `est:mpb`, que não declara `custo_maximo`,
  seria exatamente nada — as 12 etapas medidas são todas do desempate.
- **Zerar `custo` no `Recurso`** (por `dataclasses.replace` na borda), porque a tela
  passaria a chamar o exemplar de "grátis" e o `catalogo.lock.json` deixaria de ser a
  única resposta à pergunta "quanto custa este material".
- **Fator `posse` em `fatores`**, porque a escolha do recurso não pontua etapa, e um
  sétimo peso teria de sair dos outros seis para somar 1.

## Consequências

- **A sugestão de `est:mpb` não muda hoje.** A estante declarada é
  `rec:ia/biblia-claude-chat`, que se propaga às sete fatias da Bíblia — e as sete etapas
  que elas atendem estão concluídas no log. O campo fica declarado, correto, exercitado
  pelos testes e inerte no painel até a próxima obra entrar. As 6 etapas vivas da medição
  esperam declarações que o repositório ainda não tem evidência para fazer sozinho: posse
  é do estudante, e esta ADR não a adivinha.
- **Desfazer é apagar uma linha de YAML**, que é exatamente o que ADR-0012 argumentou que
  o log não ofereceria. O campo ser inerte hoje torna isso barato de verificar.
- **Posse errada é sugestão errada, e nada a detecta.** Vendido o livro e esquecida a
  linha, o motor segue mandando ler o que não está mais na estante, e com `custo_maximo`
  baixo chega a ressuscitar etapas que o orçamento deveria eliminar. Não há conferência
  possível: o catálogo sabe o preço, não quem pagou. O remédio é a linha ser visível e
  curta, não uma validação.
- **Posse não é aditiva, e isso vai confundir.** Declarar uma obra muda a sugestão de uma
  etapa; declarar a segunda obra da mesma etapa pode desfazer a mudança, como em
  `ia/rag-em-producao`. O resultado está certo em ambos os casos, mas a explicação não
  conta essa história, porque posse não é fator.
- **`obra` ganha um segundo consumidor, e com ele uma consequência.** ADR-0009 escreveu
  que o campo era "inerte até existir um consumidor"; agora ele decide propagação de
  posse. Renomear uma obra continua mecânico — nada persiste o slug —, mas **reagrupar**
  (juntar duas obras, ou separar uma) muda silenciosamente o alcance de uma `estante` já
  declarada. É menos grave que gravar o slug no percurso, e não é zero.
- **O ramo de custo de `_recursos_viaveis` fica coberto nos dois regimes**, com e sem
  estante, somando-se aos três testes que `3cd41d6` já deixou. Os outros ramos —
  `indisponivel`, `idioma`, `formato` — seguem como estavam.
- **`percurso/*.yaml` ganha campo sem ganhar esquema.** O arquivo continua "formato
  provisório, nenhuma ADR o decidiu" (CLAUDE.md), e `web/percurso.py` continua o único
  lugar que o lê. Esta ADR decide o significado de `estante`, não o esquema do arquivo
  que a hospeda.
- **A estante não se cruza com o que foi percorrido.** `RecursoPercorrido`
  ([ADR-0012](0012-fato-de-recurso-no-percurso.md)) diz que o material foi lido; `estante`
  diz que ele está em mãos. Um não implica o outro em nenhuma direção — livro emprestado
  se lê sem possuir, livro comprado dorme na prateleira — e esta ADR não deriva um do
  outro. Derivar seria inventar o fato que nenhum dos dois registra.
- **O custo de caminho previsto por ADR-0009 fica mais fácil e mais ambíguo.** Somar o
  máximo por obra agora tem duas respostas — com e sem a estante —, e quem construir a
  coluna "quanto custa esta trilha" terá de escolher qual mostra. Não é decidido aqui.
- **Posse continua sem data.** Não se pode perguntar "o que eu tinha em março", e a
  sugestão gravada em `SugestaoEmitida` não registra que a estante a produziu. Era o preço
  de não pôr posse no log, pago com os olhos abertos em ADR-0012 e cobrado aqui.
