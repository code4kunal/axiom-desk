from dataclasses import dataclass
from enum import StrEnum


class Role(StrEnum):
    PM = "pm"
    ANALYST = "analyst"
    TRADER = "trader"
    QUANT = "quant"
    ADMIN = "admin"


class PrincipalKind(StrEnum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


@dataclass(frozen=True)
class Principal:
    kind: PrincipalKind
    tenant_id: str
    user_id: str
    authenticated_at: float | None = None
