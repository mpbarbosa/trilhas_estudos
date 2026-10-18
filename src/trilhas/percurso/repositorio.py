"""O log append-only em SQLite (ADR-0008). Borda de I/O.

Terceira borda do projeto, ao lado de `catalogo/cli.py` e `web/dados.py`: é o único
módulo de `percurso/` que toca disco e relógio. `UPDATE` e `DELETE` são bloqueados por
*trigger* — o log só cresce, e quem impõe isso é o banco, não a convenção.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from types import TracebackType
from typing import Any, Self

from .eventos import Evento, Registro, evento_de_dados, nome_do_tipo

VERSAO_DO_ESQUEMA = 1

_PROIBIDO = "o log de percurso é append-only (ADR-0008)"

_ESQUEMA = f"""
CREATE TABLE IF NOT EXISTS evento (
    seq       INTEGER PRIMARY KEY AUTOINCREMENT,
    estudante TEXT NOT NULL,
    tipo      TEXT NOT NULL,
    em        TEXT NOT NULL,
    dados     TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_evento_estudante ON evento (estudante, seq);

CREATE TRIGGER IF NOT EXISTS evento_sem_update
BEFORE UPDATE ON evento
BEGIN
    SELECT RAISE(ABORT, '{_PROIBIDO}: UPDATE proibido');
END;

CREATE TRIGGER IF NOT EXISTS evento_sem_delete
BEFORE DELETE ON evento
BEGIN
    SELECT RAISE(ABORT, '{_PROIBIDO}: DELETE proibido');
END;
"""


class Repositorio:
    """Abre (e cria, se preciso) o log de um diretório de percurso."""

    NOME_DO_ARQUIVO = "percurso.sqlite3"

    def __init__(self, caminho: Path) -> None:
        self.caminho = caminho
        caminho.parent.mkdir(parents=True, exist_ok=True)
        self._con = sqlite3.connect(caminho, isolation_level="DEFERRED")
        self._con.execute("PRAGMA foreign_keys = ON")
        self._con.executescript(_ESQUEMA)
        self._con.execute(f"PRAGMA user_version = {VERSAO_DO_ESQUEMA}")
        self._con.commit()

    @classmethod
    def em_diretorio(cls, diretorio: Path) -> Self:
        return cls(diretorio / cls.NOME_DO_ARQUIVO)

    def anexar(
        self,
        estudante: str,
        eventos: Iterable[Evento],
        *,
        em: datetime | None = None,
    ) -> list[Registro]:
        """Grava os eventos numa única transação (interface.md §9).

        Ou entram todos, ou nenhum: concluir etapa são dois fatos, e meia conclusão
        produziria progresso sem a evidência que o justifica.
        """
        instante = em or datetime.now(UTC)
        lote = list(eventos)
        if not lote:
            return []

        with self._con:  # commit no fim, rollback em exceção
            cursor = self._con.cursor()
            gravados: list[Registro] = []
            for evento in lote:
                cursor.execute(
                    "INSERT INTO evento (estudante, tipo, em, dados) VALUES (?, ?, ?, ?)",
                    (
                        estudante,
                        nome_do_tipo(evento),
                        instante.isoformat(),
                        json.dumps(evento.como_dados(), ensure_ascii=False),
                    ),
                )
                gravados.append(
                    Registro(
                        evento=evento,
                        em=instante,
                        estudante=estudante,
                        seq=int(cursor.lastrowid or 0),
                    )
                )
        return gravados

    def importar(self, estudante: str, fatos: Iterable[tuple[Evento, datetime]]) -> list[Registro]:
        """Grava fatos com a data que cada um declarava (migração, ver `migrar`).

        Numa transação só, como `anexar`: migração pela metade deixaria o percurso
        num estado que nunca existiu.
        """
        lote = list(fatos)
        if not lote:
            return []
        with self._con:
            cursor = self._con.cursor()
            gravados: list[Registro] = []
            for evento, instante in lote:
                cursor.execute(
                    "INSERT INTO evento (estudante, tipo, em, dados) VALUES (?, ?, ?, ?)",
                    (
                        estudante,
                        nome_do_tipo(evento),
                        instante.isoformat(),
                        json.dumps(evento.como_dados(), ensure_ascii=False),
                    ),
                )
                gravados.append(
                    Registro(
                        evento=evento,
                        em=instante,
                        estudante=estudante,
                        seq=int(cursor.lastrowid or 0),
                    )
                )
        return gravados

    def registros(self, estudante: str) -> list[Registro]:
        """Todos os fatos de um estudante, em ordem de log."""
        linhas = self._con.execute(
            "SELECT seq, estudante, tipo, em, dados FROM evento WHERE estudante = ? ORDER BY seq",
            (estudante,),
        ).fetchall()
        return [registro for registro in map(_de_linha, linhas) if registro is not None]

    def exportar(self, estudante: str) -> str:
        """O log em JSONL: uma linha por fato, em ordem, para commitar e auditar.

        O `.sqlite3` é estado local e fica fora do git; esta exportação é o que torna
        o histórico durável e legível em `git diff`. Reconstruir o banco a partir dela
        **não** está implementado: é cópia de auditoria, não segunda fonte da verdade.
        """
        linhas = self._con.execute(
            "SELECT seq, tipo, em, dados FROM evento WHERE estudante = ? ORDER BY seq",
            (estudante,),
        ).fetchall()
        return "".join(
            json.dumps(
                {
                    "seq": int(seq),
                    "tipo": str(tipo),
                    "em": str(em),
                    "dados": json.loads(dados),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n"
            for seq, tipo, em, dados in linhas
        )

    def estudantes(self) -> Sequence[str]:
        linhas = self._con.execute(
            "SELECT DISTINCT estudante FROM evento ORDER BY estudante"
        ).fetchall()
        return [str(linha[0]) for linha in linhas]

    def fechar(self) -> None:
        self._con.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        valor: BaseException | None,
        pilha: TracebackType | None,
    ) -> None:
        self.fechar()


def registros_em(diretorio: Path, estudante: str) -> list[Registro]:
    """Fatos de um estudante sem abrir o log para escrita. Para quem só lê.

    `Repositorio` cria o arquivo e o esquema ao abrir — certo para quem escreve, errado
    para quem lê: a interface é somente leitura (ADR-0007) e não pode fazer nascer um
    log ao renderizar uma página. Daí a conexão em `mode=ro`, que o SQLite recusa se o
    arquivo não existir, em vez de criá-lo.

    Banco ausente, ilegível ou sem a tabela vira lista vazia — é o "percurso sem fatos"
    do estudante novo, que a projeção já trata como caso normal (ADR-0008), e não um
    erro que derrube a tela.
    """
    caminho = diretorio / Repositorio.NOME_DO_ARQUIVO
    if not caminho.is_file():
        return []
    try:
        con = sqlite3.connect(f"file:{caminho}?mode=ro", uri=True)
    except sqlite3.Error:
        return []
    try:
        linhas = con.execute(
            "SELECT seq, estudante, tipo, em, dados FROM evento WHERE estudante = ? ORDER BY seq",
            (estudante,),
        ).fetchall()
    except sqlite3.Error:
        return []
    finally:
        con.close()
    return [registro for registro in map(_de_linha, linhas) if registro is not None]


def _de_linha(linha: tuple[Any, ...]) -> Registro | None:
    """Linha ilegível é ignorada, não derruba a leitura.

    Mesma tolerância de `web/percurso.py`: um percurso pela metade tem de render uma
    tela, e o motor já sabe responder a perfil insuficiente (motor §4).
    """
    seq, estudante, tipo, em, dados = linha
    try:
        evento = evento_de_dados(str(tipo), json.loads(dados))
        instante = datetime.fromisoformat(str(em))
    except (ValueError, KeyError, TypeError):
        return None
    if evento is None:
        return None
    return Registro(evento=evento, em=instante, estudante=str(estudante), seq=int(seq))
