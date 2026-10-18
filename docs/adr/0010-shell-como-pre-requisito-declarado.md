# ADR-0010 — Shell como pré-requisito declarado, em etapa avulsa compartilhada

- **Data**: 2026-10-17
- **Status**: aceito

## Contexto

[docs/acervo-lido.md § 3.1](../acervo-lido.md) apontou que nenhuma etapa do catálogo
tratava linha de comando, shell ou automação por script. O mais próximo,
`etapa:programacao/c-interface-com-o-unix`, é a API do UNIX vista do C (`read`,
`write`, `open`, `lseek`) — o sistema por baixo da biblioteca padrão, não a casca por
cima dele.

A lacuna não é de assunto ausente; é de **pré-requisito implícito**. Duas trilhas
ativas pressupõem a casca e não a declaram:

- `trilha:so/projeto-e-implementacao` manda compilar e modificar o MINIX em máquina
  virtual (`rec:so/minix3-projeto`, em `etapa:so/projeto-modificar-o-minix`);
- `trilha:programacao/linguagem-c-ansi` supõe compilação separada e `make` a partir
  de `etapa:programacao/c-funcoes-e-estrutura-de-programa`, cuja verificação pede
  "compilar e ligar à mão".

Quem não domina shell não era barrado por nenhum `requires` — travava no projeto, sem
que o catálogo soubesse dizer por quê. É exatamente o caso que o modelo de
competências existe para tornar explícito ([CONTEXT.md §3.2](../CONTEXT.md):
pré-requisito é sempre entre etapa e competência).

Três formas foram consideradas:

1. **Etapa avulsa** em `catalogo/etapas/avulsas.yaml`, referenciada pelas trilhas que
   a pressupõem.
2. **Trilha nova** de fundamentos de ambiente UNIX — shell, ferramentas de texto,
   `make`, automação —, com a etapa de shell dentro.
3. **Etapa dentro de uma trilha existente**, provavelmente a de C.

A (3) põe a mesma etapa na trilha de C e deixa a de SO sem ela, ou força a segunda a
redefinir o que a primeira já define — o que a validação 1 pega como id duplicado.
A (2) é uma decisão de **escopo**, não de catalogação: nada no acervo lido sustenta
que a área mereça objetivo próprio e matrícula própria. O relatório trouxe dois
livros; dois livros não são semente de trilha.

## Decisão

**Duas etapas avulsas**, definidas em `catalogo/etapas/avulsas.yaml` e referenciadas
pelas trilhas que as pressupõem:

| Etapa | Competência | Papel |
|---|---|---|
| `etapa:so/linha-de-comando` | `comp:so/linha-de-comando` | obrigatória; o pré-requisito |
| `etapa:so/script-shell` | `comp:so/script-shell` | `opcional: true`; aprofundamento |

E o pré-requisito passa a ser **declarado**, com `rev` subindo nas quatro entidades
afetadas:

- `comp:so/linha-de-comando` entra nos `requires` de
  `etapa:so/projeto-modificar-o-minix` e de
  `etapa:programacao/c-funcoes-e-estrutura-de-programa` — as duas vão a `rev: 2`;
- as duas trilhas passam a `rev: 2` por referenciarem uma etapa obrigatória nova
  ([catalogo.md §4](../catalogo.md)).

Por que **duas** etapas e não uma: só a primeira é pré-requisito daquelas trilhas.
Compilar o MINIX e ligar C à mão cobram fluência de linha de comando, não a escrita de
script portável — unir as duas numa competência só exigiria mais do que o projeto
cobra, e a precisão é justamente o ganho de tornar o pré-requisito explícito. A
segunda etapa fica no papel que `etapa:programacao/pratica-da-programacao` já tem na
trilha de C: aprofundamento opcional fora do objetivo declarado.

Por que na área `so`: a casca é a interface do sistema operacional com quem o usa.
`area` é organizacional, não semântica ([catalogo.md §3](../catalogo.md)), e é por isso
que uma competência de `so/` pode ser pré-requisito de uma etapa de `programacao/`.

## Consequências

- **Etapa `nao_iniciada` volta a travar**, nas duas trilhas, até que a competência de
  linha de comando tenha evidência. É o comportamento previsto pela tabela de
  [catalogo.md §4](../catalogo.md) para `requires` mais exigente, e é o efeito
  pretendido: o travamento passa a ser visível e explicado, em vez de acontecer na
  cadeira do estudante. Nenhuma trilha concluída reabre, porque nenhuma está
  concluída no percurso de hoje.
- **Referenciar não é decoração.** O motor gera `proxima_etapa` só a partir das etapas
  da trilha matriculada, `etapas_referenciadas` incluídas
  ([motor §2.1](../motor-de-sugestao.md)). Sem a referência, a etapa nova ficaria
  órfã (aviso da validação 11), alcançável apenas por `exploracao` — que exige que a
  competência esteja no objetivo declarado. O estudante travaria no projeto **e** não
  receberia a etapa que o destrava. É a referência, não o `requires`, que fecha o
  caminho.
- **A trilha de C não referencia a etapa de script.** Escrever script não é
  pré-requisito de compilar C, e referenciá-la ali a incluiria na trilha sem razão.
- **O acervo lido entra, com limite declarado.** *Shell Script Profissional* (Jargas)
  é recurso da etapa de script, não da de linha de comando: é livro sobre escrever
  script que se mantenha, e pressupõe a casca em vez de ensiná-la. Com isso
  `etapa:so/linha-de-comando` fica **sem recurso pago em pt-BR** — serviço de um
  gratuito pt-BR (Guia Foca, parado desde 2020) e de dois en-US. Registrado em
  comentário no YAML, não aqui.
- **Fica aberto o que esta ADR não decide**: se a área merece trilha própria —
  ferramentas de texto, `make`, automação de build. Se merecer, a trilha nasce
  **referenciando** estas duas etapas, sem recriá-las, porque o id é imutável
  ([ADR-0005](0005-identidade-imutavel-e-depreciacao.md)) e `etapas_referenciadas`
  existe para isso. Esta decisão é o caminho de migração, não um obstáculo.
- **Custo**: duas competências e duas etapas a manter, e quatro `rev` que sobem de uma
  vez. Em troca, um pré-requisito que o catálogo afirmava por omissão passa a ser
  dado do modelo, conferível pela validação 4 e pelo motor.
