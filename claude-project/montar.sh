#!/usr/bin/env bash
# Monta o conhecimento do projeto no claude.ai a partir do repositório.
#
# A fonte da verdade é o repositório; o conhecimento é derivado, como o
# catalogo.lock.json. Nada aqui se edita à mão — rode de novo e suba o resultado.
#
#   ./claude-project/montar.sh            # grava em claude-project/conhecimento/
#   DESTINO=/tmp/x ./claude-project/montar.sh
set -euo pipefail

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

{ cabecalho "Domínio e glossário" docs/CONTEXT.md; cat docs/CONTEXT.md; } \
  > "$destino/01-dominio-e-glossario.md"

{ cabecalho "Catálogo: autoria, identidade e versionamento" docs/catalogo.md; cat docs/catalogo.md; } \
  > "$destino/02-catalogo.md"

{ cabecalho "Motor de sugestão (especificação v1)" docs/motor-de-sugestao.md; cat docs/motor-de-sugestao.md; } \
  > "$destino/03-motor-de-sugestao.md"

{ cabecalho "Decisões de arquitetura" docs/README.md "docs/adr/*.md"
  concatenar docs/README.md docs/adr/*.md; } \
  > "$destino/04-decisoes.md"

{ cabecalho "Catálogo autorado (YAML)" "catalogo/**/*.yaml"
  printf 'Fonte da verdade do catálogo. O que a aplicação consome é o snapshot\n'
  printf 'compilado `catalogo.lock.json`, omitido aqui por ser derivado destes arquivos.\n'
  shopt -s nullglob
  embutir_yaml catalogo/competencias/*.yaml catalogo/trilhas/*.yaml \
    catalogo/etapas/*.yaml catalogo/recursos/*.yaml
  shopt -u nullglob; } \
  > "$destino/05-catalogo-autorado.md"

{ cabecalho "Percurso do estudante" "percurso/*.yaml"
  printf 'Formato provisório: a persistência do percurso depende de decisão ainda\n'
  printf 'não tomada (ver 04-decisoes, ADR-0001). Espere que mude.\n'
  embutir_yaml percurso/*.yaml; } \
  > "$destino/06-percurso.md"

{ cabecalho "Estado do código" "src/, tests/, catalogo.lock.json, git"
  printf '## Resumo do snapshot\n\n```\n'
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
  find src tests -name '*.py' -not -path '*/__pycache__/*' | sort | while read -r f; do
    printf '%6s  %s\n' "$(wc -l < "$f")" "$f"
  done
  printf '```\n\n## Interface de linha de comando\n\n```\n'
  python3 -c 'import sys; sys.path.insert(0, "src"); from trilhas.catalogo.cli import main; main(["--help"])' \
    2>/dev/null || printf 'trilhas [--catalogo DIR] [--lock ARQ] {validar,compilar [--conferir]}\n'
  printf '```\n\n## Último estado do repositório ao montar\n\n```\n'
  git log --oneline -12
  printf '```\n'
  printf '\nO motor de sugestão (`src/trilhas/motor/`) **não existe ainda** — é a próxima\n'
  printf 'capacidade a construir, especificada em 03-motor-de-sugestao.\n'; } \
  > "$destino/07-estado-do-codigo.md"

printf 'conhecimento em %s:\n' "${destino#"$raiz"/}"
for arquivo in "$destino"/*.md; do
  printf '  %-34s %6s linhas  %5s\n' "$(basename "$arquivo")" \
    "$(wc -l < "$arquivo")" "$(du -h "$arquivo" | cut -f1)"
done
printf '\nsuba estes arquivos no conhecimento do projeto e cole claude-project/instrucoes.md\n'
