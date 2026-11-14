"""Corporate actions and adjusted price/volume history (R3, R11, R12, R13, R14).

Governed by KTD4 (two-integer ratios), KTD7 (licence scope), and KTD10 (action versioning).
"""

import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from axiom_core.envelope import Source

from axiom_data.pointintime import (
    IST,
    NaiveTimestampRefused,
    end_of_day_ist_utc,
    ensure_utc_aware,
)


@dataclass(frozen=True)
class Bar:
    """OHLCV market data bar."""

    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class CorporateAction:
    """Versioned corporate action record (KTD10)."""

    action_id: str
    recorded_at: datetime
    instrument_id: str
    type: str  # "split", "bonus", "dividend", "rights", "merger", "demerger"
    status: str  # "active", "cancelled"
    ex_date: date
    from_qty: int | None = None
    to_qty: int | None = None
    amount: str | None = None
    published_at: datetime | None = None
    source: str = ""
    licence_scope: str = "public"

    def __post_init__(self) -> None:
        if not self.action_id:
            raise ValueError("action_id must be non-empty")
        if not self.source:
            raise ValueError("source must be non-empty")
        if not self.licence_scope:
            raise ValueError("licence_scope must be non-empty")
        if self.from_qty is not None and self.from_qty <= 0:
            raise ValueError(f"from_qty must be positive, got {self.from_qty}")
        if self.to_qty is not None and self.to_qty <= 0:
            raise ValueError(f"to_qty must be positive, got {self.to_qty}")


@dataclass(frozen=True)
class AdjustedHistoryResult:
    """Adjusted price/volume series carrying limitations and sources."""

    bars: list[Bar]
    limitations: tuple[str, ...]
    sources: tuple[Source, ...]


