# ADR-0006 — Stack: Python, domínio puro, CLI como primeira entrega

- **Data**: 2026-10-08
- **Status**: aceito

## Contexto

[ADR-0001](0001-modelar-dominio-antes-da-stack.md) adiou a escolha de stack até a
modelagem existir. Ela existe, e a ordem de construção implicada
([docs/README.md](../README.md)) põe o **compilador/validador de catálogo** como
primeiro executável — antes do motor, que sem ele não tem entrada.

Isso define os requisitos reais da escolha, em ordem de peso:

1. **Grafos**: fecho de alcançabilidade sobre o grafo de pré-requisitos
   (validações 3, 4 e 6 de [catalogo.md §5](../catalogo.md)).
2. **YAML** com erros de forma localizáveis (arquivo e linha).
3. **Lógica pura testável por cenário**: os 7 cenários de [motor §5](../motor-de-sugestao.md)
   exigem determinismo e entrada/saída de dados, sem I/O nem framework.
4. **Relatório de erro legível em CI**.
5. Porta aberta para calibração estatística dos pesos e, muito depois, ML
   ([ADR-0003](0003-motor-de-sugestao-por-regras-explicavel.md)).

A camada de entrega (API, web) **não** é requisito desta fase e não deve pesar na decisão.

## Decisão

**Python 3.12+**, com domínio puro e CLI como única entrega inicial.

- Algoritmos de grafo sobre estruturas da stdlib, sem dependência externa.
- `dataclasses` congeladas para o modelo; o catálogo é dado imutável.
- Dependência de runtime: **PyYAML**, e nada mais.
- Desenvolvimento: `pytest`, `ruff`, `mypy`; gerenciamento com `uv`.
- Estrutura: `src/trilhas/catalogo/` (carregar → validar → compilar) e
  `src/trilhas/motor/` depois. Nenhum módulo de domínio importa I/O ou CLI.

Descartado **TypeScript/Next.js**: entregaria a camada de entrega que não é requisito
agora, e pagaria em algoritmo de grafo escrito à mão o que a stdlib do Python já dá.
Revisitável quando houver interface — o snapshot `catalogo.lock.json` é a fronteira,
e uma UI em outra linguagem pode consumi-lo sem tocar no domínio.

## Nota de correção (2026-10-08)

A primeira redação justificava a escolha por `graphlib.TopologicalSorter`. Na
implementação, ordenação topológica mostrou-se a ferramenta **errada**: como uma
competência pode ser desenvolvida em vários níveis por etapas distintas, o grafo
"etapa depende de quem ensina o que ela exige" tem arestas nos dois sentidos entre
etapas perfeitamente ordenadas, e acusa ciclo onde não há. A verificação correta é
fecho progressivo a partir de perfil vazio ([catalogo.md §5.3](../catalogo.md)).
`graphlib` não é usado. A decisão pela stack não muda — o peso real está em
dataclasses, tipagem e lógica pura testável.

## Consequências

- O validador sai com uma dependência só, e o domínio permanece testável sem rede,
  banco ou servidor.
- Tipagem é opcional em Python: sem `mypy` em CI o modelo congelado não se sustenta
  sozinho. `mypy --strict` sobre `src/trilhas/` passa a ser condição de merge.
- Distribuição para usuário final não está resolvida — CLI em Python exige ambiente
  Python. Irrelevante enquanto o público é quem autora catálogo.
- Se a interface web vier a ser Next.js, haverá duas linguagens no repositório. O
  snapshot limita o atrito à fronteira de dados, mas o custo existe e é aceito.
