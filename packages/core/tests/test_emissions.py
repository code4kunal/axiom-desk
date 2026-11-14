import sqlite3
from datetime import UTC, datetime

import pytest
from axiom_core.emissions import EmissionLog
from conftest import Clock


def at(hour: int, minute: int) -> datetime:
    return datetime(2026, 11, 13, hour, minute, tzinfo=UTC)


def write(
    log: EmissionLog,
    clock: Clock,
    written: datetime,
    payload: object,
    event: datetime | None = None,
    tenant: str = "desk",
) -> None:
    clock.now = written.timestamp()
    log.record(tenant, "gamma-flip", "NIFTY", event or written, "v1", payload)


def test_read_as_of_returns_only_what_was_known_then(
    conn: sqlite3.Connection, clock: Clock
) -> None:
    log = EmissionLog(conn, clock)
    write(log, clock, at(10, 28), {"level": 24100})
    write(log, clock, at(11, 0), {"level": 24180})

    known = log.as_of("desk", "gamma-flip", "NIFTY", at(10, 30))

    assert [e.payload for e in known] == [{"level": 24100}]
    assert known[0].knowledge_ts == at(10, 28)
    assert known[0].event_ts == at(10, 28)
    assert known[0].version == "v1"
    assert [e.payload for e in log.as_of("desk", "gamma-flip", "NIFTY", at(11, 0))] == [
        {"level": 24100},
        {"level": 24180},
    ]


def test_correction_reemits_later_and_earlier_reads_keep_the_original(
    conn: sqlite3.Connection, clock: Clock
) -> None:
    log = EmissionLog(conn, clock)
    write(log, clock, at(10, 28), {"level": 24100})
    write(log, clock, at(12, 0), {"level": 24120}, event=at(10, 28))

    before = log.as_of("desk", "gamma-flip", "NIFTY", at(11, 0))
    after = log.as_of("desk", "gamma-flip", "NIFTY", at(12, 5))

    assert [e.payload for e in before] == [{"level": 24100}]
    assert [(e.payload, e.knowledge_ts) for e in after] == [({"level": 24120}, at(12, 0))]


def test_emissions_cannot_be_edited_or_deleted(conn: sqlite3.Connection, clock: Clock) -> None:
    write(EmissionLog(conn, clock), clock, at(10, 28), {"level": 24100})
    with pytest.raises(sqlite3.DatabaseError, match="append-only"):
        conn.execute("UPDATE emissions SET payload = '{}'")
    with pytest.raises(sqlite3.DatabaseError, match="append-only"):
        conn.execute("DELETE FROM emissions")


def test_read_for_another_tenant_returns_nothing(conn: sqlite3.Connection, clock: Clock) -> None:
    log = EmissionLog(conn, clock)
    write(log, clock, at(10, 28), {"level": 24100}, tenant="desk")

    assert log.as_of("broker-b", "gamma-flip", "NIFTY", at(12, 0)) == []


def test_naive_timestamps_are_refused(conn: sqlite3.Connection, clock: Clock) -> None:
    log = EmissionLog(conn, clock)
    with pytest.raises(ValueError, match="timezone"):
        log.record("desk", "gamma-flip", "NIFTY", datetime(2026, 11, 13, 10, 28), "v1", {})
    with pytest.raises(ValueError, match="timezone"):
        log.as_of("desk", "gamma-flip", "NIFTY", datetime(2026, 11, 13, 10, 30))
