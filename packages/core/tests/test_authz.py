import itertools

import pytest
from axiom_core.audit import AuditLog
from axiom_core.authz import RECENT_AUTH_SECONDS, Action, Authorizer, Forbidden, NotFound, Resource
from axiom_core.session import SessionStore
from axiom_core.tenancy import Directory, Principal, PrincipalKind, Role
from conftest import Clock, mfa_claims

BOOK_ALPHA = Resource("desk", "book", "alpha", book_id="alpha")


def user(directory: Directory, name: str, clock: Clock) -> Principal:
    return directory.principal("desk", name, authenticated_at=clock.now)


def test_analyst_reads_a_book_in_their_tenant(
    authz: Authorizer, directory: Directory, clock: Clock
) -> None:
    authz.check(user(directory, "ana", clock), Action.READ, BOOK_ALPHA)


def test_cross_tenant_access_is_not_found_with_no_existence_leak(
    authz: Authorizer, directory: Directory, clock: Clock
) -> None:
    other = Resource("broker-b", "watchlist", "w-77")
    with pytest.raises(NotFound) as cross:
        authz.check(user(directory, "ana", clock), Action.READ, other)
    assert "broker-b" not in str(cross.value)
    assert str(cross.value) == str(NotFound("watchlist", "w-77"))


def test_analyst_cannot_sign_a_model_spec_and_a_quant_can(
    authz: Authorizer, directory: Directory, clock: Clock
) -> None:
    spec = Resource("desk", "model_spec", "surface")
    with pytest.raises(Forbidden):
        authz.check(user(directory, "ana", clock), Action.SIGN_MODEL, spec)
    authz.check(user(directory, "quinn", clock), Action.SIGN_MODEL, spec)


def test_agent_acting_for_a_trader_cannot_confirm(
    authz: Authorizer, sessions: SessionStore
) -> None:
    token = sessions.sign_in(mfa_claims("desk", "tara"))
    with pytest.raises(Forbidden):
        authz.check(sessions.agent_principal(token), Action.CONFIRM_TICKET, BOOK_ALPHA)
    authz.check(sessions.resolve(token), Action.CONFIRM_TICKET, BOOK_ALPHA)


def test_only_the_books_own_trader_confirms(
    authz: Authorizer, directory: Directory, clock: Clock
) -> None:
    tara = user(directory, "tara", clock)
    with pytest.raises(Forbidden):
        authz.check(tara, Action.CONFIRM_TICKET, Resource("desk", "book", "beta", book_id="beta"))


def test_confirm_needs_recent_reauthentication(
    authz: Authorizer, sessions: SessionStore, clock: Clock
) -> None:
    token = sessions.sign_in(mfa_claims("desk", "tara"))
    clock.now += RECENT_AUTH_SECONDS + 1
    with pytest.raises(Forbidden):
        authz.check(sessions.resolve(token), Action.CONFIRM_TICKET, BOOK_ALPHA)
    sessions.reauthenticate(token, mfa_claims("desk", "tara"))
    authz.check(sessions.resolve(token), Action.CONFIRM_TICKET, BOOK_ALPHA)


def test_admin_cannot_grant_themselves_a_role_and_the_attempt_is_audited(
    directory: Directory, audit: AuditLog
) -> None:
    admin = directory.principal("desk", "ada")
    with pytest.raises(Forbidden):
        directory.grant(admin, "desk", "ada", Role.QUANT)
    assert Role.QUANT not in directory.roles_of("desk", "ada")
    last = audit.records()[-1]
    assert (last.action, last.verdict, last.user_id) == ("grant_role", "refused", "ada")
    assert last.ids["target_user"] == "ada"


def test_role_grants_and_revocations_are_audited_with_the_granting_principal(
    directory: Directory, audit: AuditLog
) -> None:
    admin = directory.principal("desk", "ada")
    directory.grant(admin, "desk", "ana", Role.QUANT)
    directory.revoke(admin, "desk", "ana", Role.QUANT)
    grant, revoke = audit.records()[-2:]
    assert (grant.action, grant.user_id, grant.ids["target_user"], grant.ids["role"]) == (
        "grant_role",
        "ada",
        "ana",
        "quant",
    )
    assert (revoke.action, revoke.verdict) == ("revoke_role", "allowed")
    assert Role.QUANT not in directory.roles_of("desk", "ana")


