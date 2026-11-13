import sqlite3
from collections.abc import Iterator

import pytest
from axiom_core.audit import AuditLog
from axiom_core.authz import Authorizer
from axiom_core.db import migrate
from axiom_core.session import SessionStore, VerifiedClaims
from axiom_core.tenancy import Directory, Role


class Clock:
    def __init__(self) -> None:
        self.now = 1_000_000.0

    def __call__(self) -> float:
        return self.now


@pytest.fixture
def clock() -> Clock:
    return Clock()


@pytest.fixture
def conn() -> Iterator[sqlite3.Connection]:
    c = sqlite3.connect(":memory:")
    migrate(c)
    yield c
    c.close()


@pytest.fixture
def audit(conn: sqlite3.Connection, clock: Clock) -> AuditLog:
    return AuditLog(conn, clock)


@pytest.fixture
def directory(conn: sqlite3.Connection, audit: AuditLog) -> Directory:
    d = Directory(conn, audit)
    d.add_book("desk", "alpha")
    d.add_book("desk", "beta")
    d.add_book("broker-b", "retail")
    d.bootstrap_admin("desk", "ada")
    d.bootstrap_admin("broker-b", "bob-admin")
    admin = d.principal("desk", "ada")
    d.grant(admin, "desk", "ana", Role.ANALYST)
    d.grant(admin, "desk", "tara", Role.TRADER, book_id="alpha")
    d.grant(admin, "desk", "quinn", Role.QUANT)
    d.grant(admin, "desk", "pam", Role.PM)
    return d


@pytest.fixture
def authz(directory: Directory, audit: AuditLog, clock: Clock) -> Authorizer:
    return Authorizer(directory, audit, clock)


@pytest.fixture
def sessions(
    conn: sqlite3.Connection, directory: Directory, audit: AuditLog, clock: Clock
) -> SessionStore:
    return SessionStore(conn, directory, audit, clock)


def mfa_claims(tenant: str, user: str, auth_time: float | None) -> VerifiedClaims:
    return VerifiedClaims(
        subject=user,
        tenant_id=tenant,
        amr=("pwd", "mfa"),
        display_name=f"{user.title()} Example",
        auth_time=auth_time,
    )
