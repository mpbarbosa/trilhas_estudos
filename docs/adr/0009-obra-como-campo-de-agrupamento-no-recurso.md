# ADR-0009 — Obra como campo de agrupamento no recurso, não como entidade

- **Data**: 2026-10-15
- **Status**: aceito

## Contexto

Um recurso pertence a exatamente uma etapa ([catalogo.md §2](../catalogo.md)). Um livro
que atende sete etapas vira, por isso, sete entradas de `recurso` — cada uma com o
`custo` do exemplar inteiro, que se compra uma vez. [catalogo.md §8](../catalogo.md)
registrava isto como pendência e condicionava a decisão a um segundo caso real.

O caso chegou em excesso. Hoje o acervo tem **nove obras pagas fatiadas em 37
recursos**:

| Obra | Fatias | Exemplar | Soma das fatias | Repetição |
|---|---|---|---|---|
| AI Engineering (Huyen) | 3 | 350 | 1050 | +700 |
| An Introduction to Database Systems, vol. I (Date) | 8 | 90 | 720 | +630 |
| AI-Powered Search | 2 | 350 | 700 | +350 |
| Hands-On Machine Learning, 3ª ed. (Géron) | 2 | 350 | 700 | +350 |
| LLM Engineer's Handbook | 2 | 280 | 560 | +280 |
| Sistemas Operacionais: Projeto e Implementação (Tanenbaum & Woodhull) | 6 | 60 | 360 | +300 |
| Calculus (Kline) | 4 | 90 | 360 | +270 |
| Arquitetura de software: as partes difíceis (Ford) | 3 | 120 | 360 | +240 |
| A Bíblia do Claude AI | 7 | 30 | 210 | +180 |
| **Total** | **37** | **1720** | **5020** | **+3300** |

Duas obras atravessam áreas: Kline aparece sob `rec:dados/` e `rec:matematica/`,
Géron sob `rec:dados/` e `rec:ia/`. O id não carrega o agrupamento.

### A premissa da pendência está errada

A pendência afirmava que a repetição "superestima o custo de um caminho para o filtro
de `custo_maximo`". Conferido no código, não é o que acontece: o filtro é **por
recurso**, nunca por caminho —
[`sugerir.py:398`](../../src/trilhas/motor/sugerir.py) compara `rec.custo >
custo_maximo` uma fatia por vez. `grep` sobre `src/` não encontra nenhuma soma de
`custo`: as duas únicas agregações são contadores (`gratuitos`, `culpas["custo"]`).

Medido contra o catálogo real, com perfil cheio para que o custo seja o único filtro
que ainda pode eliminar:

| `custo_maximo` | Etapas eliminadas por custo na trilha de Date |
|---|---|
| ausente | 0 |
| 89 | 1 — `etapa:dados/normalizacao-superior` |
| 90 | 0 |

O corte acontece entre 89 e 90, não entre 719 e 720. Para quem não tem o livro, cada
fatia é individualmente honesta: ler qualquer uma custa o exemplar inteiro, e é esse
o número que a fatia declara. **A distorção no filtro de hoje é zero.**

### Onde a distorção é real

Só numa soma de caminho — e nenhuma existe. Se existisse, o viés seria estreito:
somando o recurso mais barato de cada etapa, apenas **uma** das oito trilhas é
afetada, porque só nela duas etapas sem alternativa gratuita dependem do mesmo
exemplar:

| Trilha | Soma dos mínimos | Custo real | Viés |
|---|---|---|---|
| `dados/bancos-de-dados-relacionais` | 270 | 90 | 3× |
| as outras sete | — | — | nenhum |

### O agrupamento já existe, à mão, e já desandou

[bibliografia.md](../bibliografia.md) é uma ficha por **obra**, com a lista dos
recursos que a citam: 12 das 49 fichas agrupam mais de um recurso, 81 recursos no
total. O documento declara-se descritivo — não entra na validação nem no lock —, e
nada o mantém em dia. As **oito fatias de Date não têm ficha**: a obra foi fatiada
três dias depois de a bibliografia ter sido verificada, e o agrupamento exato que
motivou esta ADR é o que a versão manual perdeu.

Para escrever esta ADR foi preciso reconstruir o agrupamento a partir dos títulos, com
duas heurísticas diferentes que erraram em sentidos opostos — uma separou Kline e
Ford, a outra separou uma fatia de Date. A informação existe na hora da autoria e não
é recuperável depois senão por adivinhação.

### Opções

1. **Entidade `obra`** com recursos-parte que a referenciam e carregam `custo` zero.
2. **Campo de agrupamento** no próprio recurso (`obra: date-vol1`), `custo` mantido
   por fatia e contado uma vez por obra em qualquer soma.
