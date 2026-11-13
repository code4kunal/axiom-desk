"""The OIDC client against the real test provider over HTTP. Tokens the provider cannot issue
(expired, other audience, odd amr) are signed in the test with the provider's own key, or with a
foreign key, and fed through the same verify path the callback uses."""

import asyncio
import base64
import hashlib
import importlib.util
import socket
import sqlite3
import time
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx2
import jwt
import pytest
from axiom_api.oidc import OidcClient, Settings, SignInFailed, load_settings
from axiom_core.audit import AuditLog
from axiom_core.db import migrate
from axiom_core.session import SessionStore, Unauthenticated, VerifiedClaims
from axiom_core.tenancy import Directory
from cryptography.hazmat.primitives.asymmetric import rsa

SPEC = importlib.util.spec_from_file_location(
    "idp", Path(__file__).resolve().parents[3] / "tools" / "test_idp" / "idp.py"
)
assert SPEC and SPEC.loader
idp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(idp)

CLIENT, SECRET, ORIGIN = "desk", "s3cret", "http://desk.test"
VERIFIER, NONCE = "v" * 64, "nonce-1"
ENV = {
    "AXIOM_OIDC_ISSUER": "https://id.example",
    "AXIOM_OIDC_CLIENT_ID": "desk",
    "AXIOM_OIDC_CLIENT_SECRET": "hidden-value",
    "AXIOM_PUBLIC_ORIGIN": "https://desk.example",
}


@pytest.fixture
def provider() -> Iterator[Any]:
    server = idp.start(client_id=CLIENT, client_secret=SECRET, tenant_claim="tenant")
    yield server
    server.shutdown()
    server.server_close()


def settings_for(issuer: str, client_id: str = CLIENT) -> Settings:
    return Settings(
        issuer=issuer,
        client_id=client_id,
        client_secret=SECRET,
        tenant_claim="tenant",
        public_origin=ORIGIN,
    )


@pytest.fixture
def client(provider: Any) -> OidcClient:
    return OidcClient(settings_for(provider.url))


def stop(provider: Any) -> None:
    provider.shutdown()
    provider.server_close()


def code_for(client: OidcClient, hint: str) -> str:
    url = asyncio.run(client.authorize_url(state="st", nonce=NONCE, verifier=VERIFIER))
    back = httpx2.get(f"{url}&login_hint={hint}", timeout=5)
    assert back.status_code == 302
    return parse_qs(urlparse(back.headers["location"]).query)["code"][0]


def exchange(client: OidcClient, code: str, nonce: str = NONCE) -> VerifiedClaims:
    return asyncio.run(client.exchange(code=code, verifier=VERIFIER, nonce=nonce))


def sign_in(client: OidcClient, hint: str, nonce: str = NONCE) -> VerifiedClaims:
    return exchange(client, code_for(client, hint), nonce)


def mint(key: Any, provider: Any, **overrides: Any) -> str:
    now = int(time.time())
    claims: dict[str, Any] = {
        "iss": provider.url,
        "aud": CLIENT,
        "sub": "user-mfa",
        "iat": now,
        "exp": now + 300,
        "auth_time": now,
        "nonce": NONCE,
        "amr": ["pwd", "mfa"],
        "name": "Maya Desk",
        "tenant": "axiom-desk",
    }
    claims.update(overrides)
    claims = {k: v for k, v in claims.items() if v is not None}
    return jwt.encode(claims, key, algorithm="RS256", headers={"kid": "test-key"})


def verify(client: OidcClient, token: str) -> VerifiedClaims:
    return asyncio.run(client.verify(token, nonce=NONCE))


def failure(call: Callable[[], object]) -> str:
    with pytest.raises(SignInFailed) as raised:
        call()
    return raised.value.reason


def refusal(claims: VerifiedClaims) -> str:
    conn = sqlite3.connect(":memory:")
    migrate(conn)
    audit = AuditLog(conn, time.time)
    with pytest.raises(Unauthenticated) as raised:
        SessionStore(conn, Directory(conn, audit), audit, time.time).sign_in(claims)
    conn.close()
    return raised.value.reason


def closed_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port: int = s.getsockname()[1]
    s.close()
    return port


# --- settings


def test_settings_come_from_the_environment_with_a_default_tenant_claim() -> None:
    settings = load_settings(ENV)
    assert settings == Settings(
        "https://id.example", "desk", "hidden-value", "tenant", "https://desk.example"
    )
    assert "hidden-value" not in repr(settings)
    assert load_settings({**ENV, "AXIOM_OIDC_TENANT_CLAIM": "org"}) == Settings(
        "https://id.example", "desk", "hidden-value", "org", "https://desk.example"
    )


@pytest.mark.parametrize("missing", sorted(ENV))
def test_any_missing_setting_means_sign_in_is_not_configured(missing: str) -> None:
    assert load_settings({k: v for k, v in ENV.items() if k != missing}) is None


# --- authorize URL and discovery


def test_authorize_url_carries_login_prompt_max_age_pkce_state_and_nonce(
    client: OidcClient, provider: Any
) -> None:
    url = asyncio.run(client.authorize_url(state="st-1", nonce="n-1", verifier=VERIFIER))
    parts = urlparse(url)
    q = {k: v[0] for k, v in parse_qs(parts.query).items()}
    challenge = base64.urlsafe_b64encode(hashlib.sha256(VERIFIER.encode()).digest())
    assert f"{parts.scheme}://{parts.netloc}{parts.path}" == f"{provider.url}/authorize"
    assert q == {
        "response_type": "code",
        "client_id": CLIENT,
        "redirect_uri": f"{ORIGIN}/auth/callback",
        "scope": "openid",
        "state": "st-1",
        "nonce": "n-1",
        "code_challenge": challenge.rstrip(b"=").decode(),
        "code_challenge_method": "S256",
        "prompt": "login",
        "max_age": "28800",
    }


