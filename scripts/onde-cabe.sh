#!/usr/bin/env bash
# Responde, antes de autorar, as duas perguntas que decidem o recorte: esta obra
# já está no catálogo? e, se não, que trilhas e etapas da área poderiam abrigá-la?
# Só leitura.
#
# Existe porque descobrir isso custava três ou quatro idas ao disco, cada uma
# despejando um YAML inteiro no contexto — e a resposta útil são vinte linhas.
# A regra que ele serve está na memória do projeto: antes de autorar a partir de
# link colado, procure a OBRA (autor, título, ISBN, slug de `obra`), não o ASIN,
# porque edição diferente não é url equivalente.
#
# ELE SUBSTITUI A DESCOBERTA, NÃO A AUTORIA. A convenção deste repositório — o
# tom dos comentários, como se escreve um LIMITE DE VERIFICAÇÃO, por que uma
# fatia existe — mora na prosa dos arquivos, não no esquema. Antes de escrever
# em catalogo/recursos/<area>.yaml, leia o arquivo.
#
# A busca é por substring sem acento, então ela traz falso positivo de
# propósito — "ramos" casa "cinco ramos" num comentário de trilha. Por isso
# cada achado sai com arquivo:linha: quem lê julga, o script não filtra. Uso:
#
#   scripts/onde-cabe.sh Ramos                  # a obra já tem casa?
#   scripts/onde-cabe.sh --area computacao      # o que já há na área
#   scripts/onde-cabe.sh 9786555067163 --area computacao
#
# Saída: 0 = algum casamento (a obra provavelmente JÁ está no catálogo, ou foi
#         pedida só a área); 1 = nada casou (obra provavelmente nova);
#         2 = erro de uso.
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ" || { echo "não consegui entrar em $RAIZ" >&2; exit 2; }

AREA=""
TERMO=""
while [ $# -gt 0 ]; do
  case "$1" in
    --area) AREA="${2:?--area exige um nome, p.ex. computacao}"; shift 2 ;;
    -h|--ajuda) sed -n '2,26p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) echo "opção desconhecida: $1" >&2; exit 2 ;;
    *) [ -z "$TERMO" ] || { echo "informe um termo só (use aspas)" >&2; exit 2; }; TERMO="$1"; shift ;;
  esac
done
[ -n "$TERMO" ] || [ -n "$AREA" ] || { echo "uso: scripts/onde-cabe.sh <termo> | --area <area>" >&2; exit 2; }
[ -f catalogo.lock.json ] || { echo "catalogo.lock.json não existe — rode 'uv run trilhas compilar'" >&2; exit 2; }

python3 -I - "$TERMO" "$AREA" <<'PY'
import json
import pathlib
import re
import sys
import unicodedata

termo, area = sys.argv[1], sys.argv[2]
lock = json.load(open("catalogo.lock.json", encoding="utf-8"))


def pelado(s):
    """Sem acento e em minúsculas: 'Autômatos' tem de casar com 'automatos'."""
    return "".join(
        c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn"
    )


achou = False

if termo:
    alvo = pelado(termo)
    print(f"=== a obra já está no catálogo?  termo: {termo!r} ===")

    # 1. Os recursos do snapshot, que é o que o motor e a web consomem.
    casados = [
        r for r in lock["recursos"]
        if alvo in pelado(r["titulo"]) or alvo in pelado(r.get("obra") or "") or alvo in pelado(r.get("url") or "")
    ]
    if casados:
        achou = True
        print(f"{len(casados)} recurso(s) no snapshot:")
        for r in sorted(casados, key=lambda r: r["id"]):
            obra = r.get("obra") or "— sem obra —"
            print(f"  {r['id']}")
            print(f"     obra={obra}  etapa={r['etapa']}  custo={r['custo']}  status={r['status']}")
    else:
        print("nenhum recurso do snapshot casou.")

    # 2. O YAML de autoria, que pega comentário e ISBN que o lock não guarda.
    linhas = []
    for arq in sorted(pathlib.Path("catalogo").rglob("*.yaml")):
        for n, linha in enumerate(arq.read_text(encoding="utf-8").splitlines(), 1):
            if alvo in pelado(linha):
                linhas.append(f"  {arq}:{n}: {linha.strip()[:110]}")
    if linhas:
        achou = True
        print(f"{len(linhas)} linha(s) no YAML de autoria" + (" (10 primeiras)" if len(linhas) > 10 else "") + ":")
        print("\n".join(linhas[:10]))
    else:
        print("nenhuma linha do YAML de autoria casou.")

    if not achou:
        print("\nVEREDITO: nada casou — obra provavelmente nova.")
        print("Procure também pelo sobrenome do outro autor e pelo ISBN antes de concluir:")
        print("edição diferente da mesma obra não é recurso novo.")
    else:
        print("\nVEREDITO: há casamento. Confira se é a MESMA OBRA ou só outra edição")
        print("antes de criar recurso — e, se for a mesma, relate e pare.")

if area:
    print(f"\n=== o que a área {area!r} já tem ===")
    trilhas = [t for t in lock["trilhas"] if t["id"].startswith(f"trilha:{area}/")]
    etapas = {e["id"]: e for e in lock["etapas"]}
    por_etapa = {}
    for r in lock["recursos"]:
        por_etapa.setdefault(r["etapa"], []).append(r)

    if not trilhas:
        print(f"nenhuma trilha em trilha:{area}/ — seria área nova")
        print("(área nova pede entrada em SETOR_DA_AREA, src/trilhas/web/apresentar/comum.py)")
    for t in trilhas:
        achou = True
        print(f"\n{t['id']}  rev={t['rev']} {t['status']}")
        print(f"  {t['titulo']}")
        for eid in t["etapas"]:
            e = etapas.get(eid, {})
            recs = por_etapa.get(eid, [])
            obras = sorted({r.get("obra") or "sem-obra" for r in recs})
            marca = " (opcional)" if e.get("opcional") else ""
            print(f"  - {eid}{marca}  {len(recs)} recurso(s)")
            if obras:
                print(f"      obras: {', '.join(obras)}")

    arq = pathlib.Path("catalogo/recursos") / f"{area}.yaml"
    print(f"\narquivo de recursos: {arq}" + ("" if arq.exists() else "  (NÃO EXISTE — criar)"))
    exemplos = [r["id"] for r in lock["recursos"] if r["id"].startswith(f"rec:{area}/")][:3]
    if exemplos:
        print("convenção de id de recurso, como está na área:")
        for e in exemplos:
            print(f"  {e}")
    print("\nLEIA O ARQUIVO antes de escrever nele: a convenção está nos comentários.")

raise SystemExit(0 if achou or not termo else 1)
PY