3. **Manter como está** e documentar o viés.

## Decisão

**Opção 2.** `obra` passa a ser campo **opcional** de `Recurso`: slug em minúsculas,
dígitos e hífen, sem prefixo `<tipo>:` — não é id de catálogo, não nomeia entidade,
não tem `rev`, `status` nem depreciação.

- **`custo` não muda de lugar nem de significado**: continua por recurso e continua
  querendo dizer "o que custa ter acesso a este recurso". O filtro do motor fica
  byte a byte como está.
- **Qualquer agregação monetária conta cada obra uma vez**, pelo `custo` de uma de suas
  fatias. Recurso sem `obra` é obra de si mesmo.
- **Validação nova**: fatias que declaram a mesma `obra` declaram o mesmo `custo` —
  *erro*. Fatias de uma obra são um exemplar por definição; dois preços significam
  ou um erro de digitação ou duas obras, e os dois casos se corrigem.
- `obra` é mudança **substantiva** para `rev`, na mesma linha de `custo`
  ([catalogo.md §4](../catalogo.md)): declarar ou trocar o agrupamento muda o custo
  que o sistema atribui a um caminho.
- **A implementação fica pendente.** Esta ADR decide a forma; o campo só existe
  depois de entrar em `carregar`, na validação e no esquema de §2.

A opção 1 foi recusada pela consequência no motor. Com `custo` zero na parte, o único
consumidor que hoje está correto passa a estar errado: um estudante com
`custo_maximo = 0` veria as fatias de Date passarem o filtro, embora lê-las exija
comprar um livro de R$ 90. Consertar isso obriga o filtro a resolver
parte → obra → custo, de modo que se paga um quinto tipo de entidade — identidade,
`rev`, ciclo de vida e depreciação por [ADR-0005](0005-identidade-imutavel-e-depreciacao.md),
carregador, coleção no snapshot, validações — **e** a reescrita do filtro, para
produzir um número que ninguém lê.

A opção 3 foi recusada pelo esforço de autoria, não pelo modelo. O agrupamento não é
trabalho novo: ele já está sendo mantido à mão em bibliografia.md, onde nada o
confere e onde já está incompleto. Declará-lo no recurso é uma linha por fatia — 37
hoje, nenhuma nas outras 98 — no mesmo arquivo que o autor já está editando, no
momento em que ele é a única pessoa que sabe a resposta.

## Consequências

- **Nada muda no motor agora.** O filtro continua idêntico e os sete cenários de
  [motor §5](../motor-de-sugestao.md) continuam verdes. Esta ADR compra um campo, não
  um comportamento — e o campo é inerte até existir um consumidor.
- **Custo de caminho passa a ser calculável certo** quando alguém quiser: somar o
  máximo por `obra`. O consumidor óbvio é uma coluna "quanto custa esta trilha" no
  acervo, que hoje mostra esforço somado e nenhum dinheiro somado.
- **O viés que sobra é outro, e `obra` não o resolve**: quem já comprou o livro
  continua vendo o preço cheio em cada fatia restante. Posse é percurso, não
  catálogo, e nenhuma entidade a registra. Fica nomeado aqui para não ser confundido
  com o problema que esta ADR fechou.
- **A "Citada por" de bibliografia.md fica conferível** contra `obra`, em vez de
  mantida à mão. As oito fatias de Date são a primeira coisa que tal conferência
  pegaria. Esta ADR não obriga a conferência — o documento segue descritivo.
- **O campo é opcional e ninguém é obrigado a declará-lo.** A validação do `custo`
  igual pega o erro de digitação, não a omissão: um autor pode fatiar um livro novo e
  esquecer a `obra`, que é exatamente o que aconteceu com Date na bibliografia.
  Detectar a omissão exige a conferência contra a bibliografia, que não está aqui.
- **Renomear uma obra é um rename mecânico** entre suas fatias, sem a cerimônia de
  [ADR-0005](0005-identidade-imutavel-e-depreciacao.md), porque `obra` não é id e nada
  histórico aponta para ela. O que se perde é o agrupamento de um agregado que ninguém
  persiste.
- **Se `obra` precisar de identidade própria** — porque a ficha bibliográfica virou
  normativa, ou porque uma parte passou a ser comprável em separado —, isso é a ADR
  seguinte, e este campo é o caminho de migração, não um obstáculo.
- **O filtro de `custo_maximo` não tem teste.** `custo_maximo` não aparece em
  `tests/`. A medição desta ADR foi feita por script, fora da suíte; o ramo de custo
  de [`_recursos_viaveis`](../../src/trilhas/motor/sugerir.py) só está coberto pela
  leitura. Dívida anterior a esta ADR, registrada aqui porque foi ela que a revelou.
