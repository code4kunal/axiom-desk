"""Trading calendar: sessions per segment, exchange holidays, and special sessions (R4, R5).

Governed by KTD5 (fixed IST offset) and KTD11 (CalendarHorizonExceeded).
"""

import csv
import importlib.resources
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from io import StringIO

from axiom_core.authz import Refused
from axiom_core.envelope import Source

from axiom_data.pointintime import (
    IST,
    NaiveTimestampRefused,
    RuleUnknown,
)

COVERAGE_START: date = date(2019, 1, 1)
COVERAGE_END: date = date(2026, 12, 31)


class CalendarHorizonExceeded(RuleUnknown):
    """Raised when date is past covered holiday horizon or before history start (R5, B3)."""

    def __init__(self, asked_date: date, horizon: date) -> None:
        # horizon is the boundary that was crossed: COVERAGE_START when asked_date is before it.
        where = "before the start of" if asked_date < horizon else "past the end of"
        Refused.__init__(
            self,
            f"calendar horizon exceeded: {asked_date} is {where} published holiday coverage "
            f"{horizon}",
        )
        self.rule = "trading_calendar"
        self.on = asked_date
        self.asked_date = asked_date
        self.horizon = horizon


@dataclass(frozen=True)
class Session:
    """Trading session with start, exclusive end, and session type."""

    start: datetime
    end: datetime
    is_regular: bool = True
    session_name: str | None = None

    def __post_init__(self) -> None:
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise NaiveTimestampRefused("naive session timestamp is refused")
        if self.start >= self.end:
            raise ValueError(f"start ({self.start}) must precede end ({self.end})")


