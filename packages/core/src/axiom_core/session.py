"""Sessions: the only source of a request's tenant, user and role.

Sign-in exchanges claims already verified by the desk's OIDC provider for an opaque session
token. Request parameters never choose the principal. Sessions and pending sign-ins live in the
records database, keyed by the SHA-256 of the token or handle the browser holds.
"""

import hashlib
import secrets
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Literal

from axiom_core.audit import AuditLog
from axiom_core.authz import Forbidden
from axiom_core.db import Connection
from axiom_core.principals import Principal, PrincipalKind
from axiom_core.tenancy import Directory

Reason = Literal["mfa_required", "unknown_user", "expired", "invalid"]


class Unauthenticated(Exception):
    def __init__(self, reason: Reason) -> None:
        super().__init__(reason)
        self.reason: Reason = reason


@dataclass(frozen=True)
class VerifiedClaims:
    """Claims from an ID token whose signature, issuer, audience and expiry were checked."""

    subject: str
    tenant_id: str
    amr: tuple[str, ...]
    display_name: str
    auth_time: float | None


def _digest(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()


class SessionStore:
    TTL_SECONDS = 8 * 3600.0

    def __init__(
        self,
        conn: Connection,
        directory: Directory,
        audit: AuditLog,
        clock: Callable[[], float],
    ) -> None:
        self._conn = conn
        self._directory = directory
        self._audit = audit
        self._clock = clock

    def sign_in(self, claims: VerifiedClaims) -> str:
        user = Principal(PrincipalKind.USER, claims.tenant_id, claims.subject)
        reason = self._refusal(claims)
        if reason is not None:
            self._audit.record(user, "sign_in", "refused", {"reason": reason})
            raise Unauthenticated(reason)
        token = secrets.token_urlsafe(32)
        now = self._clock()
        with self._conn:
            self._conn.execute("DELETE FROM sessions WHERE expires_at <= ?", (now,))
            self._conn.execute(
                "INSERT INTO sessions (token_hash, tenant_id, user_id, display_name,"
                " authenticated_at, expires_at) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    _digest(token),
                    claims.tenant_id,
                    claims.subject,
                    claims.display_name,
                    claims.auth_time,
                    now + self.TTL_SECONDS,
                ),
            )
        self._audit.record(user, "sign_in", "allowed", {})
        return token

    def reauthenticate(self, token: str, claims: VerifiedClaims) -> None:
        session = self.resolve(token)
        reason = self._refusal(claims)
        if reason is not None:
            raise Unauthenticated(reason)
        if (claims.tenant_id, claims.subject) != (session.tenant_id, session.user_id):
            raise Unauthenticated("invalid")
        with self._conn:
            self._conn.execute(
                "UPDATE sessions SET authenticated_at = ? WHERE token_hash = ?",
                (claims.auth_time, _digest(token)),
            )

    def resolve(self, token: str) -> Principal:
        key = _digest(token)
        row = self._conn.execute(
            "SELECT tenant_id, user_id, authenticated_at, expires_at FROM sessions"
            " WHERE token_hash = ?",
            (key,),
        ).fetchone()
        if row is None:
            raise Unauthenticated("invalid")
        tenant_id, user_id, authenticated_at, expires_at = row
        reason: Reason | None = None
        if self._clock() >= expires_at:
            reason = "expired"
        elif not self._directory.has_user(tenant_id, user_id):
            reason = "unknown_user"
        if reason is not None:
            with self._conn:
                self._conn.execute("DELETE FROM sessions WHERE token_hash = ?", (key,))
            raise Unauthenticated(reason)
        return Principal(PrincipalKind.USER, tenant_id, user_id, authenticated_at)

    def describe(self, token: str) -> tuple[Principal, str]:
        """The session's principal and display name, refused exactly as resolve refuses."""
        principal = self.resolve(token)
        (name,) = self._conn.execute(
            "SELECT display_name FROM sessions WHERE token_hash = ?", (_digest(token),)
        ).fetchone()
        return principal, name

    def resolve_request(self, token: str, params: Mapping[str, str]) -> Principal:
        principal = self.resolve(token)
        for key, own in (("tenant_id", principal.tenant_id), ("user_id", principal.user_id)):
            if key in params and params[key] != own:
                raise Forbidden(f"{key} in the request does not match the session")
        return principal

    def agent_principal(self, token: str) -> Principal:
        user = self.resolve(token)
        return Principal(PrincipalKind.AGENT, user.tenant_id, user.user_id)

    def sign_out(self, token: str) -> None:
        with self._conn:
            row = self._conn.execute(
                "DELETE FROM sessions WHERE token_hash = ? RETURNING tenant_id, user_id",
                (_digest(token),),
            ).fetchone()
        if row is not None:
            self._audit.record(Principal(PrincipalKind.USER, *row), "sign_out", "allowed", {})

    def _refusal(self, claims: VerifiedClaims) -> Reason | None:
        if "mfa" not in claims.amr:
            return "mfa_required"
        if not self._directory.has_user(claims.tenant_id, claims.subject):
            return "unknown_user"
        return None


@dataclass(frozen=True)
class PendingLogin:
    state: str
    nonce: str
    verifier: str


class PendingLogins:
    """Sign-ins started and not finished; each completes once, by the browser holding its handle."""

    TTL_SECONDS = 600.0

    def __init__(self, conn: Connection, clock: Callable[[], float]) -> None:
        self._conn = conn
        self._clock = clock

    def create(self, *, state: str, nonce: str, verifier: str) -> str:
        handle = secrets.token_urlsafe(32)
        now = self._clock()
        with self._conn:
            self._conn.execute("DELETE FROM pending_logins WHERE expires_at <= ?", (now,))
            self._conn.execute(
                "INSERT INTO pending_logins (handle_hash, state, nonce, verifier, expires_at)"
                " VALUES (?, ?, ?, ?, ?)",
                (_digest(handle), state, nonce, verifier, now + self.TTL_SECONDS),
            )
        return handle

    def take(self, handle: str) -> PendingLogin | None:
        with self._conn:
            row = self._conn.execute(
                "DELETE FROM pending_logins WHERE handle_hash = ?"
                " RETURNING state, nonce, verifier, expires_at",
                (_digest(handle),),
            ).fetchone()
        if row is None or self._clock() >= row[3]:
            return None
        return PendingLogin(*row[:3])
