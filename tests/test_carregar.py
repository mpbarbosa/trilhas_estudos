"""Erros de forma: YAML inválido, campo ausente, valor fora do domínio."""

from __future__ import annotations

from pathlib import Path

from trilhas.catalogo.carregar import carregar
from trilhas.catalogo.modelo import Nivel, Status
from trilhas.catalogo.problemas import Codigo, tem_erro


def escrever(raiz: Path, nome: str, conteudo: str) -> Path:
    destino = raiz / nome
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(conteudo, encoding="utf-8")
    return destino


def codigos(problemas: list) -> set[Codigo]:
    return {p.codigo for p in problemas}


def test_diretorio_inexistente(tmp_path: Path) -> None:
    _, problemas = carregar(tmp_path / "nao-existe")
    assert Codigo.YAML_INVALIDO in codigos(problemas)


def test_yaml_malformado_reporta_arquivo(tmp_path: Path) -> None:
    escrever(tmp_path, "competencias/x.yaml", "versao_schema: 1\ncompetencias: [\n")
    _, problemas = carregar(tmp_path)
    assert Codigo.YAML_INVALIDO in codigos(problemas)
    assert problemas[0].arquivo is not None
    assert problemas[0].arquivo.endswith("competencias/x.yaml")


def test_versao_schema_ausente(tmp_path: Path) -> None:
    escrever(tmp_path, "competencias/x.yaml", "competencias: []\n")
    _, problemas = carregar(tmp_path)
    assert any("versao_schema" in p.mensagem for p in problemas)


def test_versao_schema_futura(tmp_path: Path) -> None:
    escrever(tmp_path, "competencias/x.yaml", "versao_schema: 99\ncompetencias: []\n")
    _, problemas = carregar(tmp_path)
    assert Codigo.SCHEMA_INVALIDO in codigos(problemas)


def test_competencia_sem_verificacao_e_descartada(tmp_path: Path) -> None:
    """`verificacao` é obrigatório (catalogo.md §2): sem ele a entidade não entra."""
    escrever(
        tmp_path,
        "competencias/x.yaml",
        "versao_schema: 1\ncompetencias:\n  - id: comp:x/a\n    titulo: A\n    rev: 1\n",
    )
    catalogo, problemas = carregar(tmp_path)
    assert catalogo.competencias == {}
    assert any("verificacao" in p.mensagem for p in problemas)


def test_nivel_desconhecido(tmp_path: Path) -> None:
    escrever(
        tmp_path,
        "etapas/x.yaml",
        """versao_schema: 1
etapas:
  - id: etapa:x/a
    titulo: A
    rev: 1
    esforco_estimado_min: 10
    teaches:
      - competencia: comp:x/a
        nivel_resultante: semideus
""",
    )
    _, problemas = carregar(tmp_path)
    assert any("nível desconhecido" in p.mensagem for p in problemas)


def test_id_duplicado_entre_arquivos(tmp_path: Path) -> None:
    corpo = (
        "versao_schema: 1\ncompetencias:\n  - id: comp:x/a\n    titulo: A\n"
        "    rev: 1\n    verificacao: v\n"
    )
    escrever(tmp_path, "competencias/um.yaml", corpo)
    escrever(tmp_path, "competencias/dois.yaml", corpo)
    _, problemas = carregar(tmp_path)
    assert Codigo.ID_INVALIDO in codigos(problemas)


def test_etapa_da_trilha_recebe_a_trilha_como_dona(tmp_path: Path) -> None:
    escrever(
        tmp_path,
        "trilhas/t.yaml",
        """versao_schema: 1
trilha:
  id: trilha:x/t
  titulo: T
  rev: 1
  etapas:
    - id: etapa:x/a
      titulo: A
      rev: 1
      esforco_estimado_min: 30
      status: rascunho
""",
    )
    catalogo, problemas = carregar(tmp_path)
    assert not tem_erro(problemas)
    assert catalogo.etapas["etapa:x/a"].trilha == "trilha:x/t"
    assert catalogo.etapas["etapa:x/a"].status is Status.RASCUNHO
    assert catalogo.trilhas["trilha:x/t"].etapas == ("etapa:x/a",)


def test_niveis_sao_ordinais() -> None:
    assert Nivel.DESCONHECE < Nivel.INICIANTE < Nivel.INTERMEDIARIO < Nivel.AVANCADO
    assert str(Nivel.de_texto("AVANCADO")) == "avancado"


RECURSO_COM_OBRA = """versao_schema: 1
recursos:
  - id: rec:x/fatia
    etapa: etapa:x/a
    titulo: Fatia
    rev: 1
    formato: texto
    custo: 90
    duracao_min: 60
    obra: {obra}
"""


def test_obra_fora_do_formato_de_slug_e_erro_de_forma(tmp_path: Path) -> None:
    """`obra` é slug puro: prefixo de tipo não passa, porque obra não é id."""
    escrever(tmp_path, "recursos/x.yaml", RECURSO_COM_OBRA.format(obra="rec:dados/date-vol1"))
    catalogo, problemas = carregar(tmp_path)
    assert Codigo.SCHEMA_INVALIDO in codigos(problemas)
    assert catalogo.recursos["rec:x/fatia"].obra is None


def test_obra_em_slug_e_aceita(tmp_path: Path) -> None:
    escrever(tmp_path, "recursos/x.yaml", RECURSO_COM_OBRA.format(obra="date-vol1"))
    catalogo, problemas = carregar(tmp_path)
    assert not tem_erro(problemas)
    assert catalogo.recursos["rec:x/fatia"].obra == "date-vol1"


def test_recurso_sem_obra_fica_sem_agrupamento(tmp_path: Path) -> None:
    corpo = "\n".join(ln for ln in RECURSO_COM_OBRA.splitlines() if "obra:" not in ln) + "\n"
    escrever(tmp_path, "recursos/x.yaml", corpo)
    catalogo, problemas = carregar(tmp_path)
    assert not tem_erro(problemas)
    assert catalogo.recursos["rec:x/fatia"].obra is None
