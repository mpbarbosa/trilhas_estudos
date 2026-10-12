"""`trilhas-web` — sobe a interface em localhost.

Sem autenticação e sem exposição em rede: a interface é local e para um estudante
(ADR-0007). Expor em rede exige decisão nova.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .dados import NOME_DO_LOCK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="trilhas-web", description="Interface de trilhas")
    parser.add_argument(
        "--lock",
        type=Path,
        default=Path(NOME_DO_LOCK),
        help=f"snapshot compilado (padrão: ./{NOME_DO_LOCK})",
    )
    parser.add_argument("--porta", type=int, default=8000)
    parser.add_argument("--host", default="127.0.0.1", help="padrão: só localhost")
    args = parser.parse_args(argv)

    try:
        import uvicorn
    except ModuleNotFoundError:
        print("extra `web` não instalado — use: uv run --extra web trilhas-web")
        return 1

    from .app import criar_app

    print(f"http://{args.host}:{args.porta}  (catálogo: {args.lock})")
    uvicorn.run(criar_app(lock=args.lock.resolve()), host=args.host, port=args.porta)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
