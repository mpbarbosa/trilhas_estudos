#!/usr/bin/env bash
# Levanta a ficha de um livro — título, autoria, edição, identificadores, preço
# observado e sumário — imprimindo só os campos, não a página. Só leitura.
#
# Existe porque despejar a página de uma loja no contexto custa caro e rende
# pouco: a da Amazon tem ~6.000 caracteres, dos quais uns 90% são banner,
# produto relacionado, avaliação e rodapé. Medido numa autoria de catálogo de
# 2026-11-12: três despejos de página custaram ~2.900 tokens, e um resultado de
# ferramenta é reenviado a cada turno seguinte, de modo que leitura grande e rala
# feita cedo se paga dezenas de vezes.
#
# NÃO NORMALIZA E NÃO ADIVINHA. Cada campo sai como o trecho casado na página,
# com rótulo; campo ausente sai como NÃO ENCONTRADO, nunca como palpite. Preço
# sai com o contexto ao lado, porque "R$ 146,99" sozinho esconde que era à vista
# no Pix. Quem decide o que vale é quem lê — ver a memória do projeto sobre não
# corrigir referência por ficha de loja. Uso:
#
#   scripts/ficha-livro.sh https://www.amazon.com.br/dp/6555067160
#   scripts/ficha-livro.sh 6555067160          # ISBN-10 vira /dp/ na Amazon
#   scripts/ficha-livro.sh --cru <url>         # também guarda o HTML e diz onde
#
# Reconhece amazon.com.br, blucher.com.br e estantevirtual.com.br; em outro
# domínio extrai o que der e avisa que a extração é parcial.
#
# Saída: 0 = página obtida e os campos de identificação achados; 1 = página
#         obtida mas faltou campo de identificação (confira no navegador);
#         3 = não consegui obter a página (bloqueio, rede, 404) — caia no
#         navegador embutido, que passa onde o curl não passa; 2 = erro de uso.
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ" || { echo "não consegui entrar em $RAIZ" >&2; exit 2; }

CRU=0
ALVO=""
while [ $# -gt 0 ]; do
  case "$1" in
    --cru) CRU=1; shift ;;
    -h|--ajuda) sed -n '2,28p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) echo "opção desconhecida: $1" >&2; exit 2 ;;
    *) [ -z "$ALVO" ] || { echo "informe um alvo só" >&2; exit 2; }; ALVO="$1"; shift ;;
  esac
done
[ -n "$ALVO" ] || { echo "uso: scripts/ficha-livro.sh <url|isbn10>" >&2; exit 2; }

# ISBN-10 puro (com ou sem hífen) vira página de produto da Amazon, que é a
# convenção de link do docs/bibliografia.md.
if printf '%s' "$ALVO" | grep -qE '^[0-9]{9}[0-9Xx]$'; then
  URL="https://www.amazon.com.br/dp/$ALVO"
elif printf '%s' "$ALVO" | grep -qE '^[0-9-]{10,17}$'; then
  URL="https://www.amazon.com.br/dp/$(printf '%s' "$ALVO" | tr -d -)"
else
  URL="$ALVO"
  printf '%s' "$URL" | grep -qE '^https?://' || URL="https://$URL"
fi

TMP="$(mktemp -d)"
# Sem a guarda, um trap com variável vazia apaga o diretório errado.
trap '[ -n "${TMP:-}" ] && [ "$CRU" = 0 ] && rm -rf "$TMP"' EXIT