class TradingCalendar:
    """Trading calendar for Indian markets across segments."""

    def __init__(
        self,
        *,
        holidays: dict[str, set[date]] | None = None,
        special_sessions: dict[tuple[str, date], Session] | None = None,
        session_hours: dict[str, tuple[time, time]] | None = None,
        start_date: date | None = None,
        horizon_date: date | None = None,
    ) -> None:
        # Provenance of the reference rows (R10); empty when the caller injects its own data.
        self.limitations: tuple[str, ...] = ()
        self.sources: tuple[Source, ...] = ()
        if holidays is None or special_sessions is None or session_hours is None:
            hols, specials, hours, rows = self._load_from_reference()
            self._holidays = holidays if holidays is not None else hols
            self._special_sessions = special_sessions if special_sessions is not None else specials
            self._session_hours = session_hours if session_hours is not None else hours
            if any(not r["verified_against"].strip() for r in rows):
                self.limitations += ("unverified rule",)
            if any(r["published_at_synthetic"].strip() == "true" for r in rows):
                self.limitations += ("synthetic publication date",)
            row_sources = dict.fromkeys(
                (r["source"].strip(), r["licence_scope"].strip()) for r in rows
            )
            self.sources = tuple(Source(n, s) for n, s in row_sources)
        else:
            self._holidays = holidays
            self._special_sessions = special_sessions
            self._session_hours = session_hours
        self._start_date = start_date or COVERAGE_START
        self._horizon_date = horizon_date or COVERAGE_END

    @classmethod
    def _load_from_reference(
        cls,
    ) -> tuple[
        dict[str, set[date]],
        dict[tuple[str, date], Session],
        dict[str, tuple[time, time]],
        list[dict[str, str]],
    ]:
        ref_pkg = importlib.resources.files("axiom_data.reference")
        rows: list[dict[str, str]] = []

        # 1. Holidays
        holidays: dict[str, set[date]] = {}
        h_text = ref_pkg.joinpath("holidays.csv").read_text(encoding="utf-8")
        h_reader = csv.DictReader(StringIO(h_text))
        for row in h_reader:
            rows.append(row)
            seg = row["segment"].strip()
            d = date.fromisoformat(row["date"].strip())
            holidays.setdefault(seg, set()).add(d)

        # 2. Special sessions
        special_sessions: dict[tuple[str, date], Session] = {}
        sp_text = ref_pkg.joinpath("special_sessions.csv").read_text(encoding="utf-8")
        sp_reader = csv.DictReader(StringIO(sp_text))
        for row in sp_reader:
            rows.append(row)
            seg = row["segment"].strip()
            d = date.fromisoformat(row["date"].strip())
            o_time = time.fromisoformat(row["open_time"].strip())
            c_time = time.fromisoformat(row["close_time"].strip())
            start_dt = datetime.combine(d, o_time, tzinfo=IST)
            end_dt = datetime.combine(d, c_time, tzinfo=IST)
            s_name = row.get("session_name", "").strip() or None
            special_sessions[(seg, d)] = Session(
                start=start_dt, end=end_dt, is_regular=False, session_name=s_name
            )

        # 3. Session hours
        session_hours: dict[str, tuple[time, time]] = {}
        sh_text = ref_pkg.joinpath("session_hours.csv").read_text(encoding="utf-8")
        sh_reader = csv.DictReader(StringIO(sh_text))
        for row in sh_reader:
            seg = row["segment"].strip()
            o_time = time.fromisoformat(row["open_time"].strip())
            c_time = time.fromisoformat(row["close_time"].strip())
            session_hours[seg] = (o_time, c_time)

        return holidays, special_sessions, session_hours, rows

    @property
    def horizon(self) -> date:
        return self._horizon_date

    @property
    def start_date(self) -> date:
        return self._start_date

    def _check_horizon(self, d: date) -> None:
        if d < self._start_date:
            raise CalendarHorizonExceeded(d, self._start_date)
        if d > self._horizon_date:
            raise CalendarHorizonExceeded(d, self._horizon_date)

    def _check_segment(self, segment: str, d: date) -> None:
        # No holiday data means we cannot tell a holiday from a trading day (typo or no rows).
        if segment not in self._holidays:
            raise RuleUnknown(f"holidays for segment {segment!r}", d)

    def is_regular_session_day(self, segment: str, d: date) -> bool:
        """Check if d is a regular trading session day (weekday and not an exchange holiday)."""
        self._check_horizon(d)
        self._check_segment(segment, d)
        if d.weekday() >= 5:  # Saturday or Sunday
            return False
        return d not in self._holidays.get(segment, set())

    def get_session(self, segment: str, d: date) -> Session | None:
        """Return the trading session on date d, or None if market is closed all day."""
        self._check_horizon(d)
        self._check_segment(segment, d)
        # Check special session first
        if (segment, d) in self._special_sessions:
            return self._special_sessions[(segment, d)]

        if not self.is_regular_session_day(segment, d):
            return None

        hours = self._session_hours.get(segment, (time(9, 15), time(15, 30)))
        start_dt = datetime.combine(d, hours[0], tzinfo=IST)
        end_dt = datetime.combine(d, hours[1], tzinfo=IST)
        return Session(start=start_dt, end=end_dt, is_regular=True)

    def is_inside_session(self, segment: str, ts: datetime) -> bool:
        """Check whether timestamp ts is inside an active trading session."""
        if ts.tzinfo is None:
            raise NaiveTimestampRefused("naive timestamp is refused")
        ts_ist = ts.astimezone(IST)
        session = self.get_session(segment, ts_ist.date())
        if session is None:
            return False
        return session.start <= ts_ist < session.end

    def session_containing(self, segment: str, ts: datetime) -> Session | None:
        """Return the session containing ts, or None."""
        if self.is_inside_session(segment, ts):
            return self.get_session(segment, ts.astimezone(IST).date())
        return None

    def previous_session(self, segment: str, ts: datetime) -> Session:
        """Return the latest session before ts."""
        if ts.tzinfo is None:
            raise NaiveTimestampRefused("naive timestamp is refused")
        ts_ist = ts.astimezone(IST)
        d = ts_ist.date()
        today_session = self.get_session(segment, d)
        if today_session is not None and ts_ist >= today_session.end:
            return today_session

        # Search backward
        curr = d - timedelta(days=1)
        while curr >= self._start_date:
            session = self.get_session(segment, curr)
            if session is not None:
                return session
            curr -= timedelta(days=1)
        raise CalendarHorizonExceeded(curr, self._start_date)

    def next_session(self, segment: str, ts: datetime) -> Session:
        """Return the earliest session starting strictly after ts."""
        if ts.tzinfo is None:
            raise NaiveTimestampRefused("naive timestamp is refused")
        ts_ist = ts.astimezone(IST)
        d = ts_ist.date()
        today_session = self.get_session(segment, d)
        if today_session is not None and ts_ist < today_session.start:
            return today_session

        # Search forward
        curr = d + timedelta(days=1)
        while curr <= self._horizon_date:
            session = self.get_session(segment, curr)
            if session is not None:
                return session
            curr += timedelta(days=1)
        raise CalendarHorizonExceeded(curr, self._horizon_date)

    def sessions_in_range(self, segment: str, start: date, end: date) -> list[Session]:
        """Return all sessions in the inclusive date range [start, end]."""
        self._check_horizon(start)
        self._check_horizon(end)
        if start > end:
            return []
        res: list[Session] = []
        curr = start
        while curr <= end:
            s = self.get_session(segment, curr)
            if s is not None:
                res.append(s)
            curr += timedelta(days=1)
        return res

    def previous_regular_session_day(self, segment: str, d: date) -> date:
        """Return d if regular session day, else closest prior regular session day (KTD3)."""
        self._check_horizon(d)
        curr = d
        while curr >= self._start_date:
            if self.is_regular_session_day(segment, curr):
                return curr
            curr -= timedelta(days=1)
        raise CalendarHorizonExceeded(curr, self._start_date)
