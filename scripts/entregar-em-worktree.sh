#!/usr/bin/env bash
# Prepara a entrega de um trabalho em worktree próprio: cria o worktree a partir
# de origin/main, leva para lá o diff dos caminhos que você nomear, instala os
# extras e roda o gate inteiro. NÃO commita, NÃO publica e NÃO toca na árvore
# compartilhada além de ler o diff dela.
#
# Existe porque a regra 7 do COORDINATION.md manda todo trabalho que vai gerar
# commit nascer em worktree próprio, e fazer isso à mão são cinco idas em que o
# venv do worktree nasce sem os extras — e sem eles o pytest coleta menos e o
# ruff nem existe, de modo que o gate passa verde sem ter rodado.
#
# POR QUE OS CAMINHOS SÃO OBRIGATÓRIOS: este checkout é compartilhado, e o `git
# diff` dele mistura o seu trabalho com o de quem mais estiver editando agora.
# Nenhum script sabe o que é seu. Nomeie, ou peça --vazio. Uso:
#
#   scripts/entregar-em-worktree.sh livro-novo catalogo/ docs/bibliografia.md
#   scripts/entregar-em-worktree.sh so-o-gate --vazio
#   scripts/entregar-em-worktree.sh x --em /outro/lugar catalogo/
#
# Saída: 0 = worktree pronto e gate verde; 1 = worktree pronto e alguma etapa do
#         gate falhou (o relatório diz qual); 2 = erro de uso ou de preparação.
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ" || { echo "não consegui entrar em $RAIZ" >&2; exit 2; }

VAZIO=0
DESTINO=""
SLUG=""
CAMINHOS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --vazio) VAZIO=1; shift ;;
    --em) DESTINO="${2:?--em exige um diretório}"; shift 2 ;;
    -h|--ajuda) sed -n '2,24p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) echo "opção desconhecida: $1" >&2; exit 2 ;;
    *) if [ -z "$SLUG" ]; then SLUG="$1"; else CAMINHOS+=("$1"); fi; shift ;;
  esac
done

[ -n "$SLUG" ] || { echo "uso: scripts/entregar-em-worktree.sh <slug> <caminho>... | --vazio" >&2; exit 2; }
printf '%s' "$SLUG" | grep -qE '^[a-z0-9][a-z0-9-]*$' || {
  echo "slug inválido: use minúsculas, dígitos e hífen" >&2; exit 2; }
if [ "$VAZIO" = 0 ] && [ "${#CAMINHOS[@]}" -eq 0 ]; then
  echo "nomeie os caminhos do SEU trabalho, ou use --vazio." >&2
  echo "a árvore é compartilhada: 'tudo que mudou' não é o mesmo que 'o que é seu'." >&2
  exit 2
fi

# Rodar de dentro de um worktree ligado criaria worktree de worktree e o
# `git diff` leria a árvore errada.
if [ "$(git rev-parse --git-dir)" != "$(git rev-parse --git-common-dir)" ]; then
  echo "você está num worktree ligado ($RAIZ). Rode do checkout principal." >&2
  exit 2
fi

BRANCH="worktree-$SLUG"
if [ -n "$(git for-each-ref --format='%(refname:short)' "refs/heads/$BRANCH")" ]; then
  echo "o branch $BRANCH já existe. Escolha outro slug ou encerre o anterior" >&2
  echo "com scripts/conferir-branch.sh $BRANCH" >&2
  exit 2
fi
[ -n "$DESTINO" ] || DESTINO="$(dirname "$RAIZ")/$(basename "$RAIZ").worktrees/$SLUG"
[ -e "$DESTINO" ] && { echo "$DESTINO já existe" >&2; exit 2; }

