#!/usr/bin/env bash
# Sobe `trilhas-web` e exercita todas as rotas com ids reais do snapshot.
#
# A interface é só-leitura sobre catalogo.lock.json (ADR-0004/0007), então um
# smoke test aqui é barato e cobre o caminho inteiro: snapshot → Fonte → rota →
# template. Uso:
#
#   scripts/fumaca-web.sh              # sobe, testa, derruba; 0 = tudo verde
#   scripts/fumaca-web.sh --manter     # deixa o servidor de pé ao terminar
#   scripts/fumaca-web.sh --porta 9001
#
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

PORTA=8042
MANTER=0
while [ $# -gt 0 ]; do
  case "$1" in
    --porta) PORTA="${2:?--porta exige um número}"; shift 2 ;;
    --manter) MANTER=1; shift ;;
    -h|--help) sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "argumento desconhecido: $1" >&2; exit 2 ;;
  esac
done

LOCK="$RAIZ/catalogo.lock.json"
BASE="http://127.0.0.1:$PORTA"
LOG="$(mktemp -t fumaca-web-XXXXXX.log)"
PID=""

vermelho() { printf '\033[31m%s\033[0m\n' "$*" >&2; }
verde()    { printf '\033[32m%s\033[0m\n' "$*"; }

limpar() {
  if [ -n "$PID" ] && [ "$MANTER" -eq 0 ]; then
    kill "$PID" 2>/dev/null
    wait "$PID" 2>/dev/null
  fi
}
trap limpar EXIT

# --- 1. A árvore está em estado de rodar? --------------------------------
# Um merge por resolver deixa marcador de conflito dentro do .py e o app morre
# com SyntaxError numa linha que você não escreveu. Checar isto primeiro evita
# caçar um bug que não existe. Outras sessões commitam neste mesmo checkout.
if [ -e .git/MERGE_HEAD ] || [ -e .git/rebase-merge ] || [ -e .git/rebase-apply ]; then
  vermelho "merge/rebase por resolver nesta árvore — o app não sobe assim."
  git --no-pager diff --name-only --diff-filter=U | sed 's/^/  conflito: /' >&2
  vermelho "resolva (ou 'git merge --abort') antes de rodar."
  exit 1
fi

CONFLITADOS="$(git --no-pager grep -lE '^(<{7}|={7}|>{7})( |$)' -- 'src/**/*.py' '*.json' 2>/dev/null)"
if [ -n "$CONFLITADOS" ]; then
  vermelho "marcadores de conflito em arquivos versionados:"
  printf '  %s\n' $CONFLITADOS >&2
  exit 1
fi

# --- 2. O snapshot existe e é JSON? --------------------------------------
# A interface lê o lock, nunca o YAML de autoria. Sem lock válido não há app.
if [ ! -f "$LOCK" ]; then
  vermelho "sem $LOCK — rode: uv run trilhas compilar"
  exit 1
fi
if ! python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$LOCK" 2>/dev/null; then
  vermelho "$LOCK não é JSON válido — rode: uv run trilhas compilar"
  exit 1
fi

# --- 3. Porta livre? ------------------------------------------------------
# Subshell: o descritor nasce e morre lá. `exec 3<&- 2>/dev/null` mandaria todo
# o stderr seguinte do script para /dev/null — `exec` sem comando redireciona o
# shell inteiro —, e a mensagem abaixo não apareceria.
if (exec 3<>"/dev/tcp/127.0.0.1/$PORTA") >/dev/null 2>&1; then
  vermelho "porta $PORTA já ocupada — use --porta N ou derrube o servidor anterior."
  exit 1
fi

# --- 4. Sobe o servidor ---------------------------------------------------
echo "subindo trilhas-web em $BASE (log: $LOG)"
uv run --extra web trilhas-web --porta "$PORTA" >"$LOG" 2>&1 &
PID=$!

pronto=0
for _ in $(seq 1 60); do
  if ! kill -0 "$PID" 2>/dev/null; then break; fi
  if curl -fsS -o /dev/null "$BASE/" 2>/dev/null; then pronto=1; break; fi
  sleep 0.5
done

