"""Snapshot: hash estável, versão monotônica, ida e volta do estado anterior."""

from __future__ import annotations

from fabrica import minimo_valido
from trilhas.catalogo.compilar import compilar, estado_anterior, mudou
from trilhas.catalogo.snapshot import EstadoAnterior


def test_hash_ignora_gerado_em() -> None:
    a = compilar(minimo_valido())
    b = compilar(minimo_valido())
    assert a["hash"] == b["hash"]
    assert not mudou(b, a)


def test_versao_avanca_a_partir_do_anterior() -> None:
    snapshot = compilar(minimo_valido(), EstadoAnterior(versao=6, ids=frozenset(), revs={}))
    assert snapshot["catalogo_versao"] == 7


def test_conteudo_diferente_muda_o_hash() -> None:
    base = compilar(minimo_valido())
    catalogo = minimo_valido()
    catalogo.competencias.pop("comp:x/base")
    assert mudou(compilar(catalogo), base)


def test_estado_anterior_le_ids_e_revs_do_snapshot() -> None:
    snapshot = compilar(minimo_valido())
    estado = estado_anterior(snapshot)
    assert estado.versao == 1
    assert "comp:x/base" in estado.ids
    assert estado.revs["comp:x/base"] == 1


def test_estado_anterior_de_snapshot_ausente() -> None:
    assert estado_anterior(None) == EstadoAnterior.vazio()


def test_enums_serializam_como_texto() -> None:
    snapshot = compilar(minimo_valido())
    etapa = snapshot["etapas"][0]
    assert etapa["status"] == "ativo"
    assert etapa["teaches"][0]["nivel_resultante"] == "iniciante"
