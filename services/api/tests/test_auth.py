"""Desk sign-in routes against the real test provider over HTTP. The test client plays the
browser: it follows each redirect by hand, carrying a login_hint to the provider's authorize page
the way a person would pick an account there."""

import importlib.util
import json
import logging
import socket
import sqlite3
import threading
import time
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx2
import pytest
from axiom_api.app import Services, build_services, create_app
from axiom_api.oidc import Settings
from axiom_core.db import migrate
from axiom_core.session import SessionStore
from axiom_core.tenancy import Role
from fastapi.testclient import TestClient

SPEC = importlib.util.spec_from_file_location(
    "idp", Path(__file__).resolve().parents[3] / "tools" / "test_idp" / "idp.py"
)
assert SPEC and SPEC.loader
idp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(idp)

CLIENT, SECRET, TENANT = "desk", "s3cret", "axiom-desk"
ORIGIN = "https://testserver"
LOGIN, SESSION = "__Host-axiom_login", "__Host-axiom_session"


@pytest.fixture
def provider() -> Iterator[Any]:
    server = idp.start(client_id=CLIENT, client_secret=SECRET, tenant_claim="tenant")
    yield server
    server.shutdown()
    server.server_close()


@pytest.fixture
def services() -> Iterator[Services]:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    migrate(conn)
    svc = build_services(conn, time.time)
    svc.directory.bootstrap_admin(TENANT, "boss")
    boss = svc.directory.principal(TENANT, "boss")
    # user-nomfa is in the Directory, but signs in without MFA
    for user in ("user-mfa", "user-nomfa"):
        svc.directory.grant(boss, TENANT, user, Role.ANALYST)
    yield svc
    conn.close()


def settings_for(issuer: str) -> Settings:
    return Settings(
        issuer=issuer,
        client_id=CLIENT,
        client_secret=SECRET,
        tenant_claim="tenant",
        public_origin=ORIGIN,
    )


def browser(services: Services, issuer: str) -> TestClient:
    app = create_app(services, settings_for(issuer))
    return TestClient(app, base_url=ORIGIN, follow_redirects=False)


@pytest.fixture
def desk(services: Services, provider: Any) -> TestClient:
    return browser(services, provider.url)


def start(desk: TestClient) -> str:
    """GET /auth/login; returns the provider authorize URL it redirects to."""
    r = desk.get("/auth/login")
    assert r.status_code == 303, r.text
    return r.headers["location"]


def at_provider(authorize_url: str, hint: str) -> str:
    """The provider's answer for the person picking `hint`; returns the callback URL."""
    back = httpx2.get(f"{authorize_url}&login_hint={hint}", timeout=5)
    assert back.status_code == 302, back.text
    return back.headers["location"]


def sign_in(desk: TestClient, hint: str = "mfa") -> httpx2.Response:
    return desk.get(at_provider(start(desk), hint))


def cookie(response: httpx2.Response, name: str) -> str:
    (header,) = [h for h in response.headers.get_list("set-cookie") if h.startswith(f"{name}=")]
    return header


def flags(header: str) -> set[str]:
    return {part.strip().lower() for part in header.split(";")[1:]}


def assert_refused_with(response: httpx2.Response, code: str) -> None:
    assert response.status_code == 303
    assert response.headers["location"] == f"/sign-in?error={code}"
    assert "max-age=0" in flags(cookie(response, LOGIN))


def closed_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port: int = s.getsockname()[1]
    s.close()
    return port


# --- the round trip


def test_signing_in_through_the_provider_lands_on_the_desk_and_names_the_user(
    desk: TestClient,
) -> None:
    done = sign_in(desk)

    assert done.status_code == 303
    assert done.headers["location"] == "/desk"
    assert "max-age=0" in flags(cookie(done, LOGIN))
    me = desk.get("/auth/me")
    assert me.status_code == 200
    assert me.json() == {"name": "Maya Desk", "tenant": TENANT}
    assert me.headers["cache-control"] == "no-store"