class CorporateActionAdjuster:
    """Adjuster for stock price/volume history point-in-time."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def load_corporate_actions(self, actions: Iterable[dict[str, Any] | CorporateAction]) -> None:
        """Write versioned corporate actions into records DB."""
        with self._conn:
            for item in actions:
                if isinstance(item, CorporateAction):
                    act = item
                else:
                    pub = ensure_utc_aware(datetime.fromisoformat(item["published_at"]))
                    rec = ensure_utc_aware(datetime.fromisoformat(item["recorded_at"]))
                    ex_d = (
                        date.fromisoformat(item["ex_date"])
                        if isinstance(item["ex_date"], str)
                        else item["ex_date"]
                    )
                    act = CorporateAction(
                        action_id=item["action_id"],
                        recorded_at=rec,
                        instrument_id=item["instrument_id"],
                        type=item["type"],
                        status=item.get("status", "active"),
                        ex_date=ex_d,
                        from_qty=item.get("from_qty"),
                        to_qty=item.get("to_qty"),
                        amount=item.get("amount"),
                        published_at=pub,
                        source=item["source"],
                        licence_scope=item.get("licence_scope", "public"),
                    )

                pub_iso = act.published_at.isoformat() if act.published_at else ""
                self._conn.execute(
                    """
                    INSERT OR REPLACE INTO corporate_actions (
                        action_id, recorded_at, instrument_id, type, status,
                        ex_date, from_qty, to_qty, amount, published_at,
                        source, licence_scope
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        act.action_id,
                        act.recorded_at.isoformat(),
                        act.instrument_id,
                        act.type,
                        act.status,
                        act.ex_date.isoformat(),
                        act.from_qty,
                        act.to_qty,
                        act.amount,
                        pub_iso,
                        act.source,
                        act.licence_scope,
                    ),
                )

    def get_actions_as_of(
        self, instrument_id: str, as_of: date | datetime
    ) -> list[CorporateAction]:
        """Fetch effective corporate actions for instrument as of date D (KTD10)."""
        if isinstance(as_of, datetime):
            if as_of.tzinfo is None:
                raise NaiveTimestampRefused("naive timestamp is refused")
            as_of_date = as_of.astimezone(IST).date()
        else:
            as_of_date = as_of

        end_of_as_of_utc = end_of_day_ist_utc(as_of_date).isoformat()

        # Group by action_id, select latest recorded_at published by end of D
        cursor = self._conn.execute(
            """
            SELECT action_id, recorded_at, instrument_id, type, status,
                   ex_date, from_qty, to_qty, amount, published_at,
                   source, licence_scope
            FROM corporate_actions
            WHERE instrument_id = ?
              AND published_at <= ?
            ORDER BY recorded_at DESC
            """,
            (instrument_id, end_of_as_of_utc),
        )

        latest_versions: dict[str, CorporateAction] = {}
        for row in cursor.fetchall():
            act_id = row[0]
            if act_id not in latest_versions:
                latest_versions[act_id] = CorporateAction(
                    action_id=row[0],
                    recorded_at=datetime.fromisoformat(row[1]),
                    instrument_id=row[2],
                    type=row[3],
                    status=row[4],
                    ex_date=date.fromisoformat(row[5]),
                    from_qty=row[6],
                    to_qty=row[7],
                    amount=row[8],
                    published_at=datetime.fromisoformat(row[9]),
                    source=row[10],
                    licence_scope=row[11],
                )

        # Filter: active only, ex_date <= as_of_date
        effective_actions = [
            a for a in latest_versions.values() if a.status == "active" and a.ex_date <= as_of_date
        ]
        effective_actions.sort(key=lambda a: a.ex_date)
        return effective_actions

    def adjust_bars(
        self,
        instrument_id: str,
        bars: list[Bar],
        as_of: date | datetime,
        total_return: bool = False,
    ) -> AdjustedHistoryResult:
        """Apply corporate actions to price and volume series as of date D (R11, R12)."""
        actions = self.get_actions_as_of(instrument_id, as_of)
        res_bars = list(bars)
        limitations: list[str] = []
        sources: list[Source] = []

        for action in actions:
            sources.append(Source(name=action.source, licence_scope=action.licence_scope))

            if action.type in ("split", "bonus"):
                from_q = action.from_qty or 1
                to_q = action.to_qty or 1
                price_factor = from_q / to_q
                vol_factor = to_q / from_q

                for i, b in enumerate(res_bars):
                    if b.date < action.ex_date:
                        res_bars[i] = Bar(
                            date=b.date,
                            open=b.open * price_factor,
                            high=b.high * price_factor,
                            low=b.low * price_factor,
                            close=b.close * price_factor,
                            volume=b.volume * vol_factor,
                        )

            elif action.type == "dividend":
                if total_return:
                    prior_bars = [b for b in res_bars if b.date < action.ex_date]
                    if not prior_bars:
                        limitations.append(
                            f"total-return dividend on {action.ex_date} skipped: "
                            "no prior close bar available"
                        )
                    else:
                        prior_close = prior_bars[-1].close
                        amount_flt = float(action.amount or "0")
                        div_factor = 1.0 - (amount_flt / prior_close)
                        for i, b in enumerate(res_bars):
                            if b.date < action.ex_date:
                                res_bars[i] = Bar(
                                    date=b.date,
                                    open=b.open * div_factor,
                                    high=b.high * div_factor,
                                    low=b.low * div_factor,
                                    close=b.close * div_factor,
                                    volume=b.volume,
                                )

            elif action.type in ("rights", "merger", "demerger"):
                limitations.append(f"unhandled corporate action: {action.type} on {action.ex_date}")

        # De-duplicate sources
        seen: set[tuple[str, str]] = set()
        uniq_sources: list[Source] = []
        for s in sources:
            key_s = (s.name, s.licence_scope)
            if key_s not in seen:
                seen.add(key_s)
                uniq_sources.append(s)

        return AdjustedHistoryResult(
            bars=res_bars,
            limitations=tuple(limitations),
            sources=tuple(uniq_sources),
        )
