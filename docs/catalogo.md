# Catálogo — autoria, identidade e versionamento

O **catálogo** é a parte compartilhada e versionada do domínio: competências, etapas,
recursos e trilhas ([CONTEXT.md §3.5](CONTEXT.md)). Este documento fecha como ele é
escrito, identificado, validado e evoluído — e, principalmente, o que acontece com o
**percurso** do estudante quando o catálogo muda.

Decisões em [ADR-0004](adr/0004-catalogo-em-yaml-compilado-para-snapshot.md) e
[ADR-0005](adr/0005-identidade-imutavel-e-depreciacao.md).

---

## 1. Forma: YAML no repositório, compilado para snapshot

```
autoria (YAML, humano, em git)  →  validação  →  catalogo.lock.json (consumido)
```

A fonte da verdade são arquivos YAML revisáveis em pull request. O que a aplicação
carrega é um **snapshot compilado e validado** — nunca o YAML cru. Compilar resolve
referências, calcula o grafo e falha cedo em catálogo inválido (§5).

```
catalogo/
  competencias/
    dados.yaml                 # agrupadas por área
    programacao.yaml
  trilhas/
    fundamentos-dados.yaml     # trilha + as etapas que ela introduz
  etapas/
    avulsas.yaml               # etapas que não nascem de uma trilha
  recursos/
    dados.yaml                 # separado: ciclo de vida próprio (§4)
catalogo.lock.json             # gerado, commitado, nunca editado à mão
```

**Por que recursos em arquivo separado:** um link morre, um preço muda, um vídeo sai
do ar — eventos frequentes e sem significado pedagógico. Misturá-los às etapas faria
a etapa parecer alterada quando nada mudou no que ela ensina. É o que mantém a
regra de revisão da §4 honesta.

**Por que etapas moram na trilha que as introduz:** uma etapa é *definida* em exatamente
um arquivo. Outras trilhas a **referenciam** por id (`etapas_referenciadas`), nunca
redefinem. Sem isso o mesmo conteúdo divergiria entre trilhas.

---

## 2. Esquema

### Competência

```yaml
versao_schema: 1
competencias:
  - id: comp:dados/modelagem-relacional
    titulo: Modelagem relacional
    rev: 1
    status: ativo
    descricao: Traduzir requisitos em entidades, relações e chaves.
    verificacao: >
      Normalizar até 3FN um esquema dado em texto, justificando cada decomposição.
```

`verificacao` é **obrigatório**. Uma competência sem critério de verificação torna
toda `Evidencia` sobre ela indefensável, e a `confianca` da evidência vira um número
sem referência. É o campo que liga catálogo a percurso.

### Etapa

```yaml
trilha:
  id: trilha:fundamentos-dados
  titulo: Fundamentos de dados
  rev: 2
  status: ativo
  objetivo_declarado:
    - competencia: comp:dados/sql-consultas
      nivel: intermediario
  etapas:
    - id: etapa:dados/sql-select
      titulo: SELECT, WHERE e ORDER BY
      rev: 1
      status: ativo
      esforco_estimado_min: 60
      opcional: false
      requires: []
      teaches:
        - competencia: comp:dados/sql-consultas
          nivel_resultante: iniciante

    - id: etapa:dados/sql-join
      titulo: JOINs e relacionamentos
      rev: 3
      status: ativo
      esforco_estimado_min: 90
      opcional: false
      requires:
        - competencia: comp:dados/sql-consultas
          nivel_minimo: iniciante
        - competencia: comp:dados/modelagem-relacional
          nivel_minimo: iniciante
      teaches:
        - competencia: comp:dados/sql-consultas
          nivel_resultante: intermediario

  etapas_referenciadas:
    - etapa:programacao/logica-booleana
```

### Recurso

```yaml
versao_schema: 1
recursos:
  - id: rec:dados/sql-join-exercicios
    etapa: etapa:dados/sql-join
    titulo: 20 exercícios de JOIN com correção
    rev: 1
    status: ativo
    formato: exercicio          # video | texto | exercicio | projeto
    idioma: pt-BR
    custo: 0
    duracao_min: 45
    url: https://exemplo.invalid/sql-join
    disponivel: true
    verificado_em: 2026-10-08
```

