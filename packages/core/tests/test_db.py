import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from axiom_core import db


def tables(conn: sqlite3.Connection) -> set[str]:
    return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}


def test_a_migration_that_fails_midway_leaves_nothing_behind(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "0001_ok.sql").write_text("CREATE TABLE first (x INTEGER);")
    broken = tmp_path / "0002_broken.sql"
    broken.write_text("CREATE TABLE half (x INTEGER);\nCREATE TABLE oops (;")
    monkeypatch.setattr(db, "MIGRATIONS", tmp_path)
    conn = sqlite3.connect(tmp_path / "records.db")

    with pytest.raises(sqlite3.OperationalError):
        db.migrate(conn)
    assert "first" in tables(conn)
    assert "half" not in tables(conn)
    assert [r[0] for r in conn.execute("SELECT name FROM schema_migrations")] == ["0001_ok.sql"]

    broken.write_text("CREATE TABLE half (x INTEGER);")
    assert db.migrate(conn) == ["0002_broken.sql"]
    assert "half" in tables(conn)


def test_a_migration_another_process_already_applied_is_skipped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "0001_ok.sql").write_text("CREATE TABLE first (x INTEGER);")
    monkeypatch.setattr(db, "MIGRATIONS", tmp_path)
    path = tmp_path / "records.db"
    rival_pending = [True]
    real_glob = Path.glob

    def glob_after_rival(self: Path, pattern: str) -> Iterator[Path]:
        # the rival process finishes after this one has read which migrations are done
        if rival_pending:
            rival_pending.pop()
            assert db.migrate(sqlite3.connect(path)) == ["0001_ok.sql"]
        return real_glob(self, pattern)

    monkeypatch.setattr(Path, "glob", glob_after_rival)
    late = sqlite3.connect(path)
    assert db.migrate(late) == []
    assert [r[0] for r in late.execute("SELECT name FROM schema_migrations")] == ["0001_ok.sql"]
