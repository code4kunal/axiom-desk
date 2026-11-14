"""Composition root and HTTP surface. Every route comes from the capability registry."""

import os
import sqlite3
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Any

from axiom_core.audit import AuditLog
from axiom_core.authz import Authorizer, Forbidden, NotFound, Refused
from axiom_core.capabilities import latest_run
from axiom_core.db import migrate
from axiom_core.registry import Binding, Entitlements, Registry
from axiom_core.runs import RunStore
from axiom_core.session import PendingLogins, SessionStore, Unauthenticated
from axiom_core.tenancy import Directory
from axiom_data.calendar import TradingCalendar
from axiom_data.capabilities import fno_contract_rules, instrument_lookup, trading_calendar
from axiom_data.fno_rules import FnoRulesEngine
from axiom_data.instruments import InstrumentStore
from fastapi import Body, FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from axiom_api.auth import register_auth
from axiom_api.oidc import Settings, load_settings

# Surfaces a browser may claim. The agent calls the registry in-process as its own principal.
HTTP_SURFACES = {b.value: b for b in Binding if b is not Binding.AGENT}


@dataclass(frozen=True)
class Services:
    audit: AuditLog
    directory: Directory
    authz: Authorizer
    sessions: SessionStore
    pending: PendingLogins
    runs: RunStore
    entitlements: Entitlements
    registry: Registry
    instruments: InstrumentStore
    calendar: TradingCalendar
    fno_rules: FnoRulesEngine


def build_services(conn: sqlite3.Connection, clock: Callable[[], float]) -> Services:
    audit = AuditLog(conn, clock)
    directory = Directory(conn, audit)
    authz = Authorizer(directory, audit, clock)
    runs = RunStore(conn, clock)
    entitlements = Entitlements(conn)
    registry = Registry(authz, entitlements, audit)
    calendar = TradingCalendar()
    instruments = InstrumentStore(conn)
    fno_rules = FnoRulesEngine(conn, calendar)
    registry.register(latest_run(runs))
    registry.register(instrument_lookup(instruments))
    registry.register(trading_calendar(calendar))
    registry.register(fno_contract_rules(fno_rules))
    sessions = SessionStore(conn, directory, audit, clock)
    pending = PendingLogins(conn, clock)
    return Services(
        audit,
        directory,
        authz,
        sessions,
        pending,
        runs,
        entitlements,
        registry,
        instruments,
        calendar,
        fno_rules,
    )


def create_app(svc: Services, settings: Settings | None = None) -> FastAPI:
    """Sign-in routes answer only when `settings` is given; /auth/login otherwise refuses."""

    # async on purpose: every request then runs on the event loop thread, one at a time. A sync
    # route runs in a thread pool, and on the one shared sqlite connection a failing request's
    # rollback would also undo another request's uncommitted audit write.
    # shortcut: DB work blocks the loop, fine for one desk; use a connection per request (or a
    # Postgres pool) before concurrent traffic grows.
    async def call_capability(
        name: str,
        body: Annotated[dict[str, Any], Body()],
        authorization: Annotated[str | None, Header()] = None,
        x_axiom_surface: Annotated[str, Header()] = "screen",
    ) -> JSONResponse:
        try:
            if not authorization or not authorization.startswith("Bearer "):
                raise Unauthenticated("invalid")
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
        except Refused as err:
            return JSONResponse({"error": str(err)}, status_code=422)
        except ValidationError as err:
            return JSONResponse(
                {"error": err.errors(include_url=False, include_context=False)}, status_code=422
            )
        return JSONResponse(envelope.to_json())

    app = FastAPI(title="Axiom Desk")
    app.add_api_route("/capabilities/{name}", call_capability, methods=["POST"])
    register_auth(app, svc.sessions, svc.pending, settings)
    return app


def default_app() -> FastAPI:
    """Factory for `uvicorn --factory axiom_api.app:default_app`, records DB from AXIOM_DB,
    sign-in from the AXIOM_OIDC_* and AXIOM_PUBLIC_ORIGIN variables (see axiom_api.oidc)."""
    conn = sqlite3.connect(os.environ.get("AXIOM_DB", "axiom.db"), check_same_thread=False)
    migrate(conn)
    return create_app(build_services(conn, time.time), load_settings())
