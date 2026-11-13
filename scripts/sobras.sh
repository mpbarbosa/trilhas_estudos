#!/usr/bin/env bash
# Inventaria o que este repositório tem de sobra — worktrees, branches locais,
# branches no servidor e refs de rastreio — classifica cada item e IMPRIME os
# comandos de limpeza SEM EXECUTAR NENHUM. Só leitura.
#
# Existe porque a limpeza é a parte mais mecânica do ciclo e a mais perigosa de
# automatizar: a skill encerrar-branch registra nove correções, seis delas vindas
# de alguém executar uma recomendação que lia bem, e observa que o erro aqui
# "falha na direção tranquilizadora" — um script que apaga imprime sucesso de
# qualquer jeito. Então este não apaga. Ele reúne o diagnóstico de todas as
# camadas numa ida e deixa a decisão para quem lê.
#
# Complementa scripts/conferir-branch.sh, que responde por UM branch; este varre
# tudo e diz o que é seguro, o que é decisão sua e o que não dá para conferir.
# Uso:
#
#   scripts/sobras.sh                # varre tudo (faz fetch)
#   scripts/sobras.sh --sem-rede     # não faz fetch; o veredito fica mais fraco
#
# Saída: 0 = nenhuma sobra; 1 = há sobra classificada (leia o relatório);
#         2 = erro de uso ou de ambiente.
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ" || { echo "não consegui entrar em $RAIZ" >&2; exit 2; }

BASE=main
FETCH=1
while [ $# -gt 0 ]; do
  case "$1" in
    --sem-rede) FETCH=0; shift ;;
    --base) BASE="${2:?--base exige um nome}"; shift 2 ;;
    -h|--ajuda) sed -n '2,24p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "opção desconhecida: $1" >&2; exit 2 ;;
  esac
done

vermelho() { printf '\033[31m%s\033[0m\n' "$*"; }
amarelo()  { printf '\033[33m%s\033[0m\n' "$*"; }
verde()    { printf '\033[32m%s\033[0m\n' "$*"; }

if [ "$FETCH" = 1 ]; then
  git fetch origin --quiet 2>/dev/null || echo "aviso: fetch falhou; o veredito usa o origin/$BASE que há" >&2
fi
git rev-parse --verify --quiet "origin/$BASE" >/dev/null || {
  echo "não existe origin/$BASE neste clone" >&2; exit 2; }

# PRs abertos, uma chamada só. Sem gh, o relatório diz que não conferiu.
PRS=""
TEM_GH=0
if command -v gh >/dev/null 2>&1; then
  if PRS="$(gh pr list --state open --json number,headRefName \
            --jq '.[] | "\(.headRefName) \(.number)"' 2>/dev/null)"; then
    TEM_GH=1
  fi
fi
pr_de() {
  [ "$TEM_GH" = 1 ] || { echo "?"; return; }
  printf '%s\n' "$PRS" | awk -v b="$1" '$1==b {print $2; achou=1} END {if(!achou) print "-"}'
}

SOBRAS=0
PRINCIPAL="$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")"

echo "base: origin/$BASE   checkout principal: $PRINCIPAL"
echo
echo "=== worktrees ==="
CAMINHO=""; CABECA=""; RAMO=""
classificar_worktree() {
  [ -n "$CAMINHO" ] || return 0
  [ "$CAMINHO" = "$PRINCIPAL" ] && { printf '  %s  (principal, não é sobra)\n' "$CAMINHO"; return 0; }
  SOBRAS=$((SOBRAS + 1))
  local sujo ignorado contido
  sujo="$(git -C "$CAMINHO" status --porcelain -uall 2>/dev/null | wc -l)"
  # Sem -uall de propósito: com ele um .venv vira milhares de linhas e enterra
  # o achado que importa.
  ignorado="$(git -C "$CAMINHO" status --porcelain --ignored 2>/dev/null | grep -c '^!!' || true)"
  if git merge-base --is-ancestor "$CABECA" "origin/$BASE" 2>/dev/null; then contido=sim; else contido=NÃO; fi
  printf '  %s\n' "$CAMINHO"
  printf '     branch=%s  contido_na_base=%s  nao_commitado=%s  ignorado=%s\n' \
    "${RAMO:-<destacado>}" "$contido" "$sujo" "$ignorado"
  if [ "$sujo" != 0 ]; then
    vermelho "     NÃO REMOVA: há trabalho não commitado, que pode ser de outra sessão."
  elif [ "$contido" = NÃO ]; then
    amarelo "     DECISÃO SUA: a ponta tem commit fora da base; publique antes de remover."
  else
    verde "     sobra de arrumação; o ignorado ($ignorado item) some junto, sem aviso:"
    printf '       git -C %s status --porcelain --ignored | grep "^!!"\n' "$CAMINHO"
    printf '       git worktree remove %s\n' "$CAMINHO"
  fi
}
while IFS= read -r linha; do
  case "$linha" in
    worktree\ *) classificar_worktree; CAMINHO="${linha#worktree }"; CABECA=""; RAMO="" ;;
    HEAD\ *) CABECA="${linha#HEAD }" ;;
    branch\ *) RAMO="${linha#branch refs/heads/}" ;;
  esac
