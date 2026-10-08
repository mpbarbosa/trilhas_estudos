# ADR-0003 — Motor de sugestão por regras com score explicável (v1)

- **Data**: 2026-10-08
- **Status**: aceito

## Contexto

O motor pode ser construído como regras determinísticas, como modelo de
aprendizado de máquina (filtragem colaborativa ou ranking aprendido), ou híbrido.
No início não há usuários, não há histórico de feedback e não há catálogo —
portanto não há dado para treinar nem para avaliar um modelo. Além disso, o
estudante precisa poder discordar de uma sugestão com fundamento, e quem mantém o
catálogo precisa entender por que uma etapa não apareceu.

## Decisão

A v1 é determinística: candidatos → filtros duros → soma ponderada de fatores
nomeados → top-N. Cada sugestão persiste os fatores e suas contribuições, e a
explicação textual é **gerada a partir desses fatores**. Pesos ficam em
configuração, não no código. Candidatos eliminados por filtro duro registram o
motivo da eliminação.

## Consequências

- Mesma entrada produz sempre a mesma saída — testável por cenários de catálogo fixo.
- Os pesos iniciais são um palpite declarado; a calibração depende de uso real e é
  trabalho futuro, não parte da v1.
- O registro de `fatores` e de motivos de eliminação cria o conjunto de dados que um
  modelo futuro precisaria. A decisão de usar ML fica **habilitada**, não tomada, e
  exigirá nova ADR com critério de avaliação definido antes do treino.
- Custo: regras escritas à mão envelhecem e precisam de manutenção; sem a calibração
  os pesos podem produzir ordenações ruins em catálogos grandes.
