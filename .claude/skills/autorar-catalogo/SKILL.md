---
name: autorar-catalogo
description: Procedimento para autorar ou alterar o catálogo de trilhas_estudos — criar trilha, etapa, competência ou recurso em YAML, escolher ids, decidir se `rev` sobe, e fazer a compilação passar nas 12 validações. Use ao criar ou editar qualquer arquivo em catalogo/, ao depreciar uma entidade, ou quando `trilhas validar` falha.
---

# Autorar catálogo

O esquema, a tabela de `rev` e as 12 validações estão em
[docs/catalogo.md](../../../docs/catalogo.md) — leia a seção citada em cada passo em
vez de confiar na memória. Esta skill é o **procedimento** e os erros que ele evita.

## 1. Antes de escrever

- `uv run trilhas validar` para começar de um catálogo verde. Se já está vermelho,
  resolva isso primeiro ou saiba que a falha não é sua.
- Decida **o objetivo da trilha em competências**, não em assuntos. Uma trilha sem
  `objetivo_declarado` verificável não passa na validação 6.
- Para cada competência nova: escreva `verificacao` antes do `titulo`. Se não
  consegue descrever como se verifica, não é uma competência — é um assunto, e
  provavelmente deve ser uma etapa ou se dissolver em outras competências.

## 2. Onde cada coisa mora

| O quê | Arquivo |
|---|---|
| Competência | `catalogo/competencias/<area>.yaml` |
| Trilha + as etapas que ela **introduz** | `catalogo/trilhas/<slug>.yaml` |
| Etapa que não nasce de uma trilha | `catalogo/etapas/avulsas.yaml` |
| Recurso | `catalogo/recursos/<area>.yaml` |

Uma etapa é definida em **exatamente um** arquivo. Outra trilha que precise dela usa
`etapas_referenciadas: [etapa:...]`. Redefinir a mesma etapa em duas trilhas é o erro
mais fácil de cometer aqui e a validação 1 o pega como id duplicado.

## 3. Ids

`<tipo>:<area>/<slug>` — `comp:`, `etapa:`, `trilha:`, `rec:`. Minúsculas, dígitos e
hífen; sem acento, sem `_`, sem maiúscula. `area` é organizacional: uma etapa de
`dados/` pode ensinar competência de `programacao/` — o acoplamento real está em
`requires`/`teaches`.

Id é imutável e nunca reaproveitado. **Nunca renomeie um id para corrigi-lo**: crie
o novo e deprecie o antigo (§6 de docs/catalogo.md), porque progresso, evidência e
sugestões históricas apontam para ids.

## 4. Escrever a trilha

Ordem que reduz retrabalho:

1. Competências (com `verificacao`) na área certa.
2. Etapas no arquivo da trilha, cada uma com `requires` e `teaches` em competências
   — nunca etapa→etapa. Confira que nenhum `nivel_resultante` é inferior a um
   `nivel_minimo` que a própria etapa exige da mesma competência (validação 7).
3. A primeira etapa de qualquer caminho precisa de `requires: []`, senão a trilha
   não parte de perfil vazio (validações 3 e 6).
4. **≥ 1 recurso ativo e disponível por etapa ativa** (validação 5) — etapa sem
   recurso bloqueia o snapshot. Preencha `verificado_em` com a data de hoje.
   Se o recurso é um capítulo de livro que outras etapas também usam, declare `obra`
   com o mesmo slug em todas as fatias e o mesmo `custo` — o do exemplar inteiro, que
   se compra uma vez (validação 12). Só você sabe o agrupamento no momento de
   escrever; depois ele não se recupera senão por adivinhação (ADR-0009).
5. Toda competência exigida por alguma etapa ativa tem de ser ensinada por alguma
   etapa ativa (validação 4) — inclusive as que você assumiu como "pré-requisito
   externo". Se vem de outra trilha, use `etapas_referenciadas`.

`uv run trilhas validar` após cada bloco, não só no fim: as mensagens de erro
nomeiam a entidade e o problema, e lotes grandes mascaram a causa.

## 5. Alterar algo que já existe

Consulte a tabela de docs/catalogo.md §4 e só então decida `rev`:

- Substantivo (sobe `rev`): `requires`, `teaches`, `opcional`, `status`,
  `objetivo_declarado`, incluir/remover etapa **obrigatória** de uma trilha,
  `esforco_estimado_min` com variação > 20%, e em recurso `status`, `disponivel`,
  `custo`, `obra`, `idioma`, `formato`.
- Cosmético (não sobe): `titulo`, `descricao`, ordem no arquivo, `verificado_em`,
  `url` para o mesmo material.

`rev` nunca decresce (validação 9). Mudança em recurso **nunca** altera a `rev` da
etapa — trocar o vídeo não muda o que a etapa ensina.

Antes de subir `rev`, leia a tabela de **efeito no percurso** (docs/catalogo.md §4):
adicionar etapa obrigatória reabre trilha já concluída, e `requires` mais exigente
re-trava etapa `nao_iniciada`. Isso é comportamento correto, mas tem de ser
intencional.

## 6. Depreciar

```yaml
- id: etapa:dados/sql-join
  status: depreciado
  substituido_por: etapa:dados/sql-join-v2
  depreciado_em: 2026-10-08
```

`substituido_por` é exigido pela validação 8 quando outra entidade ativa ainda aponta
para a depreciada. Nenhuma etapa ativa pode depender de competência ensinada apenas
por etapa depreciada.

## 7. Fechar

```bash
uv run trilhas validar     # 0 = válido
uv run trilhas compilar    # grava catalogo.lock.json
uv run pytest
```

Commite o YAML **e** o `catalogo.lock.json` no mesmo commit — o lock é gerado, nunca
editado à mão, e um lock defasado faz `compilar --conferir` falhar para a próxima
pessoa. Avisos (recurso verificado há mais de 180 dias, etapa órfã) não bloqueiam,
mas leia-os: etapa órfã só é alcançável por `exploracao`.

Se a trilha for nova, acrescente-a à lista do [README.md](../../../README.md) e à
tabela de `CLAUDE.md`.
