"""F&O contract rules, expiry calendar, lot sizes and daily ban list (R6, R7, R8, R108).

Governed by KTD2 (effective dates), KTD3 (expiry resolution), KTD8 (golden dates),
KTD9 (unverified limitations), and KTD12 (ban list days coverage).
"""

import importlib.resources
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

from axiom_core.authz import Refused
from axiom_core.envelope import Source

from axiom_data.calendar import TradingCalendar
from axiom_data.instruments import InstrumentStore
from axiom_data.pointintime import (
    IST,
    EffectiveDatedRow,
    LookupResult,
    NaiveTimestampRefused,
    PointInTimeTable,
    RuleUnknown,
    end_of_day_ist_utc,
    ensure_utc_aware,
    parse_csv_rule_rows,
)

WEEKDAY_NAME_TO_INT = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


class MalformedRule(Refused):
    """Raised when a rule row lacks a column the engine needs; no default is invented."""

    def __init__(self, key: str, column: str) -> None:
        super().__init__(f"malformed rule: row {key} has no usable {column} column")


def _column(row: EffectiveDatedRow, column: str) -> Any:
    try:
        return row.payload[column]
    except KeyError:
        raise MalformedRule(row.key, column) from None


def _weekday(row: EffectiveDatedRow) -> int:
    try:
        return WEEKDAY_NAME_TO_INT[_column(row, "expiry_weekday").strip().lower()]
    except (KeyError, AttributeError):
        raise MalformedRule(row.key, "expiry_weekday") from None


def _min_contract_value(row: EffectiveDatedRow) -> int:
    try:
        return int(_column(row, "min_contract_value"))
    except (ValueError, TypeError):
        raise MalformedRule(row.key, "min_contract_value") from None


@dataclass(frozen=True)
class ContractRulesResult:
    """Consolidated contract rules for an underlying and date."""

    exchange: str
    underlying: str
    on: date
    min_contract_value: int
    weekly_eligible: bool
    calendar_spread_benefit: bool
    expiry_weekdays: dict[str, str]
    position_limit_rule: str
    is_banned: bool | None
    sources: tuple[Source, ...]
    limitations: tuple[str, ...]
    is_verified: bool


