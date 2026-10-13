#!/usr/bin/env bash
# Diz se um branch pode ser apagado e se a árvore pode trocar de branch — sem
# apagar, trocar nem guardar nada. Só leitura.
#
# Existe porque `git branch -d` neste repositório mente por omissão: ele aceita
# apagar um branch "mesclado" ao *remote tracking ref* (origin/<branch>), que não
# é a main. O commit some do seu clone e sobrevive só no origin — e some de vez
# se alguém apagar o branch remoto depois. Uso:
#
#   scripts/conferir-branch.sh                 # confere o branch atual
#   scripts/conferir-branch.sh meu-branch
#   scripts/conferir-branch.sh --sem-rede      # não faz fetch
#   scripts/conferir-branch.sh --base main     # outra base (padrão: main)
#
# Saída: 0 = pode apagar o branch local; 1 = não pode; 2 = erro de uso.
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

BASE=main
ALVO=""
FETCH=1
while [ $# -gt 0 ]; do
  case "$1" in
    --sem-rede) FETCH=0; shift ;;
    --base) BASE="${2:?--base exige um nome}"; shift 2 ;;
    -h|--help) sed -n '2,15p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) echo "argumento desconhecido: $1" >&2; exit 2 ;;
    *) ALVO="$1"; shift ;;
  esac
done

vermelho() { printf '\033[31m%s\033[0m\n' "$*"; }
amarelo()  { printf '\033[33m%s\033[0m\n' "$*"; }
verde()    { printf '\033[32m%s\033[0m\n' "$*"; }

[ -n "$ALVO" ] || ALVO="$(git branch --show-current)"
if [ -z "$ALVO" ]; then
  echo "HEAD destacado e nenhum branch informado." >&2; exit 2
fi
[ "$FETCH" -eq 1 ] && git fetch -q origin 2>/dev/null

# Branch local já apagado: ainda pode haver ref de rastreio pendurada (3ª camada).
if ! git show-ref --verify --quiet "refs/heads/$ALVO"; then
  echo "branch local inexistente: $ALVO"
  if git show-ref --verify --quiet "refs/remotes/origin/$ALVO"; then
    if [ "$FETCH" -eq 0 ]; then
      amarelo "⚠ há ref de rastreio origin/$ALVO; rode sem --sem-rede para saber se é obsoleta"
      exit 1
    fi
    if [ -n "$(git ls-remote --heads origin "$ALVO" 2>/dev/null)" ]; then
      amarelo "⚠ o branch existe só no origin — apagar lá perde o que não estiver na base:"
      amarelo "    git log --oneline ${BASE}..origin/$ALVO"
    else
      amarelo "⚠ ref de rastreio OBSOLETA: origin/$ALVO não existe mais no servidor"
      amarelo "    git remote prune origin"
    fi
    exit 1
  fi
  verde "✓ não existe em lugar nenhum: local, remoto nem ref de rastreio"
  exit 0
fi

REMOTO="refs/remotes/origin/$ALVO"
BASE_REF="refs/remotes/origin/$BASE"
git show-ref --verify --quiet "$BASE_REF" || BASE_REF="refs/heads/$BASE"
git show-ref --verify --quiet "$BASE_REF" || { echo "base inexistente: $BASE" >&2; exit 2; }

# A existência do remoto se decide PERGUNTANDO AO SERVIDOR. A ref de rastreio
# (refs/remotes/origin/X) sobrevive à exclusão do branch no servidor até alguém
# rodar prune — confiar nela faz o script dizer "está no origin" sobre um branch
# que já não existe lá, e declarar reversível uma exclusão que perde trabalho.
tem_remoto=0
remoto_incerto=0
if [ "$FETCH" -eq 1 ]; then
  [ -n "$(git ls-remote --heads origin "$ALVO" 2>/dev/null)" ] && tem_remoto=1
elif git show-ref --verify --quiet "$REMOTO"; then
  tem_remoto=1
  remoto_incerto=1
fi

if [ "$ALVO" = "$BASE" ]; then
  echo "$ALVO é a própria base — não há o que apagar."
  exit 0
fi

echo "branch:  $ALVO"
echo "base:    ${BASE_REF#refs/}"
echo

# --- 1. O que existe aqui e não existe na base ---------------------------
mapfile -t EXCLUSIVOS < <(git rev-list "$ALVO" "^$BASE_REF")
problema=0

if [ "${#EXCLUSIVOS[@]}" -eq 0 ]; then
  verde "✓ nada exclusivo: tudo deste branch já está na base"
