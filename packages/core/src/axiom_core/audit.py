"""Append-only audit log of material actions: principal, action, ids and verdict, never data."""

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from axiom_core.db import Connection
from axiom_core.principals import Principal

MAX_ID_LEN = 128
MAX_IDS = 16


@dataclass(frozen=True)
class AuditRecord:
    at: float
    kind: str
    tenant_id: str
    user_id: str
    action: str
    verdict: str
    ids: dict[str, str]


class AuditLog:
    def __init__(self, conn: Connection, clock: Callable[[], float]) -> None:
        self._conn = conn
        self.clock = clock

    def record(
        self, principal: Principal, action: str, verdict: str, ids: Mapping[str, str]
    ) -> None:
        if len(ids) > MAX_IDS or any(len(v) > MAX_ID_LEN for v in ids.values()):
            raise ValueError("audit ids must be short identifiers, not payloads")
        with self._conn:
            self._conn.execute(
                "INSERT INTO audit_log (at, kind, tenant_id, user_id, action, verdict, ids)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    self.clock(),
                    principal.kind.value,
                    principal.tenant_id,
                    principal.user_id,
                    action,
                    verdict,
                    json.dumps(dict(ids), sort_keys=True),
                ),
            )

    def records(self) -> list[AuditRecord]:
        rows = self._conn.execute(
            "SELECT at, kind, tenant_id, user_id, action, verdict, ids FROM audit_log ORDER BY id"
        )
        return [AuditRecord(*row[:6], ids=json.loads(row[6])) for row in rows]
