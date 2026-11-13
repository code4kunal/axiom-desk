import base64
import hashlib
import importlib.util
import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import jwt
import pytest

SPEC = importlib.util.spec_from_file_location(
    "idp", Path(__file__).resolve().parents[1] / "test_idp" / "idp.py"
)
assert SPEC and SPEC.loader
idp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(idp)

CLIENT, SECRET, REDIRECT = "desk", "s3cret", "http://127.0.0.1:9/cb"
VERIFIER = "v" * 64
CHALLENGE = (
    base64.urlsafe_b64encode(hashlib.sha256(VERIFIER.encode()).digest()).rstrip(b"=").decode()
)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def call(url: str, data: dict[str, str] | None = None) -> tuple[int, dict[str, str], bytes]:
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    try:
        with OPENER.open(url, body, timeout=5) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


@pytest.fixture
def provider() -> Iterator[Any]:
    server = idp.start(client_id=CLIENT, client_secret=SECRET, tenant_claim="tenant")
    yield server
    server.shutdown()
    server.server_close()


def authorize(base: str, hint: str = "mfa") -> str:
    query = urllib.parse.urlencode(
        {
            "client_id": CLIENT,
            "redirect_uri": REDIRECT,
            "response_type": "code",
            "state": "st1",
            "nonce": "n1",
            "code_challenge": CHALLENGE,
            "code_challenge_method": "S256",
            "login_hint": hint,
        }
    )
    status, headers, _ = call(f"{base}/authorize?{query}")
    assert status == 302
    params = urllib.parse.parse_qs(urllib.parse.urlparse(headers["Location"]).query)
    assert params["state"] == ["st1"]
    return params["code"][0]


def exchange(
    base: str, code: str, verifier: str = VERIFIER, secret: str = SECRET
) -> tuple[int, Any]:
    status, _, body = call(
        f"{base}/token",
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT,
            "client_id": CLIENT,
            "client_secret": secret,
            "code_verifier": verifier,
        },
    )
    return status, json.loads(body)


def test_discovery_is_on_own_origin_and_jwks_verifies_issued_token(provider: Any) -> None:
    base = provider.url
    doc = json.loads(call(f"{base}/.well-known/openid-configuration")[2])
    assert doc["issuer"] == base
    for key in ("authorization_endpoint", "token_endpoint", "jwks_uri"):
        assert doc[key].startswith(base + "/")
    status, tokens = exchange(base, authorize(base))
    assert status == 200
    jwks = jwt.PyJWKClient(doc["jwks_uri"]).get_signing_key_from_jwt(tokens["id_token"])
    claims = jwt.decode(
        tokens["id_token"], jwks.key, algorithms=["RS256"], audience=CLIENT, issuer=base
    )
    assert claims["nonce"] == "n1"
    assert claims["amr"] == ["pwd", "mfa"]
    assert claims["tenant"] == "axiom-desk"
    assert claims["name"] == "Maya Desk"
    assert claims["auth_time"] <= claims["iat"]


def test_wrong_verifier_or_secret_is_refused(provider: Any) -> None:
    base = provider.url
    assert exchange(base, authorize(base), verifier="x" * 64) == (400, {"error": "invalid_grant"})
    assert exchange(base, authorize(base), secret="nope") == (401, {"error": "invalid_client"})


def test_code_is_single_use(provider: Any) -> None:
    base = provider.url
    code = authorize(base)
    assert exchange(base, code)[0] == 200
    assert exchange(base, code) == (400, {"error": "invalid_grant"})
