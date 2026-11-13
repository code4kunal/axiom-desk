"""Minimal OIDC provider for tests. The RS256 key lives in memory only. Never import from src/."""

import argparse
import base64
import hashlib
import json
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

USERS: dict[str, dict[str, Any]] = json.loads((Path(__file__).parent / "users.json").read_text())


def b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


class Idp(ThreadingHTTPServer):
    def __init__(self, port: int, client_id: str, client_secret: str, tenant_claim: str) -> None:
        super().__init__(("127.0.0.1", port), Handler)
        self.client_id, self.client_secret, self.tenant_claim = (
            client_id,
            client_secret,
            tenant_claim,
        )
        self.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.codes: dict[str, dict[str, Any]] = {}
        self.url = f"http://127.0.0.1:{self.server_port}"

    def jwk(self) -> dict[str, str]:
        nums = self.key.public_key().public_numbers()
        size = (nums.n.bit_length() + 7) // 8
        return {
            "kty": "RSA",
            "use": "sig",
            "alg": "RS256",
            "kid": "test-key",
            "n": b64(nums.n.to_bytes(size, "big")),
            "e": b64(nums.e.to_bytes(3, "big")),
        }

    def id_token(self, rec: dict[str, Any]) -> str:
        user, now = USERS[rec["hint"]], int(time.time())
        claims: dict[str, Any] = {
            "iss": self.url,
            "aud": self.client_id,
            "sub": user["sub"],
            "iat": now,
            "exp": now + 300,
            "nonce": rec["nonce"],
            "amr": user["amr"],
            "name": user["name"],
        }
        if not user.get("omit_auth_time"):
            claims["auth_time"] = rec["auth_time"]
        if "tenant" in user:
            claims[self.tenant_claim] = user["tenant"]
        head = {"alg": "RS256", "typ": "JWT", "kid": "test-key"}
        signing = f"{b64(json.dumps(head).encode())}.{b64(json.dumps(claims).encode())}"
        sig = self.key.sign(signing.encode(), padding.PKCS1v15(), hashes.SHA256())
        return f"{signing}.{b64(sig)}"


class Handler(BaseHTTPRequestHandler):
    @property
    def idp(self) -> Idp:
        assert isinstance(self.server, Idp)
        return self.server

    def send(self, status: int, body: Any, location: str | None = None) -> None:
        self.send_response(status)
        if location:
            self.send_header("Location", location)
        payload = json.dumps(body).encode() if body is not None else b""
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        url, s = urlparse(self.path), self.idp
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        if url.path == "/.well-known/openid-configuration":
            self.send(
                200,
                {
                    "issuer": s.url,
                    "authorization_endpoint": f"{s.url}/authorize",
                    "token_endpoint": f"{s.url}/token",
                    "jwks_uri": f"{s.url}/jwks",
                    "response_types_supported": ["code"],
                    "subject_types_supported": ["public"],
                    "id_token_signing_alg_values_supported": ["RS256"],
                },
            )
        elif url.path == "/jwks":
            self.send(200, {"keys": [s.jwk()]})
        elif url.path == "/authorize" and q.get("client_id") == s.client_id and "redirect_uri" in q:
            hint = q.get("login_hint", "")
            if hint == "deny":
                back = {"error": "access_denied", "state": q.get("state", "")}
            elif hint in USERS:
                code = secrets.token_urlsafe(24)
                s.codes[code] = {
                    "hint": hint,
                    "nonce": q.get("nonce"),
                    "challenge": q.get("code_challenge"),
                    "client_id": q["client_id"],
                    "redirect_uri": q["redirect_uri"],
                    "auth_time": int(time.time()),
                }
                back = {"code": code, "state": q.get("state", "")}
            else:
                return self.send(400, {"error": "unknown login_hint"})
            self.send(302, None, f"{q['redirect_uri']}?{urlencode(back)}")
        else:
            self.send(404, {"error": "not_found"})

    def do_POST(self) -> None:
        s = self.idp
        raw = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()
        f = {k: v[0] for k, v in parse_qs(raw).items()}
        if urlparse(self.path).path != "/token":
            return self.send(404, {"error": "not_found"})
        cid, secret = f.get("client_id"), f.get("client_secret")
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Basic "):
            cid, _, secret = base64.b64decode(auth[6:]).decode().partition(":")
        if cid != s.client_id or not secrets.compare_digest(secret or "", s.client_secret):
            return self.send(401, {"error": "invalid_client"})
        rec = s.codes.pop(f.get("code", ""), None)  # pop: a code works once
        challenge = b64(hashlib.sha256(f.get("code_verifier", "").encode()).digest())
        if (
            f.get("grant_type") != "authorization_code"
            or rec is None
            or rec["client_id"] != cid
            or rec["redirect_uri"] != f.get("redirect_uri")
            or rec["challenge"] != challenge
        ):
            return self.send(400, {"error": "invalid_grant"})
        self.send(
            200,
            {
                "token_type": "Bearer",
                "access_token": secrets.token_urlsafe(16),
                "expires_in": 300,
                "id_token": s.id_token(rec),
            },
        )

    def log_message(self, format: str, *args: Any) -> None:
        return


def start(client_id: str, client_secret: str, tenant_claim: str, port: int = 0) -> Idp:
    server = Idp(port, client_id, client_secret, tenant_claim)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--client-id", required=True)
    ap.add_argument("--client-secret", required=True)
    ap.add_argument("--tenant-claim", required=True)
    a = ap.parse_args()
    print(f"test idp on http://127.0.0.1:{a.port}", flush=True)
    start(a.client_id, a.client_secret, a.tenant_claim, a.port).serve_forever()
