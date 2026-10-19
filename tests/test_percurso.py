"""Percurso: log append-only e projeção (ADR-0008).

O foco é nas duas invariantes que a ADR promete valer **por construção**, não por
disciplina: competência exige evidência, e fato datado não retroage.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime
from itertools import permutations
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
    conferir_retratacao,
    dar_feedback,
    eventos_do_yaml,
    iniciar_etapa,
    montar_percurso,
    percorrer_recurso,
    percorridos_de,
    progresso_de,
    registrar_autoavaliacao,
    retratar_evidencia,
)
from trilhas.percurso.eventos import EvidenciaRegistrada, EvidenciaRetratada, Registro
from trilhas.percurso.repositorio import registros_em

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


# --- retratação de evidência (ADR-0014) ---------------------------------------


def test_nenhuma_sequencia_de_eventos_baixa_um_nivel_evidenciado() -> None:
    """A monotonia é invariante de fato, não acidente de um caminho (ADR-0014 §Contexto).

    Varre as ações registráveis — todas menos `retratar` — em cada permutação de até
    três, aplicadas sobre um `avancado` já evidenciado. Se alguma rebaixar, a decisão
    de ADR-0014 perdeu a premissa: haveria remédio sem evento novo.
    """
    comp = "comp:x/a"
    baixa = etapa("etapa:x/baixa", teaches=[(comp, N.INICIANTE)])
    acoes = [
        registrar_autoavaliacao(comp, N.INICIANTE),
        registrar_autoavaliacao(comp, N.INTERMEDIARIO),
        concluir_etapa(baixa),
        abandonar_etapa(baixa),
        iniciar_etapa(baixa),
        dar_feedback("etapa:x/alta", Reacao.REJEITADA),
    ]
    base = concluir_etapa(etapa("etapa:x/alta", teaches=[(comp, N.AVANCADO)]))

    for tamanho in (1, 2, 3):
        for combinacao in permutations(acoes, tamanho):
            eventos = list(base)
            for acao in combinacao:
                eventos += acao
            projetadas = competencias_de(registros(*[(e, EM) for e in eventos]))
            assert projetadas[0].nivel is Nivel.AVANCADO


def test_retratacao_tira_a_evidencia_da_projecao() -> None:
    """O guarda de `competencias_de`: a evidência retratada projeta como se não existisse."""
    log = registros(
        (EvidenciaRegistrada("comp:x/a", Nivel.INTERMEDIARIO, Origem.CONCLUSAO_DE_ETAPA), EM),
        (retratar_evidencia(1)[0], EM),
    )
    assert competencias_de(log) == ()


def test_retratar_a_unica_evidencia_apaga_a_competencia() -> None:
    """CONTEXT §4: competência sem evidência não retratada não existe."""
    passo = etapa("etapa:x/a", teaches=[("comp:x/a", N.INTERMEDIARIO)])
    conclusao, evidencia = concluir_etapa(passo)
    log = registros(
        (conclusao, dia("2026-01-01")),
        (evidencia, dia("2026-01-01")),
        (retratar_evidencia(2, motivo="li só o capítulo 1")[0], dia("2026-02-01")),
    )
    assert competencias_de(log) == ()
    # o progresso não é afetado: retratação fala de evidência, não de etapa
    assert progresso_de(log)[0].estado is EstadoEtapa.CONCLUIDA


def test_retratacao_cai_para_a_evidencia_anterior_nao_para_desconhece() -> None:
    """O caso de `est:mpb` #30: havia um `iniciante` legítimo embaixo (ADR-0014)."""
    ev = EvidenciaRegistrada
    log = registros(
        (ev("comp:x/a", Nivel.INICIANTE, Origem.CONCLUSAO_DE_ETAPA), dia("2026-01-01")),
        (ev("comp:x/a", Nivel.INTERMEDIARIO, Origem.CONCLUSAO_DE_ETAPA), dia("2026-10-18")),
        (retratar_evidencia(2)[0], dia("2026-10-19")),
    )
    (projetada,) = competencias_de(log)
    assert projetada.nivel is Nivel.INICIANTE
    assert projetada.ultima_evidencia_em == date(2026, 1, 1)


