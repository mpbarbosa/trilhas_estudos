# ADR-0002 — Trilha é um grafo de etapas com pré-requisitos por competência

- **Data**: 2026-10-08
- **Status**: aceito

## Contexto

A representação óbvia de uma trilha de estudos é uma lista ordenada de itens — é
como trilhas são apresentadas ao estudante. Mas o sistema precisa **sugerir**, e uma
lista linear reduz a sugestão a "o próximo item ainda não marcado", o que não
aproveita conhecimento prévio, não permite caminhos alternativos e não reconhece
competências adquiridas em outra trilha ou fora do sistema.

Duas formas de dependência foram consideradas: etapa → etapa, e etapa → competência.

## Decisão

Trilha é um **grafo direcionado acíclico** de etapas. A dependência é declarada
sempre como **etapa requer competência em nível mínimo**, nunca etapa requer etapa.
A ordem de estudo é derivada, não armazenada.

## Consequências

- Competências adquiridas em qualquer origem destravam etapas, incluindo etapas de
  outras trilhas — o catálogo deixa de duplicar conhecimento.
- Existem caminhos paralelos; "a próxima etapa" passa a ser um conjunto (a fronteira
  do grafo) que o motor precisa ordenar. É isso que torna o motor necessário.
- O catálogo exige validação de aciclicidade e de que toda competência exigida seja
  desenvolvida por alguma etapa, ou o estudante encontra beco sem saída.
- Apresentar uma trilha como lista para o estudante passa a ser uma **linearização**
  do grafo (ordem topológica), decisão de interface, não de modelo.
- Custo: modelagem e autoria de catálogo mais trabalhosas que uma lista.
