# ADR-0008 — Percurso como log append-only de fatos datados, perfil derivado

- **Data**: 2026-10-13
- **Status**: aceito

## Contexto

O catálogo tem forma decidida ([ADR-0004](0004-catalogo-em-yaml-compilado-para-snapshot.md))
e o motor de sugestão existe como lógica pura. O percurso, não: `percurso/*.yaml`
avisa de si mesmo que é provisório, e `web/percurso.py` **lê e nunca escreve**. O laço
do [motor §2](../motor-de-sugestao.md) — feedback alimentando o estado — está aberto:
não há como concluir etapa, registrar evidência ou reagir a uma sugestão.

O modelo já impõe três restrições que qualquer persistência tem de honrar:

1. **Toda `CompetenciaDominada` tem ao menos uma `Evidencia`** ([CONTEXT §4](../CONTEXT.md)).
   Num YAML editável, `competencias_dominadas` é um campo que alguém pode preencher
   à mão — a invariante vale por disciplina, e disciplina não é garantia.
2. **Fato datado não retroage** ([catalogo.md §4](../catalogo.md)). Mudar o `teaches`
   de uma etapa não concede nem retira competência de quem já tem evidência emitida.
3. **Toda `Sugestao` é reproduzível**: persiste os fatores e a `catalogo_versao`.

`Evidencia`, `Progresso`, `Sugestao` e `Feedback` são as quatro entidades de percurso
que **acontecem num instante**. As demais — perfil, restrições, objetivo, matrícula —
são estado declarado, que o estudante edita.

## Decisão

Separar o percurso em duas naturezas, e persistir cada uma conforme o que ela é.

**Fatos datados vão para um log append-only em SQLite** (`sqlite3` da stdlib, sem
dependência nova — [ADR-0006](0006-stack-python.md) continua com `pyyaml` e nada mais
em runtime). Uma tabela, ordem total por `seq`, e `UPDATE`/`DELETE` bloqueados por
*trigger*: o log só cresce, e isso é imposto pelo banco, não pela convenção.

**Estado declarado continua em YAML** — perfil, restrições, objetivo e matrícula
seguem legíveis, versionáveis em git, exportáveis e editáveis à mão, como hoje.

**`competencias_dominadas` deixa de ser campo e passa a ser projeção** do log: nível é
o máximo evidenciado, e a data é a da evidência mais recente que sustenta esse nível.
Com isso a invariante 1 passa a valer **por construção** — não existe caminho no código
que produza competência dominada sem evidência que a origine.

**Concluir etapa emite dois fatos**, não um: a conclusão e a evidência do que aquela
etapa ensinava **naquele momento**, com a `rev` da etapa. É aqui que o catálogo é
consultado — na escrita, uma vez. A projeção nunca reconsulta `teaches`, e é isso que
faz a invariante 2 valer por construção em vez de depender de ninguém recalcular.

## Consequências

- O laço do motor fecha: ação do estudante vira evento, evento vira projeção, projeção
  é a entrada do motor. Nada no caminho precisa reescrever história.
- Auditoria sai de graça: o log responde "por que o sistema acha que eu sei isso" com
  a evidência datada, e "o que foi sugerido e com quais fatores" com a sugestão emitida.
- **Corrigir um erro passa a ser escrever outro evento**, nunca editar. Marcar uma
  evidência como equivocada exige um fato de retratação; não está nesta ADR e será
  necessário na primeira vez que alguém clicar errado.
- O banco é estado local e fica fora do git. O histórico durável e inspecionável em
  `git diff` é a exportação em JSONL (`trilhas-percurso exportar`), uma linha por
  fato. **Reconstruir o banco a partir dela não está implementado**: é cópia de
  auditoria, não segunda fonte da verdade — e isso precisa existir antes de alguém
  depender da exportação como backup.
- A exportação é instantâneo e envelhece em silêncio a cada fato novo.
  `trilhas-percurso exportar --conferir` acusa isso, como `trilhas compilar --conferir`
  faz pelo catálogo — mas, ao contrário dele, **não pode entrar no CI**: o banco é
  local e está fora do git, então no runner não existe log com que comparar. É
  verificação da máquina de quem estuda, e isso é consequência direta de manter o
  banco fora do versionamento.
- Adotar o log sem migrar o YAML apagaria o progresso já declarado nele.
  `percurso/migrar.py` converte os fatos declarados preservando **as datas de lá**, e
  a importação recusa rodar duas vezes. Uma etapa já concluída não gera evidência na
  migração: sintetizá-la a partir do `teaches` de hoje seria exatamente o que esta
  ADR proíbe.
- Duas fontes para um percurso (YAML + banco) significa que um pode existir sem o
  outro. A projeção trata log vazio como percurso sem fatos, não como erro — é o
  caso do estudante novo, que o motor já sabe responder ([motor §4](../motor-de-sugestao.md)).
- SQLite é arquivo local e serializa escrita por transação. Suficiente para um
  estudante por vez; decisão a revisitar se houver concorrência real de escrita.
- `percurso/*.yaml` perde o aviso de "formato provisório" na parte que esta ADR
  decide, e o mantém no que ela não decide.