def test_retratacao_alcanca_uma_evidencia_so_do_lote_da_conclusao() -> None:
    """Granularidade por `seq`: a conclusão emitiu duas evidências, retrata-se uma.

    É a razão de a retratação apontar para `seq` e não para (competência, etapa).
    """
    passo = etapa(
        "etapa:x/a", teaches=[("comp:x/a", N.INTERMEDIARIO), ("comp:x/b", N.INTERMEDIARIO)]
    )
    conclusao, de_a, de_b = concluir_etapa(passo)
    # #1 conclusão, #2 evidência de comp:x/a, #3 evidência de comp:x/b
    log = registros((conclusao, EM), (de_a, EM), (de_b, EM), (retratar_evidencia(2)[0], EM))
    assert [c.competencia for c in competencias_de(log)] == ["comp:x/b"]


def test_retratacao_alcanca_autoavaliacao() -> None:
    """Evidência de `sei` tem `etapa=None`; o par (competência, etapa) não a endereçaria."""
    log = registros(
        (registrar_autoavaliacao("comp:x/a", N.AVANCADO)[0], EM),
        (retratar_evidencia(1)[0], EM),
    )
    assert competencias_de(log) == ()


def test_retratacao_sobrevive_ao_banco(repo: Repositorio) -> None:
    repo.anexar("est:x", registrar_autoavaliacao("comp:x/a", N.AVANCADO))
    repo.anexar("est:x", retratar_evidencia(1, motivo="engano"))
    lidos = repo.registros("est:x")
    assert isinstance(lidos[1].evento, EvidenciaRetratada)
    assert lidos[1].evento.evidencia_seq == 1
    assert lidos[1].evento.motivo == "engano"
    assert competencias_de(lidos) == ()


def test_retratacao_consta_da_exportacao(repo: Repositorio) -> None:
    """Quem lê o JSONL tem de ver a retratação, ou superestima competências."""
    repo.anexar("est:x", registrar_autoavaliacao("comp:x/a", N.AVANCADO))
    repo.anexar("est:x", retratar_evidencia(1))
    assert "evidencia_retratada" in repo.exportar("est:x")


# --- a conferência do alvo, na escrita (ADR-0014) -----------------------------


def test_conferir_retratacao_aceita_uma_evidencia_do_estudante() -> None:
    log = registros((registrar_autoavaliacao("comp:x/a", N.AVANCADO)[0], EM))
    assert conferir_retratacao(1, log) is None


def test_conferir_retratacao_recusa_seq_que_nao_existe() -> None:
    """Guarda: retratação sem alvo seria evento inerte — gravado e sem efeito."""
    log = registros((registrar_autoavaliacao("comp:x/a", N.AVANCADO)[0], EM))
    problema = conferir_retratacao(999, log)
    assert problema is not None and "#999" in problema


def test_conferir_retratacao_recusa_evento_que_nao_e_evidencia() -> None:
    """Guarda: só evidência se retrata. Progresso se corrige com `iniciar`/`abandonar`."""
    log = registros((concluir_etapa(etapa("etapa:x/a"))[0], EM))
    problema = conferir_retratacao(1, log)
    assert problema is not None and "não uma evidência" in problema


def test_conferir_retratacao_recusa_retratar_duas_vezes() -> None:
    """Guarda: retratação de retratação não está modelada (ADR-0014)."""
    log = registros(
        (registrar_autoavaliacao("comp:x/a", N.AVANCADO)[0], EM),
        (retratar_evidencia(1)[0], EM),
    )
    problema = conferir_retratacao(1, log)
    assert problema is not None and "já está retratada" in problema


def test_conferir_retratacao_nao_alcanca_evidencia_de_outro_estudante(
    repo: Repositorio,
) -> None:
    """A CLI passa os registros de um estudante só; o alvo não existe fora deles."""
    repo.anexar("est:outro", registrar_autoavaliacao("comp:x/a", N.AVANCADO))
    assert conferir_retratacao(1, repo.registros("est:x")) is not None


# --- CLI de escrita -----------------------------------------------------------


