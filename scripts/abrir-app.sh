#!/usr/bin/env bash
# Sobe `trilhas-web` e abre a interface no navegador.
#
# O servidor fica em primeiro plano: Ctrl-C derruba. Se a porta já tiver um
# trilhas-web de pé, reaproveita — só abre o navegador e sai. Uso:
#
#   scripts/abrir-app.sh                     # sobe na 8042 e abre /
#   scripts/abrir-app.sh --porta 9001
#   scripts/abrir-app.sh --rota /catalogo/diagnostico
#   scripts/abrir-app.sh --sem-navegador     # só sobe, imprime a URL
#
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ" || exit 1

PORTA=8042
ROTA="/"
NAVEGADOR=1
while [ $# -gt 0 ]; do
  case "$1" in
    --porta) PORTA="${2:?--porta exige um número}"; shift 2 ;;
    --rota) ROTA="${2:?--rota exige um caminho}"; shift 2 ;;
    --sem-navegador) NAVEGADOR=0; shift ;;
    -h|--help) sed -n '2,11p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "argumento desconhecido: $1" >&2; exit 2 ;;
  esac
done
case "$ROTA" in /*) ;; *) ROTA="/$ROTA" ;; esac

LOCK="$RAIZ/catalogo.lock.json"
BASE="http://127.0.0.1:$PORTA"
LOG="$(mktemp -t abrir-app-XXXXXX.log)"
PID=""

vermelho() { printf '\033[31m%s\033[0m\n' "$*" >&2; }
verde()    { printf '\033[32m%s\033[0m\n' "$*"; }

limpar() {
  if [ -n "$PID" ]; then
    kill "$PID" 2>/dev/null
    wait "$PID" 2>/dev/null
  fi
  rm -f "$LOG"
}
trap limpar EXIT

# A rota de uma entidade leva o id inteiro, prefixo incluído — /trilha/trilha:area/slug.
# Avisar aqui é mais barato que a 404 tratada, que se parece com "a entidade sumiu".
case "$ROTA" in
  /trilha/*|/etapa/*|/competencia/*)
    tipo="${ROTA#/}"; tipo="${tipo%%/*}"
    resto="${ROTA#/$tipo/}"
    case "$resto" in
      "$tipo":*) ;;
      *) vermelho "aviso: '$ROTA' provavelmente dá 404 — o id já traz o prefixo, use /$tipo/$tipo:$resto" ;;
    esac
    ;;
esac

# --- 1. A árvore está em estado de rodar? --------------------------------
# Outras sessões commitam neste checkout. Marcador de conflito dentro do .py
# mata o app com SyntaxError numa linha que você não escreveu.
if [ -e .git/MERGE_HEAD ] || [ -e .git/rebase-merge ] || [ -e .git/rebase-apply ]; then
  vermelho "merge/rebase por resolver nesta árvore — o app não sobe assim."
  git --no-pager diff --name-only --diff-filter=U | sed 's/^/  conflito: /' >&2
  exit 1
fi

CONFLITADOS="$(git --no-pager grep -lE '^(<{7}|={7}|>{7})( |$)' -- 'src/**/*.py' '*.json' 2>/dev/null)"
if [ -n "$CONFLITADOS" ]; then
  vermelho "marcadores de conflito em arquivos versionados:"
  printf '  %s\n' $CONFLITADOS >&2
  exit 1
fi

# --- 2. O snapshot existe e é JSON? --------------------------------------
# A interface lê o lock, nunca o YAML de autoria (ADR-0004).
if [ ! -f "$LOCK" ]; then
  vermelho "sem $LOCK — rode: uv run trilhas compilar"
  exit 1
fi
if ! python3 -I -c "import json,sys; json.load(open(sys.argv[1]))" "$LOCK" 2>/dev/null; then
  vermelho "$LOCK não é JSON válido — rode: uv run trilhas compilar"
  exit 1
fi

abrir() {
  local url="$1"
  if [ "$NAVEGADOR" -eq 0 ]; then
    echo "navegador não solicitado — abra: $url"
    return 0
  fi
  for cmd in "${BROWSER:-}" xdg-open gio sensible-browser open; do
    [ -n "$cmd" ] || continue
    command -v "$cmd" >/dev/null 2>&1 || continue
    if [ "$cmd" = gio ]; then
      gio open "$url" >/dev/null 2>&1 && return 0
    else
      "$cmd" "$url" >/dev/null 2>&1 && return 0
    fi
  done
  vermelho "nenhum abridor de navegador encontrado — abra à mão: $url"
}

# --- 3. Porta livre? Ou já é o nosso app? --------------------------------
# A sonda roda em subshell: o descritor nasce e morre lá, e o shell não precisa
# fechá-lo. `exec 3<&- 2>/dev/null` faria pior que nada — `exec` sem comando
# aplica o redirecionamento ao shell inteiro, e todo stderr seguinte (inclusive
# a mensagem de erro abaixo) iria para /dev/null.
porta_ocupada() { (exec 3<>"/dev/tcp/127.0.0.1/$1") >/dev/null 2>&1; }

if porta_ocupada "$PORTA"; then
  if curl -fsS --max-time 3 -o /dev/null "$BASE/" 2>/dev/null; then
    verde "já há um servidor respondendo em $BASE — reaproveitando."
    abrir "$BASE$ROTA"
    exit 0
  fi
  vermelho "porta $PORTA ocupada por algo que não responde HTTP — use --porta N."
  exit 1
fi

# --- 4. Sobe o servidor ---------------------------------------------------
# O extra `web` não é instalado por padrão; sem ele o entrypoint avisa e sai 1.
echo "subindo trilhas-web em $BASE (log: $LOG)"
uv run --extra web trilhas-web --porta "$PORTA" >"$LOG" 2>&1 &
PID=$!

# Espera limitada por relógio, não por número de tentativas: um app que aceita a
# conexão e não responde consome o --max-time de cada curl, e 60 tentativas de 3s
# seriam uma espera de minutos.
pronto=0
LIMITE=$((SECONDS + 30))
while [ "$SECONDS" -lt "$LIMITE" ]; do
  if ! kill -0 "$PID" 2>/dev/null; then break; fi
  if curl -fsS --max-time 3 -o /dev/null "$BASE/" 2>/dev/null; then pronto=1; break; fi
  sleep 0.5
done

if [ "$pronto" -eq 0 ]; then
  vermelho "o servidor não respondeu em 30s. Fim do log:"
  tail -20 "$LOG" >&2
  exit 1
fi

verde "de pé em $BASE$ROTA"
abrir "$BASE$ROTA"

# --- 5. Fica em primeiro plano; Ctrl-C derruba ---------------------------
# O servidor não recarrega sozinho: ao editar src/trilhas/web/, derrube e suba
# de novo, senão você confere a versão antiga.
echo "Ctrl-C para derrubar. Log do servidor:"
tail -f "$LOG" --pid "$PID" 2>/dev/null &
wait "$PID"
