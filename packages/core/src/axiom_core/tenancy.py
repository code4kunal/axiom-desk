"""Tenants, books and role assignments. Role changes are authorized and audited."""

from collections.abc import Mapping

from axiom_core.audit import AuditLog
from axiom_core.authz import Action, Authorizer, Resource
from axiom_core.db import Connection
from axiom_core.principals import Principal, PrincipalKind, Role

__all__ = ["Directory", "Principal", "PrincipalKind", "Role"]


class Directory:
    def __init__(self, conn: Connection, audit: AuditLog) -> None:
        self._conn = conn
        self._audit = audit
        self._authz = Authorizer(self, audit, audit.clock)

    def add_book(self, tenant_id: str, book_id: str) -> None:
        with self._conn:
            self._conn.execute("INSERT INTO books VALUES (?, ?)", (tenant_id, book_id))

    def roles_of(self, tenant_id: str, user_id: str) -> Mapping[Role, frozenset[str | None]]:
        rows = self._conn.execute(
            "SELECT role, book_id FROM role_assignments WHERE tenant_id = ? AND user_id = ?",
            (tenant_id, user_id),
        ).fetchall()
        out: dict[Role, set[str | None]] = {}
        for role, book in rows:
            out.setdefault(Role(role), set()).add(book or None)
        return {role: frozenset(books) for role, books in out.items()}

    def has_user(self, tenant_id: str, user_id: str) -> bool:
        return bool(self.roles_of(tenant_id, user_id))

    def principal(
        self,
        tenant_id: str,
        user_id: str,
        *,
        authenticated_at: float | None = None,
        kind: PrincipalKind = PrincipalKind.USER,
    ) -> Principal:
        return Principal(kind, tenant_id, user_id, authenticated_at)

    def bootstrap_admin(self, tenant_id: str, user_id: str) -> None:
        """Create a tenant's first admin. Recorded as a system action."""
        system = Principal(PrincipalKind.SYSTEM, tenant_id, "system")
        self._write_role(tenant_id, user_id, Role.ADMIN, None, insert=True)
        self._audit.record(
            system, "grant_role", "allowed", {"target_user": user_id, "role": Role.ADMIN.value}
        )

    def grant(
        self, by: Principal, tenant_id: str, user_id: str, role: Role, *, book_id: str | None = None
    ) -> None:
        self._check_role_change(by, tenant_id, user_id, role, book_id, "grant_role")
        self._write_role(tenant_id, user_id, role, book_id, insert=True)

    def revoke(
        self, by: Principal, tenant_id: str, user_id: str, role: Role, *, book_id: str | None = None
    ) -> None:
        self._check_role_change(by, tenant_id, user_id, role, book_id, "revoke_role")
        self._write_role(tenant_id, user_id, role, book_id, insert=False)

    def _check_role_change(
        self,
        by: Principal,
        tenant_id: str,
        user_id: str,
        role: Role,
        book_id: str | None,
        verb: str,
    ) -> None:
        ids = {"target_user": user_id, "role": role.value}
        if book_id:
            ids["book_id"] = book_id
        self._authz.check(
            by,
            Action.GRANT_ROLE,
            Resource(tenant_id, "user", user_id),
            audit_as=verb,
            extra_ids=ids,
        )

    def _write_role(
        self, tenant_id: str, user_id: str, role: Role, book_id: str | None, *, insert: bool
    ) -> None:
        sql = (
            "INSERT OR IGNORE INTO role_assignments VALUES (?, ?, ?, ?)"
            if insert
            else "DELETE FROM role_assignments"
            " WHERE tenant_id = ? AND user_id = ? AND role = ? AND book_id = ?"
        )
        with self._conn:
            self._conn.execute(sql, (tenant_id, user_id, role.value, book_id or ""))
