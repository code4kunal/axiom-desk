import sqlite3
from pathlib import Path

import pytest
from axiom_core.audit import AuditLog
from axiom_core.authz import Action, Authorizer, Forbidden, Resource
from axiom_core.db import migrate
from axiom_core.session import PendingLogins, SessionStore, Unauthenticated, VerifiedClaims
from axiom_core.tenancy import Directory, PrincipalKind, Role
from conftest import Clock, mfa_claims

BOOK_ALPHA = Resource("desk", "book", "alpha", book_id="alpha")


def refusal(err: pytest.ExceptionInfo[Unauthenticated]) -> str:
    return err.value.reason


def test_sign_in_without_mfa_is_refused(sessions: SessionStore, clock: Clock) -> None:
    claims = VerifiedClaims(
        subject="ana", tenant_id="desk", amr=("pwd",), display_name="Ana", auth_time=clock.now
    )
    with pytest.raises(Unauthenticated) as err:
        sessions.sign_in(claims)
    assert refusal(err) == "mfa_required"


def test_unknown_user_cannot_sign_in(sessions: SessionStore, clock: Clock) -> None:
    with pytest.raises(Unauthenticated) as err:
        sessions.sign_in(mfa_claims("desk", "stranger", clock.now))
    assert refusal(err) == "unknown_user"


def test_session_decides_the_principal_not_request_parameters(
    sessions: SessionStore, clock: Clock
) -> None:
    token = sessions.sign_in(mfa_claims("desk", "ana", clock.now))
    principal = sessions.resolve_request(token, {"symbol": "NIFTY"})
    assert (principal.tenant_id, principal.user_id) == ("desk", "ana")

    with pytest.raises(Forbidden):
        sessions.resolve_request(token, {"tenant_id": "broker-b"})
    with pytest.raises(Forbidden):
        sessions.resolve_request(token, {"user_id": "tara"})


def test_session_resolves_until_expiry_and_is_refused_a_second_after(
    sessions: SessionStore, clock: Clock
) -> None:
    signed_in_at = clock.now
    token = sessions.sign_in(mfa_claims("desk", "ana", clock.now))
    clock.now = signed_in_at + SessionStore.TTL_SECONDS - 1
    assert sessions.resolve(token).user_id == "ana"
    clock.now = signed_in_at + SessionStore.TTL_SECONDS + 1
    with pytest.raises(Unauthenticated) as err:
        sessions.resolve(token)
    assert refusal(err) == "expired"


def test_forged_token_is_refused(sessions: SessionStore) -> None:
    with pytest.raises(Unauthenticated) as err:
        sessions.resolve("not-a-token")
    assert refusal(err) == "invalid"


def test_agent_principal_acts_for_the_session_user(sessions: SessionStore, clock: Clock) -> None:
    token = sessions.sign_in(mfa_claims("desk", "tara", clock.now))
    agent = sessions.agent_principal(token)
    assert agent.kind is PrincipalKind.AGENT
    assert (agent.tenant_id, agent.user_id) == ("desk", "tara")
    assert agent.authenticated_at is None


def test_session_survives_a_restart_on_the_same_database_file(tmp_path: Path, clock: Clock) -> None:
    path = tmp_path / "records.db"

    def store() -> tuple[sqlite3.Connection, SessionStore]:
        conn = sqlite3.connect(path)
        migrate(conn)
        audit = AuditLog(conn, clock)
        return conn, SessionStore(conn, Directory(conn, audit), audit, clock)

    first_conn, first = store()
    Directory(first_conn, AuditLog(first_conn, clock)).bootstrap_admin("desk", "ada")
    token = first.sign_in(mfa_claims("desk", "ada", clock.now))
    first_conn.close()

    second_conn, second = store()
    assert (second.resolve(token).tenant_id, second.resolve(token).user_id) == ("desk", "ada")
    second_conn.close()


def test_the_database_never_holds_the_raw_token(
    sessions: SessionStore, conn: sqlite3.Connection, clock: Clock
) -> None:
    token = sessions.sign_in(mfa_claims("desk", "ana", clock.now))
    rows = conn.execute("SELECT * FROM sessions").fetchall()
    assert len(rows) == 1
    assert token not in rows[0]


def test_each_sign_in_is_a_new_session_and_signing_out_ends_only_that_one(
    sessions: SessionStore, clock: Clock
) -> None:
    first = sessions.sign_in(mfa_claims("desk", "ana", clock.now))
    second = sessions.sign_in(mfa_claims("desk", "ana", clock.now))
    assert first != second

    sessions.sign_out(first)
    with pytest.raises(Unauthenticated) as err:
        sessions.resolve(first)
    assert refusal(err) == "invalid"
    assert sessions.resolve(second).user_id == "ana"


def test_a_user_removed_from_the_directory_loses_the_session_on_the_next_request(
    sessions: SessionStore, directory: Directory, clock: Clock
) -> None:
    token = sessions.sign_in(mfa_claims("desk", "ana", clock.now))
    admin = directory.principal("desk", "ada")
    directory.revoke(admin, "desk", "ana", Role.ANALYST)
    with pytest.raises(Unauthenticated) as err:
        sessions.resolve(token)
    assert refusal(err) == "unknown_user"

    # The row is gone, so giving the role back does not bring the old session back.
    directory.grant(admin, "desk", "ana", Role.ANALYST)
    with pytest.raises(Unauthenticated) as err:
        sessions.resolve(token)
    assert refusal(err) == "invalid"


