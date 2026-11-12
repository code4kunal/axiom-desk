import sqlite3

import pytest
from axiom_core.audit import AuditLog
from axiom_core.tenancy import Principal, PrincipalKind
from conftest import Clock


def test_records_round_trip_through_the_database(conn: sqlite3.Connection, clock: Clock) -> None:
    log = AuditLog(conn, clock)
    p = Principal(PrincipalKind.AGENT, "desk", "tara")
    log.record(p, "write_draft", "allowed", {"draft_id": "d-1"})
    fresh = AuditLog(conn, clock).records()
    assert len(fresh) == 1
    r = fresh[0]
    assert (r.kind, r.tenant_id, r.user_id, r.action, r.verdict, r.at) == (
        "agent",
        "desk",
        "tara",
        "write_draft",
        "allowed",
        clock.now,
    )
    assert r.ids == {"draft_id": "d-1"}


def test_ids_must_be_short_identifiers_never_payloads(
    conn: sqlite3.Connection, clock: Clock
) -> None:
    log = AuditLog(conn, clock)
    p = Principal(PrincipalKind.USER, "desk", "ana")
    with pytest.raises(ValueError):
        log.record(p, "read", "allowed", {"ticks": "[" + "101.5," * 50 + "]"})
