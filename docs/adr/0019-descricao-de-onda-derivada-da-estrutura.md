# ADR-0019 — Descrição de onda derivada da estrutura, nunca autorada

- **Data**: 2026-10-26
- **Status**: aceito

## Contexto

A tela da trilha desenha o grafo em faixas verticais, e a faixa é a **onda**: a
profundidade de pré-requisito que `fecho_progressivo` calcula
([ADR-0002](0002-trilha-como-grafo-de-etapas.md), [interface.md §4](../interface.md)).
Pediu-se descrição "para todas as ondas e etapas" — uma frase só, que esconde duas
coisas de natureza diferente.

**Etapa é entidade de catálogo**: tem id imutável, `rev`, `status` e depreciação
([ADR-0005](0005-identidade-imutavel-e-depreciacao.md)), mora num arquivo de autoria e
tem dono. Dar-lhe `descricao` é acrescentar um campo cosmético ao lado do que a
competência já tinha, e isso se resolveu pela tabela de
[catalogo.md §4](../catalogo.md), sem decisão estrutural nenhuma.

**Onda não é entidade.** Não tem id, `rev`, `status` nem arquivo: é o resultado de uma
função sobre o conjunto das etapas ativas. O único nome que ela tem é um inteiro, e
esse inteiro é **posicional** — diz o lugar na fila, não a identidade do que está nele.

### O número da onda se desloca, e já se deslocou aqui

Medido no catálogo de hoje: **8 ondas**, com `[19, 26, 27, 20, 16, 7, 2, 1]` etapas.

O experimento que importa é remover **uma** etapa e recalcular. Tirando
`etapa:programacao/programacao-de-sistemas` — a avulsa que
[ADR-0018](0018-programacao-de-sistemas-como-pre-requisito-compartilhado.md) criou, cujo
ponto inteiro era ter `requires: []` — o grafo vai de 8 para **12 ondas**, e **12 das
117 etapas restantes mudam de onda**:

| Sem a avulsa | Com a avulsa (hoje) | Etapa |
|---|---|---|
| onda 7 | onda 5 | `etapa:so/projeto-modificar-o-minix` |
| onda 7 | onda 3 | `etapa:terminal/analisador-de-estados` |
| onda 9 | onda 5 | `etapa:terminal/entrada-de-teclado-e-mouse` |
| onda 11 | onda 7 | `etapa:terminal/projeto-emulador-minimo` |
| onda 12 | onda 8 | `etapa:terminal/leitura-de-emuladores-reais` |

As 12 são `trilha:terminal/emulador` inteira mais o projeto do MINIX, deslocadas de 2 a
4 posições. Uma etapa autorada num arquivo de outra área reescreveu o número de onda de
uma trilha que não a menciona — e foi para melhor, porque era exatamente o que a
ADR-0018 queria. **O deslocamento não é defeito: é o modelo funcionando.**

### E o deslocamento é silencioso

Nenhuma validação compara ondas entre compilações, e o snapshot não guarda onda
nenhuma: as duas ocorrências de `onda` em `catalogo.lock.json` estão dentro da palavra
"responda", em dois critérios de verificação. A onda é calculada na hora de desenhar e
não existe em lugar nenhum entre uma renderização e a seguinte. Texto autorado por
número de onda ficaria errado sem que coisa alguma percebesse — "onda 9" continuaria
compilando, validando e renderizando, descrevendo a onda 5.

### Opções

1. **Campo autorado na trilha**, com um texto por número de onda.
2. **Entidade `Onda`** de catálogo, com id, `rev` e ciclo de vida.
3. **Frase derivada na apresentação**, montada a partir das etapas que a onda contém.

## Decisão

**Opção 3.** A descrição da onda é derivada no servidor, em `_descrever_ondas`
([`web/apresentar/disposicao.py`](../../src/trilhas/web/apresentar/disposicao.py)),
função pura sobre as etapas da onda e as arestas do escopo desenhado. Ela diz o que a
onda exige, o que desenvolve — competências com o nível, que é o que distingue uma
segunda passagem pela mesma competência — e quantas etapas libera, a partir de qual
onda. Chega ao rótulo do SVG e a uma seção da tabela equivalente, que é a versão que
leitor de tela e `curl` recebem ([interface.md §4](../interface.md)).