`verificado_em` existe porque link morto é a falha mais comum de um catálogo de
estudos, e o motor filtra por `disponivel` (§2.2 do motor). Um recurso não verificado
há mais de 180 dias é reportado pela validação como aviso, não erro.

---

## 3. Identidade

Formato: `<tipo>:<area>/<slug>` — `comp:`, `etapa:`, `trilha:`, `rec:`.

- **O id é imutável.** Renomear o `titulo` não muda o id. Corrigir um slug é criar
  outra entidade e depreciar a anterior (§6).
- **O id nunca é reaproveitado**, mesmo depois de depreciado.
- `area` é organizacional, não semântica: uma etapa de `dados/` pode desenvolver
  competência de `programacao/`. O acoplamento real está em `requires`/`teaches`.

Motivo: progresso, evidência e sugestões históricas apontam para ids. Um id mutável
reescreveria o passado do estudante — e a invariante de reprodutibilidade das
sugestões ([motor §1](motor-de-sugestao.md)) cairia.

---

## 4. Revisão: o que conta como mudança substantiva

Cada entidade tem `rev`, inteiro monotônico. **`rev` sobe só em mudança substantiva.**

| Entidade | Substantivo (sobe `rev`) | Cosmético (não sobe) |
|---|---|---|
| Competência | `verificacao`, `status` | `titulo`, `descricao` |
| Etapa | `requires`, `teaches`, `opcional`, `status`, `esforco_estimado_min` com variação > 20% | `titulo`, ordem no arquivo, ajuste fino de esforço |
| Trilha | incluir/remover etapa **obrigatória**, `objetivo_declarado`, `status` | `titulo`, ordem de apresentação, etapa opcional |
| Recurso | `status`, `disponivel`, `custo`, `idioma`, `formato` | `titulo`, `verificado_em`, `url` que aponta ao mesmo material |

Mudança em recurso **nunca** altera a `rev` da etapa: trocar o vídeo não muda o que
a etapa ensina.

O progresso grava `(etapa_id, rev)` no momento da conclusão. Isso é o que permite
responder "o estudante concluiu *qual versão* desta etapa" sem versionar o catálogo
inteiro a cada correção de vírgula.

### Efeito de cada mudança no percurso já existente

Esta é a tabela que fecha o assunto. O princípio: **fato datado não retroage.**

| Mudança no catálogo | Efeito no percurso |
|---|---|
| `teaches` de uma etapa passa a conceder **mais** | Evidências já emitidas permanecem como estão. Ninguém ganha competência retroativamente — a evidência é um fato datado, não uma consequência recalculável. |
| `teaches` passa a conceder **menos** (ou nível menor) | Igual: evidências emitidas permanecem. A competência continua dominada, com a evidência antiga. |
| `requires` de uma etapa fica **mais exigente** | Etapa `nao_iniciada` pode voltar a travar — comportamento correto. Etapa `em_andamento` ou `concluida` **não** re-trava. |
| `requires` fica **menos** exigente | Etapas destravam normalmente na próxima sugestão. |
| Etapa obrigatória **adicionada** à trilha | Trilha antes concluída volta a `em_andamento`, e a etapa nova entra como `proxima_etapa`. O estudante é notificado do motivo. |
| Etapa obrigatória **removida** da trilha | Conclusão da trilha é recalculada; progresso da etapa removida é preservado e deixa de contar para a trilha. |
| Etapa **depreciada** | Sai de `proxima_etapa` e `exploracao`; continua válida para `retomada` (se em andamento) e `revisao`. |
| Competência **depreciada** | `requires` que a citam são ignorados na satisfação; `objetivo_declarado` que a citam exigem migração explícita (validação falha, §5.8). |
| Recurso indisponível | Etapa pode ser filtrada por falta de recurso ([motor §2.2](motor-de-sugestao.md)); se for a única via, a validação já teria falhado (§5.5). |
| `esforco_estimado_min` alterado | Afeta só sugestões futuras (fator `encaixe_de_esforco`). |

