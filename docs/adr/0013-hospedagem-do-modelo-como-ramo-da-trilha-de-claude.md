# ADR-0013 — Hospedagem do modelo como ramo opcional da trilha de Claude

- **Data**: 2026-10-18
- **Status**: aceito

## Contexto

O estudante começou a estudar a página oficial *Claude no Amazon Bedrock*:
autenticação da AWS por função de serviço, função assumida do IAM ou token de curta
duração; SDK com sufixo de Bedrock; id de modelo com prefixo `anthropic.`; endpoint
global e endpoint regional, com acréscimo de preço no segundo; cota em tokens por
minuto; retenção de dados regida pela AWS; log de atividade no CloudWatch e no
CloudTrail. O catálogo não tinha onde pôr isso, e o recurso entrou pendurado em
`etapa:ia/claude-api-e-sdk` — a etapa da API por dentro: mensagens, streaming, cache
e custo.

O encaixe era apertado, e a `verificacao` é o que permite dizer isso sem recorrer a
gosto. Recurso é "material concreto que **realiza** uma etapa"
([CONTEXT §1](../CONTEXT.md)). A etapa de API concede `comp:ia/uso-de-llm-por-api` no
nível avançado, e a verificação dessa competência cobra uma chamada que devolva JSON
conforme esquema, com temperatura e limite de tokens controlados, mais a estimativa de
custo por mil chamadas. Nada disso se verifica lendo sobre `iam:PassRole`, residência
de dados ou cota por região. O recurso ensinava mais do que a etapa cobra, e o
excedente ficava **invisível ao modelo**: nenhuma competência o declarava, nenhuma
evidência o registraria, nenhuma sugestão poderia citá-lo.

Daí o teste que separa os dois casos, e que vale como regra de autoria: **se o
material cabe na `verificacao` da competência que a etapa concede, é recurso; se
ensina o que nenhuma `verificacao` do catálogo cobra, falta etapa.** Aqui faltava.
É **assunto ausente** — o caso de
[ADR-0011](0011-python-no-servidor-como-ramo-da-trilha-web.md) —, não pré-requisito
implícito, que é o de
[ADR-0010](0010-shell-como-pre-requisito-declarado.md): nenhuma etapa desta trilha
pressupõe plataforma de nuvem, e o estudante não travava por falta dela.

Quatro formas foram consideradas:

1. **Recurso da etapa de API** — o estado de hoje, que é o que está em questão.
2. **Etapa nova dentro de `trilha:ia/claude-do-chat-ao-agente`**.
3. **Etapa avulsa** em `catalogo/etapas/avulsas.yaml`.
4. **Trilha nova** de operação de LLM em nuvem.

A (3) tropeça no cabeçalho do próprio arquivo, que reserva `avulsas.yaml` às etapas
referenciadas por **mais de uma** trilha: só esta tem razão de carregar hospedagem de
Claude hoje, e etapa avulsa com um referenciador só é a etapa de uma trilha escrita no
arquivo errado — o argumento de ADR-0011.

A (4) é decisão de **escopo**, e uma competência não a sustenta. Uma trilha tem
objetivo declarado e matrícula própria ([CONTEXT §1](../CONTEXT.md)); "operar LLM em
nuvem" com uma etapa dentro é objetivo que se satisfaz na primeira etapa. O que
sustentaria a trilha seria a cadeia inteira — Microsoft Foundry, throughput
provisionado, rede privada, conformidade e auditoria —, e nada disso está decidido.
Se esses ramos crescerem, a trilha nasce **referenciando** esta etapa, sem recriá-la,
porque o id é imutável
([ADR-0005](0005-identidade-imutavel-e-depreciacao.md)).

## Decisão

**Uma etapa nova, opcional, dentro de `trilha:ia/claude-do-chat-ao-agente`** — a
opção (2):

| Entidade | Papel |
|---|---|
| `comp:ia/hospedagem-de-modelo-em-nuvem` | a competência que faltava |
| `etapa:ia/claude-em-plataforma-de-nuvem` | `opcional: true`; ramo depois da etapa de API |
| `rec:ia/claude-docs-bedrock` | muda de etapa; `rev` 1 → 2 |
| `rec:ia/claude-docs-google-cloud` | novo |
| `rec:ia/claude-docs-recursos-por-plataforma` | novo |

**Competência nova, e não `comp:ia/operacao-de-aplicacoes-llm` ampliada.** Três saídas
foram pesadas, e a que parecia mais barata é a única proibida:

- **Reusar como está** faria a etapa conceder uma competência cuja `verificacao` cobra
  custo por requisição, latência p95 e salvaguarda de saída demonstrada — coisas que a
  etapa nova não ensina. A evidência emitida não se sustentaria, e é exatamente o que
  `verificacao` existe para impedir ([catalogo.md §2](../catalogo.md)).
- **Ampliar só a `descricao`** é cosmético pela tabela de `rev`, e é o pior dos três
  justamente por isso: `descricao` e `verificacao` passariam a descrever competências
  diferentes, sem que nada no catálogo registrasse a divergência.
