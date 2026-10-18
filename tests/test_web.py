"""Rotas da interface. HTML é o contrato: as asserções olham o que a tela precisa dizer."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import pytest
from starlette.testclient import TestClient

import fabrica
from trilhas.catalogo.carregar import carregar
from trilhas.catalogo.compilar import compilar
from trilhas.percurso import (
    EtapaAbandonada,
    Repositorio,
    concluir_etapa,
    iniciar_etapa,
)
from trilhas.percurso.repositorio import registros_em
from trilhas.web.app import criar_app

HOJE = date(2026, 10, 12)
MODELOS = Path(__file__).resolve().parent.parent / "src" / "trilhas" / "web" / "modelos"

# Termos descartados por ambiguidade (docs/CONTEXT.md §1). A tela usa a linguagem única.
PROIBIDOS = ("curso", "módulo", "aula", "lição", "tarefa")


@pytest.fixture
def lock(tmp_path: Path, fixture_catalogo: Path) -> Path:
    """Compila o catálogo-fixture num snapshot temporário — o caminho real de leitura."""
    catalogo, problemas = carregar(fixture_catalogo)
    assert not problemas
    destino = tmp_path / "catalogo.lock.json"
    destino.write_text(json.dumps(compilar(catalogo), ensure_ascii=False), encoding="utf-8")
    return destino


@pytest.fixture
def cliente(lock: Path) -> TestClient:
    return TestClient(criar_app(lock=lock, hoje=lambda: HOJE))


def test_acervo_mostra_o_catalogo(cliente: TestClient) -> None:
    resposta = cliente.get("/acervo")
    assert resposta.status_code == 200
    assert "Acervo" in resposta.text
    assert "trilha:dados/fundamentos" in resposta.text or "Fundamentos" in resposta.text


def test_acervo_sem_snapshot_pede_para_compilar(tmp_path: Path) -> None:
    """Estado vazio é tela desenhada, não erro 500 (docs/interface.md §1.2)."""
    cliente = TestClient(criar_app(lock=tmp_path / "nao-existe.json", hoje=lambda: HOJE))
    resposta = cliente.get("/acervo")
    assert resposta.status_code == 200
    assert "trilhas compilar" in resposta.text


def test_explorador_filtra_por_tipo(cliente: TestClient) -> None:
    resposta = cliente.get("/catalogo", params={"tipo": "comp"})
    assert resposta.status_code == 200
    assert "comp:" in resposta.text
    assert "rec:" not in resposta.text


def test_explorador_sem_resultado_diz_que_nao_ha(cliente: TestClient) -> None:
    resposta = cliente.get("/catalogo", params={"q": "zzzznaoexiste"})
    assert "Nada corresponde a este filtro" in resposta.text


def test_trilha_desenha_grafo_e_tabela_equivalente(cliente: TestClient) -> None:
    """Sem a tabela, o grafo não é acessível nem legível sem script (§6.9)."""
    ident = _uma_trilha(cliente)
    resposta = cliente.get(f"/trilha/{ident}")
    assert resposta.status_code == 200
    assert "<svg" in resposta.text
    assert "Tabela equivalente ao grafo" in resposta.text
    assert "onda" in resposta.text


def test_trilha_inexistente_responde_404_com_tela(cliente: TestClient) -> None:
    resposta = cliente.get("/trilha/trilha:x/fantasma")
    assert resposta.status_code == 404
    assert "Nenhuma entidade de catálogo com este id" in resposta.text


def test_etapa_mostra_recursos_e_dependencias(cliente: TestClient) -> None:
    etapa = _uma_etapa(cliente)
    resposta = cliente.get(f"/etapa/{etapa}")
    assert resposta.status_code == 200
    for secao in ("Exige", "Desenvolve", "Recursos", "Destrava"):
        assert secao in resposta.text


def test_competencia_destaca_o_criterio_de_verificacao(cliente: TestClient) -> None:
    """`verificacao` é o campo que liga catálogo a percurso (docs/catalogo.md §2)."""
    resposta = cliente.get("/competencia/comp:dados/sql-consultas")
    assert resposta.status_code == 200
    assert "Como se verifica" in resposta.text


def test_diagnostico_roda_as_validacoes(cliente: TestClient) -> None:
    resposta = cliente.get("/catalogo/diagnostico")
    assert resposta.status_code == 200
    assert "Catálogo válido" in resposta.text


def test_diagnostico_acusa_snapshot_desatualizado(tmp_path: Path, fixture_catalogo: Path) -> None:
    """O equivalente visual de `trilhas compilar --conferir`."""
    import shutil

    autoria = tmp_path / "catalogo"
    shutil.copytree(fixture_catalogo, autoria)
    catalogo, _ = carregar(autoria)
    (tmp_path / "catalogo.lock.json").write_text(
        json.dumps(compilar(catalogo), ensure_ascii=False), encoding="utf-8"
    )

    alvo = autoria / "competencias" / "dados.yaml"
    alvo.write_text(
        alvo.read_text(encoding="utf-8").replace("rev: 1", "rev: 2", 1), encoding="utf-8"
    )

    cliente = TestClient(criar_app(lock=tmp_path / "catalogo.lock.json", hoje=lambda: HOJE))
    resposta = cliente.get("/catalogo/diagnostico")
    assert "Snapshot desatualizado" in resposta.text


def test_recarrega_quando_o_snapshot_muda(cliente: TestClient, lock: Path) -> None:
    """Dá para rodar `trilhas compilar` com a interface aberta."""
    assert "catálogo v1" in cliente.get("/acervo").text
    dados = json.loads(lock.read_text(encoding="utf-8"))
    dados["catalogo_versao"] = 99
    lock.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    assert "catálogo v99" in cliente.get("/acervo").text


def test_estatico_e_servido(cliente: TestClient) -> None:
    assert cliente.get("/estatico/estilo.css").status_code == 200
    assert cliente.get("/estatico/pan-zoom.js").status_code == 200


@pytest.mark.parametrize("modelo", sorted(p.name for p in MODELOS.glob("*.html")))
def test_template_nao_usa_termo_descartado(modelo: str) -> None:
    """Vocabulário único, inclusive em rótulo e texto de botão (docs/interface.md §6.1)."""
    texto = (MODELOS / modelo).read_text(encoding="utf-8").casefold()
    achados = [t for t in PROIBIDOS if re.search(rf"\b{t}s?\b", texto)]
    assert not achados, f"{modelo} usa termo fora do glossário: {achados}"


def _uma_trilha(cliente: TestClient) -> str:
    achado = re.search(r"/trilha/(trilha:[\w\-/]+)", cliente.get("/acervo").text)
    assert achado
    return achado.group(1)


def _uma_etapa(cliente: TestClient) -> str:
    pagina = cliente.get(f"/trilha/{_uma_trilha(cliente)}").text
    achado = re.search(r"/etapa/(etapa:[\w\-/]+)", pagina)
    assert achado
    return achado.group(1)


# --- painel Agora --------------------------------------------------------------

PERCURSO_MATRICULADO = """
versao_schema: 1
estudante:
  id: est:teste
  nome: Estudante de Teste
