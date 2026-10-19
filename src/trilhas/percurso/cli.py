"""CLI de escrita do percurso: `trilhas-percurso` (ADR-0008).

Fecha o laço do motor pela linha de comando — ação vira evento, evento vira projeção,
projeção é entrada do motor. A interface web é a fase 2 de docs/interface.md e usará
exatamente estes mesmos `registrar.*` e `Repositorio`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from trilhas.catalogo.carregar import do_snapshot
from trilhas.catalogo.modelo import Catalogo, Etapa, Nivel
from trilhas.motor.modelo import Percurso, Reacao
from trilhas.web.percurso import carregar_percurso

from . import registrar
from .eventos import Evento, Registro
from .migrar import eventos_do_yaml
from .projecao import Percorrido, evidencias_de, montar_percurso, percorridos_de
from .repositorio import Repositorio

LOCK_PADRAO = Path("catalogo.lock.json")
PERCURSO_PADRAO = Path("percurso")
ESTUDANTE_PADRAO = "est:mpb"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="trilhas-percurso", description="Registra fatos do percurso de um estudante"
    )
    parser.add_argument("--percurso", type=Path, default=PERCURSO_PADRAO)
    parser.add_argument("--lock", type=Path, default=LOCK_PADRAO)
    parser.add_argument("--estudante", default=ESTUDANTE_PADRAO)
    sub = parser.add_subparsers(dest="comando", required=True)

    p = sub.add_parser("iniciar", help="marca uma etapa como em andamento")
    p.add_argument("etapa")
    p.add_argument(
        "--recurso",
        help="id do recurso pelo qual se está estudando; tem de ser um recurso desta etapa",
    )

    p = sub.add_parser("concluir", help="conclui a etapa e grava a evidência do que ela ensina")
    p.add_argument("etapa")

    p = sub.add_parser("abandonar", help="abandona a etapa; evidência já emitida permanece")
    p.add_argument("etapa")
    p.add_argument("--motivo")

    p = sub.add_parser(
        "percorrer",
        help="registra material percorrido de ponta a ponta; não emite evidência",
    )
    p.add_argument("recurso")

    p = sub.add_parser("sei", help="autoavaliação de competência adquirida fora do sistema")
    p.add_argument("competencia")
    p.add_argument("nivel", choices=[str(n) for n in Nivel if n is not Nivel.DESCONHECE])

    p = sub.add_parser(
        "retratar", help="declara que uma evidência foi emitida por engano (ADR-0014)"
    )
    p.add_argument("seq", type=int, help="o #seq da evidência; `mostrar` os lista")
    p.add_argument("--motivo")

    p = sub.add_parser("reagir", help="feedback sobre uma sugestão")
    p.add_argument("etapa")
    p.add_argument("reacao", choices=[str(r) for r in Reacao])
    p.add_argument("--motivo")

    sub.add_parser("mostrar", help="imprime a projeção atual do percurso")
    p = sub.add_parser("exportar", help="grava o log em JSONL para commitar e auditar")
    p.add_argument("--saida", type=Path, help="padrão: <percurso>/<estudante>.log.jsonl")
    p.add_argument(
        "--conferir",
        action="store_true",
        help="não grava; sai com 1 se a exportação estiver atrás do log (uso local)",
    )
    sub.add_parser(
        "importar",
        help="converte os fatos declarados no YAML em eventos, com as datas de lá",
    )

    args = parser.parse_args(argv)

    saida_padrao = args.percurso / f"{args.estudante.replace(':', '-')}.log.jsonl"

    # `--conferir` sem log local não tem com o que comparar — e abrir o repositório
    # criaria um banco vazio, fazendo a conferência parecer "exportação adiantada".
    # Acontece em qualquer clone novo, porque o banco está no .gitignore (ADR-0008).
    if args.comando == "exportar" and args.conferir:
        banco = args.percurso / Repositorio.NOME_DO_ARQUIVO
        if not banco.is_file():
            print(f"sem log em {banco}; nada a conferir")
            return 0

    catalogo = _catalogo(args.lock)
    base = _base(args.percurso, args.estudante)

    with Repositorio.em_diretorio(args.percurso) as repo:
        if args.comando == "mostrar":
            guardados = repo.registros(args.estudante)
            _mostrar(
                montar_percurso(base, guardados),
                percorridos_de(guardados),
                catalogo,
                guardados,
            )
            return 0

        if args.comando == "retratar":
            # Precisa do log, não do catálogo: o alvo é um fato gravado. Branch próprio
            # por isso — `_eventos` recebe catálogo e percurso declarado, não registros.
            guardados = repo.registros(args.estudante)
            problema = registrar.conferir_retratacao(args.seq, guardados)
            if problema is not None:
                print(problema, file=sys.stderr)
                return 1
            gravado = repo.anexar(
                args.estudante, registrar.retratar_evidencia(args.seq, motivo=args.motivo)
            )
            for registro in gravado:
                print(f"#{registro.seq} {type(registro.evento).__name__} retrata #{args.seq}")
            return 0

        if args.comando == "exportar":
            texto = repo.exportar(args.estudante)
            saida = args.saida or saida_padrao
            if args.conferir:
                return _conferir_exportacao(saida, texto)
            saida.write_text(texto, encoding="utf-8")
            print(f"{saida}: {len(texto.splitlines())} fato(s)")
            return 0

        if args.comando == "importar":
            fatos = eventos_do_yaml(_yaml_do_estudante(args.percurso, args.estudante))
            if not fatos:
                print("nada declarado no YAML para importar")
                return 0
            if repo.registros(args.estudante):
                print(
                    "o log já tem fatos deste estudante; importar de novo duplicaria "
                    "história. Nada foi gravado.",
                    file=sys.stderr,
                )
                return 1
            for registro in repo.importar(args.estudante, fatos):
                print(f"#{registro.seq} {type(registro.evento).__name__} {registro.dia}")
            return 0

        eventos, erro = _eventos(args, catalogo, base)
        if erro:
            print(erro, file=sys.stderr)
            return 1
        if not eventos:
            print("nada a registrar")
            return 0

        gravados = repo.anexar(args.estudante, eventos)
        for registro in gravados:
            print(f"#{registro.seq} {type(registro.evento).__name__}")
        return 0


def _eventos(
    args: argparse.Namespace, catalogo: Catalogo, base: Percurso
) -> tuple[list[Evento], str | None]:
    if args.comando in {"iniciar", "concluir", "abandonar"}:
        etapa = catalogo.etapas.get(args.etapa)
        if etapa is None:
            return [], f"etapa desconhecida no catálogo: {args.etapa}"
        if args.comando == "iniciar" and args.recurso is not None:
            erro = registrar.conferir_recurso(args.recurso, catalogo, etapa)
            if erro is not None:
                return [], erro
        return _de_etapa(args, etapa), None

    if args.comando == "percorrer":
        erro = registrar.conferir_recurso_avulso(args.recurso, catalogo)
        if erro is not None:
            return [], erro
        return registrar.percorrer_recurso(catalogo.recursos[args.recurso]), None

    if args.comando == "sei":
        if args.competencia not in catalogo.competencias:
            return [], f"competência desconhecida no catálogo: {args.competencia}"
        return registrar.registrar_autoavaliacao(args.competencia, Nivel.de_texto(args.nivel)), None

    if args.comando == "reagir":
        return registrar.dar_feedback(args.etapa, Reacao(args.reacao), motivo=args.motivo), None

    return [], f"comando desconhecido: {args.comando}"


def _de_etapa(args: argparse.Namespace, etapa: Etapa) -> list[Evento]:
    if args.comando == "iniciar":
        return registrar.iniciar_etapa(etapa, recurso=args.recurso)
    if args.comando == "concluir":
        return registrar.concluir_etapa(etapa)
    return registrar.abandonar_etapa(etapa, motivo=args.motivo)


def _conferir_exportacao(saida: Path, esperado: str) -> int:
    """Compara o arquivo exportado com o log, sem gravar nada.

    A exportação é instantâneo: cada fato novo a deixa atrás, e nada avisa. Isto é o
    equivalente de `trilhas compilar --conferir` para o percurso — com uma diferença
    que importa: **não serve para CI**. O banco é estado local e está fora do git
    (ADR-0008), então no runner não há log com que comparar. O lugar disto é a máquina
    de quem estuda, antes de commitar.
    """
    atual = saida.read_text(encoding="utf-8") if saida.is_file() else ""
    if atual == esperado:
        print(f"{saida}: em dia ({len(esperado.splitlines())} fato(s))")
        return 0

    nossos = len(esperado.splitlines())
    deles = len(atual.splitlines())
    if not saida.is_file():
        motivo = "não existe"
    elif deles < nossos:
        motivo = f"tem {deles} fato(s), o log tem {nossos}"
    elif deles > nossos:
        motivo = f"tem {deles} fato(s), mais que os {nossos} do log"
    else:
        motivo = f"divergente do log ({nossos} fato(s) em ambos)"
    print(
        f"{saida}: {motivo}; rode `trilhas-percurso exportar` e commite junto",
        file=sys.stderr,
    )
    return 1


def _catalogo(lock: Path) -> Catalogo:
    if not lock.is_file():
        return Catalogo()
    catalogo, _ = do_snapshot(json.loads(lock.read_text(encoding="utf-8")))
    return catalogo


def _arquivo_do_estudante(diretorio: Path, estudante: str) -> Path | None:
    alvo = diretorio / f"{estudante.replace(':', '-')}.yaml"
    if alvo.is_file():
        return alvo
    for candidato in sorted(diretorio.glob("*.yaml")) if diretorio.is_dir() else []:
        lido = carregar_percurso(candidato)
        if lido is not None and lido.estudante_id == estudante:
            return candidato
    return None


def _yaml_do_estudante(diretorio: Path, estudante: str) -> dict[str, object]:
    arquivo = _arquivo_do_estudante(diretorio, estudante)
    if arquivo is None:
        return {}
    dados = yaml.safe_load(arquivo.read_text(encoding="utf-8"))
    return dados if isinstance(dados, dict) else {}


def _base(diretorio: Path, estudante: str) -> Percurso:
    """O estado declarado em YAML. Sem arquivo, um percurso vazio — não um erro."""
    arquivo = _arquivo_do_estudante(diretorio, estudante)
    if arquivo is None:
        return Percurso(estudante_id=estudante)
    return carregar_percurso(arquivo) or Percurso(estudante_id=estudante)


def _mostrar(
    percurso: Percurso,
    percorridos: tuple[Percorrido, ...],
    catalogo: Catalogo,
    registros: list[Registro],
) -> None:
    print(f"estudante: {percurso.estudante_id}")
    print(f"matrículas: {len(percurso.matriculas)}")
    print("competências dominadas:")
    for c in percurso.competencias or ():
        print(
            f"  {c.competencia:46} {c.nivel!s:14} {c.ultima_evidencia_em}  conf {c.confianca:.2f}"
        )
    if not percurso.competencias:
        print("  (nenhuma — toda competência exige evidência)")
    print("progresso:")
    for p in percurso.progresso or ():
        print(f"  {p.etapa:46} {p.estado!s:14} {p.atualizado_em}")
    if not percurso.progresso:
        print("  (nenhum)")
    if percorridos:
        print("recursos percorridos:")
        for r in percorridos:
            print(f"  {r.recurso:46} rev {r.recurso_rev:<3} {r.percorrido_em}")
        _mostrar_obras(percorridos, catalogo)
    if percurso.feedback:
        print("feedback:")
        for f in percurso.feedback:
            print(f"  {f.etapa:46} {f.reacao!s:14} {f.em}")
    _mostrar_evidencias(registros)


def _mostrar_evidencias(registros: list[Registro]) -> None:
    """Lista as evidências com seu `seq`, marcando as retratadas.

    É o que torna `retratar` usável: o alvo é um `seq`, e sem isto a única forma de
    achá-lo seria ler o JSONL à mão (ADR-0014).

    A varredura é de `projecao.evidencias_de` — a **mesma** que a tela da competência
    projeta (ADR-0015). Duas listas de evidência montadas em lugares diferentes dariam
    dois `seq` para o mesmo fato na hora em que uma delas errasse a retratação.
    """
    evidencias = evidencias_de(registros)
    if not evidencias:
        return
    print("evidências:")
    for e in evidencias:
        marca = " RETRATADA" if e.retratada else ""
        print(f"  #{e.seq:<5} {e.competencia:40} {e.nivel!s:14} {e.em} {e.origem!s}{marca}")


def _mostrar_obras(percorridos: tuple[Percorrido, ...], catalogo: Catalogo) -> None:
    """Agrupa as fatias percorridas por obra, contra o catálogo de **hoje** (ADR-0012).

    É o que responde "li este livro" em vez de listar sete ids soltos. O agrupamento não
    está no fato de propósito: `obra` é apresentação, e resolvê-la na leitura é o que
    mantém o renomear-obra mecânico de ADR-0009.
    """
    vistos = {p.recurso for p in percorridos}
    fatias: dict[str, list[str]] = {}
    for recurso in catalogo.recursos.values():
        if recurso.obra is not None:
            fatias.setdefault(recurso.obra, []).append(recurso.id)
    tocadas = {
        obra: sorted(vistos.intersection(ids)) for obra, ids in fatias.items() if vistos & set(ids)
    }
    if not tocadas:
        return
    print("obras:")
    for obra, lidas in sorted(tocadas.items()):
        total = len(fatias[obra])
        marca = "completa" if len(lidas) == total else "em parte"
        print(f"  {obra:46} {len(lidas)}/{total} fatia(s)  {marca}")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
