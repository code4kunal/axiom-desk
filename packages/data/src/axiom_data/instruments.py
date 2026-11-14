"""Instruments, asset-class roles, and basket/order eligibility (R1, R2, R3, R14).

Governed by KTD1 (records DB for dynamic data), KTD2 (point-in-time lookup),
KTD7 (licence scope tracking), and platform R7, R8, AE2.
"""

import importlib.resources
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from axiom_data.pointintime import (
    IST,
    NaiveTimestampRefused,
    PointInTimeTable,
    end_of_day_ist_utc,
    ensure_utc_aware,
    parse_csv_rule_rows,
)


@dataclass(frozen=True)
class Instrument:
    """Identity record for an instrument."""

    instrument_id: str
    asset_class: str
    kind: str
    exchange: str
    name: str
    source: str
    licence_scope: str

    def __post_init__(self) -> None:
        if not self.instrument_id:
            raise ValueError("instrument_id must be non-empty")
        if not self.source:
            raise ValueError("source must be non-empty")
        if not self.licence_scope:
            raise ValueError("licence_scope must be non-empty")


@dataclass(frozen=True)
class RoleResult:
    """Resolved instrument role on a date."""

    role: str
    source: str
    licence_scope: str
    is_verified: bool = True
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True)
class Eligibility:
    """Eligibility decision for basket membership or order execution (R2, AE2)."""

    status: str  # "allowed", "conditional", "refused"
    condition: str | None = None
    reason: str | None = None
    suggestions: tuple[str, ...] = ()
    role: str = ""


