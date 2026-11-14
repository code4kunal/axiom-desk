"""Append-only emission log: every recorded output, read back exactly as it was known at a time."""

import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from axiom_core.db import Connection
from axiom_core.envelope import JsonValue


@dataclass(frozen=True)
class Emission:
    id: str
    tenant_id: str
    kind: str
    instrument: str
    knowledge_ts: datetime
    event_ts: datetime
    version: str
    payload: JsonValue


class EmissionLog:
    def __init__(self, conn: Connection, clock: Callable[[], float]) -> None:
        self._conn = conn
        # knowledge time comes from the clock, never the caller, so nothing lands in the past
        self._clock = clock

    def record(
        self,
        tenant_id: str,
        kind: str,
        instrument: str,
        event_ts: datetime,
        version: str,
        payload: JsonValue,
    ) -> Emission:
        if event_ts.tzinfo is None:
            raise ValueError("an emission needs a timezone-aware event_ts")
        emission = Emission(
            f"emi_{uuid.uuid4().hex}",
            tenant_id,
            kind,
            instrument,
            datetime.fromtimestamp(self._clock(), UTC),
            event_ts,
            version,
            payload,
        )
        with self._conn:
            self._conn.execute(
                "INSERT INTO emissions (id, tenant_id, kind, instrument, knowledge_ts, event_ts,"
                " version, payload) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    emission.id,
                    tenant_id,
                    kind,
                    instrument,
                    emission.knowledge_ts.timestamp(),
                    event_ts.timestamp(),
                    version,
                    json.dumps(payload),
                ),
            )
        return emission

    def as_of(self, tenant_id: str, kind: str, instrument: str, as_of: datetime) -> list[Emission]:
        """Per event time, the latest emission known at `as_of`; a later correction supersedes."""
        if as_of.tzinfo is None:
            raise ValueError("as_of must be timezone-aware")
        rows = self._conn.execute(
            "SELECT id, tenant_id, kind, instrument, knowledge_ts, event_ts, version, payload"
            " FROM (SELECT *, ROW_NUMBER() OVER ("
            "   PARTITION BY event_ts ORDER BY knowledge_ts DESC, rowid DESC) AS rank"
            "  FROM emissions"
            "  WHERE tenant_id = ? AND kind = ? AND instrument = ? AND knowledge_ts <= ?)"
            " WHERE rank = 1 ORDER BY event_ts",
            (tenant_id, kind, instrument, as_of.timestamp()),
        ).fetchall()
        return [
            Emission(
                r[0],
                r[1],
                r[2],
                r[3],
                datetime.fromtimestamp(r[4], UTC),
                datetime.fromtimestamp(r[5], UTC),
                r[6],
                json.loads(r[7]),
            )
            for r in rows
        ]