def test_discovery_is_fetched_once_and_cached(client: OidcClient, provider: Any) -> None:
    first = asyncio.run(client.authorize_url(state="a", nonce="b", verifier=VERIFIER))
    stop(provider)
    assert asyncio.run(client.authorize_url(state="a", nonce="b", verifier=VERIFIER)) == first


# --- code exchange and ID token checks


def test_the_mfa_users_code_yields_verified_claims(client: OidcClient) -> None:
    claims = sign_in(client, "mfa")
    assert (claims.subject, claims.tenant_id, claims.display_name) == (
        "user-mfa",
        "axiom-desk",
        "Maya Desk",
    )
    assert "mfa" in claims.amr
    assert claims.auth_time is not None and abs(claims.auth_time - time.time()) < 60


def test_a_token_without_auth_time_has_no_auth_time(client: OidcClient) -> None:
    assert sign_in(client, "noauthtime").auth_time is None


def test_a_nonce_other_than_the_pending_one_is_refused(client: OidcClient) -> None:
    assert failure(lambda: sign_in(client, "mfa", nonce="another-nonce")) == "failed"


def test_a_reused_code_fails(client: OidcClient) -> None:
    code = code_for(client, "mfa")
    exchange(client, code)
    assert failure(lambda: exchange(client, code)) == "failed"


def test_a_token_for_another_audience_is_refused(client: OidcClient, provider: Any) -> None:
    assert failure(lambda: verify(client, mint(provider.key, provider, aud="other"))) == "failed"


def test_a_client_expecting_another_audience_refuses_the_providers_token(
    provider: Any,
) -> None:
    other = OidcClient(settings_for(provider.url, client_id="someone-else"))
    assert failure(lambda: verify(other, mint(provider.key, provider))) == "failed"


def test_several_audiences_need_azp_naming_this_client(client: OidcClient, provider: Any) -> None:
    both = [CLIENT, "other"]
    assert failure(lambda: verify(client, mint(provider.key, provider, aud=both))) == "failed"
    wrong = mint(provider.key, provider, aud=both, azp="other")
    assert failure(lambda: verify(client, wrong)) == "failed"
    assert verify(client, mint(provider.key, provider, aud=both, azp=CLIENT)).subject == "user-mfa"


def test_a_token_signed_by_a_key_outside_the_jwks_is_refused(
    client: OidcClient, provider: Any
) -> None:
    foreign = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    assert failure(lambda: verify(client, mint(foreign, provider))) == "failed"


def test_expiry_is_checked_with_60_seconds_of_leeway(client: OidcClient, provider: Any) -> None:
    now = int(time.time())
    late = mint(provider.key, provider, iat=now - 400, exp=now - 30)
    assert verify(client, late).subject == "user-mfa"
    expired = mint(provider.key, provider, iat=now - 400, exp=now - 90)
    assert failure(lambda: verify(client, expired)) == "failed"


def test_a_token_with_no_tenant_claim_fails(client: OidcClient) -> None:
    assert failure(lambda: sign_in(client, "notenant")) == "failed"


def test_amr_without_mfa_is_refused_as_mfa_required(client: OidcClient) -> None:
    claims = sign_in(client, "nomfa")
    assert "mfa" not in claims.amr
    assert refusal(claims) == "mfa_required"


@pytest.mark.parametrize("amr", [None, "mfa", "pwd mfa", {"mfa": True}])
def test_missing_or_non_list_amr_counts_as_no_mfa(
    client: OidcClient, provider: Any, amr: object
) -> None:
    claims = verify(client, mint(provider.key, provider, amr=amr))
    assert claims.amr == ()
    assert refusal(claims) == "mfa_required"


def test_display_name_falls_back_to_email_then_subject(client: OidcClient, provider: Any) -> None:
    by_email = mint(provider.key, provider, name=None, email="maya@desk.example")
    assert verify(client, by_email).display_name == "maya@desk.example"
    assert verify(client, mint(provider.key, provider, name=None)).display_name == "user-mfa"


# --- provider unreachable: real closed ports, no raised exceptions


def test_a_provider_on_a_closed_port_is_unavailable_within_the_timeout() -> None:
    client = OidcClient(settings_for(f"http://127.0.0.1:{closed_port()}"))
    started = time.monotonic()
    reason = failure(
        lambda: asyncio.run(client.authorize_url(state="a", nonce="b", verifier=VERIFIER))
    )
    assert reason == "provider_unavailable"
    assert time.monotonic() - started < 5


def test_a_token_endpoint_gone_after_discovery_is_unavailable(
    client: OidcClient, provider: Any
) -> None:
    code = code_for(client, "mfa")
    stop(provider)
    assert failure(lambda: exchange(client, code)) == "provider_unavailable"


def test_a_jwks_endpoint_gone_after_discovery_is_unavailable(
    client: OidcClient, provider: Any
) -> None:
    asyncio.run(client.authorize_url(state="a", nonce="b", verifier=VERIFIER))
    token = mint(provider.key, provider)
    stop(provider)
    assert failure(lambda: verify(client, token)) == "provider_unavailable"