perfil:
  competencias_dominadas: []
  restricoes:
    idiomas: [pt-BR]
matriculas:
  - trilha: trilha:dados/fundamentos
    rev: 1
    iniciada_em: 2026-10-01
    estado: em_andamento
progresso:
  - etapa: etapa:dados/sql-select
    rev: 1
    estado: em_andamento
    iniciada_em: 2026-10-05
"""

PERCURSO_SEM_RUMO = """
versao_schema: 1
estudante:
  id: est:novo
  nome: Estudante Novo
perfil:
  competencias_dominadas: []
"""


@pytest.fixture
def com_percurso(lock: Path) -> TestClient:
    """Painel precisa de catálogo e percurso lado a lado, como no repositório."""
    pasta = lock.parent / "percurso"
    pasta.mkdir()
    (pasta / "est-teste.yaml").write_text(PERCURSO_MATRICULADO, encoding="utf-8")
    return TestClient(criar_app(lock=lock, hoje=lambda: HOJE))


def test_painel_sugere_com_os_fatores_a_vista(com_percurso: TestClient) -> None:
    """Sem os fatores o cartão não pode existir (docs/interface.md §6.2)."""
    resposta = com_percurso.get("/")
    assert resposta.status_code == 200
    for fator in (
        "relevância",
        "prontidão",
        "momentum",
        "encaixe de esforço",
        "desbloqueio",
        "urgência de revisão",
    ):
        assert fator in resposta.text
    assert "etapa:dados/sql-select" in resposta.text  # a etapa em andamento é retomada


def test_painel_registra_a_versao_do_catalogo(com_percurso: TestClient) -> None:
    """Toda sugestão guarda a versão que a produziu (CONTEXT.md §4)."""
    assert "catálogo versão 1" in com_percurso.get("/").text


def test_painel_explica_quem_nao_apareceu(com_percurso: TestClient) -> None:
    """`motor §2.2`: candidato eliminado registra o motivo."""
    resposta = com_percurso.get("/")
    assert "Por que isto não apareceu" in resposta.text
    assert "candidatos eliminados" in resposta.text


def test_tempo_disponivel_entra_na_url(com_percurso: TestClient) -> None:
    """Sugestão reproduzível exige estado na URL, não em sessão (ADR-0007)."""
    resposta = com_percurso.get("/", params={"tempo": "15"})
    assert resposta.status_code == 200
    assert "Sessão de 15 min" in resposta.text


def test_tempo_curto_filtra_em_vez_de_despontuar(com_percurso: TestClient) -> None:
    sem_limite = com_percurso.get("/").text.count('class="sugestao"')
    com_limite = com_percurso.get("/", params={"tempo": "5"}).text
    assert com_limite.count('class="sugestao"') < sem_limite
    assert "não cabe no tempo informado" in com_limite


def test_restricao_que_bloqueia_tudo_e_nomeada_com_saida(com_percurso: TestClient) -> None:
    """Estado vazio diz qual restrição eliminou mais e oferece afrouxá-la (§5.2)."""
    resposta = com_percurso.get("/", params={"tempo": "5"}).text
    assert "Suas restrições eliminaram tudo" in resposta
    assert "A restrição que mais eliminou" in resposta
    assert "Ver sem limite de tempo" in resposta


def test_quantidade_controla_o_top_n(com_percurso: TestClient) -> None:
    assert com_percurso.get("/", params={"quantidade": "1"}).text.count('class="sugestao"') == 1


def test_perfil_insuficiente_e_tela_desenhada(lock: Path) -> None:
    """Estudante novo não recebe sugestão inventada (motor §4)."""
    pasta = lock.parent / "percurso"
    pasta.mkdir()
    (pasta / "est-novo.yaml").write_text(PERCURSO_SEM_RUMO, encoding="utf-8")
    cliente = TestClient(criar_app(lock=lock, hoje=lambda: HOJE))

    resposta = cliente.get("/")
    assert resposta.status_code == 200
    assert "Nada a sugerir ainda" in resposta.text
    assert "Escolher uma trilha" in resposta.text


def test_sem_percurso_nenhum_o_painel_diz_o_que_falta(cliente: TestClient) -> None:
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    assert "Nenhum percurso encontrado" in resposta.text


def test_painel_nao_quebra_sem_catalogo(tmp_path: Path) -> None:
    cliente = TestClient(criar_app(lock=tmp_path / "nao-existe.json", hoje=lambda: HOJE))
    assert cliente.get("/").status_code == 200


# --- desligar ------------------------------------------------------------------


@pytest.fixture
def desligamentos() -> list[int]:
    return []


@pytest.fixture
def cliente_desligavel(lock: Path, desligamentos: list[int]) -> TestClient:
    """Cliente com o desligamento substituído — senão o teste mataria o pytest."""
    return TestClient(
        criar_app(lock=lock, hoje=lambda: HOJE, desligar=lambda: desligamentos.append(1))
    )


def test_toda_tela_oferece_o_botao_de_desligar(cliente: TestClient) -> None:
    """Quem subiu a interface pelo navegador não tem terminal para dar Ctrl-C."""
    for rota in ("/", "/acervo", "/catalogo", "/catalogo/diagnostico"):
        pagina = cliente.get(rota).text
        assert 'action="/desligar"' in pagina, rota
        assert ">Desligar<" in pagina, rota


def test_desligar_encerra_o_servidor_depois_de_responder(
    cliente_desligavel: TestClient, desligamentos: list[int]
) -> None:
    resposta = cliente_desligavel.post("/desligar")
    assert resposta.status_code == 200
    assert "Servidor desligado" in resposta.text
    assert desligamentos == [1]


def test_desligar_recusa_get(cliente_desligavel: TestClient, desligamentos: list[int]) -> None:
    """Efeito colateral não mora em GET: link visitado ou pré-carregado derrubaria o app."""
    assert cliente_desligavel.get("/desligar").status_code == 405
    assert desligamentos == []


def test_desligar_recusa_outra_origem(
    cliente_desligavel: TestClient, desligamentos: list[int]
) -> None:
    """Qualquer página aberta no navegador pode fazer POST para localhost."""
    resposta = cliente_desligavel.post("/desligar", headers={"origin": "http://exemplo.invalido"})
    assert resposta.status_code == 403
    assert desligamentos == []


def test_desligado_nao_oferece_rota_que_nao_responde_mais(cliente_desligavel: TestClient) -> None:
    pagina = cliente_desligavel.post("/desligar").text
    assert 'href="/catalogo"' not in pagina
    assert "abrir-app.sh" in pagina


# --- progresso do estudante nas telas de detalhe --------------------------------

CLASSES_DO_NO = {
    "no",
    "no-opcional",
    "no-emprestada",
    "no-entrada",
    "no-rascunho",
    "no-depreciado",
    "no-estado-concluida",
    "no-estado-em_andamento",
    "no-estado-abandonada",
}


@pytest.fixture
def com_log(lock: Path) -> TestClient:
    """Percurso declarado em YAML **mais** o log de fatos, como no repositório.

    A etapa de entrada e a seguinte ficam concluídas; a de entrada é o nó que acumula
    duas classes no grafo, e é por isso que ela entra aqui.
    """
    pasta = lock.parent / "percurso"
    pasta.mkdir(exist_ok=True)
    (pasta / "est-teste.yaml").write_text(PERCURSO_MATRICULADO, encoding="utf-8")
    entrada = fabrica.etapa("etapa:dados/modelagem-basica")
    seguinte = fabrica.etapa("etapa:dados/sql-select")
    with Repositorio.em_diretorio(pasta) as repo:
        repo.anexar(
            "est:teste",
            [
                *iniciar_etapa(entrada, recurso="rec:dados/modelagem-basica-texto"),
                *concluir_etapa(entrada),
                *iniciar_etapa(seguinte, recurso="rec:dados/sql-select-video"),
                *concluir_etapa(seguinte),
            ],
        )
    return TestClient(criar_app(lock=lock, hoje=lambda: HOJE))


def test_etapa_concluida_se_diz_concluida(com_log: TestClient) -> None:
    resposta = com_log.get("/etapa/etapa:dados/sql-select")
    assert resposta.status_code == 200
    assert "concluída" in resposta.text


def test_etapa_marca_o_recurso_pelo_qual_se_estudou(com_log: TestClient) -> None:
    """A etapa tem mais de um recurso; marcar todos seria o mesmo que não marcar."""
    html = com_log.get("/etapa/etapa:dados/sql-select").text
    marcadas = re.findall(r'<tr id="([^"]+)" class="recurso-em-uso', html)
    assert marcadas == ["rec:dados/sql-select-video"]


def test_etapa_nao_tocada_nao_ganha_marca(com_log: TestClient) -> None:
    html = com_log.get("/etapa/etapa:dados/sql-join").text
    assert "recurso-em-uso" not in html
    assert 'class="etiqueta estado' not in html


def test_trilha_conta_as_etapas_concluidas(com_log: TestClient) -> None:
    html = com_log.get("/trilha/trilha:dados/fundamentos").text
    assert "2 concluída(s)" in html


def test_sem_percurso_a_tela_nao_afirma_progresso_zero(cliente: TestClient) -> None:
    """Não saber e saber que não houve são coisas diferentes (docs/interface.md §6)."""
    html = cliente.get("/trilha/trilha:dados/fundamentos").text
    assert "sem percurso" in html
    assert "concluída(s)" not in html


def test_progresso_declarado_no_yaml_nao_vale_mais_que_o_log(com_percurso: TestClient) -> None:
    """ADR-0008: progresso é projeção do log, e o campo do YAML é histórico pré-ADR.

    `PERCURSO_MATRICULADO` declara `sql-select` em andamento e não há log nenhum. Honrar
    o YAML aqui faria a tela discordar de `trilhas-percurso mostrar` sem dizer por quê —
    que foi exatamente o sintoma que motivou ligar a web ao log.
    """
    html = com_percurso.get("/etapa/etapa:dados/sql-select").text
    assert "estado-em_andamento" not in html


def test_classes_do_no_do_grafo_nao_saem_grudadas(com_log: TestClient) -> None:
    """`trim_blocks` come a quebra de linha depois de `{% endif %}` e `lstrip_blocks`
    come o recuo antes do `{% if %}` seguinte: duas classes condicionais em linhas
    separadas saíam como `no-entradano-estado-concluida`, que não casa com seletor
    nenhum e some sem erro — o nó fica sem marca e a tela mente em silêncio.
    """
    html = com_log.get("/trilha/trilha:dados/fundamentos").text
    atributos = [v.split() for v in re.findall(r'class="(no(?:\s[^"]*)?)"', html)]
    assert any(len(tokens) >= 2 for tokens in atributos), "nenhum nó acumulou classes"
    for tokens in atributos:
        for token in tokens:
            assert token in CLASSES_DO_NO, f"classe desconhecida no grafo: {token!r}"


# --- escrita de percurso pela tela (docs/interface.md §5.10) --------------------

TRAVADA = "etapa:dados/sql-join"
"""Exige três competências e o log começa vazio — nenhuma está satisfeita."""


def _fatos(cliente: TestClient, estudante: str = "est:teste") -> list[str]:
    """Os fatos gravados, pelo nome do evento. Lê o log, não a tela."""
    pasta = Path(cliente.app.state.ctx.fonte.percursos)  # type: ignore[attr-defined]
    return [type(r.evento).__name__ for r in registros_em(pasta, estudante)]


def test_etapa_oferece_iniciar_quando_ha_percurso(com_percurso: TestClient) -> None:
    html = com_percurso.get(f"/etapa/{TRAVADA}").text
    assert 'name="acao" value="iniciar"' in html
    assert ">Iniciar<" in html


def test_sem_percurso_a_tela_nao_oferece_registrar(cliente: TestClient) -> None:
    """Um fato datado precisa de estudante; o botão faria o clique inventar um."""
    html = cliente.get(f"/etapa/{TRAVADA}").text
    assert 'name="acao"' not in html
    assert "Declare" in html


def test_iniciar_pela_tela_grava_o_fato_e_redireciona(com_percurso: TestClient) -> None:
    resposta = com_percurso.post(
        f"/etapa/{TRAVADA}",
        data={"acao": "iniciar", "recurso": "rec:dados/sql-join-exercicios"},
        follow_redirects=False,
    )
    assert resposta.status_code == 303
    assert resposta.headers["location"] == f"/etapa/{TRAVADA}"
    assert _fatos(com_percurso) == ["EtapaIniciada"]

    html = com_percurso.get(f"/etapa/{TRAVADA}").text
    assert "em andamento" in html
    assert re.findall(r'<tr id="([^"]+)" class="recurso-em-uso', html) == [
        "rec:dados/sql-join-exercicios"
    ]


def test_concluir_grava_conclusao_e_evidencia_numa_transacao(com_percurso: TestClient) -> None:
    """Dois fatos, um POST: meia conclusão daria progresso sem a evidência que o funda."""
    com_percurso.post(f"/etapa/{TRAVADA}", data={"acao": "concluir"})
    assert _fatos(com_percurso) == ["EtapaConcluida", "EvidenciaRegistrada"]


def test_concluir_etapa_travada_e_gravado(com_percurso: TestClient) -> None:
    """O log é de fatos, não de permissões (web/escrever.py).

    `sql-join` exige três competências e o estudante não tem nenhuma. Quem estudou
    fora do sistema concluiu a etapa, e o sistema discordar não desfaz a leitura —
    filtrar por fronteira satisfeita é papel do motor, ao escolher o que *sugerir*.
    """
    assert com_percurso.post(f"/etapa/{TRAVADA}", data={"acao": "concluir"}).status_code == 200
    assert "EtapaConcluida" in _fatos(com_percurso)
    assert "concluída" in com_percurso.get(f"/etapa/{TRAVADA}").text


def test_f5_depois_do_post_nao_duplica_fato(com_percurso: TestClient) -> None:
    """O 303 existe por isto: recarregar a página é GET, e GET não grava."""
    com_percurso.post(f"/etapa/{TRAVADA}", data={"acao": "iniciar"})
    depois = _fatos(com_percurso)
    for _ in range(3):
        assert com_percurso.get(f"/etapa/{TRAVADA}").status_code == 200
    assert _fatos(com_percurso) == depois


def test_abandonar_guarda_o_motivo(com_percurso: TestClient) -> None:
    com_percurso.post(f"/etapa/{TRAVADA}", data={"acao": "iniciar"})
    com_percurso.post(f"/etapa/{TRAVADA}", data={"acao": "abandonar", "motivo": "material ruim"})
    pasta = Path(com_percurso.app.state.ctx.fonte.percursos)  # type: ignore[attr-defined]
    ultimo = registros_em(pasta, "est:teste")[-1].evento
    assert isinstance(ultimo, EtapaAbandonada)
    assert ultimo.motivo == "material ruim"


def test_etapa_concluida_pode_ser_reiniciada(com_percurso: TestClient) -> None:
    """Enquanto não houver fato de retratação (ADR-0008), é a saída de quem clicou errado."""
    com_percurso.post(f"/etapa/{TRAVADA}", data={"acao": "concluir"})
    html = com_percurso.get(f"/etapa/{TRAVADA}").text
    assert ">Estudar de novo<" in html

    com_percurso.post(f"/etapa/{TRAVADA}", data={"acao": "iniciar"})
    assert _fatos(com_percurso)[-1] == "EtapaIniciada"
    assert "em andamento" in com_percurso.get(f"/etapa/{TRAVADA}").text


def test_post_de_outra_origem_e_recusado(com_percurso: TestClient) -> None:
    """Qualquer página aberta no navegador faz POST para localhost, e o log não desfaz."""
    resposta = com_percurso.post(
        f"/etapa/{TRAVADA}",
        data={"acao": "concluir"},
        headers={"origin": "http://exemplo.invalido"},
    )
    assert resposta.status_code == 403
    assert _fatos(com_percurso) == []


def test_recurso_de_outra_etapa_e_recusado_como_na_cli(com_percurso: TestClient) -> None:
    """Mesma `registrar.conferir_recurso` da CLI — a tela não afrouxa nem aperta."""
    resposta = com_percurso.post(
        f"/etapa/{TRAVADA}",
        data={"acao": "iniciar", "recurso": "rec:dados/sql-select-video"},
    )
    assert resposta.status_code == 400
    assert "recurso de outra etapa" in resposta.text
    assert _fatos(com_percurso) == []


def test_acao_desconhecida_nao_grava(com_percurso: TestClient) -> None:
    resposta = com_percurso.post(f"/etapa/{TRAVADA}", data={"acao": "apagar"})
    assert resposta.status_code == 400
    assert _fatos(com_percurso) == []


def test_post_sem_percurso_nao_faz_nascer_log(cliente: TestClient, lock: Path) -> None:
    """Desenhar — ou recusar — uma tela nunca cria banco (ADR-0008, interface.md §9.1)."""
    resposta = cliente.post(f"/etapa/{TRAVADA}", data={"acao": "concluir"})
    assert resposta.status_code == 409
    assert not (lock.parent / "percurso").exists()


def test_post_preserva_o_estudante_da_url(com_percurso: TestClient) -> None:
    """O POST não troca de pessoa: quem a tela mostrava é quem recebe o fato."""
    resposta = com_percurso.post(
        f"/etapa/{TRAVADA}?estudante=est:teste",
        data={"acao": "iniciar"},
        follow_redirects=False,
    )
    assert resposta.headers["location"] == f"/etapa/{TRAVADA}?estudante=est%3Ateste"
