"""Percurso: log append-only e projeção (ADR-0008).

O foco é nas duas invariantes que a ADR promete valer **por construção**, não por
disciplina: competência exige evidência, e fato datado não retroage.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
import yaml

from fabrica import N, catalogo, competencia, etapa, recurso
from trilhas.catalogo.modelo import Ensino, Nivel
from trilhas.motor.modelo import EstadoEtapa, Percurso, Reacao
from trilhas.percurso import (
    Origem,
    Repositorio,
    abandonar_etapa,
    competencias_de,
    concluir_etapa,
    dar_feedback,
    eventos_do_yaml,
    iniciar_etapa,
    montar_percurso,
    progresso_de,
    registrar_autoavaliacao,
)
from trilhas.percurso.eventos import EvidenciaRegistrada, Registro

EM = datetime(2026, 10, 13, tzinfo=UTC)


def registros(*pares: tuple[object, datetime]) -> list[Registro]:
    return [
        Registro(evento=ev, em=quando, estudante="est:x", seq=i + 1)
        for i, (ev, quando) in enumerate(pares)
    ]


def dia(d: str) -> datetime:
    return datetime.fromisoformat(d).replace(tzinfo=UTC)


@pytest.fixture
def repo(tmp_path: Path) -> Repositorio:
    with Repositorio.em_diretorio(tmp_path) as r:
        yield r


# --- competência exige evidência (CONTEXT §4, por construção) ------------------


def test_log_vazio_nao_produz_competencia_alguma() -> None:
    """Mesmo partindo de um percurso que as declarava: o campo do YAML é ignorado."""
    declarado = Percurso(estudante_id="est:x")
    assert montar_percurso(declarado, []).competencias == ()


def test_evidencia_e_a_unica_origem_de_competencia() -> None:
    projetadas = competencias_de(
        registros((registrar_autoavaliacao("comp:x/a", N.INICIANTE)[0], EM))
    )
    assert [(c.competencia, c.nivel) for c in projetadas] == [("comp:x/a", Nivel.INICIANTE)]


def test_nivel_e_o_maximo_evidenciado() -> None:
    ev = EvidenciaRegistrada
    projetadas = competencias_de(
        registros(
            (ev("comp:x/a", Nivel.INICIANTE, Origem.AUTOAVALIACAO), dia("2026-01-01")),
            (ev("comp:x/a", Nivel.AVANCADO, Origem.AUTOAVALIACAO), dia("2026-02-01")),
            (ev("comp:x/a", Nivel.INTERMEDIARIO, Origem.AUTOAVALIACAO), dia("2026-03-01")),
        )
    )
    assert projetadas[0].nivel is Nivel.AVANCADO
    # a data é da evidência do nível vigente, não da mais recente de qualquer nível
    assert projetadas[0].ultima_evidencia_em == date(2026, 2, 1)


def test_evidencia_nova_no_mesmo_nivel_renova_a_data() -> None:
    ev = EvidenciaRegistrada
    projetadas = competencias_de(
        registros(
            (ev("comp:x/a", Nivel.INTERMEDIARIO, Origem.AUTOAVALIACAO), dia("2026-01-01")),
            (ev("comp:x/a", Nivel.INTERMEDIARIO, Origem.CONCLUSAO_DE_ETAPA), dia("2026-06-01")),
        )
    )
    assert projetadas[0].ultima_evidencia_em == date(2026, 6, 1)


def test_autoavaliacao_vale_menos_que_conclusao() -> None:
    uma = registrar_autoavaliacao("comp:x/a", N.INICIANTE)[0]
    passo = etapa("etapa:x/a", teaches=[("comp:x/a", N.INICIANTE)])
    outra = concluir_etapa(passo)[1]
    assert uma.confianca < outra.confianca


# --- fato datado não retroage (catalogo.md §4, por construção) -----------------


def test_concluir_grava_a_evidencia_do_que_a_etapa_ensinava() -> None:
    passo = etapa(
        "etapa:x/a",
        rev=3,
        teaches=[("comp:x/a", N.INTERMEDIARIO), ("comp:x/b", N.INICIANTE)],
    )
    eventos = concluir_etapa(passo)
    assert len(eventos) == 3  # conclusão + duas evidências
    evidencias = [e for e in eventos if isinstance(e, EvidenciaRegistrada)]
    assert all(e.etapa == "etapa:x/a" and e.etapa_rev == 3 for e in evidencias)
    assert all(e.origem is Origem.CONCLUSAO_DE_ETAPA for e in evidencias)


def test_mudar_teaches_depois_nao_altera_o_que_ja_foi_evidenciado() -> None:
    passo = etapa("etapa:x/a", rev=1, teaches=[("comp:x/a", N.INTERMEDIARIO)])
    gravados = registros(*[(e, EM) for e in concluir_etapa(passo)])
    antes = competencias_de(gravados)

    # o catálogo muda: a etapa passa a ensinar menos, noutra rev
    replace(passo, rev=2, teaches=(Ensino("comp:x/a", Nivel.INICIANTE),))

    assert competencias_de(gravados) == antes
    assert antes[0].nivel is Nivel.INTERMEDIARIO


def test_etapa_sem_teaches_gera_progresso_sem_competencia() -> None:
    eventos = concluir_etapa(etapa("etapa:x/a"))
    assert len(eventos) == 1
    assert competencias_de(registros((eventos[0], EM))) == ()


def test_abandonar_nao_retira_evidencia() -> None:
    passo = etapa("etapa:x/a", teaches=[("comp:x/a", N.INICIANTE)])
    gravados = registros(
        *[(e, dia("2026-01-01")) for e in concluir_etapa(passo)],
        *[(e, dia("2026-02-01")) for e in abandonar_etapa(passo)],
    )
    assert len(competencias_de(gravados)) == 1
    assert progresso_de(gravados)[0].estado is EstadoEtapa.ABANDONADA


# --- progresso ----------------------------------------------------------------


def test_o_ultimo_fato_sobre_a_etapa_vence() -> None:
    passo = etapa("etapa:x/a")
    gravados = registros(
        (iniciar_etapa(passo)[0], dia("2026-01-01")),
        (concluir_etapa(passo)[0], dia("2026-02-01")),
    )
    estados = progresso_de(gravados)
    assert len(estados) == 1
    assert estados[0].estado is EstadoEtapa.CONCLUIDA
    assert estados[0].atualizado_em == date(2026, 2, 1)


def test_projecao_e_deterministica() -> None:
    passo = etapa("etapa:x/a", teaches=[("comp:x/a", N.INICIANTE)])
    gravados = registros(*[(e, EM) for e in concluir_etapa(passo)])
    assert montar_percurso(Percurso("est:x"), gravados) == montar_percurso(
        Percurso("est:x"), list(reversed(gravados))
    )


# --- o log é append-only (imposto pelo banco) ---------------------------------


def test_update_no_log_e_proibido(repo: Repositorio) -> None:
    repo.anexar("est:x", dar_feedback("etapa:x/a", Reacao.ACEITA), em=EM)
    with pytest.raises(Exception, match="append-only"):
        repo._con.execute("UPDATE evento SET tipo = 'outro'")


def test_delete_no_log_e_proibido(repo: Repositorio) -> None:
    repo.anexar("est:x", dar_feedback("etapa:x/a", Reacao.ACEITA), em=EM)
    with pytest.raises(Exception, match="append-only"):
        repo._con.execute("DELETE FROM evento")


def test_ida_e_volta_pelo_banco(repo: Repositorio) -> None:
    passo = etapa("etapa:x/a", rev=7, teaches=[("comp:x/a", N.AVANCADO)])
    repo.anexar("est:x", concluir_etapa(passo), em=EM)
    lidos = repo.registros("est:x")
    assert [type(r.evento).__name__ for r in lidos] == ["EtapaConcluida", "EvidenciaRegistrada"]
    assert competencias_de(lidos)[0].nivel is Nivel.AVANCADO


def test_estudantes_nao_se_misturam(repo: Repositorio) -> None:
    repo.anexar("est:a", registrar_autoavaliacao("comp:x/a", N.INICIANTE), em=EM)
    repo.anexar("est:b", registrar_autoavaliacao("comp:x/b", N.AVANCADO), em=EM)
    assert [c.competencia for c in competencias_de(repo.registros("est:a"))] == ["comp:x/a"]
    assert list(repo.estudantes()) == ["est:a", "est:b"]


def test_log_sobrevive_a_reabertura(tmp_path: Path) -> None:
    with Repositorio.em_diretorio(tmp_path) as r:
        r.anexar("est:x", registrar_autoavaliacao("comp:x/a", N.INICIANTE), em=EM)
    with Repositorio.em_diretorio(tmp_path) as r:
        assert len(r.registros("est:x")) == 1


def test_lote_vazio_nao_grava_nada(repo: Repositorio) -> None:
    assert repo.anexar("est:x", []) == []
    assert repo.registros("est:x") == []


# --- migração do YAML ---------------------------------------------------------


def test_migracao_preserva_as_datas_declaradas() -> None:
    dados = {
        "progresso": [
            {
                "etapa": "etapa:x/a",
                "rev": 2,
                "estado": "em_andamento",
                "iniciada_em": "2026-10-08",
                "recurso_em_uso": "rec:x/a",
            }
        ],
        "perfil": {
            "competencias_dominadas": [
                {
                    "competencia": "comp:x/a",
                    "nivel": "iniciante",
                    "ultima_evidencia_em": "2026-09-01",
                    "confianca": 0.8,
                }
            ]
        },
    }
    fatos = eventos_do_yaml(dados)
    assert [par[1].date() for par in fatos] == [date(2026, 9, 1), date(2026, 10, 8)]
    assert fatos[0][0].confianca == 0.8
    assert fatos[1][0].recurso == "rec:x/a"
    assert fatos[1][0].etapa_rev == 2


def test_migracao_nao_inventa_evidencia_para_etapa_concluida() -> None:
    """Sintetizar evidência a partir do `teaches` de hoje seria retroagir."""
    fatos = eventos_do_yaml(
        {"progresso": [{"etapa": "etapa:x/a", "estado": "concluida", "concluida_em": "2026-01-01"}]}
    )
    assert [type(e).__name__ for e, _ in fatos] == ["EtapaConcluida"]


def test_migracao_do_percurso_real_do_projeto() -> None:
    arquivo = Path(__file__).resolve().parent.parent / "percurso" / "est-mpb.yaml"
    if not arquivo.is_file():  # pragma: no cover
        pytest.skip("percurso real ausente")
    fatos = eventos_do_yaml(yaml.safe_load(arquivo.read_text(encoding="utf-8")))
    assert fatos, "o YAML real declara progresso; a migração não pode devolver vazio"
    assert all(par[1].tzinfo is not None for par in fatos)


def test_migracao_de_yaml_vazio_nao_gera_fato() -> None:
    assert eventos_do_yaml({}) == []


# --- o laço fecha: log -> projeção -> motor -----------------------------------


def test_percurso_do_log_alimenta_o_motor(repo: Repositorio) -> None:
    from trilhas.catalogo.modelo import Alvo
    from trilhas.motor import Objetivo, sugerir

    base_etapa = etapa("etapa:x/base", teaches=[("comp:x/base", N.INICIANTE)], trilha="trilha:x/t")
    cat = catalogo(
        competencia("comp:x/base"),
        competencia("comp:x/avancada"),
        base_etapa,
        etapa(
            "etapa:x/seq",
            requires=[("comp:x/base", N.INICIANTE)],
            teaches=[("comp:x/avancada", N.INICIANTE)],
            trilha="trilha:x/t",
        ),
        # Sem recurso viável a etapa é filtrada (motor §2.2), não despontuada.
        recurso("rec:x/base", "etapa:x/base"),
        recurso("rec:x/seq", "etapa:x/seq"),
    )
    repo.anexar("est:x", concluir_etapa(base_etapa), em=EM)

    percurso = montar_percurso(
        Percurso(
            estudante_id="est:x",
            objetivo=Objetivo((Alvo("comp:x/avancada", Nivel.INICIANTE),), date(2026, 10, 1)),
        ),
        repo.registros("est:x"),
    )
    # a etapa seguinte só está liberada porque a conclusão gerou a evidência
    assert any(c.competencia == "comp:x/base" for c in percurso.competencias)
    resultado = sugerir(cat, percurso, EM)
    assert [s.etapa_id for s in resultado.sugestoes] == ["etapa:x/seq"]


# --- CLI de escrita -----------------------------------------------------------


def _ambiente(tmp_path: Path) -> tuple[Path, Path]:
    """Um diretório de percurso e um `catalogo.lock.json` mínimo mas real."""
    from trilhas.catalogo.compilar import compilar

    cat = catalogo(
        competencia("comp:x/base"),
        etapa("etapa:x/base", teaches=[("comp:x/base", N.INICIANTE)], trilha="trilha:x/t"),
        recurso("rec:x/base", "etapa:x/base"),
    )
    lock = tmp_path / "catalogo.lock.json"
    import json

    lock.write_text(json.dumps(compilar(cat), ensure_ascii=False), encoding="utf-8")
    destino = tmp_path / "percurso"
    destino.mkdir()
    return destino, lock


def rodar(destino: Path, lock: Path, *args: str) -> int:
    from trilhas.percurso.cli import main

    return main(["--percurso", str(destino), "--lock", str(lock), *args])


def test_cli_concluir_grava_conclusao_e_evidencia(tmp_path: Path, capsys) -> None:
    destino, lock = _ambiente(tmp_path)
    assert rodar(destino, lock, "concluir", "etapa:x/base") == 0
    saida = capsys.readouterr().out
    assert "EtapaConcluida" in saida and "EvidenciaRegistrada" in saida

    assert rodar(destino, lock, "mostrar") == 0
    assert "comp:x/base" in capsys.readouterr().out


def test_cli_recusa_etapa_fora_do_catalogo(tmp_path: Path, capsys) -> None:
    destino, lock = _ambiente(tmp_path)
    assert rodar(destino, lock, "concluir", "etapa:x/inexistente") == 1
    assert "etapa desconhecida" in capsys.readouterr().err


def test_cli_recusa_competencia_fora_do_catalogo(tmp_path: Path, capsys) -> None:
    destino, lock = _ambiente(tmp_path)
    assert rodar(destino, lock, "sei", "comp:x/fantasma", "iniciante") == 1
    assert "competência desconhecida" in capsys.readouterr().err


def test_cli_importar_nao_duplica_historia(tmp_path: Path, capsys) -> None:
    destino, lock = _ambiente(tmp_path)
    (destino / "est-x.yaml").write_text(
        yaml.safe_dump(
            {
                "estudante": {"id": "est:x"},
                "progresso": [
                    {
                        "etapa": "etapa:x/base",
                        "rev": 1,
                        "estado": "em_andamento",
                        "iniciada_em": "2026-10-08",
                    }
                ],
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    assert rodar(destino, lock, "--estudante", "est:x", "importar") == 0
    assert "2026-10-08" in capsys.readouterr().out
    assert rodar(destino, lock, "--estudante", "est:x", "importar") == 1
    assert "duplicaria" in capsys.readouterr().err


def test_cli_feedback_dispensa_catalogo(tmp_path: Path) -> None:
    """Reagir a uma sugestão não exige resolver a etapa: a reação é sobre o que foi visto."""
    destino, lock = _ambiente(tmp_path)
    assert rodar(destino, lock, "reagir", "etapa:x/qualquer", "rejeitada") == 0


def test_cli_exportar_gera_jsonl_commitavel(tmp_path: Path) -> None:
    import json as _json

    destino, lock = _ambiente(tmp_path)
    rodar(destino, lock, "concluir", "etapa:x/base")
    assert rodar(destino, lock, "exportar") == 0

    saida = destino / "est-mpb.log.jsonl"
    linhas = [_json.loads(linha) for linha in saida.read_text(encoding="utf-8").splitlines()]
    assert [linha["tipo"] for linha in linhas] == ["etapa_concluida", "evidencia_registrada"]
    assert [linha["seq"] for linha in linhas] == [1, 2]
    assert linhas[1]["dados"]["competencia"] == "comp:x/base"


def test_exportacao_e_estavel_entre_chamadas(repo: Repositorio) -> None:
    repo.anexar("est:x", registrar_autoavaliacao("comp:x/a", N.INICIANTE), em=EM)
    assert repo.exportar("est:x") == repo.exportar("est:x")


# --- exportar --conferir ------------------------------------------------------


def test_conferir_sem_log_local_nao_falha(tmp_path: Path, capsys) -> None:
    """Clone novo não tem o banco (está no .gitignore): não há com o que comparar."""
    destino, lock = _ambiente(tmp_path)
    assert rodar(destino, lock, "exportar", "--conferir") == 0
    assert "nada a conferir" in capsys.readouterr().out
    assert not (destino / Repositorio.NOME_DO_ARQUIVO).exists(), "conferir não cria banco"


def test_conferir_acusa_exportacao_ausente(tmp_path: Path, capsys) -> None:
    destino, lock = _ambiente(tmp_path)
    rodar(destino, lock, "concluir", "etapa:x/base")
    assert rodar(destino, lock, "exportar", "--conferir") == 1
    assert "não existe" in capsys.readouterr().err


def test_conferir_passa_quando_em_dia(tmp_path: Path, capsys) -> None:
    destino, lock = _ambiente(tmp_path)
    rodar(destino, lock, "concluir", "etapa:x/base")
    rodar(destino, lock, "exportar")
    capsys.readouterr()
    assert rodar(destino, lock, "exportar", "--conferir") == 0
    assert "em dia" in capsys.readouterr().out


def test_conferir_acusa_fato_novo_depois_da_exportacao(tmp_path: Path, capsys) -> None:
    destino, lock = _ambiente(tmp_path)
    rodar(destino, lock, "concluir", "etapa:x/base")
    rodar(destino, lock, "exportar")
    rodar(destino, lock, "reagir", "etapa:x/base", "aceita")
    capsys.readouterr()
    assert rodar(destino, lock, "exportar", "--conferir") == 1
    erro = capsys.readouterr().err
    assert "o log tem 3" in erro and "exportar" in erro


def test_conferir_nao_grava_nada(tmp_path: Path) -> None:
    destino, lock = _ambiente(tmp_path)
    rodar(destino, lock, "concluir", "etapa:x/base")
    rodar(destino, lock, "exportar")
    saida = destino / "est-mpb.log.jsonl"
    antes = saida.read_text(encoding="utf-8")
    rodar(destino, lock, "reagir", "etapa:x/base", "aceita")
    rodar(destino, lock, "exportar", "--conferir")
    assert saida.read_text(encoding="utf-8") == antes, "conferir não deve reescrever"
