---
description: Escreve a próxima ADR no formato do repositório e a registra no índice
argument-hint: <decisão a registrar>
---

Registre esta decisão como ADR: **$ARGUMENTS**

1. Leia duas ADRs existentes em `docs/adr/` para pegar o tom: contexto que expõe os
   requisitos em ordem de peso, decisão curta, alternativas descartadas **com o
   motivo**, consequências incluindo as ruins e aceitas.
2. Numere na sequência (`docs/adr/000N-<slug>.md`), com `**Data**` e
   `**Status**: aceito`.
3. Acrescente a linha na tabela de ADRs de `docs/README.md`.
4. Se a decisão contradiz uma ADR aceita, **não edite a antiga**: escreva a nova
   referenciando-a, ou acrescente à antiga uma "Nota de correção" como a de
   ADR-0006 — o histórico de decisão não se reescreve.

Se eu te pedir para registrar algo que ainda não é uma decisão (não há alternativa
descartada, ou o motivo é "parece melhor"), diga isso em vez de escrever a ADR.
