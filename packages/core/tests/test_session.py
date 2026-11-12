import pytest
from axiom_core.authz import Forbidden
from axiom_core.session import SessionStore, Unauthenticated, VerifiedClaims
from axiom_core.tenancy import PrincipalKind
from conftest import Clock, mfa_claims


def test_sign_in_without_mfa_is_refused(sessions: SessionStore) -> None:
    with pytest.raises(Unauthenticated):
        sessions.sign_in(VerifiedClaims(subject="ana", tenant_id="desk", amr=("pwd",)))


def test_unknown_user_cannot_sign_in(sessions: SessionStore) -> None:
    with pytest.raises(Unauthenticated):
        sessions.sign_in(mfa_claims("desk", "stranger"))


def test_session_decides_the_principal_not_request_parameters(sessions: SessionStore) -> None:
    token = sessions.sign_in(mfa_claims("desk", "ana"))
    principal = sessions.resolve_request(token, {"symbol": "NIFTY"})
    assert (principal.tenant_id, principal.user_id) == ("desk", "ana")

    with pytest.raises(Forbidden):
        sessions.resolve_request(token, {"tenant_id": "broker-b"})
    with pytest.raises(Forbidden):
        sessions.resolve_request(token, {"user_id": "tara"})


def test_expired_session_is_refused(sessions: SessionStore, clock: Clock) -> None:
    token = sessions.sign_in(mfa_claims("desk", "ana"))
    clock.now += SessionStore.TTL_SECONDS + 1
    with pytest.raises(Unauthenticated):
        sessions.resolve(token)


def test_forged_token_is_refused(sessions: SessionStore) -> None:
    with pytest.raises(Unauthenticated):
        sessions.resolve("not-a-token")


def test_agent_principal_acts_for_the_session_user(sessions: SessionStore) -> None:
    token = sessions.sign_in(mfa_claims("desk", "tara"))
    agent = sessions.agent_principal(token)
    assert agent.kind is PrincipalKind.AGENT
    assert (agent.tenant_id, agent.user_id) == ("desk", "tara")
    assert agent.authenticated_at is None


def test_reauthentication_refreshes_auth_time(sessions: SessionStore, clock: Clock) -> None:
    token = sessions.sign_in(mfa_claims("desk", "tara"))
    first = sessions.resolve(token).authenticated_at
    clock.now += 600
    sessions.reauthenticate(token, mfa_claims("desk", "tara"))
    assert sessions.resolve(token).authenticated_at == clock.now != first

    with pytest.raises(Unauthenticated):
        sessions.reauthenticate(token, mfa_claims("desk", "ana"))
