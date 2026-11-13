"""OpenID Connect client for desk sign-in. The API is a confidential client; the browser never
holds provider tokens.

Configured from the environment: AXIOM_OIDC_ISSUER, AXIOM_OIDC_CLIENT_ID,
AXIOM_OIDC_CLIENT_SECRET, AXIOM_OIDC_TENANT_CLAIM (default "tenant") and AXIOM_PUBLIC_ORIGIN.
Each provider call blocks, so it runs in a worker thread with a 5 s timeout; those threads never
touch the records database. MFA and Directory membership are refused by SessionStore, which audits
the refusal, so this module passes amr through instead of judging it.
"""

import asyncio
import base64
import hashlib
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Literal, cast
from urllib.parse import quote, urlencode

import httpx2
import jwt
from axiom_core.session import VerifiedClaims

TIMEOUT_SECONDS = 5.0
LEEWAY_SECONDS = 60
MAX_AGE_SECONDS = 28800  # the session TTL; obliges the provider to return auth_time
ALGORITHMS = ["RS256", "ES256"]

Reason = Literal["failed", "provider_unavailable"]


class SignInFailed(Exception):
    def __init__(self, reason: Reason) -> None:
        super().__init__(reason)
        self.reason: Reason = reason


@dataclass(frozen=True)
class Settings:
    issuer: str
    client_id: str
    client_secret: str = field(repr=False)
    tenant_claim: str
    public_origin: str


def load_settings(env: Mapping[str, str] = os.environ) -> Settings | None:
    """None means sign-in is not configured: auth routes refuse, capability calls are unaffected."""
    issuer, client_id, secret, origin = (
        env.get(name, "")
        for name in (
            "AXIOM_OIDC_ISSUER",
            "AXIOM_OIDC_CLIENT_ID",
            "AXIOM_OIDC_CLIENT_SECRET",
            "AXIOM_PUBLIC_ORIGIN",
        )
    )
    if not (issuer and client_id and secret and origin):
        return None
    tenant_claim = env.get("AXIOM_OIDC_TENANT_CLAIM") or "tenant"
    return Settings(issuer, client_id, secret, tenant_claim, origin.rstrip("/"))


async def _fetch(send: Callable[[], httpx2.Response]) -> dict[str, Any]:
    try:
        response = await asyncio.to_thread(send)
    except httpx2.TransportError as e:
        raise SignInFailed("provider_unavailable") from e
    if response.status_code >= 500:
        raise SignInFailed("provider_unavailable")
    if response.status_code != 200:
        raise SignInFailed("failed")
    try:
        body = response.json()
    except ValueError as e:
        raise SignInFailed("failed") from e
    if not isinstance(body, dict):
        raise SignInFailed("failed")
    return cast(dict[str, Any], body)  # JSON object keys are always strings


class OidcClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._discovery: dict[str, Any] | None = None
        self._jwks: jwt.PyJWKClient | None = None

    async def _provider(self) -> tuple[dict[str, Any], jwt.PyJWKClient]:
        if self._discovery is None or self._jwks is None:
            url = self._settings.issuer.rstrip("/") + "/.well-known/openid-configuration"
            doc = await _fetch(lambda: httpx2.get(url, timeout=TIMEOUT_SECONDS))
            self._jwks = jwt.PyJWKClient(str(doc.get("jwks_uri")), timeout=TIMEOUT_SECONDS)
            self._discovery = doc
        return self._discovery, self._jwks

    async def authorize_url(self, *, state: str, nonce: str, verifier: str) -> str:
        discovery, _ = await self._provider()
        digest = hashlib.sha256(verifier.encode()).digest()
        query = urlencode(
            {
                "response_type": "code",
                "client_id": self._settings.client_id,
                "redirect_uri": self._settings.public_origin + "/auth/callback",
                "scope": "openid",
                "state": state,
                "nonce": nonce,
                "code_challenge": base64.urlsafe_b64encode(digest).rstrip(b"=").decode(),
                "code_challenge_method": "S256",
                "prompt": "login",
                "max_age": MAX_AGE_SECONDS,
            }
        )
        return f"{discovery['authorization_endpoint']}?{query}"

    async def exchange(self, *, code: str, verifier: str, nonce: str) -> VerifiedClaims:
        discovery, _ = await self._provider()
        s = self._settings
        endpoint = str(discovery.get("token_endpoint"))
        # client_secret_basic: RFC 6749 2.3.1 form-encodes both parts before Basic.
        auth = httpx2.BasicAuth(quote(s.client_id, safe=""), quote(s.client_secret, safe=""))
        form = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": s.public_origin + "/auth/callback",
            "code_verifier": verifier,
        }
        body = await _fetch(
            lambda: httpx2.post(endpoint, data=form, auth=auth, timeout=TIMEOUT_SECONDS)
        )
        id_token = body.get("id_token")
        if not isinstance(id_token, str):
            raise SignInFailed("failed")
        return await self.verify(id_token, nonce=nonce)

    async def verify(self, id_token: str, *, nonce: str) -> VerifiedClaims:
        """Check an ID token against the provider's JWKS and the nonce of the pending sign-in."""
        _, jwks = await self._provider()
        s = self._settings
        try:
            key = await asyncio.to_thread(jwks.get_signing_key_from_jwt, id_token)
            claims = jwt.decode(
                id_token,
                key,
                algorithms=ALGORITHMS,
                audience=s.client_id,
                issuer=s.issuer,
                leeway=LEEWAY_SECONDS,
                options={"require": ["exp", "iat", "sub"]},
            )
        except jwt.PyJWKClientConnectionError as e:
            raise SignInFailed("provider_unavailable") from e
        except jwt.PyJWTError as e:
            raise SignInFailed("failed") from e
        aud = claims["aud"]
        # Several audiences: azp must name this client (PyJWT does not check azp).
        if isinstance(aud, list) and aud != [s.client_id] and claims.get("azp") != s.client_id:
            raise SignInFailed("failed")
        if claims.get("nonce") != nonce:
            raise SignInFailed("failed")
        tenant = claims.get(s.tenant_claim)
        if not isinstance(tenant, str) or not tenant:
            raise SignInFailed("failed")
        amr = claims.get("amr")
        auth_time = claims.get("auth_time")
        subject: str = claims["sub"]
        return VerifiedClaims(
            subject=subject,
            tenant_id=tenant,
            amr=tuple(m for m in cast(list[object], amr) if isinstance(m, str))
            if isinstance(amr, list)
            else (),
            display_name=str(claims.get("name") or claims.get("email") or subject),
            auth_time=float(auth_time) if isinstance(auth_time, int | float) else None,
        )