def test_authenticated_at_is_the_tokens_auth_time_not_the_clock(
    sessions: SessionStore, authz: Authorizer, clock: Clock
) -> None:
    twenty_minutes_ago = clock.now - 20 * 60
    token = sessions.sign_in(mfa_claims("desk", "tara", twenty_minutes_ago))
    assert sessions.resolve(token).authenticated_at == twenty_minutes_ago
    with pytest.raises(Forbidden):
        authz.check(sessions.resolve(token), Action.CONFIRM_TICKET, BOOK_ALPHA)

    sessions.reauthenticate(token, mfa_claims("desk", "tara", twenty_minutes_ago))
    assert sessions.resolve(token).authenticated_at == twenty_minutes_ago
    with pytest.raises(Forbidden):
        authz.check(sessions.resolve(token), Action.CONFIRM_TICKET, BOOK_ALPHA)

    sessions.reauthenticate(token, mfa_claims("desk", "tara", clock.now))
    authz.check(sessions.resolve(token), Action.CONFIRM_TICKET, BOOK_ALPHA)

    with pytest.raises(Unauthenticated):
        sessions.reauthenticate(token, mfa_claims("desk", "ana", clock.now))


def test_claims_without_auth_time_never_count_as_a_recent_sign_in(
    sessions: SessionStore, authz: Authorizer, clock: Clock
) -> None:
    token = sessions.sign_in(mfa_claims("desk", "tara", None))
    assert sessions.resolve(token).authenticated_at is None
    with pytest.raises(Forbidden):
        authz.check(sessions.resolve(token), Action.CONFIRM_TICKET, BOOK_ALPHA)

    sessions.reauthenticate(token, mfa_claims("desk", "tara", clock.now))
    sessions.reauthenticate(token, mfa_claims("desk", "tara", None))
    with pytest.raises(Forbidden):
        authz.check(sessions.resolve(token), Action.CONFIRM_TICKET, BOOK_ALPHA)


def test_an_expired_session_row_is_gone_after_the_next_sign_in(
    sessions: SessionStore, conn: sqlite3.Connection, clock: Clock
) -> None:
    sessions.sign_in(mfa_claims("desk", "ana", clock.now))
    clock.now += SessionStore.TTL_SECONDS + 1
    sessions.sign_in(mfa_claims("desk", "tara", clock.now))
    assert conn.execute("SELECT user_id FROM sessions").fetchall() == [("tara",)]


def test_sign_in_refusals_and_sign_out_each_write_one_audit_record(
    sessions: SessionStore, audit: AuditLog, clock: Clock
) -> None:
    before = len(audit.records())
    token = sessions.sign_in(mfa_claims("desk", "ana", clock.now))
    with pytest.raises(Unauthenticated):
        sessions.sign_in(
            VerifiedClaims(
                subject="ana", tenant_id="desk", amr=("pwd",), display_name="Ana", auth_time=None
            )
        )
    with pytest.raises(Unauthenticated):
        sessions.sign_in(mfa_claims("desk", "stranger", clock.now))
    sessions.resolve(token)
    sessions.agent_principal(token)
    sessions.sign_out(token)
    sessions.sign_out(token)
    sessions.sign_out("not-a-token")

    after = audit.records()[before:]
    assert [(r.kind, r.tenant_id, r.user_id, r.action, r.verdict, r.ids) for r in after] == [
        ("user", "desk", "ana", "sign_in", "allowed", {}),
        ("user", "desk", "ana", "sign_in", "refused", {"reason": "mfa_required"}),
        ("user", "desk", "stranger", "sign_in", "refused", {"reason": "unknown_user"}),
        ("user", "desk", "ana", "sign_out", "allowed", {}),
    ]


@pytest.fixture
def pending(conn: sqlite3.Connection, clock: Clock) -> PendingLogins:
    return PendingLogins(conn, clock)


def test_a_pending_sign_in_can_be_taken_once(pending: PendingLogins) -> None:
    handle = pending.create(state="s1", nonce="n1", verifier="v1")
    taken = pending.take(handle)
    assert taken is not None
    assert (taken.state, taken.nonce, taken.verifier) == ("s1", "n1", "v1")
    assert pending.take(handle) is None
    assert pending.take("not-a-handle") is None


def test_an_expired_pending_sign_in_is_not_returned(pending: PendingLogins, clock: Clock) -> None:
    handle = pending.create(state="s1", nonce="n1", verifier="v1")
    clock.now += PendingLogins.TTL_SECONDS + 1
    assert pending.take(handle) is None


def test_an_abandoned_pending_sign_in_is_gone_after_the_next_start(
    pending: PendingLogins, conn: sqlite3.Connection, clock: Clock
) -> None:
    pending.create(state="old", nonce="n1", verifier="v1")
    clock.now += PendingLogins.TTL_SECONDS + 1
    pending.create(state="new", nonce="n2", verifier="v2")
    assert conn.execute("SELECT state FROM pending_logins").fetchall() == [("new",)]


def test_the_database_never_holds_the_raw_pending_handle(
    pending: PendingLogins, conn: sqlite3.Connection
) -> None:
    handle = pending.create(state="s1", nonce="n1", verifier="v1")
    rows = conn.execute("SELECT * FROM pending_logins").fetchall()
    assert len(rows) == 1
    assert handle not in rows[0]
