from collections.abc import Iterable
from dataclasses import dataclass, replace
from datetime import date, datetime, time, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30), "IST")


@dataclass(frozen=True, slots=True)
class Bar:
    """One bar. `ts` is the bar's open time, timezone-aware; daily bars are stamped 09:15 IST."""

    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    oi: float | None = None
    delivery_qty: float | None = None


@dataclass(frozen=True)
class SessionCalendar:
    """NSE cash and F&O session: 09:15-15:30 IST on weekdays that are not holidays.

    shortcut: holidays are passed in; swap for the platform trading calendar when it lands.
    """

    holidays: frozenset[date] = frozenset()
    open: time = time(9, 15)
    close: time = time(15, 30)

    def session_date(self, ts: datetime) -> date | None:
        """The trading date a bar belongs to, or None when it falls outside any session."""
        local = ts.astimezone(IST)
        day = local.date()
        if day.weekday() >= 5 or day in self.holidays:
            return None
        if not self.open <= local.time().replace(tzinfo=None) < self.close:
            return None
        return day


def adjust_splits(bars: Iterable[Bar], splits: Iterable[tuple[date, float]]) -> list[Bar]:
    """Back-adjust for splits and bonuses: `(ex_date, factor)`, factor 2.0 for a 1:2 split.

    Bars before the ex-date get prices divided, and volume and delivery multiplied, by the factor.
    """
    splits = list(splits)
    out: list[Bar] = []
    for bar in bars:
        f = 1.0
        day = bar.ts.astimezone(IST).date()
        for ex, factor in splits:
            if day < ex:
                f *= factor
        out.append(
            bar
            if f == 1.0
            else replace(
                bar,
                open=bar.open / f,
                high=bar.high / f,
                low=bar.low / f,
                close=bar.close / f,
                volume=bar.volume * f,
                delivery_qty=None if bar.delivery_qty is None else bar.delivery_qty * f,
            )
        )
    return out
