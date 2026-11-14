import sqlite3
from collections.abc import Iterable
from datetime import UTC, datetime

import pytest
from axiom_core.audit import AuditLog
from axiom_core.authz import Action, Authorizer, Forbidden
from axiom_core.envelope import HandlerResult, Source
from axiom_core.registry import (
    ALL_BINDINGS,
    Binding,
    CallContext,
    Capability,
    Entitlements,
    Registry,
)
from axiom_core.tenancy import Directory
from conftest import Clock
from pydantic import BaseModel

AS_OF = datetime(2026, 11, 12, 9, 15, tzinfo=UTC)


class Echo(BaseModel):
    text: str


def echo_with(scope: str):
    def handler(ctx: CallContext, inputs: Echo) -> HandlerResult:
        return HandlerResult(
            value={"echo": inputs.text},
            as_of=AS_OF,
            sources=(Source("desk-notes", scope),),
            method="echo",
        )

    return handler


def cap(
    name: str = "echo",
    *,
    bindings: Iterable[Binding] = ALL_BINDINGS,
    parity: bool = True,
    scope: str = "public",
    human_only_reason: str | None = None,
) -> Capability:
    return Capability(
        name=name,
        summary="Echo text back",
        inputs=Echo,
        handler=echo_with(scope),
        permission=Action.READ,
        bindings=frozenset(bindings),
        version="1",
        parity_inputs={"text": "hi"} if parity else None,
        human_only_reason=human_only_reason,
    )


@pytest.fixture
def registry(
    directory: Directory, audit: AuditLog, authz: Authorizer, conn: sqlite3.Connection
) -> Registry:
    return Registry(authz, Entitlements(conn), audit)


def test_entry_missing_its_agent_binding_fails_the_check(registry: Registry) -> None:
    registry.register(cap("ok"))
    registry.register(cap("no_agent", bindings={Binding.SCREEN, Binding.COMMAND}))
    registry.register(cap("no_fixture", parity=False))
    problems = registry.check()
    assert any("no_agent" in p and "agent" in p for p in problems)
    assert any("no_fixture" in p and "parity" in p for p in problems)
    assert not any(p.startswith("ok:") for p in problems)


def test_human_only_entry_needs_a_stated_reason(registry: Registry) -> None:
    screen_only = {Binding.SCREEN, Binding.COMMAND}
    registry.register(cap("confirm", bindings=screen_only, human_only_reason="a person confirms"))
    registry.register(cap("blank", bindings=screen_only, human_only_reason="  "))
    registry.register(cap("silent", bindings=screen_only))
    registry.register(cap("both", human_only_reason="agent-bound but claims human-only"))
    problems = registry.check()
    assert not any(p.startswith("confirm:") for p in problems)
    assert "blank: missing agent binding" in problems
    assert "silent: missing agent binding" in problems
    assert any(p.startswith("both:") and "human-only" in p for p in problems)
    human_only = [c.name for c in registry.capabilities() if c.human_only_reason]
    assert sorted(human_only) == ["blank", "both", "confirm"]


def test_human_only_entry_refuses_the_agent_and_audits_it(
    registry: Registry, directory: Directory, audit: AuditLog
) -> None:
    registry.register(
        cap(bindings={Binding.SCREEN, Binding.COMMAND}, human_only_reason="a person confirms")
    )
    ana = directory.principal("desk", "ana")
    with pytest.raises(Forbidden, match="agent"):
        registry.call(ana, "echo", {"text": "hi"}, Binding.AGENT)
    last = audit.records()[-1]
    assert (last.action, last.verdict) == ("capability_surface", "refused")
    assert last.ids == {"capability": "echo", "surface": "agent"}


def test_names_must_be_valid_tool_names(registry: Registry) -> None:
    with pytest.raises(ValueError):
        registry.register(cap("runs.latest"))


def test_same_inputs_give_the_same_result_id_on_every_surface(
    registry: Registry, directory: Directory, clock: Clock
) -> None:
    registry.register(cap())
    ana = directory.principal("desk", "ana", authenticated_at=clock.now)
    ids = {registry.call(ana, "echo", {"text": "hi"}, surface).result_id for surface in Binding}
    assert len(ids) == 1
    assert registry.call(ana, "echo", {"text": "bye"}, Binding.SCREEN).result_id not in ids


def test_internal_only_source_carries_its_scope_and_needs_entitlement(
    registry: Registry,
    directory: Directory,
    conn: sqlite3.Connection,
    clock: Clock,
    audit: AuditLog,
) -> None:
    registry.register(cap(scope="internal-only"))
    ana = directory.principal("desk", "ana", authenticated_at=clock.now)
    with pytest.raises(Forbidden, match="licence"):
        registry.call(ana, "echo", {"text": "hi"}, Binding.SCREEN)
    assert audit.records()[-1].action == "licence_scope"

    Entitlements(conn).grant("desk", "internal-only")
    env = registry.call(ana, "echo", {"text": "hi"}, Binding.SCREEN)
    assert [s.licence_scope for s in env.sources] == ["internal-only"]


def test_surface_without_binding_is_refused(registry: Registry, directory: Directory) -> None:
    registry.register(cap(bindings={Binding.SCREEN}))
    with pytest.raises(Forbidden):
        registry.call(directory.principal("desk", "ana"), "echo", {"text": "hi"}, Binding.AGENT)


def test_tool_list_matches_agent_bound_entries_exactly(registry: Registry) -> None:
    registry.register(cap("a"))
    registry.register(cap("b", bindings={Binding.SCREEN, Binding.COMMAND}))
    tools = registry.tool_list()
    assert [t["name"] for t in tools] == ["a"]
    assert tools[0]["input_schema"]["properties"]["text"]["type"] == "string"
    assert [c["name"] for c in registry.command_index()] == ["a", "b"]
