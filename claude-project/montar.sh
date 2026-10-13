#!/usr/bin/env bash
# Monta o conhecimento do projeto no claude.ai a partir do repositório.
#
# A fonte da verdade é o repositório; o conhecimento é derivado, como o
# catalogo.lock.json. Nada aqui se edita à mão — rode de novo e suba o resultado.
#
# Os documentos de docs/*.md entram todos, automaticamente: documento novo aparece
# no bundle sem mexer neste script. Nada aqui afirma o estado do projeto por conta
# própria — o estado sai de docs/README.md, do snapshot e da árvore de arquivos.
#
#   ./claude-project/montar.sh            # grava em claude-project/conhecimento/
#   DESTINO=/tmp/x ./claude-project/montar.sh
set -euo pipefail
shopt -s nullglob

raiz="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
destino="${DESTINO:-$raiz/claude-project/conhecimento}"
cd "$raiz"

rm -rf "$destino"
mkdir -p "$destino"

cabecalho() { # cabecalho <titulo> <origem...>
  local titulo="$1"; shift
  printf '<!-- Gerado por claude-project/montar.sh a partir de: %s\n' "$*"
  printf '     Não editar: a fonte é o repositório trilhas_estudos. -->\n\n'
  printf '# %s\n\n' "$titulo"
}

concatenar() { # concatenar <arquivo...> — com separador nomeando cada origem
  local arquivo
  for arquivo in "$@"; do
    printf '\n---\n\n<!-- origem: %s -->\n\n' "$arquivo"
    cat "$arquivo"
  done
}

embutir_yaml() { # embutir_yaml <arquivo...> — em bloco de código, com a origem
  local arquivo
  for arquivo in "$@"; do
    printf '\n## `%s`\n\n```yaml\n' "$arquivo"
    cat "$arquivo"
    printf '```\n'
  done
}

secao() { # secao <titulo-da-secao> <arquivo> — da linha "## <titulo>" até a próxima "## "
  awk -v alvo="## $1" '
    $0 == alvo { dentro = 1 }
    dentro && $0 != alvo && /^## / { exit }
    dentro { print }
  ' "$2"
}

# --- documentos: todos os de docs/, com CONTEXT renomeado para o que ele é -------
for documento in docs/*.md; do
  nome="$(basename "$documento")"
  case "$nome" in
    README.md) continue ;;  # vai junto das ADRs, em decisoes.md
    CONTEXT.md) saida="dominio-e-glossario.md"; titulo="Domínio e glossário" ;;
    *) saida="$nome"
       titulo="$(head -40 "$documento" | sed -n 's/^# //p' | head -1)"
       titulo="${titulo:-$nome}" ;;
  esac
  { cabecalho "$titulo" "$documento"; cat "$documento"; } > "$destino/$saida"
done

{ cabecalho "Decisões de arquitetura" docs/README.md "docs/adr/*.md"
  concatenar docs/README.md docs/adr/*.md; } \
  > "$destino/decisoes.md"

# --- catálogo e percurso ----------------------------------------------------------
{ cabecalho "Catálogo autorado (YAML)" "catalogo/**/*.yaml"
  printf 'Fonte da verdade do catálogo. O que a aplicação consome é o snapshot\n'
  printf 'compilado `catalogo.lock.json`, omitido aqui por ser derivado destes arquivos.\n'
  embutir_yaml catalogo/competencias/*.yaml catalogo/trilhas/*.yaml \
    catalogo/etapas/*.yaml catalogo/recursos/*.yaml; } \
  > "$destino/catalogo-autorado.md"

{ cabecalho "Percurso do estudante" "percurso/*.yaml"
  embutir_yaml percurso/*.yaml; } \
  > "$destino/percurso.md"

# --- estado do código -------------------------------------------------------------
{ cabecalho "Estado do código" "docs/README.md, catalogo.lock.json, src/, tests/, pyproject.toml, git"

  printf '## O que está construído\n\n'
  printf 'Extraído de `docs/README.md` — é lá que a ordem de construção é mantida.\n\n'
  secao "Ordem de construção implicada" docs/README.md

  printf '\n## Resumo do snapshot\n\n```\n'
  python3 - <<'PY'
import json, pathlib
d = json.loads(pathlib.Path("catalogo.lock.json").read_text(encoding="utf-8"))
print(f"catalogo_versao: {d['catalogo_versao']}  gerado_em: {d['gerado_em']}")
for chave in ("trilhas", "competencias", "etapas", "recursos"):
    print(f"{chave}: {len(d[chave])}")
print()
for t in sorted(d["trilhas"], key=lambda t: t["id"]):
    etapas = [e for e in d["etapas"] if e.get("trilha") == t["id"]]
    print(f"{t['id']}  rev {t.get('rev')}  {t['titulo']}  ({len(etapas)} etapas)")
PY

  printf '```\n\n## Módulos\n\n```\n'
  find src tests scripts -type f \( -name '*.py' -o -name '*.sh' \) \
    -not -path '*/__pycache__/*' -not -path '*/fixtures/*' | LC_ALL=C sort | while read -r f; do
    printf '%6s  %s\n' "$(wc -l < "$f")" "$f"
  done

  printf '```\n\n## Pontos de entrada\n\n```\n'
  sed -n '/^\[project.scripts\]/,/^$/p' pyproject.toml
  printf '```\n\n```\n'
  python3 -c 'import sys; sys.path.insert(0, "src"); from trilhas.catalogo.cli import main; main(["--help"])' 2>/dev/null || true
  printf '```\n\n```\n'
  python3 -c 'import sys; sys.path.insert(0, "src"); from trilhas.web.__main__ import main; main(["--help"])' 2>/dev/null || true

  printf '```\n\n## Último estado do repositório ao montar\n\n```\n'
  git log --oneline -12
  printf '```\n'; } \
  > "$destino/estado-do-codigo.md"

printf 'conhecimento em %s:\n' "${destino#"$raiz"/}"
for arquivo in "$destino"/*.md; do
  printf '  %-30s %6s linhas  %5s\n' "$(basename "$arquivo")" \
    "$(wc -l < "$arquivo")" "$(du -h "$arquivo" | cut -f1)"
done
printf '\nsuba estes arquivos no conhecimento do projeto e cole claude-project/instrucoes.md\n'
