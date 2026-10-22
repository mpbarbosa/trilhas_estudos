# ADR-0019 — Capítulo como parte de recurso, fora das vias de estudo da etapa

- **Data**: 2026-10-22
- **Status**: aceito

## Contexto

O estudante terminou o capítulo 2 de *Prompt Engineering for LLMs* e quis registrar
isso. O livro é um recurso só, `rec:ia/prompt-engineering-for-llms`, que carrega
sozinho a etapa `etapa:ia/engenharia-de-prompt`. O capítulo 1 já tinha produzido o
erro que [ADR-0012](0012-fato-de-recurso-no-percurso.md) existe para evitar: a etapa
foi concluída por ele, e a evidência teve de ser retratada
([ADR-0014](0014-retratacao-de-evidencia-por-seq.md), `seq` 51 e 52 do log de
`est:mpb`).

ADR-0012 deu a leitura parcial como visível "cruzando recursos percorridos com os
recursos da etapa". Isso funciona quando o livro é fatiado **por etapa**
([ADR-0009](0009-obra-como-campo-de-agrupamento-no-recurso.md)): cada fatia atende uma
etapa inteira. Aqui o livro inteiro é a etapa, e não há fatia a percorrer — só o todo,
que ainda não foi lido.

Fatiar por capítulo com `obra` e nada mais quebra o motor. Os recursos de uma etapa
são **alternativas**: cada um, sozinho, a atende, e o motor escolhe um
([`sugerir.py`](../../src/trilhas/motor/sugerir.py), `min` por encaixe, custo efetivo,
duração). Onze capítulos com o mesmo `custo` do exemplar (validação 12) empatam com o
livro no custo e o vencem na duração, e a sugestão passa a mandar ler "o capítulo 11"
como o material da etapa inteira. A validação 5 cairia do mesmo jeito: um capítulo
disponível bastaria para dar a etapa por coberta.

## Decisão

**Campo opcional `parte_de` no recurso**, com o id de outro recurso da mesma etapa.
Um recurso que o declara é **parte**: capítulo do todo, não via de estudo.

```yaml
  - id: rec:ia/prompt-engineering-for-llms-cap-02
    etapa: etapa:ia/engenharia-de-prompt
    custo: 300
    obra: prompt-engineering-for-llms
    parte_de: rec:ia/prompt-engineering-for-llms
```

- **`Catalogo.recursos_da_etapa` deixa a parte de fora.** É o ponto pelo qual o motor
  escolhe, a validação 5 conta e a tela lista; um filtro ali cobre os três, e a regra
  não se espalha em cópias que divergiriam. Quem precisa da parte a acha em `recursos`.
- **`percorrer` aceita a parte sem mudança**: a conferência de ADR-0012 é só existir
  no catálogo. É para isso que a parte existe.
- **`iniciar --recurso` recusa a parte** e aponta o todo. "Estudo esta etapa por
  aquele material" com um capítulo seria o mesmo erro da sugestão, gravado no log.
- **Validação 13**: a parte mora na etapa do todo, e o todo não é parte — um nível só.
  Referência que não resolve é a validação 2.
- **`obra` fica nas partes, não no todo.** O rollup de `mostrar` conta fatias por
  `obra`; com o todo dentro, onze capítulos virariam doze fatias. A posse
  ([ADR-0015](0015-posse-de-exemplar-como-estante-declarada.md)) não perde nada: a
  parte nunca é escolhida, então o custo efetivo dela não pesa em sugestão alguma.
- **`parte_de` é substantivo** na tabela de `rev` (catalogo.md §4): muda o que a etapa
  oferece como via de estudo.

Recusado: um booleano (`acompanhamento: true`). Ele tira o capítulo do motor, mas não
diz de qual todo, e a validação não teria como conferir que capítulo e livro moram na
mesma etapa.

## Consequências

- **Leitura parcial de livro de uma etapa só passa a ser registrável** sem conceder
  competência: `trilhas-percurso percorrer rec:ia/prompt-engineering-for-llms-cap-02`,
  e `mostrar` dá `2/11 fatia(s)` da obra. A etapa segue `em_andamento`; concluí-la
  continua sendo fato separado, como ADR-0012 quis.
- **O motor não muda de comportamento para catálogo sem `parte_de`**: o filtro é por
  campo novo, e os recursos existentes não o declaram.
- **A tela não mostra os capítulos** na página da etapa, pelo mesmo filtro. É coerente
  com a página listar vias de estudo, e cega para o progresso por capítulo, como já
  era para o fato de recurso (ADR-0012).
- **Duração por capítulo é estimativa** quando a editora não publica páginas por
  capítulo; reparte a do todo. Não alimenta nada além do rollup, porque a parte não
  entra no `encaixe` do motor.
- **Livro fatiado por etapa (ADR-0009) não ganha `parte_de`.** Lá cada fatia é via de
  estudo de uma etapa; o campo é só para capítulo de material que atende uma etapa
  inteira.
