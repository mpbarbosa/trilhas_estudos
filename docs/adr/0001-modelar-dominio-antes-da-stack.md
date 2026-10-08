# ADR-0001 — Modelar o domínio antes de escolher a stack

- **Data**: 2026-10-08
- **Status**: aceito

## Contexto

O repositório estava vazio (README + LICENSE). O propósito do sistema — controlar e
sugerir trilhas de estudo — admite implementações muito diferentes (CLI local, API,
app full-stack), e a primeira capacidade escolhida foi o motor de sugestão, cujo
valor está na lógica de domínio e não na camada de entrega.

## Decisão

Produzir primeiro o modelo de domínio e a especificação do motor de sugestão
([CONTEXT.md](../CONTEXT.md), [motor-de-sugestao.md](../motor-de-sugestao.md)),
sem escolher linguagem, framework ou banco.

## Consequências

- O motor de sugestão deve ser projetado como lógica pura: entrada = estado do
  estudante + catálogo, saída = sugestões. Sem I/O, sem framework.
- A escolha de stack torna-se uma decisão de entrega, reversível, e será registrada
  em ADR própria.
- Custo: nada executável a curto prazo; a especificação só se valida quando houver
  os cenários de teste da §5 do motor.
