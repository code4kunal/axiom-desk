import sqlite3
from datetime import UTC, datetime

import pytest
from axiom_core.envelope import Source
from axiom_core.runs import RunStore
from conftest import Clock

AS_OF = datetime(2026, 11, 12, 9, 15, tzinfo=UTC)
SRC = (Source("nse-eod", "public"),)


def test_published_run_is_addressable_and_latest(conn: sqlite3.Connection, clock: Clock) -> None:
    store = RunStore(conn, clock)
    first = store.publish("regime", AS_OF, {"state": "risk-on"}, SRC)
    clock.now += 60
    second = store.publish("regime", AS_OF, {"state": "risk-off"}, SRC)
    assert first.id != second.id
    assert store.get(first.id) == first
    latest = store.latest("regime")
    assert latest is not None
    assert latest.id == second.id
    assert store.latest("radar") is None


def test_latest_as_of_ignores_runs_published_later(conn: sqlite3.Connection, clock: Clock) -> None:
    store = RunStore(conn, clock)
    clock.now = datetime(2026, 11, 13, 10, 28, tzinfo=UTC).timestamp()
    early = store.publish("regime", AS_OF, {"state": "risk-on"}, SRC)
    clock.now = datetime(2026, 11, 13, 11, 0, tzinfo=UTC).timestamp()
    store.publish("regime", AS_OF, {"state": "risk-off"}, SRC)

    known = store.latest_as_of("regime", datetime(2026, 11, 13, 10, 30, tzinfo=UTC))

    assert known is not None
    assert known.id == early.id
    assert store.latest_as_of("regime", datetime(2026, 11, 13, 10, 0, tzinfo=UTC)) is None


def test_runs_cannot_be_edited_or_deleted(conn: sqlite3.Connection, clock: Clock) -> None:
    run = RunStore(conn, clock).publish("regime", AS_OF, {"state": "risk-on"}, SRC)
    with pytest.raises(sqlite3.DatabaseError, match="immutable"):
        conn.execute("UPDATE runs SET payload = '{}' WHERE id = ?", (run.id,))
    with pytest.raises(sqlite3.DatabaseError, match="immutable"):
        conn.execute("DELETE FROM runs WHERE id = ?", (run.id,))
