# ADR-0005 — Identidade imutável, revisão por entidade e depreciação em vez de remoção

- **Data**: 2026-10-08
- **Status**: aceito

## Contexto

Percurso (progresso, evidência, sugestões emitidas) referencia catálogo. O catálogo
muda com frequência: correções de texto, troca de material, reorganização de
pré-requisitos, divisão de uma etapa em duas. Era preciso decidir o que o percurso
guarda e o que acontece quando o alvo da referência muda.

[CONTEXT.md §3.5](../CONTEXT.md) já exigia que progresso histórico preservasse a
versão concluída, e o motor exige que uma sugestão antiga seja reproduzível. Faltava
o mecanismo.

Opções de versionamento consideradas:

1. **Commit SHA do catálogo** na referência — exato, mas opaco ao leitor e acopla o
   percurso ao git.
2. **Versão única do catálogo inteiro** — simples, mas qualquer correção de vírgula
   "invalida" todas as conclusões anteriores.
3. **`rev` por entidade**, incrementada apenas em mudança substantiva.

## Decisão

- Opção 3: cada entidade tem `rev` monotônica, que sobe só em mudança substantiva,
  com a classificação substantivo/cosmético fixada em [catalogo.md §4](../catalogo.md).
  Progresso grava `(etapa_id, rev)`.
- Ids têm formato `<tipo>:<area>/<slug>`, são **imutáveis** e **nunca reaproveitados**.
  Renomear título não muda id; corrigir slug é criar entidade nova e depreciar a antiga.
- Nada é removido do catálogo. O ciclo é `rascunho → ativo → depreciado`, com
  `substituido_por` quando houver sucessor.
- Princípio para efeitos retroativos: **fato datado não retroage.** Alterar `teaches`
  não concede nem retira competência de quem já tem evidência emitida; endurecer
  `requires` não re-trava etapa em andamento ou concluída. A tabela de efeitos está
  em [catalogo.md §4](../catalogo.md).
- `catalogo_versao` (inteiro monotônico do catálogo inteiro) existe apenas para que
  cada `Sugestao` registre a versão que a produziu, viabilizando reprodução.

## Consequências

- Correções de texto no catálogo não geram ruído no histórico dos estudantes, porque
  não mexem em `rev`.
- A classificação substantivo/cosmético é um julgamento humano e pode ser aplicada
  errado; a validação só garante que `rev` não decresce. Mitigação: revisão em PR.
- Como nada é removido, o catálogo cresce monotonicamente e acumula entidades
  depreciadas. Aceito: o motor as filtra, e o custo é armazenamento.
- "Fato datado não retroage" implica que dois estudantes com a mesma trajetória
  podem ter competências diferentes se estudaram sob `rev` diferentes. É a
  consequência correta — e é auditável, porque o `rev` está gravado.
- Adicionar etapa obrigatória a uma trilha reabre trilhas já concluídas. Exige
  notificar o estudante com o motivo, ou a mudança parece arbitrária.