def test_login_redirects_to_the_provider_with_a_short_lived_host_only_login_cookie(
    desk: TestClient, provider: Any
) -> None:
    r = desk.get("/auth/login")

    assert r.status_code == 303
    assert r.headers["location"].startswith(f"{provider.url}/authorize?")
    query = parse_qs(urlparse(r.headers["location"]).query)
    assert query["redirect_uri"] == [f"{ORIGIN}/auth/callback"]
    assert flags(cookie(r, LOGIN)) == {
        "httponly",
        "secure",
        "samesite=lax",
        "path=/",
        "max-age=600",
    }


def test_the_session_cookie_is_host_only_httponly_secure_and_lax(desk: TestClient) -> None:
    done = sign_in(desk)

    ttl = int(SessionStore.TTL_SECONDS)
    assert flags(cookie(done, SESSION)) == {
        "httponly",
        "secure",
        "samesite=lax",
        "path=/",
        f"max-age={ttl}",
    }


# --- a sign-in completes once, in the browser that started it


def test_replaying_the_callback_url_gives_expired(desk: TestClient) -> None:
    callback = at_provider(start(desk), "mfa")
    login_handle = desk.cookies[LOGIN]
    assert desk.get(callback).headers["location"] == "/desk"

    desk.cookies.set(LOGIN, login_handle)  # even with the old login cookie put back
    assert_refused_with(desk.get(callback), "expired")


def test_a_callback_in_another_browser_gives_expired(
    desk: TestClient, services: Services, provider: Any
) -> None:
    callback = at_provider(start(desk), "mfa")

    other = browser(services, provider.url)
    assert_refused_with(other.get(callback), "expired")
    assert other.get("/auth/me").status_code == 401


def test_a_second_sign_in_in_the_same_browser_makes_the_first_callback_expired(
    desk: TestClient,
) -> None:
    first = at_provider(start(desk), "mfa")
    second = at_provider(start(desk), "mfa")

    assert desk.get(second).headers["location"] == "/desk"
    assert_refused_with(desk.get(first), "expired")


def test_a_state_other_than_the_pending_ones_gives_expired(desk: TestClient) -> None:
    callback = at_provider(start(desk), "mfa")
    login_handle = desk.cookies[LOGIN]
    forged = callback.replace("state=", "state=x")

    assert_refused_with(desk.get(forged), "expired")
    desk.cookies.set(LOGIN, login_handle)  # a forged state spends the row, not just the cookie
    assert_refused_with(desk.get(callback), "expired")


# --- failures map to a fixed code


def test_cancelling_at_the_provider_gives_cancelled(desk: TestClient) -> None:
    assert_refused_with(sign_in(desk, "deny"), "cancelled")


def test_any_other_provider_error_gives_failed_without_the_providers_text(
    desk: TestClient,
) -> None:
    start(desk)
    r = desk.get(
        "/auth/callback",
        params={"error": "server_error", "error_description": "boom <b>", "state": "s"},
    )
    assert_refused_with(r, "failed")


def test_a_user_who_signed_in_without_mfa_gives_mfa_required(desk: TestClient) -> None:
    assert_refused_with(sign_in(desk, "nomfa"), "mfa_required")
    assert desk.get("/auth/me").status_code == 401


def test_a_user_outside_the_directory_gives_unknown_user(desk: TestClient) -> None:
    assert_refused_with(sign_in(desk, "stranger"), "unknown_user")


def test_a_token_without_a_tenant_gives_failed(desk: TestClient) -> None:
    assert_refused_with(sign_in(desk, "notenant"), "failed")


def test_login_with_the_provider_on_a_closed_port_gives_provider_unavailable(
    services: Services,
) -> None:
    desk = browser(services, f"http://127.0.0.1:{closed_port()}")
    r = desk.get("/auth/login")

    assert r.status_code == 303
    assert r.headers["location"] == "/sign-in?error=provider_unavailable"
    assert LOGIN not in desk.cookies


@pytest.mark.parametrize(
    "document", [{}, {"jwks_uri": "http://127.0.0.1:9/jwks"}], ids=["empty", "jwks-only"]
)
def test_login_with_a_discovery_document_missing_its_endpoints_gives_failed(
    services: Services, document: dict[str, str]
) -> None:
    class Empty(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            body = json.dumps(document).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Empty)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        r = browser(services, f"http://127.0.0.1:{server.server_port}").get("/auth/login")
    finally:
        server.shutdown()
        server.server_close()

    assert r.status_code == 303
    assert r.headers["location"] == "/sign-in?error=failed"


