"""Schema migrations for the records database."""

import sqlite3
from pathlib import Path

MIGRATIONS = Path(__file__).parent / "migrations"

# shortcut: records run on sqlite until the Postgres deployment lands with the market-data
# store; the SQL stays portable and the `?` paramstyle is the only sqlite-specific part.
Connection = sqlite3.Connection


def migrate(conn: Connection) -> list[str]:
    conn.execute("CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY)")
    done = {row[0] for row in conn.execute("SELECT name FROM schema_migrations")}
    applied: list[str] = []
    for path in sorted(MIGRATIONS.glob("*.sql")):
        if path.name in done:
            continue
        with conn:
            conn.executescript(path.read_text())
            conn.execute("INSERT INTO schema_migrations (name) VALUES (?)", (path.name,))
        applied.append(path.name)
    return applied