Nenhum campo novo no catálogo, nenhum `rev`, nenhuma validação nova. **Quem carrega
prosa de autoria é a etapa**, que tem dono e identidade; a onda carrega só o que a
estrutura já afirma.

A opção 1 foi recusada pela medição acima. O número de onda não é chave de nada: ele
muda quando qualquer etapa entra à frente, em qualquer arquivo, e o texto antigo passa
a descrever outra onda sem que nada falhe. Seria uma segunda fonte da verdade sobre um
fato que o grafo já calcula, com a diferença de que a segunda fonte não é conferível —
o mesmo erro que [catalogo.md §1](../catalogo.md) evita ao proibir redefinir etapa em
duas trilhas, aqui agravado por não haver validação que o pegue.

A opção 2 é a mesma recusa, mais cara. Identidade por ADR-0005 exige id imutável e
nunca reaproveitado, `rev`, depreciação com `substituido_por` — tudo isso para um objeto
cuja extensão muda sozinha a cada etapa nova e que ninguém autora. E para que o id
significasse algo, o catálogo teria de **fixar** a onda, isto é, autorar um valor
derivado: o oposto de [ADR-0004](0004-catalogo-em-yaml-compilado-para-snapshot.md), onde
o derivado se compila a partir da autoria e nunca o contrário.

## Consequências

- **A frase tem teto de qualidade.** Ela enumera e conta; não diz por que a onda
  importa, não tem ironia, não escolhe o que destacar. Prosa humana diria mais. Aceita-se
  um texto medíocre e sempre verdadeiro no lugar de um texto bom que envelhece calado.
- **Onda larga vira resumo.** `comum.enumerar` nomeia três competências e conta o resto
  ("e mais 4"). Na tela real isso quase não aparece, porque o escopo é a trilha — de 3 a
  8 ondas, no máximo 16 etapas —, mas um grafo do acervo inteiro, com ondas de 26 e 27
  etapas, seria quase todo "e mais N". Quem desenhar esse grafo precisa de outra forma,
  não desta frase.
- **"Libera N etapas" conta só o que está desenhado.** As arestas chegam a `dispor` já
  filtradas pelo escopo, de propósito: prometer que a onda libera uma etapa que esta tela
  não mostra seria mentir sobre o desenho. A mesma onda diz números diferentes na tela da
  trilha e num grafo maior, e isso é correto, não inconsistente.
- **Nomear onda continua impossível, e nomear fase não é a mesma coisa.** As 14 trilhas
  já agrupam etapas por comentário no YAML — `# --- Fundamento ---`,
  `# --- Linguagem ---`, `# --- Proteção ---` —, e esse agrupamento **cruza** as ondas:
  em `trilha:dados/bancos-de-dados-relacionais`, "Fundamento" ocupa as ondas 1 e 2,
  "Armazenamento" ocupa a onda 2 junto com ele, e "Linguagem" e "Projeto de esquema"
  dividem as ondas 3 e 4. Se um dia esse agrupamento tiver de aparecer na tela, ele é
  autoral e precisa de forma própria — campo na trilha ou entidade —, e é a ADR seguinte.
  O que esta ADR fecha é usar a onda como se fosse ele.
- **O texto é testado pelo deslocamento, não só pelo conteúdo.** `tests/test_apresentar.py`
  tem um caso que insere uma etapa à frente e exige que a frase da onda deslocada seja
  reescrita. É o invariante desta ADR em forma executável — no escopo em que ele roda,
  que é `dispor` sobre um catálogo em memória, não a tela inteira.
- **Custo**: a tela da onda passa a depender do código, não da autoria. Melhorar o texto
  é mudar `disposicao.py` e seus testes, com revisão de código, enquanto melhorar a
  descrição de uma etapa é editar uma linha de YAML. Quem quiser frase melhor paga em
  código.
