"""Authorization: the role table, agent limits and tenant isolation, enforced in code.

Every decision, allowed or refused, writes one audit record.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from axiom_core.audit import AuditLog
from axiom_core.principals import Principal, PrincipalKind, Role

RECENT_AUTH_SECONDS = 300.0


class Action(StrEnum):
    READ = "read"
    WRITE_DRAFT = "write_draft"
    CONFIRM_TICKET = "confirm_ticket"
    SIGN_MODEL = "sign_model"
    GRANT_ROLE = "grant_role"
    CHANGE_BUDGET = "change_budget"
    CHANGE_INTENT = "change_intent"
    CUT_LEDGER_MODULE = "cut_ledger_module"


ALLOWED_ROLES: dict[Action, frozenset[Role]] = {
    Action.READ: frozenset(Role),
    Action.WRITE_DRAFT: frozenset({Role.PM, Role.ANALYST, Role.TRADER}),
    Action.CONFIRM_TICKET: frozenset({Role.TRADER}),
    Action.SIGN_MODEL: frozenset({Role.QUANT}),
    Action.GRANT_ROLE: frozenset({Role.ADMIN}),
    Action.CHANGE_BUDGET: frozenset({Role.PM, Role.TRADER}),
    Action.CHANGE_INTENT: frozenset({Role.PM, Role.TRADER}),
    Action.CUT_LEDGER_MODULE: frozenset({Role.PM}),
}
# The agent reads and drafts for its user; every other action needs the human.
AGENT_ACTIONS = frozenset({Action.READ, Action.WRITE_DRAFT})
SYSTEM_ACTIONS = frozenset({Action.READ, Action.WRITE_DRAFT})
# Actions whose role assignment must cover the resource's book.
BOOK_SCOPED = frozenset(
    {Action.WRITE_DRAFT, Action.CONFIRM_TICKET, Action.CHANGE_BUDGET, Action.CHANGE_INTENT}
)


class Forbidden(Exception):
    pass


class NotFound(Exception):
    def __init__(self, kind: str, resource_id: str) -> None:
        super().__init__(f"{kind} {resource_id} not found")


@dataclass(frozen=True)
class Resource:
    tenant_id: str
    kind: str
    id: str
    book_id: str | None = None


class RoleSource(Protocol):
    def roles_of(self, tenant_id: str, user_id: str) -> Mapping[Role, frozenset[str | None]]: ...


class Authorizer:
    def __init__(self, roles: RoleSource, audit: AuditLog, clock: Callable[[], float]) -> None:
        self._roles = roles
        self._audit = audit
        self._clock = clock

    def check(
        self,
        principal: Principal,
        action: Action,
        resource: Resource,
        *,
        audit_as: str | None = None,
        extra_ids: Mapping[str, str] | None = None,
    ) -> None:
        reason = self._refusal(principal, action, resource)
        ids = {"resource_kind": resource.kind, "resource_id": resource.id, **(extra_ids or {})}
        self._audit.record(
            principal, audit_as or action.value, "refused" if reason else "allowed", ids
        )
        if reason == "other tenant":
            raise NotFound(resource.kind, resource.id)
        if reason:
            raise Forbidden(f"{action.value} refused: {reason}")

    def _refusal(self, principal: Principal, action: Action, resource: Resource) -> str | None:
        if resource.tenant_id != principal.tenant_id:
            return "other tenant"
        if principal.kind is PrincipalKind.AGENT and action not in AGENT_ACTIONS:
            return "the agent cannot take this action"
        if principal.kind is PrincipalKind.SYSTEM:
            return None if action in SYSTEM_ACTIONS else "system principal cannot take this action"
        held = self._roles.roles_of(principal.tenant_id, principal.user_id)
        books = set[str | None]().union(*(held.get(r, frozenset()) for r in ALLOWED_ROLES[action]))
        if not books:
            return "role not permitted"
        if action in BOOK_SCOPED and None not in books and resource.book_id not in books:
            return "role does not cover this book"
        if action is Action.GRANT_ROLE and resource.id == principal.user_id:
            return "cannot grant a role to yourself"
        if action is Action.CONFIRM_TICKET:
            at = principal.authenticated_at
            if principal.kind is not PrincipalKind.USER or at is None:
                return "confirm needs a signed-in user"
            if self._clock() - at > RECENT_AUTH_SECONDS:
                return "confirm needs a recent re-authentication"
        return None