---

## 5. Validações da compilação

Erro bloqueia o snapshot. Aviso é reportado e permite compilar.

1. **Ids** únicos, no formato de §3, e nenhum reaproveitado em relação ao snapshot anterior — *erro*.
2. **Toda referência resolve** (`requires`, `teaches`, `etapa` de recurso, `etapas_referenciadas`) — *erro*.
3. **Aciclicidade** do grafo de pré-requisitos, por trilha e global — *erro*. Exigido por [ADR-0002](adr/0002-trilha-como-grafo-de-etapas.md).
4. **Sem beco sem saída**: toda competência exigida por alguma etapa ativa é desenvolvida por ao menos uma etapa ativa — *erro*.
5. **Toda etapa ativa tem ≥ 1 recurso** ativo e disponível — *erro*.
6. **Objetivo alcançável**: para cada trilha ativa, existe ordem topológica partindo de perfil vazio que satisfaz `objetivo_declarado` — *erro*. É esta validação que torna `sem_caminho_no_catalogo` ([motor §4](motor-de-sugestao.md)) um defeito de catálogo detectável em CI, e não uma surpresa para o estudante.
7. **Nível nunca rebaixa**: nenhum `nivel_resultante` é inferior a um `nivel_minimo` que a própria etapa exige da mesma competência — *erro*. Invariante de [CONTEXT.md §4](CONTEXT.md).
8. **Depreciação coerente**: nenhuma etapa ativa depende de competência desenvolvida apenas por etapa depreciada; nenhum `objetivo_declarado` ativo cita competência depreciada — *erro*.
9. **`rev` não decresce** em relação ao snapshot anterior — *erro*.
10. **Recurso verificado** há mais de 180 dias — *aviso*.
11. **Etapa órfã**: ativa, fora de qualquer trilha ativa e não referenciada — *aviso* (alcançável só por `exploracao`).

### Snapshot

```json
{
  "catalogo_versao": 7,
  "gerado_em": "2026-10-08T00:00:00Z",
  "hash": "sha256:…",
  "competencias": [], "etapas": [], "trilhas": [], "recursos": []
}
```

`catalogo_versao` é um inteiro monotônico do catálogo **inteiro**, usado para uma
coisa só: toda `Sugestao` persiste a versão que a produziu, de modo que uma sugestão
antiga seja reproduzível. Não é usada em progresso — lá vale `(etapa_id, rev)` (§4).

---

## 6. Ciclo de vida

`status`: `rascunho` → `ativo` → `depreciado`.

- `rascunho` entra no snapshot mas é invisível ao motor (não gera candidatos). Permite
  autorar e validar antes de expor.
- **Nada é removido do catálogo.** Remover um id quebraria progresso, evidência e
  sugestões históricas. Substituição se declara:

```yaml
- id: etapa:dados/sql-join
  status: depreciado
  substituido_por: etapa:dados/sql-join-v2
  depreciado_em: 2026-10-08
```

`substituido_por` é o que permite migrar objetivo e trilha sem perder histórico, e é
exigido pela validação §5.8 quando outra entidade ativa ainda aponta para a depreciada.

---

## 7. Pendente

- **Catálogo-fixture canônico** para os 7 cenários de teste de [motor §5](motor-de-sugestao.md):
  mínimo necessário é 2 trilhas, 6 competências e um caminho paralelo. Será escrito
  junto do validador, não antes — sem validador não há como garantir que o fixture é válido.
- **Internacionalização** de `titulo`/`descricao`: fora de escopo. Recurso já tem
  `idioma`; texto de entidade é pt-BR.
- **Autoria por não-programadores**: YAML em PR exige git. Aceito por ora; se virar
  obstáculo, a saída é uma interface que gera o YAML, não uma segunda fonte da verdade.