def _ambiente(tmp_path: Path) -> tuple[Path, Path]:
    """Um diretório de percurso e um `catalogo.lock.json` mínimo mas real.

    Duas etapas, um recurso em cada: é o que permite distinguir "recurso que não
    existe" de "recurso que existe, mas é de outra etapa".
    """
    from trilhas.catalogo.compilar import compilar

    cat = catalogo(
        competencia("comp:x/base"),
        etapa("etapa:x/base", teaches=[("comp:x/base", N.INICIANTE)], trilha="trilha:x/t"),
        recurso("rec:x/base", "etapa:x/base"),
        etapa("etapa:x/outra", trilha="trilha:x/t"),
        recurso("rec:x/outra", "etapa:x/outra"),
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


def test_cli_iniciar_aceita_recurso_da_etapa(tmp_path: Path, capsys) -> None:
    destino, lock = _ambiente(tmp_path)
    assert rodar(destino, lock, "iniciar", "etapa:x/base", "--recurso", "rec:x/base") == 0
    assert "EtapaIniciada" in capsys.readouterr().out
    with Repositorio.em_diretorio(destino) as repo:
        (registro,) = repo.registros("est:mpb")
    assert registro.evento.recurso == "rec:x/base"


def test_cli_recusa_recurso_fora_do_catalogo(tmp_path: Path, capsys) -> None:
    """O id errado passava calado e ficava no log para sempre (ADR-0008: sem UPDATE)."""
    destino, lock = _ambiente(tmp_path)
    assert rodar(destino, lock, "iniciar", "etapa:x/base", "--recurso", "rec:nao/existe") == 1
    assert "recurso desconhecido" in capsys.readouterr().err
    with Repositorio.em_diretorio(destino) as repo:
        assert repo.registros("est:mpb") == [], "recusa não grava fato"


def test_cli_recusa_recurso_de_outra_etapa(tmp_path: Path, capsys) -> None:
    """Existir no catálogo não basta: um recurso pertence a uma etapa só (catalogo.md §2)."""
    destino, lock = _ambiente(tmp_path)
    assert rodar(destino, lock, "iniciar", "etapa:x/base", "--recurso", "rec:x/outra") == 1
    erro = capsys.readouterr().err
    assert "outra etapa" in erro and "etapa:x/outra" in erro
    with Repositorio.em_diretorio(destino) as repo:
        assert repo.registros("est:mpb") == [], "recusa não grava fato"


def test_cli_iniciar_sem_recurso_segue_valendo(tmp_path: Path) -> None:
    """`--recurso` é opcional; a conferência não o torna obrigatório."""
    destino, lock = _ambiente(tmp_path)
    assert rodar(destino, lock, "iniciar", "etapa:x/base") == 0


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


# --- recurso pelo qual se estuda ------------------------------------------------


def test_progresso_guarda_o_recurso_pelo_qual_se_iniciou() -> None:
    log = registros((iniciar_etapa(etapa("etapa:x"), recurso="rec:x")[0], EM))
    assert progresso_de(log)[0].recurso_em_uso == "rec:x"


def test_concluir_nao_apaga_o_recurso_declarado_no_inicio() -> None:
    """Só `EtapaIniciada` carrega o recurso; a conclusão não o repete.

    Se a projeção deixasse o último fato sobrescrever tudo, a etapa concluída perderia
    por qual recurso foi estudada — que é justamente o que se pergunta depois.
    """
    alvo = etapa("etapa:x")
    log = registros(
        (iniciar_etapa(alvo, recurso="rec:x")[0], EM),
        (concluir_etapa(alvo)[0], EM),
    )
    (progresso,) = progresso_de(log)
    assert progresso.estado is EstadoEtapa.CONCLUIDA
    assert progresso.recurso_em_uso == "rec:x"


def test_iniciar_sem_recurso_nao_inventa_um() -> None:
    log = registros((iniciar_etapa(etapa("etapa:x"))[0], EM))
    assert progresso_de(log)[0].recurso_em_uso is None


# --- leitura do log por quem só lê ----------------------------------------------


def test_registros_em_nao_cria_o_banco_quando_ele_nao_existe(tmp_path: Path) -> None:
    """A interface é somente leitura: renderizar uma página não pode fazer nascer um log.

    `Repositorio` cria o arquivo ao abrir, e é por isso que a web não o usa.
    """
    assert registros_em(tmp_path, "est:x") == []
    assert not (tmp_path / Repositorio.NOME_DO_ARQUIVO).exists()


def test_registros_em_le_o_que_o_repositorio_gravou(tmp_path: Path) -> None:
    with Repositorio.em_diretorio(tmp_path) as repo:
        repo.anexar("est:x", iniciar_etapa(etapa("etapa:x"), recurso="rec:x"))

    lidos = registros_em(tmp_path, "est:x")
    assert [r.evento.etapa for r in lidos] == ["etapa:x"]
    assert registros_em(tmp_path, "est:outro") == []


# --- fato de recurso: percorrer não é concluir (ADR-0012) -----------------------


def test_percorrer_recurso_nao_emite_evidencia() -> None:
    """O ponto todo da ADR: a fatia vale uma fração do esforço da etapa.

    Era concluir etapa — e só isso — que dava para registrar "li o livro", e concluir
    etapa concede competência que o log depois não retira.
    """
    eventos = percorrer_recurso(recurso("rec:x/fatia", "etapa:x/inicial"))
    assert len(eventos) == 1
    assert not any(isinstance(ev, EvidenciaRegistrada) for ev in eventos)
    assert competencias_de(registros((eventos[0], EM))) == ()


def test_percorrer_grava_a_revisao_da_fatia_de_entao() -> None:
    """Como `etapa_rev` nos eventos de etapa: repontar a fatia depois não retroage."""
    (evento,) = percorrer_recurso(recurso("rec:x/fatia", "etapa:x/inicial", rev=3))
    log = registros((evento, EM))
    (percorrido,) = percorridos_de(log)
    assert (percorrido.recurso, percorrido.recurso_rev) == ("rec:x/fatia", 3)
    assert percorrido.percorrido_em == EM.date()


def test_percorrer_nao_mexe_no_progresso_da_etapa() -> None:
    """Etapa parcialmente percorrida não vira estado de `Progresso` (ADR-0012)."""
    alvo = etapa("etapa:x/inicial")
    log = registros(
        (iniciar_etapa(alvo)[0], EM),
        (percorrer_recurso(recurso("rec:x/fatia", "etapa:x/inicial"))[0], EM),
    )
    (progresso,) = progresso_de(log)
    assert progresso.estado is EstadoEtapa.EM_ANDAMENTO


def test_percorrer_de_novo_fica_com_a_ultima_passagem() -> None:
    """O último fato sobre o mesmo recurso vence, como em `progresso_de`."""
    fatia = recurso("rec:x/fatia", "etapa:x/inicial")
    log = registros(
        (percorrer_recurso(fatia)[0], dia("2026-10-01")),
        (percorrer_recurso(fatia)[0], dia("2026-10-15")),
    )
    (percorrido,) = percorridos_de(log)
    assert percorrido.percorrido_em == date(2026, 10, 15)


def test_o_fato_de_recurso_fica_fora_da_entrada_do_motor() -> None:
    """ADR-0012: `RecursoPercorrido` não entra em `Percurso`; o motor não o consome.

    Se um dia entrar, é decisão nova — e este teste é quem avisa que ela foi tomada
    por acidente.
    """
    log = registros((percorrer_recurso(recurso("rec:x/fatia", "etapa:x/inicial"))[0], EM))
    projetado = montar_percurso(Percurso(estudante_id="est:x"), log)
    assert projetado.progresso == ()
    assert projetado.competencias == ()
    assert projetado.feedback == ()


def test_percorrer_e_concluir_sao_independentes_nos_dois_sentidos() -> None:
    alvo = etapa("etapa:x/inicial", teaches=[("comp:x/base", N.INICIANTE)])
    so_percorrido = registros((percorrer_recurso(recurso("rec:x/f", "etapa:x/inicial"))[0], EM))
    assert percorridos_de(so_percorrido) and progresso_de(so_percorrido) == ()

    so_concluido = registros(*[(ev, EM) for ev in concluir_etapa(alvo)])
    assert progresso_de(so_concluido) and percorridos_de(so_concluido) == ()


def test_fato_de_recurso_vai_e_volta_pelo_banco(repo: Repositorio) -> None:
    """Tipo novo no log: gravar, desserializar e exportar têm de fechar o laço."""
    repo.anexar("est:x", percorrer_recurso(recurso("rec:x/fatia", "etapa:x/inicial", rev=2)))
    (registro,) = repo.registros("est:x")
    assert (registro.evento.recurso, registro.evento.recurso_rev) == ("rec:x/fatia", 2)

    import json as _json

    (linha,) = [_json.loads(x) for x in repo.exportar("est:x").splitlines()]
    assert linha["tipo"] == "recurso_percorrido"
    assert linha["dados"] == {"recurso": "rec:x/fatia", "recurso_rev": 2}


# --- CLI de `percorrer` ---------------------------------------------------------


def test_cli_percorrer_registra_sem_evidencia(tmp_path: Path, capsys) -> None:
    destino, lock = _ambiente(tmp_path)
    assert rodar(destino, lock, "percorrer", "rec:x/base") == 0
    saida = capsys.readouterr().out
    assert "RecursoPercorrido" in saida and "EvidenciaRegistrada" not in saida

    assert rodar(destino, lock, "mostrar") == 0
    mostrado = capsys.readouterr().out
    assert "rec:x/base" in mostrado
    assert "(nenhuma — toda competência exige evidência)" in mostrado


def test_cli_percorrer_recusa_recurso_fora_do_catalogo(tmp_path: Path, capsys) -> None:
    destino, lock = _ambiente(tmp_path)
    assert rodar(destino, lock, "percorrer", "rec:nao/existe") == 1
    assert "recurso desconhecido" in capsys.readouterr().err
    with Repositorio.em_diretorio(destino) as repo:
        assert repo.registros("est:mpb") == [], "recusa não grava fato"


def test_cli_percorrer_nao_exige_que_o_recurso_seja_de_uma_etapa_iniciada(tmp_path: Path) -> None:
    """A conferência é só existir: percorrer material não é sobre uma etapa (ADR-0012)."""
    destino, lock = _ambiente(tmp_path)
    assert rodar(destino, lock, "percorrer", "rec:x/outra") == 0


def test_cli_mostrar_agrupa_as_fatias_por_obra(tmp_path: Path, capsys) -> None:
    """O que responde "li este livro" em vez de listar fatias soltas.

    O agrupamento é resolvido na leitura, contra o catálogo de hoje — `obra` não está
    gravada no fato (ADR-0012).
    """
    import json as _json

    from trilhas.catalogo.compilar import compilar

    cat = catalogo(
        competencia("comp:x/base"),
        etapa("etapa:x/um", teaches=[("comp:x/base", N.INICIANTE)], trilha="trilha:x/t"),
        etapa("etapa:x/dois", trilha="trilha:x/t"),
        recurso("rec:x/livro-um", "etapa:x/um", custo=30.0, obra="livro-x"),
        recurso("rec:x/livro-dois", "etapa:x/dois", custo=30.0, obra="livro-x"),
    )
    lock = tmp_path / "catalogo.lock.json"
    lock.write_text(_json.dumps(compilar(cat), ensure_ascii=False), encoding="utf-8")
    destino = tmp_path / "percurso"
    destino.mkdir()

    rodar(destino, lock, "percorrer", "rec:x/livro-um")
    capsys.readouterr()
    assert rodar(destino, lock, "mostrar") == 0
    parcial = capsys.readouterr().out
    assert "livro-x" in parcial
    assert "1/2 fatia(s)" in parcial and "em parte" in parcial

    rodar(destino, lock, "percorrer", "rec:x/livro-dois")
    capsys.readouterr()
    assert rodar(destino, lock, "mostrar") == 0
    completa = capsys.readouterr().out
    assert "2/2 fatia(s)" in completa and "completa" in completa


def test_cli_retratar_desfaz_a_competencia_e_a_marca_em_mostrar(tmp_path: Path, capsys) -> None:
    destino, lock = _ambiente(tmp_path)
    assert rodar(destino, lock, "concluir", "etapa:x/base") == 0
    capsys.readouterr()

    assert rodar(destino, lock, "mostrar") == 0
    saida = capsys.readouterr().out
    assert "comp:x/base" in saida
    assert "evidências:" in saida and "#2" in saida  # o seq é descobrível

    assert rodar(destino, lock, "retratar", "2", "--motivo", "li só o capítulo 1") == 0
    assert "retrata #2" in capsys.readouterr().out

    assert rodar(destino, lock, "mostrar") == 0
    saida = capsys.readouterr().out
    assert "(nenhuma — toda competência exige evidência)" in saida
    assert "RETRATADA" in saida


def test_cli_retratar_recusa_alvo_que_nao_e_evidencia(tmp_path: Path, capsys) -> None:
    destino, lock = _ambiente(tmp_path)
    assert rodar(destino, lock, "concluir", "etapa:x/base") == 0
    capsys.readouterr()
    assert rodar(destino, lock, "retratar", "1") == 1
    assert "não uma evidência" in capsys.readouterr().err
