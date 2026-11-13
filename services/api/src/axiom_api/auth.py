"""Desk sign-in routes: /auth/login, /auth/callback, /auth/logout and /auth/me.

The browser holds two cookies only: the login handle while a sign-in is in flight, then the
session token. Failures reach /sign-in as a fixed code, never provider text. Refusals before the
ID token verifies are logged here; refusals after it are audited by SessionStore.
"""

import logging
import secrets

import jwt
from axiom_core.session import PendingLogins, SessionStore, Unauthenticated
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response

from axiom_api.oidc import OidcClient, Settings, SignInFailed

LOGIN_COOKIE = "__Host-axiom_login"
SESSION_COOKIE = "__Host-axiom_session"
NO_STORE = {"Cache-Control": "no-store"}

log = logging.getLogger(__name__)


def _see_other(path: str) -> RedirectResponse:
    return RedirectResponse(path, status_code=303)


def _set(response: Response, name: str, value: str, max_age: int) -> None:
    # __Host- cookies: Secure, Path=/, no Domain. max_age=0 deletes.
    response.set_cookie(
        name, value, max_age=max_age, path="/", secure=True, httponly=True, samesite="lax"
    )


def _refused(code: str) -> RedirectResponse:
    log.warning("sign-in refused: %s", code)
    response = _see_other(f"/sign-in?error={code}")
    _set(response, LOGIN_COOKIE, "", 0)
    return response


def register_auth(
    app: FastAPI, sessions: SessionStore, pending: PendingLogins, settings: Settings | None
) -> None:
    async def me(request: Request) -> JSONResponse:
        token = request.cookies.get(SESSION_COOKIE)
        try:
            if not token:
                raise Unauthenticated("invalid")
            principal, name = sessions.describe(token)
        except Unauthenticated as e:
            return JSONResponse({"error": e.reason}, status_code=401, headers=NO_STORE)
        return JSONResponse({"name": name, "tenant": principal.tenant_id}, headers=NO_STORE)

    app.add_api_route("/auth/me", me, methods=["GET"])  # also without sign-in configured
    if settings is None:

        async def not_configured() -> Response:
            return _refused("failed")

        app.add_api_route("/auth/login", not_configured, methods=["GET"])
        return
    oidc = OidcClient(settings)  # one per app: it caches discovery and the JWKS

    async def login() -> Response:
        state, nonce, verifier = (secrets.token_urlsafe(32) for _ in range(3))
        try:
            url = await oidc.authorize_url(state=state, nonce=nonce, verifier=verifier)
        except SignInFailed as e:
            return _refused(e.reason)
        except (KeyError, jwt.PyJWKClientError):  # discovery without its endpoints or jwks_uri
            return _refused("failed")
        handle = pending.create(state=state, nonce=nonce, verifier=verifier)
        response = _see_other(url)
        _set(response, LOGIN_COOKIE, handle, int(PendingLogins.TTL_SECONDS))
        return response

    async def callback(
        request: Request, code: str = "", state: str = "", error: str = ""
    ) -> Response:
        if error:
            return _refused("cancelled" if error == "access_denied" else "failed")
        handle = request.cookies.get(LOGIN_COOKIE)
        started = pending.take(handle) if handle else None
        if started is None or not secrets.compare_digest(started.state.encode(), state.encode()):
            return _refused("expired")
        if not code:
            return _refused("failed")
        try:
            claims = await oidc.exchange(code=code, verifier=started.verifier, nonce=started.nonce)
        except SignInFailed as e:
            return _refused(e.reason)
        try:
            token = sessions.sign_in(claims)
        except Unauthenticated as e:
            return _refused(e.reason)
        response = _see_other("/desk")
        _set(response, SESSION_COOKIE, token, int(SessionStore.TTL_SECONDS))
        _set(response, LOGIN_COOKIE, "", 0)
        return response

    async def logout(request: Request) -> Response:
        site = request.headers.get("sec-fetch-site")
        same_origin = (
            site == "same-origin"
            if site is not None
            else request.headers.get("origin") == settings.public_origin
        )
        if not same_origin:
            return JSONResponse({"error": "cross-origin sign out refused"}, status_code=403)
        token = request.cookies.get(SESSION_COOKIE)
        if token:
            sessions.sign_out(token)
        response = _see_other("/sign-in")
        _set(response, SESSION_COOKIE, "", 0)
        return response

    app.add_api_route("/auth/login", login, methods=["GET"])
    app.add_api_route("/auth/callback", callback, methods=["GET"])
    app.add_api_route("/auth/logout", logout, methods=["POST"])
