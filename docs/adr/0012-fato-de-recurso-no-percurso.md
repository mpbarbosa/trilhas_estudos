# ADR-0012 — Percurso registra fato de recurso; posse fica fora do log

- **Data**: 2026-10-18
- **Status**: aceito

## Contexto

O vocabulário de eventos do percurso ([ADR-0008](0008-percurso-como-log-de-fatos-datados.md),
`percurso/eventos.py`) é inteiramente de etapa: `EtapaIniciada`, `EtapaConcluida`,
`EtapaAbandonada`, `EvidenciaRegistrada`, `SugestaoEmitida`, `FeedbackDado`. Um recurso
aparece num lugar só — o campo opcional `recurso` de `EtapaIniciada`, que diz "estudo
esta etapa por aquele material". Não há como registrar nada **sobre** um recurso.

O caso que revelou a lacuna: o estudante terminou de ler *A Bíblia do Claude AI*, que
[ADR-0009](0009-obra-como-campo-de-agrupamento-no-recurso.md) fatiou em sete recursos
com `obra: biblia-claude`, um por etapa de `trilha:ia/claude-do-chat-ao-agente`. O fato
"li este livro" não tinha onde morar. O único registro possível era concluir as sete
etapas — e concluir etapa emite evidência de competência, um *claim* mais forte que o
fato original.

### Quanto mais forte, medido

A fatia do livro contra o esforço estimado da etapa que ela atende:

| Fatia | Duração | Etapa | Esforço | Fatia / esforço |
|---|---|---|---|---|
| `biblia-claude-chat` | 120 | `etapa:ia/claude-modelos-e-chat` | 300 | 40,0% |
| `biblia-claude-prompts` | 150 | `etapa:ia/claude-prompt-e-saida-estruturada` | 420 | 35,7% |
| `biblia-claude-code-skills` | 120 | `etapa:ia/claude-code-e-skills` | 720 | 16,7% |
| `biblia-claude-api` | 96 | `etapa:ia/claude-api-e-sdk` | 600 | 16,0% |
| `biblia-claude-mcp` | 120 | `etapa:ia/tool-use-e-mcp` | 900 | 13,3% |
| `biblia-claude-agentes` | 90 | `etapa:ia/agentes-com-claude` | 1200 | 7,5% |
| `biblia-claude-producao` | 30 | `etapa:ia/agente-em-producao` | 900 | 3,3% |

Em **nenhuma** das sete o livro é a maioria do esforço; o máximo é 40%. A conclusão
das sete etapas não exagerou na margem: ela concedeu competência por 13% de média do
trabalho previsto. E, pelo log ser append-only, a evidência emitida não se desfaz —
corrigir exige um fato de retratação, que ADR-0008 nomeou como ausente e segue ausente.

O caso não é isolado: o acervo tem hoje **16 obras em 59 fatias**, todas as 16 pagas e
14 delas com mais de uma fatia. Qualquer livro terminado recai no mesmo lugar.

### Opções

1. **Nada muda.** Fato de recurso fica fora do modelo; `EtapaIniciada.recurso` continua
   o único vínculo, e documenta-se a perda.
2. **Evento de fato datado de recurso**, sem emitir evidência de competência.
3. **Fato de posse** (`ObraAdquirida` ou equivalente), que é o viés que ADR-0009 deixou
   nomeado nas Consequências: "Posse é percurso, não catálogo, e nenhuma entidade a
   registra" — quem já comprou o livro continua vendo o `custo` cheio em cada fatia
   restante.

A (1) foi recusada pelo custo da alternativa que ela obriga. Sem fato de recurso, o
único jeito de registrar leitura é concluir etapa, e isso não é uma imprecisão de
registro: é evidência de competência gravada num log que não a retira. A opção
"não registrar nada" também não está disponível na prática — o estudante registrou, e
registrou do jeito forte, porque era o único.

### O que a opção 3 custaria agora