- **Reescrever a `verificacao`** para caber as duas coisas sobe a `rev` (substantivo),
  e aí aparece o impedimento real: `EvidenciaRegistrada` grava `competencia`, `nivel`,
  `origem` e `(etapa, etapa_rev)` — **não** grava a `rev` da competência
  (`src/trilhas/percurso/eventos.py`). Mudar o critério redefiniria, em silêncio, o
  que toda evidência já emitida sobre ela afirma. É o oposto de "fato datado não
  retroage" ([catalogo.md §4](../catalogo.md)), e o percurso não tem como se defender
  disso. Competência com critério reescrito é competência nova.

A nova é **irmã** da de operação e distinta dela no objeto: lá, a aplicação
instrumentada; aqui, **onde o modelo é servido** — de quem é o limite de segurança,
qual credencial entra, em que região o dado fica, o que a plataforma deixa de
oferecer. Nenhuma dessas quatro se mede em p95.

**`opcional: true` não é hesitação, é o modelo.** Os três objetivos declarados da
trilha são `comp:ia/ferramentas-e-mcp` e `comp:ia/desenvolvimento-assistido-por-ia` em
intermediário e `comp:ia/agentes-llm` em avançado. Nenhum exige hospedagem: quem leva
o agente até o fim pela API da Anthropic não passa por Bedrock nem por Google Cloud, e
é isso que `opcional` significa aqui. A consequência de percurso vem de graça — etapa
opcional acrescentada é **cosmética** para a trilha
([catalogo.md §4](../catalogo.md)), então a `rev` da trilha fica em 1 e as oito etapas
que `est:mpb` já concluiu nesta trilha não são tocadas. Obrigatória, a etapa reabriria
uma trilha concluída por causa de um assunto que o estudante apenas começou a ler;
reabertura é o comportamento correto quando o **objetivo** da trilha muda, e ele não
mudou.

**Três recursos, todos documentação oficial com tradução em pt-BR e gratuitos.** O do
Bedrock, que muda de casa; o do Google Cloud, onde o modelo vai na URL do endpoint e
há endpoint global, multirregional e regional; e a visão geral de recursos, que é a
única tabela onde se lê, de uma vez, o que cada hospedagem **não** oferece — é ela que
sustenta a parte de paridade da `verificacao`. O Claude Platform on AWS é nomeado pela
`verificacao` como alternativa aceitável e não tem recurso próprio: a `verificacao`
cobra uma escolha, não uma lista de leitura, e acrescentar a página é autoria futura,
não decisão.

**`etapa` de recurso é campo substantivo** — a tabela de `rev` de
[catalogo.md §4](../catalogo.md) não dizia nada sobre ele, e esta mudança precisou
dele. É substantivo pelo que decide: a `etapa` é a casa do recurso; re-encaixá-lo muda
o que a etapa de origem oferece ao estudante e pode tirar dela o último recurso, que é
erro de compilação (validação 5). A tabela foi corrigida, e `rec:ia/claude-docs-bedrock`
vai a `rev: 2`. A `rev` de etapa nenhuma muda — recurso nunca altera `rev` de etapa.

## Consequências

- **O assunto passa a existir para o motor.** Antes, hospedagem era texto dentro de um
  recurso; agora é etapa sugerível, com competência que a evidência pode registrar.
  Nada em `src/trilhas/motor/` lê `opcional` — o campo decide conclusão de trilha e
  apresentação, não candidatura —, então a etapa concorre como qualquer outra.
- **Uma única `rev` subiu**, a do recurso movido. Competência, etapa e dois recursos
  nasceram; trilha, etapas existentes e demais recursos ficaram onde estavam.
- **O log de percurso guarda um `etapa_iniciada` de `etapa:ia/claude-api-e-sdk` que
  cita `rec:ia/claude-docs-bedrock`**, gravado antes desta decisão. Ele fica como está:
  o catálogo é consultado na escrita e a projeção nunca o reconsulta
  ([ADR-0008](0008-percurso-como-log-de-fatos-datados.md)). Quem reler aquele evento
  verá um recurso que hoje mora noutra etapa — é o preço de corrigir o encaixe, e é
  menor que o de reescrever o log, que o gatilho proíbe.
- **A competência nova é folha**: desenvolvida por uma etapa e exigida por nenhuma,
  como `comp:web/python-no-servidor` depois de ADR-0011. A validação 4 cobra o inverso
  — competência exigida e não ensinada —, então isso é legítimo e permanece visível no
  catálogo.
- **O objetivo declarado da trilha não mudou.** Se um dia hospedagem virar parte do
  objetivo, a etapa vira obrigatória, a `rev` da trilha sobe e a trilha reabre para
  quem a concluiu. Essa é outra decisão, e esta ADR não a toma.
- **A etapa exige conta em nuvem.** Os três recursos são gratuitos e `custo: 0` está
  correto — `custo` é do material —, mas o exercício que a `verificacao` cobra consome
  um projeto na AWS ou no Google Cloud. O catálogo não modela custo de execução, e o
  filtro de `custo_maximo` do motor ([motor §2.2](../motor-de-sugestao.md)) não vai
  avisar o estudante disso.
- **Fica aberto** se Microsoft Foundry e Claude Platform on AWS merecem recurso próprio
  nesta etapa, e se a distinção entre plataforma operada pelo provedor e plataforma
  operada pela Anthropic na nuvem dele é conteúdo de etapa ou de trilha. A `verificacao`
  aceita as duas hoje; se a diferença virar conteúdo, é etapa nova, não ampliação desta.
