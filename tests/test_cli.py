"""A CLI é a interface de CI: o código de saída é o contrato."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from trilhas.catalogo.cli import lock_de, main


def rodar(*args: str) -> int:
    return main(list(args))


def test_catalogo_real_do_projeto_e_valido(catalogo_real: Path) -> None:
    assert rodar("--catalogo", str(catalogo_real), "validar") == 0


def test_fixture_e_valido(fixture_catalogo: Path) -> None:
    assert rodar("--catalogo", str(fixture_catalogo), "validar") == 0


def test_compilar_grava_snapshot(fixture_catalogo: Path, tmp_path: Path) -> None:
    lock = tmp_path / "catalogo.lock.json"
    assert rodar("--catalogo", str(fixture_catalogo), "--lock", str(lock), "compilar") == 0

    snapshot = json.loads(lock.read_text(encoding="utf-8"))
    assert snapshot["catalogo_versao"] == 1
    assert snapshot["hash"].startswith("sha256:")
    assert len(snapshot["trilhas"]) == 2
    assert len(snapshot["competencias"]) == 6


def test_recompilar_sem_mudanca_preserva_versao(fixture_catalogo: Path, tmp_path: Path) -> None:
    lock = tmp_path / "catalogo.lock.json"
    args = ("--catalogo", str(fixture_catalogo), "--lock", str(lock), "compilar")
    rodar(*args)
    primeiro = lock.read_text(encoding="utf-8")
    assert rodar(*args) == 0
    assert lock.read_text(encoding="utf-8") == primeiro


def test_conferir_falha_quando_o_snapshot_esta_desatualizado(
    fixture_catalogo: Path, tmp_path: Path
) -> None:
    lock = tmp_path / "catalogo.lock.json"
    assert rodar("--catalogo", str(fixture_catalogo), "--lock", str(lock), "compilar") == 0

    # remove uma entidade do snapshot: o catálogo deixa de corresponder
    snapshot = json.loads(lock.read_text(encoding="utf-8"))
    snapshot["hash"] = "sha256:0"
    lock.write_text(json.dumps(snapshot), encoding="utf-8")

    assert (
        rodar("--catalogo", str(fixture_catalogo), "--lock", str(lock), "compilar", "--conferir")
        == 1
    )


def test_catalogo_invalido_sai_com_um(tmp_path: Path) -> None:
    raiz = tmp_path / "catalogo"
    (raiz / "competencias").mkdir(parents=True)
    (raiz / "competencias" / "x.yaml").write_text(
        "versao_schema: 1\ncompetencias:\n  - id: SEM_PADRAO\n    titulo: X\n"
        "    rev: 1\n    verificacao: v\n",
        encoding="utf-8",
    )
    assert rodar("--catalogo", str(raiz), "validar") == 1


def test_lock_fica_ao_lado_do_catalogo() -> None:
    assert lock_de(Path("catalogo")) == Path("catalogo.lock.json")
    assert lock_de(Path("tests/fixtures/exemplo")) == Path("tests/fixtures/catalogo.lock.json")


def test_lock_de_outro_catalogo_nao_e_usado(fixture_catalogo: Path) -> None:
    """Regressão: o lock do catálogo real não pode invalidar outro catálogo."""
    assert rodar("--catalogo", str(fixture_catalogo), "validar") == 0


def test_comando_obrigatorio() -> None:
    with pytest.raises(SystemExit):
        rodar("--catalogo", "catalogo")
