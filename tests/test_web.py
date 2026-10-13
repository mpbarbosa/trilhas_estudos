"""Rotas da interface. HTML é o contrato: as asserções olham o que a tela precisa dizer."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from trilhas.catalogo.carregar import carregar
from trilhas.catalogo.compilar import compilar
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
