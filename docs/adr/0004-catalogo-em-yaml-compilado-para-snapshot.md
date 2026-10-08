# ADR-0004 — Catálogo autorado em YAML, compilado para um snapshot validado

- **Data**: 2026-10-08
- **Status**: aceito

## Contexto

O catálogo (competências, etapas, recursos, trilhas) é conteúdo editorial de vida
longa, revisado por humanos e compartilhado entre todos os estudantes. [ADR-0002](0002-trilha-como-grafo-de-etapas.md)
tornou-o um grafo, e grafo autorado à mão fica inválido com facilidade: ciclo,
referência quebrada, competência exigida que ninguém ensina, trilha cujo objetivo é
inalcançável. O motor de sugestão não tem como se defender disso em tempo de
execução sem degradar para silêncio ("nenhuma sugestão") sem causa aparente.

Opções consideradas:

1. **Catálogo no banco de dados**, editado por interface administrativa.
2. **Arquivos YAML no repositório**, carregados diretamente pela aplicação.
3. **Arquivos YAML no repositório, compilados para um snapshot validado** que é o
   único artefato consumido.

## Decisão

Opção 3. A fonte da verdade são arquivos YAML em `catalogo/`, revisados em pull
request. Um passo de compilação resolve referências, calcula o grafo, roda as 11
validações de [catalogo.md §5](../catalogo.md) e emite `catalogo.lock.json`, que é
commitado e é o único artefato que a aplicação carrega. Recursos ficam em arquivos
separados das etapas, por terem ciclo de vida próprio.

## Consequências

- Catálogo inválido falha na compilação, não em produção. A validação "objetivo
  alcançável a partir de perfil vazio" transforma o caso de borda
  `sem_caminho_no_catalogo` do motor em defeito detectável em CI.
- Mudança de catálogo é diff revisável, com histórico e autoria — git já resolve
  versionamento, auditoria e reversão sem construir nada.
- O snapshot desacopla o motor do formato de autoria: trocar YAML por outra coisa não
  afeta quem consome.
- Como o catálogo é um artefato de build, atualizá-lo exige um deploy ou um passo de
  publicação. Não há edição ao vivo — aceito nesta fase, em troca da garantia de validade.
- Autoria exige git e YAML, o que exclui autores não técnicos. Se virar obstáculo
  real, a resposta é uma interface que **gera** o YAML, nunca uma segunda fonte da
  verdade concorrente.
- Custo: é preciso construir e manter o compilador/validador antes de ter catálogo
  utilizável — inclusive antes do fixture de testes do motor.
