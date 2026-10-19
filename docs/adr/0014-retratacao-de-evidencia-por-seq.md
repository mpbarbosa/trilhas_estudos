# ADR-0014 — Retratação de evidência como fato novo, endereçada pelo `seq` do log

- **Data**: 2026-10-18
- **Status**: aceito

## Contexto

[ADR-0008](0008-percurso-como-log-de-fatos-datados.md) previu este momento nas suas
próprias consequências: "marcar uma evidência como equivocada exige um fato de
retratação; não está nesta ADR e será necessário na primeira vez que alguém clicar
errado." Alguém clicou errado.

No percurso de `est:mpb`, o estudante leu o capítulo 1 de um livro e rodou
`trilhas-percurso concluir etapa:ia/engenharia-de-prompt`. A conclusão emitiu os
eventos **#28–#30**: a conclusão da etapa e **duas** `EvidenciaRegistrada` de nível
`intermediario` (`comp:ia/engenharia-de-prompt` e `comp:ia/uso-de-llm-por-api`).
Reabrir a etapa com `iniciar` (evento **#31**) corrigiu o progresso, porque
`progresso_de` faz o último fato sobre a etapa vencer. A evidência ficou.

`competencias_de`, em [`projecao.py`](../../src/trilhas/percurso/projecao.py), toma o
**máximo** nível já evidenciado e descarta de propósito evidência posterior de nível
menor. Não existe evento que retire evidência, e `sei <competencia> iniciante` não
baixa nada: o nível é monotônico por construção. Uma busca exaustiva sobre as seis
ações hoje registráveis — `iniciar`, `concluir`, `abandonar`, `sei`, `reagir` e
conclusão de etapa que ensina nível menor — em todas as permutações de até três
delas aplicadas sobre um `avancado` já evidenciado, não encontrou **nenhuma**
sequência que o rebaixasse. É invariante de fato, não acidente de um caminho.

O dano não é estético. O motor filtra candidatos por `requires`/`nivel_minimo`
([motor §2.2](../motor-de-sugestao.md)), então competência inflada libera etapas para
as quais o estudante não está pronto; e `urgencia_de_revisao`
([motor §3.6](../motor-de-sugestao.md)) passa a medir o decaimento de um nível que
nunca foi atingido, ressuscitando para revisão uma etapa que nunca foi aprendida.

Era preciso decidir entre três saídas, e a primeira pergunta a responder é se a
monotonia é invariante declarada ou acidente de implementação. **É declarada, em
parte**: [CONTEXT §4](../CONTEXT.md) diz que "`teaches` de uma etapa nunca rebaixa o
nível de uma competência já dominada". Isso cobre a conclusão de etapa, que é o
caminho pelo qual quase toda evidência nasce, e existe por um motivo bom — concluir
uma etapa introdutória ou de revisão depois de uma avançada não pode rebaixar quem a
concluiu. A implementação, porém, é **mais larga que o declarado**: ela também ignora
autoavaliação de nível menor, o que a invariante escrita não pede. Essa largura extra
é que estava sem dono.

## Decisão

**Um evento novo de retratação, que a projeção honra ignorando a evidência retratada.**
Era a opção (a). `EvidenciaRetratada` carrega o `seq` do evento que retrata e um
`motivo` opcional, e `competencias_de` projeta como se a evidência retratada nunca
tivesse sido emitida — o máximo passa a ser tomado sobre as evidências restantes.
O comando é `trilhas-percurso retratar <seq> [--motivo]`.

**A retratação aponta para um `seq`, não para o par (competência, etapa).** As duas
alternativas foram pesadas e o `seq` ganha por duas razões que o par não tem resposta:

1. **O par não endereça autoavaliação.** `registrar_autoavaliacao` grava evidência com
   `etapa=None`. Uma retratação que só sabe falar de `(competência, etapa)` não alcança
   um `sei` dado por engano — seria metade de um mecanismo.
2. **O par é ambíguo exatamente na forma do caso real.** `est:mpb` concluiu a etapa e
   depois a reabriu; quando ela for concluída de verdade, haverá **duas**
   `EvidenciaRegistrada` para o mesmo par. Retratar o par retrataria as duas, incluindo
   a legítima. O `seq` é o único alvo que distingue "a evidência de 18 de outubro" de
   "a de novembro".

Além disso, o `seq` dá a granularidade que o caso pede: a conclusão errada emitiu duas
evidências, e o estudante pode querer retratar uma só — pode ser que o capítulo 1
realmente tenha ensinado engenharia de prompt, mas não uso de LLM por API.

`seq` é alvo legítimo porque é parte declarada do modelo, não detalhe de
armazenamento: `Registro.seq` "dá a ordem total" em
[`eventos.py`](../../src/trilhas/percurso/eventos.py) e a exportação em JSONL grava
`seq` em cada linha, que é onde quem estuda vai lê-lo.

**A retratação não repete a competência nem o nível que retrata.** Seria redundância
capaz de contradizer o alvo. O espírito de ADR-0008 — gravar na escrita o que o
catálogo dizia, para a projeção nunca reconsultar — não se aplica aqui, e a diferença
é o que importa: `teaches` pode mudar, o evento **#29 não pode**. O log é append-only,
então a consulta ao alvo jamais dará resposta diferente da que daria na escrita.

**A monotonia fica, agora como decisão e não como largura sem dono.** Nível de
competência não cai por evidência nova de nível menor — nem por `teaches`, nem por
autoavaliação. Cai só por retratação. A razão para manter a autoavaliação monotônica é
de intenção: `sei comp:x iniciante` depois de um `avancado` evidenciado é ambíguo entre
"me rebaixe" e "registro que sei isto ao menos no nível iniciante", e dar a um comando
ambíguo o poder de rebaixar é pior do que exigir que a retratação seja dita por nome.
A invariante de [CONTEXT §4](../CONTEXT.md) é atualizada para dizer isto.

As outras duas opções foram recusadas:

- **(b) Deixar a monotonia e documentar outro remédio** não tem remédio para documentar.
  Sem evento novo, as únicas saídas são editar o banco — que o *trigger* proíbe e a
  ADR-0008 veda — ou conviver com a competência inflada, que é o dano descrito acima.
  A opção (b) é, na prática, "não corrigir".
- **(c) Tomar a evidência mais recente em vez do máximo** viola a invariante declarada
  de [CONTEXT §4](../CONTEXT.md) e muda o significado de todo histórico já gravado: a
  conclusão de uma etapa de revisão passaria a rebaixar quem a concluiu, e a data de
  `ultima_evidencia_em` deixaria de ser a do nível vigente, que é o que faz
  `urgencia_de_revisao` medir o decaimento do que a pessoa sabe hoje e não de um nível
  já superado. O argumento forte que ela exigia não existe: nada em (c) é alcançado que
  a retratação não alcance, e (c) cobra por isso a reinterpretação de todo o log.

**Retratar uma retratação não está modelado**, e `retratar` recusa um `seq` que não
seja uma `EvidenciaRegistrada`. Quem retratou por engano escreve uma evidência nova
(`sei`, ou concluir a etapa de novo) — que é o honesto: um fato datado novo, com a
origem e a confiança que lhe couberem, em vez de uma pilha de negações.

**A conferência do alvo é pura e roda na escrita.** `conferir_retratacao` recebe os
registros e devolve o erro ou `None`, no mesmo molde de `conferir_recurso`: o alvo tem
de existir, pertencer ao estudante e ser uma evidência ainda não retratada. É a mesma
função para a CLI e para quem mais venha a escrever, para que não haja duas memórias
([interface §3.3](../interface.md)).

## Consequências

- A invariante de [CONTEXT §4](../CONTEXT.md) "toda `CompetenciaDominada` tem ao menos
  uma `Evidencia`" passa a ser "ao menos uma `Evidencia` **não retratada**", e a
  monotonia entra como invariante declarada. Retratar a última evidência de uma
  competência a faz desaparecer da projeção, que é o correto: competência sem evidência
  não existe.
- Retratar **não** restaura `desconhece` quando há evidência anterior legítima. Retratar
  a evidência `intermediario` de quem já tinha um `iniciante` evidenciado deixa a
  competência em `iniciante`. É o comportamento certo — a retratação apaga um fato, não
  a história toda —, mas não é o que a palavra "retratar" sugere a quem a lê rápido.
- A auditoria continua respondendo "por que o sistema acha que eu sei isso", e passa a
  responder "por que ele deixou de achar": a retratação é datada e carrega motivo.
- **O `seq` tem de ser descobrível, ou o comando é inútil.** `trilhas-percurso mostrar`
  passa a listar as evidências com seu `seq`, nível, origem e dia, marcando as
  retratadas. Sem isso, a única forma de achar o alvo seria ler o JSONL à mão.
- A exportação em JSONL ganha um tipo de linha novo. Quem já lia o arquivo tem de
  conhecer `evidencia_retratada` para não superestimar competências — é o mesmo custo
  que qualquer evento novo cobra, e a razão pela qual reconstruir o banco a partir da
  exportação segue não implementado (ADR-0008).
- A projeção deixa de ser uma passada única sobre o log: é preciso recolher as
  retratações antes de projetar as evidências, porque a retratação vem necessariamente
  depois do que retrata. Custo de uma varredura a mais sobre um log de um estudante.
- **A tela não retrata.** A escrita pela web é por ação sobre uma etapa
  ([`web/escrever.py`](../../src/trilhas/web/escrever.py)); retratação endereça um fato
  do log por `seq`, que não tem tela a que pertencer. Fica para
  [interface.md](../interface.md) decidir, quando houver uma tela de histórico onde o
  `seq` apareça — e até lá é correção de linha de comando.
- O caso de `est:mpb` fica com comando pronto e **não rodado**: quem estuda decide se e
  quando corrige o próprio percurso. Os alvos são os eventos #29 e #30.
