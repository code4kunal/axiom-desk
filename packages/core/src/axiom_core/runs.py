"""Published runs: immutable, addressable results that screens and the agent both read."""

import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from axiom_core.db import Connection
from axiom_core.envelope import JsonValue, Source


@dataclass(frozen=True)
class Run:
    id: str
    kind: str
    as_of: datetime
    published_at: float
    payload: JsonValue
    sources: tuple[Source, ...]


class RunStore:
    def __init__(self, conn: Connection, clock: Callable[[], float]) -> None:
        self._conn = conn
        self._clock = clock

    def publish(
        self, kind: str, as_of: datetime, payload: JsonValue, sources: tuple[Source, ...]
    ) -> Run:
        if not sources or as_of.tzinfo is None:
            raise ValueError("a run needs sources and a timezone-aware as_of")
        run = Run(f"run_{uuid.uuid4().hex}", kind, as_of, self._clock(), payload, sources)
        with self._conn:
            self._conn.execute(
                "INSERT INTO runs (id, kind, as_of, published_at, payload, sources)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (
                    run.id,
                    kind,
                    as_of.isoformat(),
                    run.published_at,
                    json.dumps(payload),
                    json.dumps([[s.name, s.licence_scope] for s in sources]),
                ),
            )
        return run

    def get(self, run_id: str) -> Run | None:
        return self._one("WHERE id = ?", (run_id,))

    def latest(self, kind: str) -> Run | None:
        return self._one("WHERE kind = ? ORDER BY published_at DESC, rowid DESC LIMIT 1", (kind,))

    def latest_as_of(self, kind: str, as_of: datetime) -> Run | None:
        if as_of.tzinfo is None:
            raise ValueError("as_of must be timezone-aware")
        return self._one(
            "WHERE kind = ? AND published_at <= ? ORDER BY published_at DESC, rowid DESC LIMIT 1",
            (kind, as_of.timestamp()),
        )

    def _one(self, where: str, args: tuple[str | float, ...]) -> Run | None:
        row = self._conn.execute(
            f"SELECT id, kind, as_of, published_at, payload, sources FROM runs {where}", args
        ).fetchone()
        if row is None:
            return None
        sources = tuple(Source(name, scope) for name, scope in json.loads(row[5]))
        return Run(
            row[0], row[1], datetime.fromisoformat(row[2]), row[3], json.loads(row[4]), sources
        )