if [ "$pronto" -eq 0 ]; then
  vermelho "o servidor não respondeu em 30s. Fim do log:"
  tail -20 "$LOG" >&2
  exit 1
fi

# --- 5. Rotas, com ids reais do snapshot ---------------------------------
# Nunca invente a URL de uma entidade: a rota é /<tipo>/<id completo>, e o id
# já traz o prefixo — /trilha/trilha:matematica/prova-e-calculo, não
# /trilha/matematica/prova-e-calculo. Por isso os ids saem do lock.
mapfile -t ALVOS < <(python3 - "$LOCK" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
print("/")
print("/catalogo")
print("/catalogo/diagnostico")
for chave, prefixo in (("trilhas", "trilha"), ("etapas", "etapa"), ("competencias", "competencia")):
    for item in d.get(chave, [])[:3]:
        print(f"/{prefixo}/{item['id']}")
# A obra é endereçada pelo slug do campo `obra`, não por id de catálogo — ela não é
# entidade (catalogo.md §2). O export entra junto: é rota de leitura como as outras.
for slug in sorted({r["obra"] for r in d.get("recursos", []) if r.get("obra")})[:2]:
    print(f"/obra/{slug}")
    print(f"/obra/{slug}/exportar")
PY
)

echo
falhas=0
for rota in "${ALVOS[@]}"; do
  codigo="$(curl -s -o /dev/null -w '%{http_code}' "$BASE$rota" 2>/dev/null)"
  if [ "$codigo" = "200" ]; then
    printf '  %s  %s\n' "$codigo" "$rota"
  else
    printf '  \033[31m%s\033[0m  %s\n' "${codigo:----}" "$rota"
    falhas=$((falhas + 1))
  fi
done

# A 404 tem de continuar sendo 404: é página tratada, não stack trace.
codigo="$(curl -s -o /dev/null -w '%{http_code}' "$BASE/trilha/trilha:nao/existe" 2>/dev/null)"
if [ "$codigo" = "404" ]; then
  printf '  %s  %s (esperado)\n' "$codigo" "/trilha/trilha:nao/existe"
else
  printf '  \033[31m%s\033[0m  %s — esperava 404\n' "${codigo:----}" "/trilha/trilha:nao/existe"
  falhas=$((falhas + 1))
fi

# --- 6. Erro de servidor no log? -----------------------------------------
if grep -qE 'Traceback|500 Internal' "$LOG"; then
  echo
  vermelho "o servidor registrou erro:"
  grep -nE 'Traceback|500 Internal' "$LOG" | head -5 >&2
  falhas=$((falhas + 1))
fi

# --- 7. O botão Desligar realmente derruba o servidor --------------------
# Só faz sentido com o servidor descartável: em --manter o ponto é deixá-lo de pé.
# Como POST /desligar encerra o processo, este é o último teste, e ele substitui o
# `kill` do trap — se o processo não morrer sozinho, o trap ainda cobre.
if [ "$MANTER" -eq 0 ]; then
  codigo="$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/desligar" 2>/dev/null)"
  if [ "$codigo" = "200" ]; then
    printf '  %s  POST %s\n' "$codigo" "/desligar"
  else
    printf '  \033[31m%s\033[0m  POST %s — esperava 200\n' "${codigo:----}" "/desligar"
    falhas=$((falhas + 1))
  fi

  morreu=0
  for _ in $(seq 1 20); do
    if ! kill -0 "$PID" 2>/dev/null; then morreu=1; break; fi
    sleep 0.5
  done
  if [ "$morreu" -eq 1 ]; then
    printf '  ok   servidor encerrou sozinho depois do POST\n'
  else
    vermelho "  o servidor seguiu de pé 10s depois de POST /desligar"
    falhas=$((falhas + 1))
  fi
fi

echo
if [ "$falhas" -gt 0 ]; then
  vermelho "$falhas rota(s) com problema. Log completo: $LOG"
  exit 1
fi
verde "todas as rotas responderam 200 (e a 404 é 404)."

if [ "$MANTER" -eq 1 ]; then
  echo "servidor de pé em $BASE (pid $PID) — derrube com: kill $PID"
else
  rm -f "$LOG"
fi