def test_login_with_sign_in_not_configured_gives_failed(services: Services) -> None:
    desk = TestClient(create_app(services), base_url=ORIGIN, follow_redirects=False)
    r = desk.get("/auth/login")

    assert r.status_code == 303
    assert r.headers["location"] == "/sign-in?error=failed"


# --- what is audited


def test_a_refusal_is_logged_with_its_code(
    desk: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.WARNING, logger="axiom_api.auth"):
        assert_refused_with(sign_in(desk, "deny"), "cancelled")

    assert [r.getMessage() for r in caplog.records] == ["sign-in refused: cancelled"]


def test_cancelled_and_expired_callbacks_write_no_audit_record(
    desk: TestClient, services: Services, provider: Any
) -> None:
    before = len(services.audit.records())
    assert_refused_with(sign_in(desk, "deny"), "cancelled")
    callback = at_provider(start(desk), "mfa")
    assert_refused_with(browser(services, provider.url).get(callback), "expired")

    assert len(services.audit.records()) == before


def test_a_no_mfa_refusal_writes_exactly_one_audit_record(
    desk: TestClient, services: Services
) -> None:
    before = len(services.audit.records())
    assert_refused_with(sign_in(desk, "nomfa"), "mfa_required")

    after = services.audit.records()[before:]
    assert [(r.user_id, r.action, r.verdict) for r in after] == [
        ("user-nomfa", "sign_in", "refused")
    ]


# --- sign out


def test_logout_ends_the_session_on_the_server_and_clears_the_cookie(
    desk: TestClient, services: Services, provider: Any
) -> None:
    sign_in(desk)
    token = desk.cookies[SESSION]

    r = desk.post("/auth/logout", headers={"Sec-Fetch-Site": "same-origin"})

    assert r.status_code == 303
    assert r.headers["location"] == "/sign-in"
    assert flags(cookie(r, SESSION)) >= {"max-age=0", "secure", "httponly", "path=/"}
    stale = browser(services, provider.url)
    stale.cookies.set(SESSION, token)
    assert stale.get("/auth/me").status_code == 401


def test_logout_with_the_public_origin_and_no_fetch_metadata_passes(desk: TestClient) -> None:
    sign_in(desk)
    r = desk.post("/auth/logout", headers={"Origin": ORIGIN})

    assert r.status_code == 303
    assert desk.get("/auth/me").status_code == 401


@pytest.mark.parametrize(
    "headers",
    [
        {"Sec-Fetch-Site": "cross-site", "Origin": ORIGIN},
        {"Sec-Fetch-Site": "same-site"},
        {"Origin": "https://evil.example"},
        {"Origin": "null"},
        {},
    ],
    ids=["cross-site", "same-site", "foreign-origin", "null-origin", "no-origin"],
)
def test_a_logout_not_from_the_desk_is_refused_and_the_session_survives(
    desk: TestClient, headers: dict[str, str]
) -> None:
    sign_in(desk)

    r = desk.post("/auth/logout", headers=headers)

    assert r.status_code == 403
    assert desk.get("/auth/me").status_code == 200


def test_logout_by_get_is_not_allowed(desk: TestClient) -> None:
    sign_in(desk)

    assert desk.get("/auth/logout").status_code == 405
    assert desk.get("/auth/me").status_code == 200


# --- /auth/me and capability calls


def test_me_without_a_session_is_401_and_not_cached(desk: TestClient) -> None:
    r = desk.get("/auth/me")

    assert r.status_code == 401
    assert r.headers["cache-control"] == "no-store"


def test_a_user_removed_from_the_directory_loses_me_on_the_next_request(
    desk: TestClient, services: Services
) -> None:
    sign_in(desk)
    boss = services.directory.principal(TENANT, "boss")
    services.directory.revoke(boss, TENANT, "user-mfa", Role.ANALYST)

    assert desk.get("/auth/me").status_code == 401


def test_a_capability_call_with_only_the_session_cookie_is_refused(desk: TestClient) -> None:
    sign_in(desk)

    r = desk.post("/capabilities/runs_latest", json={"kind": "regime"})

    assert r.status_code == 401