def test_non_admin_cannot_grant(directory: Directory) -> None:
    with pytest.raises(Forbidden):
        directory.grant(
            directory.principal("desk", "pam"), "desk", "ana", Role.TRADER, book_id="alpha"
        )


def test_each_decision_writes_exactly_one_audit_record(
    authz: Authorizer, directory: Directory, audit: AuditLog, clock: Clock
) -> None:
    before = len(audit.records())
    authz.check(user(directory, "ana", clock), Action.READ, BOOK_ALPHA)
    with pytest.raises(Forbidden):
        authz.check(
            user(directory, "ana", clock), Action.SIGN_MODEL, Resource("desk", "model_spec", "s")
        )
    after = audit.records()[before:]
    assert [(r.action, r.verdict, r.ids["resource_id"]) for r in after] == [
        ("read", "allowed", "alpha"),
        ("sign_model", "refused", "s"),
    ]


# The plan's role table, written out independently of the code under test.
ALLOWED_ROLES: dict[Action, set[Role]] = {
    Action.READ: set(Role),
    Action.WRITE_DRAFT: {Role.PM, Role.ANALYST, Role.TRADER},
    Action.CONFIRM_TICKET: {Role.TRADER},
    Action.SIGN_MODEL: {Role.QUANT},
    Action.GRANT_ROLE: {Role.ADMIN},
    Action.CHANGE_BUDGET: {Role.PM, Role.TRADER},
    Action.CHANGE_INTENT: {Role.PM, Role.TRADER},
    Action.CUT_LEDGER_MODULE: {Role.PM},
}
AGENT_MAY = {Action.READ, Action.WRITE_DRAFT}


def test_every_role_and_principal_pair_matches_the_role_table(
    authz: Authorizer, directory: Directory, clock: Clock
) -> None:
    assert set(ALLOWED_ROLES) == set(Action)
    admin = directory.principal("desk", "ada")
    for role in Role:
        name = f"probe-{role}"
        if role is not Role.ADMIN:
            directory.grant(
                admin, "desk", name, role, book_id="alpha" if role is Role.TRADER else None
            )
        else:
            directory.bootstrap_admin("desk", name)
    for role, kind, action in itertools.product(Role, PrincipalKind, Action):
        if kind is PrincipalKind.SYSTEM:
            continue
        name = f"probe-{role}"
        principal = directory.principal("desk", name, authenticated_at=clock.now, kind=kind)
        target = Resource("desk", "user", "someone-else", book_id="alpha")
        expected = role in ALLOWED_ROLES[action] and (
            kind is PrincipalKind.USER or action in AGENT_MAY
        )
        try:
            authz.check(principal, action, target)
            allowed = True
        except Forbidden:
            allowed = False
        assert allowed == expected, (role, kind, action)


# Actions that check the resource's book, written out independently of the code under test.
BOOK_SCOPED = {
    Action.WRITE_DRAFT,
    Action.CONFIRM_TICKET,
    Action.CHANGE_BUDGET,
    Action.CHANGE_INTENT,
}


def test_only_roles_whose_actions_check_the_book_can_be_granted_for_one_book(
    directory: Directory,
) -> None:
    admin = directory.principal("desk", "ada")
    book_roles = {r for a in BOOK_SCOPED for r in ALLOWED_ROLES[a]}
    for role in Role:
        name = f"booked-{role}"
        if role in book_roles:
            directory.grant(admin, "desk", name, role, book_id="alpha")
            assert directory.roles_of("desk", name) == {role: frozenset({"alpha"})}
        else:
            # the book would not limit this role's actions, so it would act tenant-wide
            with pytest.raises(ValueError, match=role.value):
                directory.grant(admin, "desk", name, role, book_id="alpha")
            assert not directory.has_user("desk", name)
