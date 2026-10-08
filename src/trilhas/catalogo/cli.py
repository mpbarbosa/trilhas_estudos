"""CLI do catálogo: `trilhas validar` e `trilhas compilar`."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .carregar import carregar
from .compilar import compilar, estado_anterior, mudou
from .problemas import Problema, Severidade, tem_erro
from .validar import validar

NOME_DO_LOCK = "catalogo.lock.json"
RAIZ_PADRAO = Path("catalogo")


def lock_de(raiz: Path) -> Path:
    """O snapshot fica ao lado do diretório de autoria, não num caminho fixo.

    Um lock fixo faria `validar --catalogo outro/` comparar com o snapshot de outro
    catálogo e acusar remoção de tudo (§5.1).
    """
    return raiz.parent / NOME_DO_LOCK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="trilhas", description="Catálogo de trilhas de estudo")
    parser.add_argument("--catalogo", type=Path, default=RAIZ_PADRAO, help="diretório de autoria")
    parser.add_argument(
        "--lock",
        type=Path,
        default=None,
        help=f"snapshot compilado (padrão: {NOME_DO_LOCK} ao lado do catálogo)",
    )
    sub = parser.add_subparsers(dest="comando", required=True)
    sub.add_parser("validar", help="valida sem gerar snapshot")
    p_compilar = sub.add_parser("compilar", help="valida e grava o snapshot")
    p_compilar.add_argument(
        "--conferir",
        action="store_true",
        help="não grava; sai com 1 se o snapshot estiver desatualizado (uso em CI)",
    )

    args = parser.parse_args(argv)
    lock: Path = args.lock or lock_de(args.catalogo)

    anterior_bruto = _ler_lock(lock)
    catalogo, problemas = carregar(args.catalogo)
    anterior = estado_anterior(anterior_bruto)
    problemas += validar(catalogo, anterior)

    _reportar(problemas, catalogo_vazio=not catalogo.ids())
    if tem_erro(problemas):
        return 1
    if args.comando == "validar":
        return 0

    snapshot = compilar(catalogo, anterior)
    if not mudou(snapshot, anterior_bruto):
        print(f"catálogo inalterado (versão {anterior.versao}); snapshot preservado")
        return 0
    if args.conferir:
        print(f"snapshot desatualizado: {lock} precisa ser recompilado", file=sys.stderr)
        return 1

    lock.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(f"{lock}: versão {snapshot['catalogo_versao']}, {snapshot['hash'][:19]}…")
    return 0


def _ler_lock(caminho: Path) -> dict[str, object] | None:
    if not caminho.is_file():
        return None
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    return dados if isinstance(dados, dict) else None


def _reportar(problemas: list[Problema], *, catalogo_vazio: bool) -> None:
    erros = [p for p in problemas if p.severidade is Severidade.ERRO]
    avisos = [p for p in problemas if p.severidade is Severidade.AVISO]
    for problema in erros + avisos:
        destino = sys.stderr if problema.severidade is Severidade.ERRO else sys.stdout
        print(problema, file=destino)
    if erros:
        print(f"\n{len(erros)} erro(s), {len(avisos)} aviso(s)", file=sys.stderr)
    elif catalogo_vazio:
        print("catálogo vazio")
    else:
        print(f"catálogo válido — {len(avisos)} aviso(s)")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