class FnoRulesEngine:
    """Engine for F&O contract rules, expiry resolution, lot sizes and ban list."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        calendar: TradingCalendar | None = None,
        instruments: InstrumentStore | None = None,
    ) -> None:
        self._conn = conn
        self._instruments = instruments or InstrumentStore(conn)
        self._calendar = calendar or TradingCalendar()
        self._load_reference_tables()

    def _load_reference_tables(self) -> None:
        ref_pkg = importlib.resources.files("axiom_data.reference")

        # 1. Contract value
        cv_text = ref_pkg.joinpath("contract_value.csv").read_text(encoding="utf-8")
        self._contract_value_table = PointInTimeTable(
            "contract_value", parse_csv_rule_rows(cv_text)
        )

        # 2. Weekly eligibility
        we_text = ref_pkg.joinpath("weekly_eligibility.csv").read_text(encoding="utf-8")
        self._weekly_eligibility_table = PointInTimeTable(
            "weekly_eligibility", parse_csv_rule_rows(we_text)
        )

        # 3. Expiry margin rules
        em_text = ref_pkg.joinpath("expiry_margin_rules.csv").read_text(encoding="utf-8")
        self._expiry_margin_table = PointInTimeTable(
            "expiry_margin_rules", parse_csv_rule_rows(em_text)
        )

        # 4. Expiry rules
        er_text = ref_pkg.joinpath("expiry_rules.csv").read_text(encoding="utf-8")
        self._expiry_rules_table = PointInTimeTable("expiry_rules", parse_csv_rule_rows(er_text))

        # 5. Position limits
        pl_text = ref_pkg.joinpath("position_limits.csv").read_text(encoding="utf-8")
        self._position_limits_table = PointInTimeTable(
            "position_limits", parse_csv_rule_rows(pl_text)
        )

    def load_contracts(self, contracts: Iterable[dict[str, Any]]) -> None:
        """Write contract identity records."""
        with self._conn:
            for c in contracts:
                self._conn.execute(
                    """
                    INSERT OR REPLACE INTO contracts (
                        contract_id, underlying_id, option_type, strike, source, licence_scope
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        c["contract_id"],
                        c["underlying_id"],
                        c.get("option_type"),
                        c.get("strike"),
                        c["source"],
                        c["licence_scope"],
                    ),
                )

    def load_contract_expiries(self, expiries: Iterable[dict[str, Any]]) -> None:
        """Write contract expiry dated rows."""
        with self._conn:
            for row in expiries:
                pub = ensure_utc_aware(datetime.fromisoformat(row["published_at"]))
                rec = ensure_utc_aware(datetime.fromisoformat(row["recorded_at"]))
                eff_from = str(row["effective_from"])
                eff_to = str(row["effective_to"]) if row.get("effective_to") else None

                self._conn.execute(
                    """
                    INSERT INTO contract_expiries (
                        contract_id, expiry_date,
                        effective_from, effective_to, published_at, recorded_at,
                        source, licence_scope
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["contract_id"],
                        str(row["expiry_date"]),
                        eff_from,
                        eff_to,
                        pub.isoformat(),
                        rec.isoformat(),
                        row["source"],
                        row["licence_scope"],
                    ),
                )

    def load_contract_lots(self, lots: Iterable[dict[str, Any]]) -> None:
        """Write contract lot size dated rows."""
        with self._conn:
            for row in lots:
                pub = ensure_utc_aware(datetime.fromisoformat(row["published_at"]))
                rec = ensure_utc_aware(datetime.fromisoformat(row["recorded_at"]))
                eff_from = str(row["effective_from"])
                eff_to = str(row["effective_to"]) if row.get("effective_to") else None

                self._conn.execute(
                    """
                    INSERT INTO contract_lots (
                        contract_id, lot_size,
                        effective_from, effective_to, published_at, recorded_at,
                        source, licence_scope
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["contract_id"],
                        int(row["lot_size"]),
                        eff_from,
                        eff_to,
                        pub.isoformat(),
                        rec.isoformat(),
                        row["source"],
                        row["licence_scope"],
                    ),
                )

    def load_ban_list_days(self, days: Iterable[dict[str, Any]]) -> None:
        """Write ban list days coverage rows (KTD12)."""
        with self._conn:
            for row in days:
                pub = ensure_utc_aware(datetime.fromisoformat(row["published_at"]))
                rec = ensure_utc_aware(datetime.fromisoformat(row["recorded_at"]))
                self._conn.execute(
                    """
                    INSERT OR REPLACE INTO ban_list_days (
                        exchange, list_date, published_at, recorded_at, source, licence_scope
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["exchange"],
                        str(row["list_date"]),
                        pub.isoformat(),
                        rec.isoformat(),
                        row["source"],
                        row["licence_scope"],
                    ),
                )

    def load_ban_list(self, items: Iterable[dict[str, Any]]) -> None:
        """Write individual banned stock rows."""
        with self._conn:
            for row in items:
                self._conn.execute(
                    """
                    INSERT OR REPLACE INTO ban_list (
                        exchange, list_date, instrument_id, source, licence_scope
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        row["exchange"],
                        str(row["list_date"]),
                        row["instrument_id"],
                        row["source"],
                        row["licence_scope"],
                    ),
                )

    def load_fixtures(
        self,
        contracts_data: dict[str, Any] | None = None,
        ban_data: dict[str, Any] | None = None,
    ) -> None:
        """Load fixture data for contracts, expiries, lots and ban lists."""
        if contracts_data:
            if "contracts" in contracts_data:
                self.load_contracts(contracts_data["contracts"])
            if "expiries" in contracts_data:
                self.load_contract_expiries(contracts_data["expiries"])
            if "lots" in contracts_data:
                self.load_contract_lots(contracts_data["lots"])
        if ban_data:
            if "ban_list_days" in ban_data:
                self.load_ban_list_days(ban_data["ban_list_days"])
            if "ban_list" in ban_data:
                self.load_ban_list(ban_data["ban_list"])

    def get_contract_lot(self, contract_id: str, on: date | datetime) -> int:
        """Get lot size of contract point-in-time (R7)."""
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
            SELECT lot_size, recorded_at
            FROM contract_lots
            WHERE contract_id = ?
              AND published_at <= ?
              AND effective_from <= ?
              AND (effective_to IS NULL OR ? < effective_to)
            ORDER BY recorded_at DESC
            LIMIT 1
            """,
            (contract_id, end_of_on_utc, on_str, on_str),
        )
        row = cursor.fetchone()
        if not row:
            raise RuleUnknown(f"contract_lot:{contract_id}", on_date)
        return int(row[0])

    def get_contract_expiry(self, contract_id: str, on: date | datetime) -> date:
        """Get explicit contract expiry point-in-time (R7)."""
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
            SELECT expiry_date, recorded_at
            FROM contract_expiries
            WHERE contract_id = ?
              AND published_at <= ?
              AND effective_from <= ?
              AND (effective_to IS NULL OR ? < effective_to)
            ORDER BY recorded_at DESC
            LIMIT 1
            """,
            (contract_id, end_of_on_utc, on_str, on_str),
        )
        row = cursor.fetchone()
        if not row:
            raise RuleUnknown(f"contract_expiry:{contract_id}", on_date)
        return date.fromisoformat(row[0])

    def is_banned(self, exchange: str, instrument_id: str, on: date | datetime) -> bool:
        """Check if an underlying is in the ban list on date D (R8, KTD12)."""
        if isinstance(on, datetime):
            if on.tzinfo is None:
                raise NaiveTimestampRefused("naive timestamp is refused")
            on_date = on.astimezone(IST).date()
        else:
            on_date = on

        end_of_on_utc = end_of_day_ist_utc(on_date).isoformat()
        on_str = on_date.isoformat()

        # Check coverage in ban_list_days
        cursor_day = self._conn.execute(
            """
            SELECT exchange FROM ban_list_days
            WHERE exchange = ? AND list_date = ? AND published_at <= ?
            """,
            (exchange, on_str, end_of_on_utc),
        )
        if not cursor_day.fetchone():
            raise RuleUnknown("ban_list_days", on_date)

        cursor_ban = self._conn.execute(
            """
            SELECT instrument_id FROM ban_list
            WHERE exchange = ? AND list_date = ? AND instrument_id = ?
            """,
            (exchange, on_str, instrument_id),
        )
        return bool(cursor_ban.fetchone())

    def resolve_expiry(
        self,
        exchange: str,
        underlying: str,
        cycle: str,
        target_date: date,
        as_of: date | datetime,
    ) -> date:
        """Resolve expiry date for (exchange, underlying, cycle, target_date) as of as_of (KTD3)."""
        if isinstance(as_of, datetime):
            if as_of.tzinfo is None:
                raise NaiveTimestampRefused("naive timestamp is refused")
            as_of_date = as_of.astimezone(IST).date()
        else:
            as_of_date = as_of

        end_of_as_of_utc = end_of_day_ist_utc(as_of_date).isoformat()

        # Step 1: Check if explicit contract record exists for this period
        # Find contract matching underlying
        cursor = self._conn.execute(
            """
            SELECT ce.expiry_date, ce.recorded_at
            FROM contract_expiries ce
            JOIN contracts c ON c.contract_id = ce.contract_id
            WHERE (c.underlying_id = ? OR c.contract_id = ?)
              AND ce.published_at <= ?
              AND ce.effective_from <= ?
              AND (ce.effective_to IS NULL OR ? < ce.effective_to)
            ORDER BY ce.recorded_at DESC
            """,
            (
                underlying,
                underlying,
                end_of_as_of_utc,
                as_of_date.isoformat(),
                as_of_date.isoformat(),
            ),
        )
        candidate_contracts: list[date] = []
        for r in cursor.fetchall():
            exp_d = date.fromisoformat(r[0])
            if cycle == "weekly":
                # Matches same calendar week
                if exp_d.isocalendar()[:2] == target_date.isocalendar()[:2]:
                    candidate_contracts.append(exp_d)
            elif cycle == "monthly" and (exp_d.year, exp_d.month) == (
                target_date.year,
                target_date.month,
            ):
                candidate_contracts.append(exp_d)

        if candidate_contracts:
            return candidate_contracts[0]

        # Step 2: Rule-derived candidate expiry
        rule_key = f"{exchange}:{underlying}:{cycle}"
        fallback_key = f"{exchange}:ALL:{cycle}"

        # Evaluate candidate weekday
        if cycle == "weekly":
            # Start from Monday of target week
            monday = target_date - timedelta(days=target_date.weekday())
            # Find candidate day by probing rules across days of this week
            # First probe Thursday / Tuesday based on rules at target_date
            res_rule = self._resolve_expiry_rule(rule_key, fallback_key, target_date)
            target_weekday_int = _weekday(res_rule.value)
            candidate_d = monday + timedelta(days=target_weekday_int)
            # Re-check rule at candidate date
            res_cand = self._resolve_expiry_rule(rule_key, fallback_key, candidate_d)
            cand_weekday_int = _weekday(res_cand.value)
            candidate_d = monday + timedelta(days=cand_weekday_int)

            # Check weekly eligibility on candidate date
            we_key = f"{exchange}:{underlying}"
            we_res = self._weekly_eligibility_table.resolve(we_key, candidate_d)
            if we_res.value.payload.get("weekly_eligible") == "false":
                raise Refused(f"weekly expiry not eligible for {underlying} on {candidate_d}")

        elif cycle == "monthly":
            # Last weekday of target month
            # Go to last day of target month
            year = target_date.year
            month = target_date.month
            next_month_first = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
            last_day_of_month = next_month_first - timedelta(days=1)

            res_month = self._resolve_expiry_rule(rule_key, fallback_key, last_day_of_month)
            weekday_int = _weekday(res_month.value)

            # Find last occurrence of weekday_int in target month
            curr = last_day_of_month
            while curr.weekday() != weekday_int:
                curr -= timedelta(days=1)
            candidate_d = curr
        else:
            raise ValueError(f"unsupported cycle: {cycle}")

        # Step 3: Shift if holiday/non-regular session day
        segment = "fno"
        return self._calendar.previous_regular_session_day(segment, candidate_d)

    def _resolve_expiry_rule(self, key: str, fallback_key: str, on_date: date) -> Any:
        try:
            return self._expiry_rules_table.resolve(key, on_date)
        except RuleUnknown:
            return self._expiry_rules_table.resolve(fallback_key, on_date)

    def get_contract_rules(
        self, exchange: str, underlying: str, on: date | datetime
    ) -> ContractRulesResult:
        """Fetch all contract rules in force on date D (R6)."""
        if isinstance(on, datetime):
            if on.tzinfo is None:
                raise NaiveTimestampRefused("naive timestamp is refused")
            on_date = on.astimezone(IST).date()
        else:
            on_date = on

        sources: list[Source] = []
        is_verified = True
        limitations: list[str] = []

        # 1. Contract value
        cv_key = f"{exchange}:{underlying}"
        try:
            cv_res = self._contract_value_table.resolve(cv_key, on_date)
        except RuleUnknown:
            cv_res = self._contract_value_table.resolve(f"{exchange}:ALL", on_date)
        min_contract_value = _min_contract_value(cv_res.value)
        sources.extend(cv_res.sources)
        if not cv_res.is_verified:
            is_verified = False

        # 2. Weekly eligibility
        we_key = f"{exchange}:{underlying}"
        we_res = None
        try:
            we_res = self._weekly_eligibility_table.resolve(we_key, on_date)
            weekly_eligible = we_res.value.payload.get("weekly_eligible") == "true"
            sources.extend(we_res.sources)
            if not we_res.is_verified:
                is_verified = False
        except RuleUnknown:
            weekly_eligible = False
            limitations.append(f"weekly eligibility unknown for {exchange}:{underlying}")

        # 3. Expiry margin
        em_key = f"{exchange}:ALL"
        em_res = self._expiry_margin_table.resolve(em_key, on_date)
        cal_spread = em_res.value.payload.get("calendar_spread_benefit") == "true"
        sources.extend(em_res.sources)
        if not em_res.is_verified:
            is_verified = False

        # 4. Expiry weekdays
        expiry_weekdays: dict[str, str] = {}
        expiry_results: list[LookupResult[EffectiveDatedRow]] = []
        for cycle in ("weekly", "monthly"):
            if cycle == "weekly" and not weekly_eligible:
                continue
            try:
                res_w = self._expiry_rules_table.resolve(
                    f"{exchange}:{underlying}:{cycle}", on_date
                )
            except RuleUnknown:
                res_w = self._expiry_rules_table.resolve(f"{exchange}:ALL:{cycle}", on_date)
            expiry_results.append(res_w)
            _weekday(res_w.value)  # refuse a blank or misspelt weekday
            expiry_weekdays[cycle] = _column(res_w.value, "expiry_weekday").strip().capitalize()
            sources.extend(res_w.sources)
            if not res_w.is_verified:
                is_verified = False

        # 5. Position limits
        # Index underlyings are the ones with weekly-eligibility rows; others have no INDEX rule.
        pl_res = None
        pos_limit = ""
        try:
            pl_res = self._position_limits_table.resolve(f"{exchange}:{underlying}", on_date)
        except RuleUnknown:
            if self._weekly_eligibility_table.has_key(we_key):
                pl_res = self._position_limits_table.resolve(f"{exchange}:INDEX", on_date)
            else:
                limitations.append(f"no position limit rule for {exchange}:{underlying}")
        if pl_res is not None:
            pos_limit = str(pl_res.value.payload.get("position_limit_rule", ""))
            sources.extend(pl_res.sources)
            if not pl_res.is_verified:
                is_verified = False

        # 6. Ban status
        # The ban list is keyed by instrument id, so map the underlying symbol first.
        banned: bool | None = None
        inst = self._instruments.resolve_identifier("symbol", underlying, on_date)
        if inst is None:
            limitations.append(f"ban status unknown: no instrument id for {underlying}")
        else:
            try:
                banned = self.is_banned(exchange, inst.instrument_id, on_date)
            except RuleUnknown:
                banned = None

        if not is_verified and "unverified rule" not in limitations:
            limitations.append("unverified rule")

        for res in (cv_res, we_res, em_res, *expiry_results, pl_res):
            if res is not None:
                for lim in res.limitations:
                    if lim not in limitations:
                        limitations.append(lim)

        # De-duplicate sources
        seen: set[tuple[str, str]] = set()
        uniq_sources: list[Source] = []
        for s in sources:
            key_s = (s.name, s.licence_scope)
            if key_s not in seen:
                seen.add(key_s)
                uniq_sources.append(s)

        return ContractRulesResult(
            exchange=exchange,
            underlying=underlying,
            on=on_date,
            min_contract_value=min_contract_value,
            weekly_eligible=weekly_eligible,
            calendar_spread_benefit=cal_spread,
            expiry_weekdays=expiry_weekdays,
            position_limit_rule=pos_limit,
            is_banned=banned,
            sources=tuple(uniq_sources),
            limitations=tuple(limitations),
            is_verified=is_verified,
        )