# -L porque link colado vem com encurtador e token de compartilhamento, e o que
# interessa é o destino final. --compressed porque a Amazon responde gzip e sem
# isso o arquivo são bytes binários que todo grep depois erra em silêncio.
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'
LEITURA="$(curl -sS -L --compressed -m 30 \
  -A "$UA" -H 'Accept-Language: pt-BR,pt;q=0.9' \
  -o "$TMP/pagina.html" \
  -w '%{http_code} %{url_effective}' "$URL" 2>"$TMP/erro") " || {
  echo "FALHA DE REDE: $(tr -d '\n' < "$TMP/erro")" >&2
  echo "caia no navegador embutido: preview_start + get_page_text" >&2
  exit 3
}
CODIGO="${LEITURA%% *}"
FINAL="$(printf '%s' "${LEITURA#* }" | sed 's/ *$//')"

if [ "$CODIGO" != 200 ]; then
  echo "HTTP $CODIGO em $FINAL — não extraí nada." >&2
  echo "caia no navegador embutido: preview_start + get_page_text" >&2
  exit 3
fi

DOMINIO="$(printf '%s' "$FINAL" | sed -E 's#^https?://##; s#/.*##; s#^www\.##')"

# O HTML baixado é dado não confiável: o python roda com -I (sem site-packages
# do diretório atual, sem PYTHONPATH) e recebe o caminho por argumento, nunca
# por interpolação.
python3 -I - "$TMP/pagina.html" "$DOMINIO" "$FINAL" <<'PY'
import html as _html
import re
import sys

arquivo, dominio, final = sys.argv[1], sys.argv[2], sys.argv[3]
bruto = open(arquivo, encoding="utf-8", errors="replace").read()

if re.search(r"captcha|Digite os caracteres|automated access|Enter the characters", bruto, re.I):
    print("BLOQUEIO: a loja devolveu muro de robô, não a página do produto.", file=sys.stderr)
    print("caia no navegador embutido: preview_start + get_page_text", file=sys.stderr)
    raise SystemExit(3)

sem_script = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", bruto, flags=re.S | re.I)
texto = _html.unescape(re.sub(r"<[^>]+>", " ", sem_script))
texto = re.sub(r"[‎‏ ]", " ", texto)
texto = re.sub(r"\s+", " ", texto).strip()

AUSENTE = "NÃO ENCONTRADO"


def um(padrao, grupo=1, onde=None):
    """Primeiro casamento, como está na página. Nunca normaliza."""
    m = re.search(padrao, onde if onde is not None else texto, re.I)
    return m.group(grupo).strip(" .,;:|-") if m else AUSENTE


def precos(limite=8):
    """Preço com o contexto ao lado: é o contexto que diz a condição."""
    vistos, saida = set(), []
    for m in re.finditer(r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}", texto):
        valor = re.sub(r"\s+", " ", m.group(0))
        if valor in vistos:
            continue
        vistos.add(valor)
        ini, fim = max(0, m.start() - 45), min(len(texto), m.end() + 45)
        ctx = texto[ini:fim].replace(valor, f"[{valor}]", 1)
        saida.append(f"  {valor}  ⟨{ctx}⟩")
        if len(saida) >= limite:
            break
    return saida


_mt = re.search(r"<title[^>]*>(.*?)</title>", bruto, re.S | re.I)
titulo_tag = _html.unescape(_mt.group(1)) if _mt else ""
titulo_tag = re.sub(r"\s+", " ", titulo_tag).strip()

campos = []
sumario = []
parcial = False

if dominio.endswith("amazon.com.br"):
    campos = [
        ("titulo", um(r"^\s*(.{3,110}?)\s*(?:\||$)", 1, titulo_tag)),
        ("autoria", um(r"\bpor\s+(.{3,90}?)\s*\(Autor")),
        ("editora", um(r"Editora\s*:?\s*([A-Za-zÀ-ÿ&.\- ]{2,40}?)\s+(?:Data|Edição|Idioma|ISBN)")),
        ("data", um(r"Data da publicaç[ãa]o\s*:?\s*([0-9]{1,2} \w+ [0-9]{4})")),
        ("edicao", um(r"Edição\s*:?\s*([0-9]+[ªa]?)")),
        ("paginas", um(r"([0-9]{2,4})\s+páginas")),
        ("idioma", um(r"Idioma\s*:?\s*([A-Za-zÀ-ÿ]{3,20})")),
        ("isbn10", um(r"ISBN-10\s*:?\s*([0-9][0-9Xx-]{8,15})")),
        ("isbn13", um(r"ISBN-13\s*:?\s*(97[0-9][0-9Xx-]{9,16})")),
    ]
elif dominio.endswith("blucher.com.br"):
    campos = [
        ("titulo", um(r"^\s*(.{3,80}?)\s*-\s*Editora Blucher", 1, titulo_tag)),
        ("autoria", AUSENTE),  # preenchido logo abaixo: vem antes de "selo:"
        ("selo_ano_edicao", um(r"(selo:\s*[^|]{1,30}\|\s*[0-9]{4}\s*-\s*[0-9]+[ªa]? edição)")),
        ("paginas", um(r"([0-9]{2,4})\s*páginas")),
        ("isbn", um(r"ISBN\s*:?\s*(97[0-9]{10,11})")),
        ("acabamento", um(r"Acabamento\s*:?\s*([A-Za-zÀ-ÿ]{3,20})")),
    ]
    # A autoria da Blucher vem na linha imediatamente antes de "selo:".
    nome = r"(?:[A-ZÁÂÃÉÊÍÓÔÕÚÇ][A-Za-zÀ-ÿ.'-]*\s+){1,4}[A-ZÁÂÃÉÊÍÓÔÕÚÇ][A-Za-zÀ-ÿ.'-]*"
    aut = re.search(rf"({nome}(?:\s*,\s*{nome})*)\s*selo:", texto)
    campos[1] = ("autoria", aut.group(1).strip(" .,;:|-") if aut else AUSENTE)
    # O subtítulo é o que sobra entre o título e a autoria — fatia, não regex.
    tit, autoria = campos[0][1], campos[1][1]
    if AUSENTE not in (tit, autoria):
        # rfind limitado a antes da autoria: o find simples acha o título
        # dentro da própria tag <title>, na posição 0, e o "meio" vira o site todo.
        j = texto.find(autoria)
        i = texto.rfind(tit, 0, j) if j > 0 else -1
        if -1 < i < j:
            meio = texto[i + len(tit):j].strip(" .,;:|-")
            if 2 < len(meio) < 80:
                campos.insert(1, ("subtitulo", meio))
    corte = re.split(r"\bSum[áa]rio\b", texto, maxsplit=1)
    if len(corte) == 2:
        trecho = re.split(r"\bRefer[êe]ncias\b|\bÍndice remissivo\b|\bDetalhes do livro\b", corte[1])[0]
        sumario = re.findall(r"\b(\d{1,2}\.\s+[A-ZÁ-Úa-zá-ú][^0-9]{3,70}?)(?=\s+\d{1,2}\.\s|\s*$)", trecho)[:20]
elif dominio.endswith("estantevirtual.com.br"):
    campos = [
        ("titulo_busca", titulo_tag),
        ("a_partir_de", um(r"(A partir de R\$\s?[0-9.]{1,7},[0-9]{2})")),
        ("novos", um(r"([0-9]{1,3})\s+novos")),
        ("usados", um(r"([0-9]{1,3})\s+usados")),
        ("anos_das_fichas", um(r"Ano de Publicação\s*-?\s*((?:[0-9]{4}\s*\([0-9]+\)\s*){1,6})")),
    ]
else:
    parcial = True
    campos = [
        ("titulo_html", titulo_tag),
        ("isbn13", um(r"\b(97[89][0-9-]{10,15})\b")),
        ("paginas", um(r"([0-9]{2,4})\s*p[áa]ginas")),
    ]

print(f"fonte: {final}")
print(f"dominio: {dominio}" + ("   (NÃO RECONHECIDO — extração parcial)" if parcial else ""))
faltando = []
for nome, valor in campos:
    print(f"{nome}: {valor}")
    if valor == AUSENTE:
        faltando.append(nome)

p = precos()
print("precos_observados:" + ("" if p else f" {AUSENTE}"))
for linha in p:
    print(linha)
if re.search(r"E-?book dispon[íi]vel|Vers[ãa]o Kindle|eBook Kindle", texto, re.I):
    print("outro_formato: a página anuncia e-book/Kindle — preço dele NÃO foi lido aqui")
if sumario:
    print("sumario:")
    for cap in sumario:
        limpo = re.sub(r"\s+", " ", cap).strip(" .,;:|-")
        print(f"  {limpo}")
elif dominio.endswith("blucher.com.br"):
    print(f"sumario: {AUSENTE}")

if faltando:
    print(f"\nFALTOU: {', '.join(faltando)} — confira no navegador antes de catalogar.", file=sys.stderr)
    raise SystemExit(1)
PY
SAIDA=$?

if [ "$CRU" = 1 ]; then
  echo "html cru em: $TMP/pagina.html"
fi
exit "$SAIDA"