done < <(git worktree list --porcelain)
classificar_worktree

echo
echo "=== branches locais (fora de $BASE) ==="
NENHUM=1
while IFS=' ' read -r nome sha; do
  [ "$nome" = "$BASE" ] && continue
  NENHUM=0; SOBRAS=$((SOBRAS + 1))
  preso="$(git worktree list --porcelain | awk -v b="refs/heads/$nome" '$0=="branch "b{print "sim"}')"
  if git merge-base --is-ancestor "$sha" "origin/$BASE" 2>/dev/null; then contido=sim; else contido=NÃO; fi
  pr="$(pr_de "$nome")"
  printf '  %s  contido=%s  pr_aberto=%s  preso_em_worktree=%s\n' "$nome" "$contido" "$pr" "${preso:-nao}"
  if [ -n "$preso" ]; then
    amarelo "     o worktree sai primeiro (git branch -d vai recusar)."
  elif [ "$contido" = NÃO ]; then
    vermelho "     NÃO APAGUE: tem commit fora da base. Publique: git push origin $nome"
  elif [ "$pr" = "?" ]; then
    amarelo "     NÃO CONSEGUI CONFERIR: sem gh não sei se há PR aberto. Confira antes:"
    printf '       gh pr list --state open --head %s\n' "$nome"
  elif [ "$pr" != "-" ]; then
    amarelo "     DECISÃO SUA: PR #$pr está aberto; fechá-lo é decisão de rumo."
  else
    verde "     pode apagar:  git branch -d $nome"
  fi
done < <(git for-each-ref --format='%(refname:short) %(objectname)' refs/heads)
[ "$NENHUM" = 1 ] && echo "  nenhum."

echo
echo "=== branches no servidor (git ls-remote, não git branch -r) ==="
NENHUM=1
while IFS=$'\t' read -r sha ref; do
  nome="${ref#refs/heads/}"
  [ "$nome" = "$BASE" ] && continue
  NENHUM=0; SOBRAS=$((SOBRAS + 1))
  pr="$(pr_de "$nome")"
  if ! git cat-file -e "${sha}^{commit}" 2>/dev/null; then
    # A assimetria da skill: ref de rastreio contida NÃO autoriza apagar, porque
    # o servidor pode ter andado desde ela.
    amarelo "  $nome  NÃO CONSEGUI CONFERIR: o objeto ${sha:0:8} não está neste clone."
    printf '     git fetch origin %s   e rode de novo\n' "$nome"
    continue
  fi
  if git merge-base --is-ancestor "$sha" "origin/$BASE" 2>/dev/null; then contido=sim; else contido=NÃO; fi
  printf '  %s  contido=%s  pr_aberto=%s\n' "$nome" "$contido" "$pr"
  if [ "$contido" = NÃO ]; then
    vermelho "     NÃO APAGUE: $(git rev-list --count "origin/$BASE..$sha" 2>/dev/null) commit(s) fora da base."
  elif [ "$pr" = "?" ]; then
    amarelo "     NÃO CONSEGUI CONFERIR: sem gh não sei se há PR aberto."
  elif [ "$pr" != "-" ]; then
    amarelo "     DECISÃO SUA: PR #$pr aberto."
  else
    verde "     pode apagar:  git push origin --delete $nome"
  fi
done < <(git ls-remote --heads origin 2>/dev/null)
[ "$NENHUM" = 1 ] && echo "  nenhum."

echo
echo "=== refs de rastreio órfãs (a camada que ninguém olha) ==="
NENHUM=1
SERVIDOR="$(git ls-remote --heads origin 2>/dev/null | sed 's#.*refs/heads/##')"
# --exclude em vez de grep: %(refname:short) encurta refs/remotes/origin/HEAD
# para "origin", sem barra, e um grep ingênuo inventa um branch chamado origin.
while IFS= read -r ref; do
  nome="${ref#origin/}"
  printf '%s\n' "$SERVIDOR" | grep -qxF "$nome" && continue
  NENHUM=0; SOBRAS=$((SOBRAS + 1))
  printf '  %s  (não existe mais no servidor)\n' "$ref"
done < <(git for-each-ref --format='%(refname:short)' \
         --exclude=refs/remotes/origin/HEAD refs/remotes/origin)
if [ "$NENHUM" = 1 ]; then
  echo "  nenhuma."
else
  echo "     git remote prune origin"
fi

echo
if [ "$TEM_GH" = 0 ]; then
  echo "aviso: gh indisponível ou não autenticado — pr_aberto saiu como '?' e"
  echo "NENHUM item foi classificado como seguro só por falta de PR."
fi
if [ "$SOBRAS" = 0 ]; then
  verde "nenhuma sobra."
  exit 0
fi
amarelo "$SOBRAS item(ns) de sobra. Nada foi apagado — os comandos acima são para você rodar"
echo "depois de reler o diagnóstico imediatamente antes de agir (a árvore muda entre"
echo "dois comandos). Por item, scripts/conferir-branch.sh <branch> dá o veredito."
exit 1