A posse tem um consumidor vivo, e ele é maior do que ADR-0009 supôs. Aquela ADR mediu o
**filtro** de `custo_maximo` ([`sugerir.py:398`](../../src/trilhas/motor/sugerir.py)) e
concluiu, corretamente, que a distorção ali era zero. O que ela não pesou é a **escolha
do recurso**, [`sugerir.py:370`](../../src/trilhas/motor/sugerir.py):

```python
min(viaveis, key=lambda r: (-_encaixe(ctx, r.duracao_min), r.custo, r.duracao_min, r.id))
```

`custo` é o segundo critério — e para o único estudante do repositório é o **primeiro**.
`est:mpb` declara apenas `idiomas`, sem `minutos_por_semana`, e sem referência de sessão
`_encaixe` devolve 0,5 para todo recurso ([motor §3.4](../motor-de-sugestao.md)): o
empate no primeiro critério é universal, e quem decide qual material a sugestão nomeia
é o preço.

Medido no catálogo real, com as restrições de `est:mpb`: 69 etapas têm dois ou mais
recursos viáveis; em 25 delas o `custo` já troca o recurso escolhido; e zerar o custo de
uma fatia possuída trocaria a escolha em **14 etapas** — entre elas seis das sete da
Bíblia, onde hoje a sugestão manda ler a documentação gratuita em vez do livro que o
estudante já tem na mão.

Isso faz da posse uma mudança de comportamento do motor, não um campo inerte. ADR-0009
teve o cuidado de comprar um campo e nenhum comportamento; o oposto disto.

## Decisão

**Opção 2 agora, opção 3 na ADR seguinte.** A ordem é esta porque a opção 2 fecha uma
lacuna que hoje não tem contorno e não toca o motor, enquanto a opção 3 muda a saída da
sugestão em 14 etapas medidas e merece ser pesada por si.

### Evento novo: `RecursoPercorrido`

```python
@dataclass(frozen=True, slots=True)
class RecursoPercorrido:
    recurso: str
    recurso_rev: int
```

- **Não emite evidência de competência.** Percorrer um material que é 13% do esforço de
  uma etapa não é prova de nada sobre a etapa. Registrar o fato é o objetivo; conceder
  competência é o erro que esta ADR existe para evitar.
- **`recurso_rev` fica gravado**, como `etapa_rev` nos eventos de etapa: a fatia que se
  percorreu é a daquela revisão, e repontar a fatia para outro capítulo depois não muda
  o que foi percorrido ([catalogo.md §4](../catalogo.md)).
- **`obra` não fica gravada.** O que o fato afirma é "percorri este recurso"; o
  agrupamento por obra é apresentação, não parte do *claim*. Gravá-lo faria o
  renomear-obra de ADR-0009 — mecânico "porque `obra` não é id e nada histórico aponta
  para ela" — partir o histórico em dois agrupamentos. O rollup por obra se faz na
  leitura, contra o catálogo de hoje, e nenhum *claim* muda com isso.
- **Verbo distinto de `concluir`, de propósito.** [CONTEXT §1](../CONTEXT.md) diz que
  "tudo que é estudável e concluível é **Etapa**", e `concluir_etapa` emite evidência.
  Um `concluir_recurso` que não emite faria o mesmo verbo significar duas forças de
  fato — exatamente a confusão que produziu o caso desta ADR. `percorrer` não colide
  com nada no glossário e serve a vídeo, exercício e projeto, não só a leitura.

### O motor não muda

`RecursoPercorrido` **não** entra em `Percurso`, `_recursos_viaveis` fica byte a byte
como está, e os sete cenários de [motor §5](../motor-de-sugestao.md) seguem verdes. A
projeção do fato é função própria, consumida pela CLI, não campo da entrada do motor.

Filtrar o recurso percorrido da sugestão foi considerado e recusado por dois efeitos:

- **Esconde a etapa em vez de trocar o material.** `etapa:ia/claude-modelos-e-chat` tem
  o livro como 40% do esforço: quem o percorreu ainda precisa dos outros 60%. Onde a
  fatia é o único recurso viável, filtrá-la derruba a etapa com
  `SEM_RECURSO_VIAVEL` — motivo que se lê como lacuna de catálogo, para uma etapa que é
  justamente a próxima coisa a fazer.
