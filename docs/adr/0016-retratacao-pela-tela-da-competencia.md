# ADR-0016 — Retratação pela tela da competência, com a evidência lida do log

- **Data**: 2026-10-18
- **Status**: aceito

## Contexto

A [ADR-0014](0014-retratacao-de-evidencia-por-seq.md) decidiu o fato de retratação e
fechou uma fronteira na última consequência: *"A tela não retrata. (…) retratação
endereça um fato do log por `seq`, que não tem tela a que pertencer. Fica para
interface.md decidir, quando houver uma tela de histórico onde o `seq` apareça."*

Enquanto isso valer, o conserto é só de linha de comando, e isso cobra um preço
concreto: a tela da etapa **oferece o botão que produz o erro** — concluir emite
evidência (interface §5.10) — e não oferece nenhum que o desfaça. A §5.10 já admitia a
dívida: *"clicar errado não tem desfazer (…) é a primeira dívida que esta fase cobra."*

Duas perguntas precisavam de resposta, e a segunda é a que tem alternativas de peso.

**Primeira: a que tela o `seq` pertence.** Não há tela de histórico, e inventar uma
seria a saída mais larga. Mas o levantamento das evidências hoje gravadas mostra que
elas já têm dono: toda `EvidenciaRegistrada` carrega `competencia` — é campo
obrigatório —, e **nem toda carrega `etapa`**: `registrar_autoavaliacao` grava com
`etapa=None` (ADR-0014 §Decisão, razão 1). A competência é, portanto, a única entidade
do catálogo a que *todas* as evidências pertencem.

**Segunda: por onde a evidência chega à tela.** A projeção devolve
`CompetenciaDominada` — competência, nível, data e confiança — e nada mais. Não há
`seq` em lugar algum da leitura da interface: `web/percurso.py` lê o log, chama
`montar_percurso` e entrega um `Percurso`, que é a entrada do **motor**. O `seq` existe
no `Registro` e morre ali.

## Decisão

**A retratação mora em `/competencia/{id}`, num bloco de evidências que lista o `seq` de
cada fato; e a evidência chega à tela por uma leitura própria do log, não por
`Percurso`.**

**O bloco é a §5.5 sendo cumprida, não uma tela nova.** O plano já previa para esta
rota *"nível atual e evidências em linha do tempo datada"*. Faltava implementar; o que
esta ADR acrescenta ao previsto é o `seq` visível e o formulário ao lado de cada linha.
Uma tela de histórico do percurso continua possível e não é necessária: ela listaria os
mesmos fatos sem o contexto que explica cada um — o critério de verificação, quem
ensina, quem exige —, e seria uma segunda resposta à pergunta "de onde veio este
nível".

**A leitura é uma segunda passada sobre o log, por `projecao.evidencias_de`.** Pura,
devolve `Evidencia` com `seq`, nível, origem, confiança, dia, a etapa (ou `None`) e a
retratação que a alcançou — datada e com motivo. Diferente de `competencias_de`, **não
descarta nada**: evidência retratada entra marcada, e evidência de nível menor que não
venceu o máximo entra igual. É histórico, não nível vigente.

A alternativa era **alargar `CompetenciaDominada`** (ou `Percurso`) com as evidências
que a sustentam, e foi recusada pelo argumento que a
[ADR-0012](0012-fato-de-recurso-no-percurso.md) já usou para manter `RecursoPercorrido`
fora de `Percurso`: `Percurso` é a entrada do motor, e o motor nunca pergunta qual fato
produziu um nível — ele filtra por `nivel_minimo` (motor §2.2) e despontua por
`ultima_evidencia_em` (motor §3.6). Pôr `seq` ali anunciaria na fronteira do motor um
consumidor que não existe, e o primeiro a tropeçar seria quem lesse a entrada do motor
procurando o que ela significa.

A mesma `evidencias_de` passou a alimentar `trilhas-percurso mostrar`, que montava sua
própria lista. Duas varreduras do mesmo log divergiriam exatamente onde dói: no `seq`
que uma delas deixasse de marcar como retratado (interface §3.3).

**O POST vai para a URL da competência, e a competência não é o alvo.** O alvo é o
`seq`, só ele, e `registrar.conferir_retratacao` — a mesma função da CLI — é a regra
inteira. A competência na URL diz de qual tela o pedido saiu e para onde o 303 volta.

Repetir a competência como alvo seria, na URL, a redundância que a ADR-0014 recusou
dentro do evento: *"seria redundância capaz de contradizer o alvo"*. Uma conferência
"o `seq` é desta competência?" também poria em `web/` uma regra sobre fatos do log que
o domínio não tem — e não protegeria nada, porque o fato gravado estaria correto de
qualquer modo: `EvidenciaRetratada` não afirma competência nenhuma.

No mais, o POST é o da §5.10 sem desvio: `Origin` presente e igual ao host, 303 em vez
de HTML, uma transação por POST, e nada escrito sem percurso carregado. Conferência e
escrita entram na **mesma** transação — "o alvo existe e está de pé" é afirmação sobre
o log, e afirmá-la fora da transação que grava a deixaria valendo sobre um log que já
mudou.

**Sem `confirm()`.** O POST que conclui etapa não pede confirmação, e pedi-la aqui diria
que retratar é mais perigoso que concluir, quando é o contrário: retratar é o conserto.
Além disso só funcionaria com script, e a tela degrada sem ele (interface §6.9).

## Consequências

- **A dívida da §5.10 está paga pela metade que importa.** Clicar errado agora tem
  conserto pela tela: concluir por engano emite evidência, e a competência que ela
  inflou é onde a retratação fica. O que continua sem desfazer pela tela é o
  **progresso** de etapa — e ali o remédio já existia: reiniciar, porque o último fato
  sobre a etapa vence.
- **A tela da competência passou a depender do percurso**, que antes ela ignorava. Sem
  percurso ela diz que não sabe, em vez de afirmar ausência de evidência — a mesma
  distinção que `VisaoTrilha.tem_percurso` já fazia.
- **Duas leituras do log por requisição** nesta rota: `percurso_completo` para o nível
  vigente e `evidencias_do_percurso` para os fatos. É um log de um estudante lido duas
  vezes; se um dia pesar, o remédio é uma leitura só dos `Registro` com as duas
  projeções aplicadas sobre ela, e não fundir as duas projeções.
- **Retratar a última evidência faz a competência sumir da tela do percurso**, como da
  projeção. É o correto (CONTEXT §4), e a linha retratada continua listada com a data e
  o motivo — que é como a pergunta "por que ele deixou de achar que eu sei isso" fica
  respondida na própria tela.
- **Autoavaliação ganhou casa sem ganhar botão.** `sei` continua só na CLI, mas a
  evidência que ele grava já aparece na tela da competência e já pode ser retratada
  ali. A assimetria é esperada: a §5.10 ligou a escrita por partes, e esta é a parte
  que a retratação exigia.
- O `seq` virou **dado de tela**, não detalhe de armazenamento. Já era parte declarada
  do modelo (ADR-0014) e já saía na exportação em JSONL; agora quem estuda o lê sem
  abrir arquivo. O preço é que ele não pode mais mudar de significado sem quebrar o que
  as pessoas veem — o que o log append-only já garantia.
