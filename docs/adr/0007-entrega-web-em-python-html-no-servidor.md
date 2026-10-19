# ADR-0007 — Camada de entrega web em Python, HTML no servidor

- **Data**: 2026-10-12
- **Status**: aceito

## Contexto

[ADR-0006](0006-stack-python.md) escolheu Python com a camada de entrega
explicitamente fora de escopo, e deixou a porta aberta: *"revisitável quando houver
interface — o snapshot `catalogo.lock.json` é a fronteira, e uma UI em outra linguagem
pode consumi-lo sem tocar no domínio"*. A interface passou a ser pedida, e o plano está
em [docs/interface.md](../interface.md).

O catálogo hoje tem 6 trilhas, 54 etapas, 41 competências e 109 recursos — 116 KB de
snapshot. Volume irrelevante; o que pesa é outra coisa:

1. **A validação não pode ser duplicada.** As 11 validações de
   [catalogo.md §5](../catalogo.md) são lógica pura em Python. Uma interface que autore
   catálogo (fase 4 do plano) precisa delas; reimplementá-las em outra linguagem criaria
   a segunda fonte da verdade que [ADR-0004](0004-catalogo-em-yaml-compilado-para-snapshot.md)
   proíbe.
2. **O motor não pode ser duplicado.** Fronteira satisfeita, decaimento de evidência e
   score são domínio ([ADR-0003](0003-motor-de-sugestao-por-regras-explicavel.md)). Uma
   segunda implementação em template ou em JavaScript divergiria em silêncio, e a
   divergência apareceria como sugestão inexplicável — o defeito que a explicabilidade
   existe para impedir.
3. **URL endereçável e determinística.** A auditoria de sugestão exige que
   `/sugestao/<id>` abra sempre o mesmo conteúdo, com a `catalogo_versao` que a produziu
   ([motor §1](../motor-de-sugestao.md)).

Opções consideradas:

1. **Front-end em TypeScript** (Next.js/React) consumindo o snapshot.
2. **Ferramenta de dashboard** em Python (Streamlit/Gradio).
3. **HTML renderizado no servidor**, em Python, sem etapa de build.

## Decisão

Opção 3: **Starlette + Uvicorn + Jinja2**, HTML renderizado no servidor, sem `npm` nem
pipeline de front-end. O grafo é **SVG gerado no servidor** a partir de um layout
determinístico. Aprimoramento progressivo com htmx quando houver fragmento que o
justifique; nada de terceiros é vendorizado antes de ser usado.

- O pacote `trilhas.web` é a **segunda borda de I/O**, no mesmo nível de
  `catalogo/cli.py`. A regra do domínio puro passa a se ler: *`cli.py` e `web/` são as
  bordas; nada abaixo delas faz I/O.* Dentro de `web/`, o subpacote `apresentar/` é
  puro de propósito — é onde mora a lógica de tela, testável sem servidor.
- A entrada da interface é o **snapshot**, nunca o YAML de autoria
  ([ADR-0004](0004-catalogo-em-yaml-compilado-para-snapshot.md)). A leitura do snapshot
  para o modelo é função pura (`carregar.do_snapshot`), reaproveitando os mesmos
  construtores do carregador de YAML: o esquema continua definido num lugar só.
- **A interface não calcula domínio.** Fecho progressivo, arestas derivadas e níveis
  são funções puras de `trilhas.catalogo` / `trilhas.motor`; os templates só formatam.
- Dependências no extra `web`; o domínio continua com `pyyaml` e nada mais, e instalar
  o pacote sem o extra continua dando a CLI de CI.
- Primeira entrega **somente leitura** sobre o catálogo. Escrita de percurso espera a
  decisão de persistência (ADR própria), porque o esquema de `percurso/` se declara
  provisório.
- `estudante_id` é parâmetro de rota desde o início, mesmo com um estudante só.
  Autenticação continua fora de escopo ([CONTEXT §5](../CONTEXT.md)).

**Descartada a opção 1**: resolve bem a fase somente-leitura e trava na autoria — sem as
11 validações é inútil, e com elas exige um backend Python de qualquer forma. Seriam duas
linguagens pelo preço de nenhuma capacidade extra, custo que a
[ADR-0006](0006-stack-python.md) aceitaria apenas em troca de ganho.

**Descartada a opção 2**: entregaria a primeira tela numa tarde e impediria as seguintes
— estado em sessão em vez de URL fere o requisito 3, e grafo interativo não é viável.

**Descartado o FastAPI** como servidor: traria Pydantic, e Pydantic traria um segundo
modelo das entidades ao lado das `dataclasses` congeladas — divergência garantida no
primeiro campo novo. Como as respostas são HTML, serialização automática não resolve
problema que exista aqui. Se houver API JSON pública, FastAPI entra por cima.

## Nota de correção (2026-10-19)

A **Decisão** acima afirma que *"`cli.py` e `web/` são as bordas; nada abaixo delas faz
I/O"*. A frase é falsa, e já era no dia em que foi escrita: `catalogo/carregar.py` lê os
YAML de autoria do disco — `read_text` mais `yaml.safe_load`, dentro de `carregar(raiz)` —
e não é `cli.py` nem está sob `web/`. O bullet seguinte desta mesma seção já dizia a
metade certa, que `carregar.do_snapshot` é função pura: o que existe é um **módulo com
duas entradas**, uma pura e uma de borda, não uma camada com duas bordas. No dia seguinte,
[ADR-0008](0008-percurso-como-log-de-fatos-datados.md) acrescentou o segundo
contraexemplo, `percurso/repositorio.py`, que abre o SQLite.

A regra passa a se ler **por módulo nomeado, não por camada**. O núcleo é puro — `modelo`,
`validar`, `compilar`, `grafo`, `snapshot`, `motor/`, `percurso/{eventos,projecao,registrar}`
e `web/apresentar/` — e o efeito mora em borda nomeada: `catalogo/carregar.py`,
`catalogo/cli.py`, `percurso/cli.py`, `percurso/repositorio.py` e a camada `web/`. Lista de
arquivo envelhece, então a fronteira se confere em vez de se recitar; o grep que a apura
mora na regra 4 do CLAUDE.md, que é onde a regra se mantém.

A decisão desta ADR não muda: HTML renderizado no servidor, `web/` como camada de entrega
e `apresentar/` puro de propósito seguem valendo, e nenhum dos descartes se reabre. O que
estava errado era o alcance de uma frase sobre I/O, não o desenho da camada.

## Consequências

- O repositório continua com uma linguagem só, e o domínio continua testável sem rede,
  banco ou servidor.
- `mypy --strict` passa a cobrir `src/trilhas/web`, e `apresentar/` é testado por
  entrada e saída, sem subir servidor.
- Toda tela de leitura responde HTML completo: a interface funciona sem JavaScript, e o
  grafo tem uma tabela equivalente com a mesma informação.
- O layout do grafo é calculado no servidor por função determinística, verificável por
  teste de ouro — e as mesmas coordenadas servem a um renderizador de terceiros se a
  interação crescer.
- Interface rica (arrastar, animar, editar em canvas) fica mais caro do que seria numa SPA.
  Aceito: a informação a transmitir é grafo com estado e tabela comparativa, não canvas.
- A interface roda em `localhost`, para um estudante, sem autenticação. Expor em rede
  exigirá decisão nova.