- **Briga com `recurso_em_uso`.** A projeção guarda por qual material a etapa está sendo
  estudada ([`projecao.py`](../../src/trilhas/percurso/projecao.py)). Percorrer esse
  material faria o motor passar a nomear outro, para uma etapa em andamento.

Revisitar quando houver um fato que distinga "percorri e não basta" de "percorri e
terminei" — que é a opção 3 somada a um estado de etapa parcial, nenhum dos dois aqui.

### Posse fica fora do log

Além de mudar o motor, a posse no log tem dois defeitos de forma:

- **Nada lê a data da aquisição.** ADR-0008 separou o percurso por natureza: o que
  acontece num instante vai para o log, o que é estado declarado fica em YAML. O que o
  motor precisaria saber é "possuo isto **agora**" — estado, não instante.
- **Posse muda e o log não.** Livro se vende, se empresta, se perde. Desfazer exige o
  fato de retratação que ADR-0008 deixou pendente, para um fato cuja correção em YAML
  seria uma linha apagada.

Então a ADR seguinte decide posse como **estado declarado** no perfil, não como evento
— e decide também em que chave (`obra` não é id; `recurso` é, mas então a posse de um
exemplar tem de se propagar às fatias irmãs).

## Consequências

- **"Li este livro" passa a ser registrável e visível.** `trilhas-percurso percorrer
  <recurso>` grava o fato; `mostrar` lista os recursos percorridos e agrupa por obra,
  com quantas fatias de cada obra já foram. É a conferência que ADR-0009 previu para a
  "Citada por" de bibliografia.md, chegando pelo lado do percurso.
- **Etapa parcialmente percorrida fica visível, mas não vira estado de `Progresso`.**
  Nenhum `EstadoEtapa` novo: a etapa segue `em_andamento`, e quem quiser a fração
  cruza recursos percorridos com os recursos da etapa. Um estado "parcial" seria
  decisão sobre o que conta como parcial — fração de duração? de fatias? — e esta ADR
  não tem o caso que a decida.
- **Percorrer recurso e concluir etapa ficam independentes nos dois sentidos.** Dá para
  percorrer todas as fatias sem concluir etapa alguma, e para concluir uma etapa sem
  ter percorrido recurso nenhum. É intencional: são fatos diferentes sobre coisas
  diferentes, e foi confundi-los que gerou o caso.
- **A evidência já emitida pelas conclusões do caso original permanece.** O log não
  retira; esta ADR só impede a repetição. A retratação continua pendente desde ADR-0008,
  e agora há um comando a mais pelo qual se erra.
- **A conferência de `percorrer` é mais fraca que a de `iniciar --recurso`.**
  `conferir_recurso` exige que o recurso pertença à etapa; aqui não há etapa com que
  comparar, então a conferência é só existir no catálogo. `status` e `disponivel` ficam
  de fora pelo mesmo motivo de lá: percorrer material depreciado ou fora do ar é fato
  legítimo de quem o tem em mãos.
- **O viés do `custo` cheio continua inteiro**, agora medido: 14 etapas em que a
  sugestão nomeia o material gratuito tendo o estudante já pago pelo outro. Fica em
  aberto até a ADR seguinte, e é o preço explícito de não embutir posse aqui.
- **Leitor antigo de log novo ignora o fato em silêncio.** `evento_de_dados` devolve
  `None` para tipo desconhecido e `_de_linha` descarta a linha
  ([`repositorio.py`](../../src/trilhas/percurso/repositorio.py)) — tolerância que
  existe para log pela metade e que aqui significa que uma versão anterior do código lê
  o log sem ver os fatos de recurso, sem erro.
- **A camada web não mostra o fato.** `montar_percurso` projeta competência, progresso e
  feedback, e nada disso muda; a tela continua correta e cega para o novo fato. Mostrá-lo
  é trabalho de [interface.md](../interface.md), não desta ADR.
- **`migrar.py` não muda**: o YAML de percurso nunca declarou fato de recurso, então não
  há o que importar — e sintetizar um a partir de `recurso_em_uso` seria inventar
  história, o que a migração de ADR-0008 já recusa fazer com evidência.