else
  echo "${#EXCLUSIVOS[@]} commit(s) fora da base:"
  for c in "${EXCLUSIVOS[@]}"; do
    if [ "$tem_remoto" -eq 1 ] && git merge-base --is-ancestor "$c" "$REMOTO" 2>/dev/null; then
      marca="[só no origin/$ALVO]"
      [ "$remoto_incerto" -eq 1 ] && marca="[ref local diz origin/$ALVO — NÃO confirmado no servidor]"
      printf '  %s  %-56s %s\n' \
        "$(git rev-parse --short "$c")" "$(git log -1 --format=%s "$c" | cut -c1-56)" "$marca"
    else
      printf '  %s  %-56s ' "$(git rev-parse --short "$c")" "$(git log -1 --format=%s "$c" | cut -c1-56)"
      vermelho "[CÓPIA ÚNICA — não está em lugar nenhum além deste clone]"
      problema=1
    fi
  done
  echo
  if [ "$problema" -eq 0 ] && [ "$remoto_incerto" -eq 1 ]; then
    amarelo "⚠ rodado com --sem-rede: a cópia remota NÃO foi confirmada no servidor."
    amarelo "  Rode sem --sem-rede antes de apagar qualquer coisa."
  elif [ "$problema" -eq 0 ]; then
    amarelo "⚠ apagar o branch LOCAL é reversível (os commits estão em origin/$ALVO),"
    amarelo "  mas NÃO apague o branch REMOTO antes de mesclá-lo à base."
  fi
fi

# --- 2. O branch está em uso em outro worktree? --------------------------
if git worktree list --porcelain | grep -qx "branch refs/heads/$ALVO" &&
   [ "$(git rev-parse --abbrev-ref HEAD)" != "$ALVO" ]; then
  vermelho "✗ este branch está em uso em outro worktree — apagar vai falhar"
  problema=1
fi

# --- 3. A árvore pode trocar de branch? ----------------------------------
echo
mapfile -t SUJOS < <(git status --porcelain -uall | sed 's/^...//')
if [ "${#SUJOS[@]}" -eq 0 ]; then
  verde "✓ árvore limpa: trocar de branch não perturba ninguém"
else
  amarelo "⚠ ${#SUJOS[@]} arquivo(s) não commitado(s) na árvore:"
  printf '    %s\n' "${SUJOS[@]:0:10}"
  [ "${#SUJOS[@]}" -gt 10 ] && echo "    … e mais $(( ${#SUJOS[@]} - 10 ))"
  echo
  amarelo "  Este checkout é compartilhado (CLAUDE.md §Git). Isso pode ser trabalho"
  amarelo "  ao vivo de outra sessão: NÃO use \`git stash\` para destravar a troca —"
  amarelo "  some da árvore dela no meio da edição. Peça que ela commite."
fi

# --- 4. Stash pendente ---------------------------------------------------
if [ -n "$(git stash list)" ]; then
  echo
  amarelo "⚠ há stash guardado (pode ser de outra sessão):"
  git stash list | sed 's/^/    /'
fi

# --- 5. Refs de rastreio obsoletas (3ª camada) ---------------------------
# `git branch -r` lê o clone, `git ls-remote` pergunta ao servidor. Apagar o
# branch remoto NÃO remove a ref local: ela fica listada por tempo indefinido.
if [ "$FETCH" -eq 1 ]; then
  SERVIDOR="$(git ls-remote --heads origin 2>/dev/null | sed 's|.*refs/heads/||')"
  if [ -n "$SERVIDOR" ]; then
    mapfile -t OBSOLETAS < <(
      git branch -r --format='%(refname:short)' |
        sed -n 's|^origin/||p' | grep -v '^HEAD$' |
        grep -vxF "$SERVIDOR"
    )
    if [ "${#OBSOLETAS[@]}" -gt 0 ]; then
      echo
      amarelo "⚠ ${#OBSOLETAS[@]} ref(s) de rastreio obsoleta(s) — não existem mais no servidor:"
      printf '    origin/%s\n' "${OBSOLETAS[@]}"
      amarelo "    git remote prune origin"
    fi
  fi
fi

echo
if [ "$problema" -ne 0 ]; then
  vermelho "NÃO PODE APAGAR — veja acima"
  exit 1
fi
# O veredito cobre as TRÊS camadas: anunciar só o local faz a pessoa limpar o
# clone e deixar a cópia do servidor para trás — a assimetria do §1 da skill.
verde "PODE APAGAR — e são exclusões separadas:"
if [ "$(git rev-parse --abbrev-ref HEAD)" = "$ALVO" ]; then
  verde "  git switch $BASE                        # ele está em HEAD"
fi
verde "  git branch -d $ALVO"

if [ "$tem_remoto" -eq 1 ]; then
  if [ "$FETCH" -eq 1 ] && [ -z "$(git ls-remote --heads origin "$ALVO" 2>/dev/null)" ]; then
    verde "  # o servidor já não tem este branch — nada a apagar lá"
    verde "  git remote prune origin                 # some a ref de rastreio"
  elif [ "${#EXCLUSIVOS[@]}" -gt 0 ]; then
    amarelo "  ⚠ NÃO apague o remoto: ele é a única cópia de ${#EXCLUSIVOS[@]} commit(s)"
    amarelo "    fora da base. Mescle primeiro; depois disso, aí sim:"
    amarelo "      git push origin --delete $ALVO && git remote prune origin"
  else
    verde "  git push origin --delete $ALVO"
    verde "  git remote prune origin                 # se a ref sobrar"
  fi
else
  verde "  # não há cópia remota: só a camada local existe"
fi
exit 0
