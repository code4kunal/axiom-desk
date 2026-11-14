"""The capability registry: one entry drives the screen API, the command bar and the agent tool.

Every call is authorized, licence-checked against the tenant's entitlements and wrapped in the
result envelope, so the three surfaces cannot drift apart.
"""

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ValidationError

from axiom_core.audit import AuditLog
from axiom_core.authz import Action, Authorizer, Forbidden, NotFound, Resource
from axiom_core.db import Connection
from axiom_core.envelope import Envelope, HandlerResult, JsonValue
from axiom_core.principals import Principal

NAME = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


class Binding(StrEnum):
    SCREEN = "screen"
    COMMAND = "command"
    AGENT = "agent"


ALL_BINDINGS = frozenset(Binding)


@dataclass(frozen=True)
class CallContext:
    principal: Principal
    surface: Binding


@dataclass(frozen=True)
class Capability:
    name: str
    summary: str
    inputs: type[BaseModel]
    handler: Callable[[CallContext, Any], HandlerResult]
    permission: Action
    bindings: frozenset[Binding]
    version: str
    parity_inputs: Mapping[str, JsonValue] | None
    # Why a person, never the agent, must take this action; exempts it from the agent binding.
    human_only_reason: str | None = None
    # Shape of the envelope's value, for typed clients; None leaves it untyped.
    output: type[BaseModel] | None = None


class Entitlements:
    PUBLIC = "public"

    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def grant(self, tenant_id: str, scope: str) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT OR IGNORE INTO tenant_entitlements VALUES (?, ?)", (tenant_id, scope)
            )

    def allows(self, tenant_id: str, scope: str) -> bool:
        if scope == self.PUBLIC:
            return True
        row = self._conn.execute(
            "SELECT 1 FROM tenant_entitlements WHERE tenant_id = ? AND scope = ?",
            (tenant_id, scope),
        ).fetchone()
        return row is not None


class Registry:
    def __init__(self, authz: Authorizer, entitlements: Entitlements, audit: AuditLog) -> None:
        self._authz = authz
        self._entitlements = entitlements
        self._audit = audit
        self._caps: dict[str, Capability] = {}

    def register(self, cap: Capability) -> None:
        if not NAME.match(cap.name):
            raise ValueError(f"{cap.name!r}: names are lowercase letters, digits and underscores")
        if cap.name in self._caps:
            raise ValueError(f"{cap.name!r} is already registered")
        self._caps[cap.name] = cap

    def capabilities(self) -> list[Capability]:
        return [self._caps[name] for name in sorted(self._caps)]

    def check(self) -> list[str]:
        problems: list[str] = []
        for cap in self.capabilities():
            human_only = bool(cap.human_only_reason and cap.human_only_reason.strip())
            expected = ALL_BINDINGS - {Binding.AGENT} if human_only else ALL_BINDINGS
            for missing in sorted(expected - cap.bindings):
                problems.append(f"{cap.name}: missing {missing} binding")
            if human_only and Binding.AGENT in cap.bindings:
                problems.append(f"{cap.name}: human-only but bound to the agent")
            if cap.parity_inputs is None:
                problems.append(f"{cap.name}: missing parity fixture")
                continue
            try:
                cap.inputs.model_validate(cap.parity_inputs)
            except ValidationError as err:
                problems.append(f"{cap.name}: parity fixture does not validate: {err}")
        return problems

    def call(
        self, principal: Principal, name: str, raw_inputs: Mapping[str, JsonValue], surface: Binding
    ) -> Envelope:
        cap = self._caps.get(name)
        if cap is None:
            raise NotFound("capability", name)
        if surface not in cap.bindings:
            self._audit.record(
                principal,
                "capability_surface",
                "refused",
                {"capability": name, "surface": surface.value},
            )
            raise Forbidden(f"{name} is not available on the {surface} surface")
        inputs = cap.inputs.model_validate(raw_inputs)
        self._authz.check(
            principal, cap.permission, Resource(principal.tenant_id, "capability", name)
        )
        result = cap.handler(CallContext(principal, surface), inputs)
        if (
            cap.output is not None
        ):  # the generated client trusts this type, so hold the server to it
            cap.output.model_validate(result.value)
        for source in result.sources:
            if not self._entitlements.allows(principal.tenant_id, source.licence_scope):
                self._audit.record(
                    principal,
                    "licence_scope",
                    "refused",
                    {"capability": name, "source": source.name, "scope": source.licence_scope},
                )
                raise Forbidden(f"licence scope {source.licence_scope} is not entitled")
        return Envelope.wrap(name, cap.version, inputs.model_dump(mode="json"), result)

    def tool_list(self) -> list[dict[str, JsonValue]]:
        return [
            {
                "name": cap.name,
                "description": cap.summary,
                "input_schema": cap.inputs.model_json_schema(),
            }
            for cap in self.capabilities()
            if Binding.AGENT in cap.bindings
        ]

    def command_index(self) -> list[dict[str, JsonValue]]:
        return [
            {"name": cap.name, "summary": cap.summary, "permission": cap.permission.value}
            for cap in self.capabilities()
            if Binding.COMMAND in cap.bindings
        ]
