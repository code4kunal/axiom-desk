"""Composition root and HTTP surface. Every route comes from the capability registry."""

import os
import sqlite3
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Any

from axiom_core.audit import AuditLog
from axiom_core.authz import Authorizer, Forbidden, NotFound
from axiom_core.capabilities import latest_run
from axiom_core.db import migrate
from axiom_core.registry import Binding, Entitlements, Registry
from axiom_core.runs import RunStore
from axiom_core.session import SessionStore, Unauthenticated
from axiom_core.tenancy import Directory
from fastapi import Body, FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import ValidationError

# Surfaces a browser may claim. The agent calls the registry in-process as its own principal.
HTTP_SURFACES = {"screen": Binding.SCREEN, "command": Binding.COMMAND}


@dataclass(frozen=True)
class Services:
    audit: AuditLog
    directory: Directory
    authz: Authorizer
    sessions: SessionStore
    runs: RunStore
    entitlements: Entitlements
    registry: Registry


def build_services(conn: sqlite3.Connection, clock: Callable[[], float]) -> Services:
    audit = AuditLog(conn, clock)
    directory = Directory(conn, audit)
    authz = Authorizer(directory, audit, clock)
    runs = RunStore(conn, clock)
    entitlements = Entitlements(conn)
    registry = Registry(authz, entitlements, audit)
    registry.register(latest_run(runs))
    return Services(
        audit, directory, authz, SessionStore(directory, clock), runs, entitlements, registry
    )


def create_app(svc: Services) -> FastAPI:
    def call_capability(
        name: str,
        body: Annotated[dict[str, Any], Body()],
        authorization: Annotated[str | None, Header()] = None,
        x_axiom_surface: Annotated[str, Header()] = "screen",
    ) -> JSONResponse:
        try:
            if not authorization or not authorization.startswith("Bearer "):
                raise Unauthenticated("missing bearer token")
            claimed = {k: str(body[k]) for k in ("tenant_id", "user_id") if k in body}
            principal = svc.sessions.resolve_request(authorization.removeprefix("Bearer "), claimed)
            surface = HTTP_SURFACES.get(x_axiom_surface)
            if surface is None:
                raise Forbidden(f"unknown surface {x_axiom_surface}")
            envelope = svc.registry.call(principal, name, body, surface)
        except Unauthenticated as err:
            return JSONResponse({"error": str(err)}, status_code=401)
        except Forbidden as err:
            return JSONResponse({"error": str(err)}, status_code=403)
        except NotFound as err:
            return JSONResponse({"error": str(err)}, status_code=404)
        except ValidationError as err:
            return JSONResponse({"error": err.errors(include_url=False)}, status_code=422)
        return JSONResponse(envelope.to_json())

    app = FastAPI(title="Axiom Desk")
    app.add_api_route("/capabilities/{name}", call_capability, methods=["POST"])
    return app


def default_app() -> FastAPI:
    """Factory for `uvicorn --factory axiom_api.app:default_app`, records DB from AXIOM_DB."""
    conn = sqlite3.connect(os.environ.get("AXIOM_DB", "axiom.db"), check_same_thread=False)
    migrate(conn)
    return create_app(build_services(conn, time.time))