class InstrumentStore:
    """Store for instruments, identifiers, role overrides and tracking links."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._role_table = self._load_asset_class_roles()

    @classmethod
    def _load_asset_class_roles(cls) -> PointInTimeTable:
        ref_pkg = importlib.resources.files("axiom_data.reference")
        csv_text = ref_pkg.joinpath("asset_class_roles.csv").read_text(encoding="utf-8")
        rows = parse_csv_rule_rows(csv_text, key_field="asset_class")
        return PointInTimeTable("asset_class_roles", rows)

    def load_instruments(self, instruments: Iterable[Instrument | dict[str, Any]]) -> None:
        """Write instrument identity records."""
        with self._conn:
            for item in instruments:
                inst = item if isinstance(item, Instrument) else Instrument(**item)
                self._conn.execute(
                    """
                    INSERT OR REPLACE INTO instruments (
                        instrument_id, asset_class, kind, exchange, name, source, licence_scope
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        inst.instrument_id,
                        inst.asset_class,
                        inst.kind,
                        inst.exchange,
                        inst.name,
                        inst.source,
                        inst.licence_scope,
                    ),
                )

    def load_identifiers(self, identifiers: Iterable[dict[str, Any]]) -> None:
        """Write effective-dated identifier rows."""
        with self._conn:
            for row in identifiers:
                if not row.get("source"):
                    raise ValueError("source is required")
                if not row.get("licence_scope"):
                    raise ValueError("licence_scope is required")

                pub = ensure_utc_aware(datetime.fromisoformat(row["published_at"]))
                rec = ensure_utc_aware(datetime.fromisoformat(row["recorded_at"]))
                eff_from = str(row["effective_from"])
                eff_to = str(row["effective_to"]) if row.get("effective_to") else None

                self._conn.execute(
                    """
                    INSERT INTO instrument_identifiers (
                        instrument_id, identifier_type, value,
                        effective_from, effective_to, published_at, recorded_at,
                        source, licence_scope
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["instrument_id"],
                        row["identifier_type"],
                        row["value"],
                        eff_from,
                        eff_to,
                        pub.isoformat(),
                        rec.isoformat(),
                        row["source"],
                        row["licence_scope"],
                    ),
                )

    def load_roles(self, roles: Iterable[dict[str, Any]]) -> None:
        """Write effective-dated role override rows."""
        with self._conn:
            for row in roles:
                if not row.get("source"):
                    raise ValueError("source is required")
                if not row.get("licence_scope"):
                    raise ValueError("licence_scope is required")

                pub = ensure_utc_aware(datetime.fromisoformat(row["published_at"]))
                rec = ensure_utc_aware(datetime.fromisoformat(row["recorded_at"]))
                eff_from = str(row["effective_from"])
                eff_to = str(row["effective_to"]) if row.get("effective_to") else None

                self._conn.execute(
                    """
                    INSERT INTO instrument_roles (
                        instrument_id, role,
                        effective_from, effective_to, published_at, recorded_at,
                        source, licence_scope
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["instrument_id"],
                        row["role"],
                        eff_from,
                        eff_to,
                        pub.isoformat(),
                        rec.isoformat(),
                        row["source"],
                        row["licence_scope"],
                    ),
                )

    def load_tracks(self, tracks: Iterable[dict[str, Any]]) -> None:
        """Write effective-dated tracking relation rows."""
        with self._conn:
            for row in tracks:
                if not row.get("source"):
                    raise ValueError("source is required")
                if not row.get("licence_scope"):
                    raise ValueError("licence_scope is required")

                pub = ensure_utc_aware(datetime.fromisoformat(row["published_at"]))
                rec = ensure_utc_aware(datetime.fromisoformat(row["recorded_at"]))
                eff_from = str(row["effective_from"])
                eff_to = str(row["effective_to"]) if row.get("effective_to") else None

                self._conn.execute(
                    """
                    INSERT INTO instrument_tracks (
                        instrument_id, tracked_instrument_id,
                        effective_from, effective_to, published_at, recorded_at,
                        source, licence_scope
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["instrument_id"],
                        row["tracked_instrument_id"],
                        eff_from,
                        eff_to,
                        pub.isoformat(),
                        rec.isoformat(),
                        row["source"],
                        row["licence_scope"],
                    ),
                )

    def load_fixture_data(self, data: dict[str, Any]) -> None:
        """Load fixture instruments, identifiers, roles and tracks."""
        if "instruments" in data:
            self.load_instruments(data["instruments"])
        if "identifiers" in data:
            self.load_identifiers(data["identifiers"])
        if "roles" in data:
            self.load_roles(data["roles"])
        if "tracks" in data:
            self.load_tracks(data["tracks"])

    def get_instrument(self, instrument_id: str) -> Instrument | None:
        """Fetch instrument identity by ID."""
        cursor = self._conn.execute(
            """
            SELECT instrument_id, asset_class, kind, exchange, name, source, licence_scope
            FROM instruments WHERE instrument_id = ?
            """,
            (instrument_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return Instrument(
            instrument_id=row[0],
            asset_class=row[1],
            kind=row[2],
            exchange=row[3],
            name=row[4],
            source=row[5],
            licence_scope=row[6],
        )

    def resolve_identifier(
        self, identifier_type: str, value: str, on: date | datetime
    ) -> Instrument | None:
        """Resolve identifier to instrument identity point-in-time (KTD2)."""
        if isinstance(on, datetime):
            if on.tzinfo is None:
                raise NaiveTimestampRefused("naive timestamp is refused")
            on_date = on.astimezone(IST).date()
        else:
            on_date = on

        end_of_on_utc = end_of_day_ist_utc(on_date).isoformat()
        on_str = on_date.isoformat()

        cursor = self._conn.execute(
            """
            SELECT instrument_id, published_at, recorded_at
            FROM instrument_identifiers
            WHERE identifier_type = ? AND value = ?
              AND published_at <= ?
              AND effective_from <= ?
              AND (effective_to IS NULL OR ? < effective_to)
            ORDER BY recorded_at DESC
            LIMIT 1
            """,
            (identifier_type, value, end_of_on_utc, on_str, on_str),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return self.get_instrument(row[0])

    def get_role(self, instrument: Instrument, on: date | datetime) -> RoleResult:
        """Resolve instrument role on date: override row wins, else asset-class default."""
        if isinstance(on, datetime):
            if on.tzinfo is None:
                raise NaiveTimestampRefused("naive timestamp is refused")
            on_date = on.astimezone(IST).date()
        else:
            on_date = on

        end_of_on_utc = end_of_day_ist_utc(on_date).isoformat()
        on_str = on_date.isoformat()

        # Check DB overrides
        cursor = self._conn.execute(
            """
            SELECT role, source, licence_scope, recorded_at
            FROM instrument_roles
            WHERE instrument_id = ?
              AND published_at <= ?
              AND effective_from <= ?
              AND (effective_to IS NULL OR ? < effective_to)
            ORDER BY recorded_at DESC
            LIMIT 1
            """,
            (instrument.instrument_id, end_of_on_utc, on_str, on_str),
        )
        row = cursor.fetchone()
        if row:
            return RoleResult(role=row[0], source=row[1], licence_scope=row[2])

        # Resolve asset-class default
        res = self._role_table.resolve(instrument.asset_class, on_date)
        role_str = str(res.value.payload.get("role", "out of scope"))
        return RoleResult(
            role=role_str,
            source=res.value.source,
            licence_scope=res.value.licence_scope,
            is_verified=res.is_verified,
            limitations=res.limitations,
        )

    def get_tracking_investables(
        self, tracked_instrument_id: str, on: date | datetime
    ) -> list[str]:
        """Find investable instruments tracking the given instrument on date D."""
        if isinstance(on, datetime):
            if on.tzinfo is None:
                raise NaiveTimestampRefused("naive timestamp is refused")
            on_date = on.astimezone(IST).date()
        else:
            on_date = on

        end_of_on_utc = end_of_day_ist_utc(on_date).isoformat()
        on_str = on_date.isoformat()

        # Find tracking rows
        cursor = self._conn.execute(
            """
            SELECT instrument_id, recorded_at
            FROM instrument_tracks
            WHERE tracked_instrument_id = ?
              AND published_at <= ?
              AND effective_from <= ?
              AND (effective_to IS NULL OR ? < effective_to)
            ORDER BY recorded_at DESC
            """,
            (tracked_instrument_id, end_of_on_utc, on_str, on_str),
        )
        candidates: dict[str, str] = {}
        for row in cursor.fetchall():
            inst_id = row[0]
            if inst_id not in candidates:
                candidates[inst_id] = row[1]

        investables: list[str] = []
        for inst_id in candidates:
            inst = self.get_instrument(inst_id)
            if inst:
                r = self.get_role(inst, on_date)
                if r.role in ("basket-eligible", "investable while open to inflows"):
                    investables.append(inst_id)
        return investables

    def check_eligibility(
        self, instrument: Instrument, purpose: str, on: date | datetime
    ) -> Eligibility:
        """Evaluate eligibility for basket member or order draft leg (R2, AE2)."""
        role_res = self.get_role(instrument, on)
        role = role_res.role

        # Checked first: later branches allow by default, which a typo must not reach.
        if purpose not in ("basket_member", "order_draft_leg", "basket_tracking_member"):
            return Eligibility(status="refused", reason=f"unknown purpose: {purpose}", role=role)

        if role == "analysis-only":
            suggestions = self.get_tracking_investables(instrument.instrument_id, on)
            return Eligibility(
                status="refused",
                reason="analysis-only",
                suggestions=tuple(suggestions),
                role=role,
            )

        if role == "out of scope":
            return Eligibility(status="refused", reason="out of scope", role=role)

        if role == "broker-executable only":
            if purpose in ("basket_member", "order_draft_leg"):
                return Eligibility(
                    status="conditional",
                    condition="broker execution",
                    role=role,
                )
            return Eligibility(status="allowed", role=role)

        if role == "tracking only":
            if purpose == "basket_tracking_member":
                return Eligibility(status="allowed", role=role)
            return Eligibility(status="refused", reason="tracking only", role=role)

        if role == "investable while open to inflows":
            return Eligibility(status="allowed", role=role)

        if role == "closed to inflows":
            return Eligibility(status="refused", reason="closed to inflows", role=role)

        if role == "basket-eligible":
            return Eligibility(status="allowed", role=role)

        return Eligibility(status="refused", reason=f"unsupported role: {role}", role=role)