# O diff sai ANTES de criar o worktree: se não houver nada a levar, melhor
# descobrir agora do que depois de montar tudo. `git diff HEAD` em vez de
# `git diff` porque o índice também é compartilhado e pode ter coisa staged.
REMENDO=""
NOVOS=()
if [ "$VAZIO" = 0 ]; then
  REMENDO="$(mktemp)"
  git diff HEAD -- "${CAMINHOS[@]}" > "$REMENDO" || { echo "git diff falhou" >&2; exit 2; }
  # Arquivo novo ainda não rastreado NÃO aparece em `git diff HEAD`, e autorar
  # trilha nova cria arquivo novo — sem isto o trabalho ficaria para trás em
  # silêncio. Copiados à mão de propósito: `git add -N` escreveria no índice,
  # que neste checkout é compartilhado.
  while IFS= read -r -d '' arq; do NOVOS+=("$arq"); done < <(
    git ls-files --others --exclude-standard -z -- "${CAMINHOS[@]}")
  if [ ! -s "$REMENDO" ] && [ "${#NOVOS[@]}" -eq 0 ]; then
    echo "nada mudou em: ${CAMINHOS[*]}" >&2
    echo "(se o trabalho ainda não começou, use --vazio)" >&2
    rm -f "$REMENDO"; exit 2
  fi
  if [ -s "$REMENDO" ]; then
    echo "--- diff a levar ---"
    git diff HEAD --stat -- "${CAMINHOS[@]}"
  fi
  if [ "${#NOVOS[@]}" -gt 0 ]; then
    echo "--- arquivos novos a copiar ---"
    printf '  %s\n' "${NOVOS[@]}"
  fi
fi

git fetch origin --quiet || { echo "fetch falhou; seguindo com o origin/main que há" >&2; }
echo "--- criando $DESTINO em $BRANCH (de origin/main) ---"
git worktree add -b "$BRANCH" "$DESTINO" origin/main >/dev/null || { echo "worktree add falhou" >&2; exit 2; }

if [ -n "$REMENDO" ] && [ -s "$REMENDO" ]; then
  if ! git -C "$DESTINO" apply "$REMENDO"; then
    echo "git apply falhou no worktree — o diff não se aplica sobre origin/main." >&2
    echo "o worktree ficou de pé em $DESTINO para você resolver à mão." >&2
    rm -f "$REMENDO"; exit 2
  fi
  rm -f "$REMENDO"
  echo "diff aplicado."
fi

if [ "${#NOVOS[@]}" -gt 0 ]; then
  for arq in "${NOVOS[@]}"; do
    mkdir -p "$DESTINO/$(dirname "$arq")" || { echo "mkdir falhou para $arq" >&2; exit 2; }
    cp -p "$arq" "$DESTINO/$arq" || { echo "cp falhou para $arq" >&2; exit 2; }
  done
  echo "${#NOVOS[@]} arquivo(s) novo(s) copiado(s)."
fi

echo "--- uv sync --all-extras (sem os extras o gate passa sem ter rodado) ---"
( cd "$DESTINO" && uv sync --all-extras --quiet ) || { echo "uv sync falhou" >&2; exit 2; }

# O gate roda inteiro e só então reporta: uma ida, o quadro todo. A ordem é a do
# CLAUDE.md §Comandos.
FALHOU=0
relatar() {
  local nome="$1"; shift
  if ( cd "$DESTINO" && "$@" >/dev/null 2>&1 ); then
    printf '  ok      %s\n' "$nome"
  else
    printf '  FALHOU  %s\n' "$nome"
    FALHOU=1
  fi
}
echo "--- gate em $DESTINO ---"
relatar "trilhas compilar --conferir" uv run trilhas compilar --conferir
relatar "pytest"                      uv run pytest -q
relatar "ruff check"                  uv run ruff check .
relatar "ruff format --check"         uv run ruff format --check .
relatar "mypy"                        uv run mypy

echo
echo "worktree: $DESTINO"
echo "branch:   $BRANCH"
if [ "$FALHOU" = 0 ]; then
  echo "gate verde. Falta, de dentro do worktree: commitar, push, abrir PR."
  echo "Depois do merge, a limpeza: scripts/sobras.sh e a skill encerrar-branch."
else
  echo "gate VERMELHO — veja acima qual etapa. Rode-a de dentro do worktree para"
  echo "ler a mensagem inteira; aqui a saída foi suprimida de propósito."
  exit 1
fi
