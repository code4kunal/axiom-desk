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
        # executescript commits before it runs, so the transaction must live inside the script.
        # The marker row goes first: a second process migrating the same file hits the primary
        # key and backs out instead of running the script twice.
        name = path.name.replace("'", "''")
        script = (
            f"BEGIN IMMEDIATE;\nINSERT INTO schema_migrations (name) VALUES ('{name}');\n"
            f"{path.read_text()}\n;COMMIT;"
        )
        try:
            conn.executescript(script)
        except BaseException:
            conn.rollback()
            taken = conn.execute(
                "SELECT 1 FROM schema_migrations WHERE name = ?", (path.name,)
            ).fetchone()
            if taken is None:
                raise
            continue
        applied.append(path.name)
    return applied
