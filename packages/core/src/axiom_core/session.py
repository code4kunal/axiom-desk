"""Sessions: the only source of a request's tenant, user and role.

Sign-in exchanges claims already verified by the desk's OIDC provider for an opaque session
token. Request parameters never choose the principal.
"""

import secrets
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from axiom_core.authz import Forbidden
from axiom_core.principals import Principal, PrincipalKind
from axiom_core.tenancy import Directory


class Unauthenticated(Exception):
    pass


@dataclass(frozen=True)
class VerifiedClaims:
    """Claims from an ID token whose signature, issuer, audience and expiry were checked."""

    subject: str
    tenant_id: str
    amr: tuple[str, ...]  # authentication methods; must include "mfa"


@dataclass
class _Session:
    tenant_id: str
    user_id: str
    authenticated_at: float
    expires_at: float


class SessionStore:
    TTL_SECONDS = 8 * 3600.0

    # shortcut: sessions live in process memory, so a restart signs everyone out and a second
    # API process cannot see them; move to the records database before running more than one.
    def __init__(self, directory: Directory, clock: Callable[[], float]) -> None:
        self._directory = directory
        self._clock = clock
        self._sessions: dict[str, _Session] = {}

    def sign_in(self, claims: VerifiedClaims) -> str:
        self._require_mfa_user(claims)
        token = secrets.token_urlsafe(32)
        now = self._clock()
        self._sessions[token] = _Session(
            claims.tenant_id, claims.subject, now, now + self.TTL_SECONDS
        )
        return token

    def reauthenticate(self, token: str, claims: VerifiedClaims) -> None:
        session = self._live(token)
        self._require_mfa_user(claims)
        if (claims.tenant_id, claims.subject) != (session.tenant_id, session.user_id):
            raise Unauthenticated("re-authentication must be by the session's own user")
        session.authenticated_at = self._clock()

    def resolve(self, token: str) -> Principal:
        s = self._live(token)
        return Principal(PrincipalKind.USER, s.tenant_id, s.user_id, s.authenticated_at)

    def resolve_request(self, token: str, params: Mapping[str, str]) -> Principal:
        principal = self.resolve(token)
        for key, own in (("tenant_id", principal.tenant_id), ("user_id", principal.user_id)):
            if key in params and params[key] != own:
                raise Forbidden(f"{key} in the request does not match the session")
        return principal

    def agent_principal(self, token: str) -> Principal:
        s = self._live(token)
        return Principal(PrincipalKind.AGENT, s.tenant_id, s.user_id)

    def sign_out(self, token: str) -> None:
        self._sessions.pop(token, None)

    def _live(self, token: str) -> _Session:
        session = self._sessions.get(token)
        if session is None:
            raise Unauthenticated("no such session")
        if self._clock() >= session.expires_at:
            del self._sessions[token]
            raise Unauthenticated("session expired")
        return session

    def _require_mfa_user(self, claims: VerifiedClaims) -> None:
        if "mfa" not in claims.amr:
            raise Unauthenticated("multi-factor sign-in required")
        if not self._directory.has_user(claims.tenant_id, claims.subject):
            raise Unauthenticated("unknown user")
