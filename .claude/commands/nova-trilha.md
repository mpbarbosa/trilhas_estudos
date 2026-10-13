---
description: Autora uma nova trilha no catálogo, do objetivo às etapas, recursos e snapshot
argument-hint: <tema da trilha, e materiais de base se houver>
---

Autore uma trilha nova para: **$ARGUMENTS**

Siga o procedimento da skill `autorar-catalogo` (`.claude/skills/autorar-catalogo/SKILL.md`)
e o esquema de `docs/catalogo.md`. Antes de escrever YAML, me apresente e espere meu aval:

1. o **objetivo declarado** em competências-alvo com nível — não em assuntos;
2. as competências novas que a trilha precisa criar, cada uma com o critério de
   `verificacao`, e as que já existem no catálogo e serão reaproveitadas
   (confira em `catalogo/competencias/`, não suponha);
3. o esqueleto das etapas com `requires`/`teaches`, deixando visível onde há
   caminho paralelo e qual etapa parte de perfil vazio;
4. os ids propostos, no formato `<tipo>:<area>/<slug>`.

Com o aval, escreva os arquivos, rode `uv run trilhas validar` a cada bloco,
compile e acrescente a trilha ao README.md e à tabela de CLAUDE.md.

Não invente recurso: toda etapa precisa de ≥ 1 recurso real, disponível, com
`url`, `custo`, `duracao_min` e `idioma` que você possa justificar. Se não tem
material concreto para uma etapa, diga qual é a lacuna em vez de preencher com
um link plausível.
